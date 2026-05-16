"""
Batch engine bridge.

Wraps execution of zerolatch.cmd with proper parameter handling.
This is the ONLY module that directly interacts with the batch engine.
zerolatch.cmd is NEVER modified — this module only calls it.
"""

from pathlib import Path
from typing import Callable, Optional

from app.backend.config import BATCH_FILE, PROJECT_ROOT
from app.backend.admin import is_admin
from app.backend.logger import LogService
from app.backend.network import check_connectivity
from app.backend.process_manager import ProcessManager, OperationResult, OperationState


# Valid parameters for the batch engine
VALID_PARAMS = {
    "/act": "Configure IDM",
    "/frz": "Preserve Evaluation",
    "/res": "Reset Configuration/Trial",
}

# Parameters that require network access
NETWORK_REQUIRED = {"/act", "/frz"}

# Singleton process manager for engine operations
_process_manager = ProcessManager()


def get_process_manager() -> ProcessManager:
    """Get the engine's process manager instance."""
    return _process_manager


def _build_command(parameter: str = "") -> str:
    """
    Build the full command string for executing zerolatch.cmd.

    Uses cmd.exe with UTF-8 code page (65001) for proper encoding.
    """
    if parameter:
        return f'cmd.exe /c "chcp 65001 >nul && "{BATCH_FILE}" {parameter}"'
    return f'cmd.exe /c "chcp 65001 >nul && "{BATCH_FILE}""'


def validate_engine() -> OperationResult:
    """
    Check that the batch engine file exists and is accessible.

    Returns:
        OperationResult indicating engine readiness.
    """
    if not BATCH_FILE.exists():
        return OperationResult(
            success=False,
            message=f"Engine file not found: {BATCH_FILE}",
            state=OperationState.FAILED,
        )
    return OperationResult(
        success=True,
        message="Engine ready",
        state=OperationState.COMPLETED,
    )


def run_engine(
    parameter: str,
    on_complete: Optional[Callable[[OperationResult], None]] = None,
    on_output: Optional[Callable[[str], None]] = None,
    on_state_change: Optional[Callable[[OperationState], None]] = None,
) -> Optional[OperationResult]:
    """
    Execute the batch engine with the given parameter.

    Performs pre-flight checks (engine exists, admin rights, network)
    then delegates to the process manager for async execution.

    Args:
        parameter: Engine parameter ("/act", "/frz", "/res").
        on_complete: Called when operation finishes.
        on_output: Called for each line of output.
        on_state_change: Called when operation state changes.

    Returns:
        OperationResult if a pre-flight check fails (synchronous failure),
        None if the operation was launched asynchronously.
    """
    logger = LogService.get_instance()

    # Validate engine exists
    engine_check = validate_engine()
    if not engine_check.success:
        logger.error(engine_check.message)
        if on_complete:
            on_complete(engine_check)
        return engine_check

    # Validate parameter
    if parameter not in VALID_PARAMS:
        result = OperationResult(
            success=False,
            message=f"Invalid engine parameter: {parameter}",
            state=OperationState.FAILED,
        )
        if on_complete:
            on_complete(result)
        return result

    # Check admin privileges
    if not is_admin():
        result = OperationResult(
            success=False,
            message="Administrator privileges are required for this operation.",
            state=OperationState.FAILED,
        )
        logger.warning("Operation attempted without admin privileges")
        if on_complete:
            on_complete(result)
        return result

    # Check network for online operations
    if parameter in NETWORK_REQUIRED:
        net_result = check_connectivity()
        if not net_result.success:
            logger.warning(f"Network check failed for {parameter}")
            if on_complete:
                on_complete(net_result)
            return net_result

    # Build command and execute asynchronously
    command = _build_command(parameter)
    logger.info(f"Executing engine: zerolatch.cmd {parameter}")

    _process_manager.run_async(
        command=command,
        cwd=PROJECT_ROOT,
        on_complete=on_complete,
        on_output=on_output,
        on_state_change=on_state_change,
    )

    return None  # Indicates async launch succeeded


def cancel_engine_op():
    """Cancel the currently running engine operation if any."""
    _process_manager.cancel()


def activate_idm(
    on_complete: Optional[Callable[[OperationResult], None]] = None,
    on_output: Optional[Callable[[str], None]] = None,
    on_state_change: Optional[Callable[[OperationState], None]] = None,
) -> Optional[OperationResult]:
    """Configure IDM with a generated registration token."""
    return run_engine("/act", on_complete, on_output, on_state_change)


def freeze_trial(
    on_complete: Optional[Callable[[OperationResult], None]] = None,
    on_output: Optional[Callable[[str], None]] = None,
    on_state_change: Optional[Callable[[OperationState], None]] = None,
) -> Optional[OperationResult]:
    """preserve IDM trial period permanently."""
    return run_engine("/frz", on_complete, on_output, on_state_change)


def reset_activation(
    on_complete: Optional[Callable[[OperationResult], None]] = None,
    on_output: Optional[Callable[[str], None]] = None,
    on_state_change: Optional[Callable[[OperationState], None]] = None,
) -> Optional[OperationResult]:
    """Reset all IDM Configuration and trial data."""
    return run_engine("/res", on_complete, on_output, on_state_change)
