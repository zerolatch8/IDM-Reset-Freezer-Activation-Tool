"""
Process manager for running batch operations in background threads.

Provides a safe, thread-aware execution layer between the GUI and
the batch engine (zerolatch.cmd). Prevents GUI freezing by running all
subprocess calls in worker threads with progress/output callbacks.
"""

import subprocess
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, List
from pathlib import Path

from app.backend.logger import LogService


class OperationState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationResult:
    """Structured result from any backend operation."""
    success: bool
    message: str
    exit_code: int = 0
    output: str = ""
    error: str = ""
    state: OperationState = OperationState.COMPLETED


class ProcessManager:
    """
    Thread-safe process manager for batch engine operations.

    Usage:
        pm = ProcessManager()

        def on_complete(result: OperationResult):
            print(f"Done: {result.message}")

        def on_output(line: str):
            print(f">> {line}")

        pm.run_async(
            command="zerolatch.cmd /act",
            on_complete=on_complete,
            on_output=on_output,
        )
    """

    def __init__(self):
        self._logger = LogService.get_instance()
        self._current_process: Optional[subprocess.Popen] = None
        self._current_thread: Optional[threading.Thread] = None
        self._state = OperationState.IDLE
        self._lock = threading.Lock()

    @property
    def state(self) -> OperationState:
        return self._state

    @property
    def is_busy(self) -> bool:
        return self._state == OperationState.RUNNING

    def run_sync(
        self,
        command: str,
        cwd: Optional[Path] = None,
        timeout: int = 300,
    ) -> OperationResult:
        """
        Run a command synchronously (blocking). Use for quick operations
        or when called from a worker thread already.

        Args:
            command: Full command string to execute.
            cwd: Working directory for the process.
            timeout: Maximum seconds to wait.

        Returns:
            OperationResult with output and exit code.
        """
        self._logger.info(f"Running sync: {command}")

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                cwd=cwd,
                timeout=timeout,
            )

            success = process.returncode == 0
            return OperationResult(
                success=success,
                message="Operation completed successfully" if success
                        else f"Operation completed with exit code {process.returncode}",
                exit_code=process.returncode,
                output=process.stdout or "",
                error=process.stderr or "",
                state=OperationState.COMPLETED,
            )

        except subprocess.TimeoutExpired:
            self._logger.error(f"Command timed out: {command}")
            return OperationResult(
                success=False,
                message="Operation timed out",
                exit_code=-1,
                state=OperationState.FAILED,
            )
        except Exception as e:
            self._logger.error(f"Command failed: {e}")
            return OperationResult(
                success=False,
                message=f"Error: {e}",
                exit_code=-1,
                state=OperationState.FAILED,
            )

    def run_async(
        self,
        command: str,
        cwd: Optional[Path] = None,
        on_complete: Optional[Callable[[OperationResult], None]] = None,
        on_output: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[OperationState], None]] = None,
        timeout: int = 300,
    ):
        """
        Run a command asynchronously in a background thread.

        Args:
            command: Full command string to execute.
            cwd: Working directory.
            on_complete: Callback when operation finishes (called from worker thread).
            on_output: Callback for each line of stdout (called from worker thread).
            on_state_change: Callback when state changes.
            timeout: Maximum seconds to wait.
        """
        with self._lock:
            if self._state == OperationState.RUNNING:
                if on_complete:
                    on_complete(OperationResult(
                        success=False,
                        message="Another operation is already running.",
                        state=OperationState.FAILED,
                    ))
                return

        def _worker():
            self._set_state(OperationState.RUNNING, on_state_change)
            self._logger.info(f"Running async: {command}")

            try:
                self._current_process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                    errors="replace",
                    cwd=cwd,
                )

                # Stream stdout line-by-line
                output_lines = []
                if self._current_process.stdout:
                    for line in self._current_process.stdout:
                        stripped = line.rstrip()
                        if stripped:
                            output_lines.append(stripped)
                            if on_output:
                                on_output(stripped)

                # Wait for process to finish
                self._current_process.wait(timeout=timeout)
                stderr = ""
                if self._current_process.stderr:
                    stderr = self._current_process.stderr.read()

                exit_code = self._current_process.returncode
                success = exit_code == 0

                if self._state == OperationState.CANCELLED:
                    result = OperationResult(
                        success=False,
                        message="Operation cancelled by user.",
                        exit_code=exit_code,
                        output="\n".join(output_lines),
                        error=stderr,
                        state=OperationState.CANCELLED,
                    )
                else:
                    result = OperationResult(
                        success=success,
                        message="Operation completed successfully" if success
                                else f"Completed with warnings (exit code: {exit_code})",
                        exit_code=exit_code,
                        output="\n".join(output_lines),
                        error=stderr,
                        state=OperationState.COMPLETED,
                    )

                self._logger.info(f"Async operation finished: exit_code={exit_code}")

            except subprocess.TimeoutExpired:
                if self._current_process:
                    self._current_process.kill()
                result = OperationResult(
                    success=False,
                    message="Operation timed out and was terminated.",
                    exit_code=-1,
                    state=OperationState.FAILED,
                )
                self._logger.error("Async operation timed out")

            except Exception as e:
                result = OperationResult(
                    success=False,
                    message=f"Error: {e}",
                    exit_code=-1,
                    state=OperationState.FAILED,
                )
                self._logger.error(f"Async operation error: {e}")

            finally:
                self._current_process = None
                final_state = result.state if result else OperationState.FAILED
                self._set_state(final_state, on_state_change)

                if on_complete:
                    on_complete(result)

        self._current_thread = threading.Thread(target=_worker, daemon=True)
        self._current_thread.start()

    def cancel(self):
        """Attempt to cancel the currently running operation and its children."""
        with self._lock:
            if self._current_process and self._state == OperationState.RUNNING:
                try:
                    pid = self._current_process.pid
                    self._state = OperationState.CANCELLED
                    self._logger.warning(f"Cancelling operation tree for PID {pid}")
                    # Kill the process and all child processes
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(pid)],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except Exception as e:
                    self._logger.error(f"Failed to cancel operation: {e}")

    def _set_state(
        self,
        state: OperationState,
        callback: Optional[Callable[[OperationState], None]] = None,
    ):
        self._state = state
        if callback:
            try:
                callback(state)
            except Exception:
                pass
