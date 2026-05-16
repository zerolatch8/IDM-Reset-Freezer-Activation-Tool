"""
Centralized logging service.

Provides structured logging to both file and in-memory buffer.
The in-memory buffer allows the GUI to display real-time log entries
without reading from disk.
"""

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from dataclasses import dataclass, field

from app.backend.config import LOG_DIR, load_config


@dataclass
class LogEntry:
    """Structured log entry for GUI consumption."""
    timestamp: str
    level: str
    message: str


class LogService:
    """
    Thread-safe logging service with file output and in-memory buffer.

    Usage:
        logger = LogService.get_instance()
        logger.info("Operation completed")
        logger.error("Something went wrong")

        # GUI can subscribe to new entries
        logger.add_listener(my_callback)
    """

    _instance: Optional["LogService"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._listeners: List[Callable[[LogEntry], None]] = []
        self._buffer: List[LogEntry] = []
        self._buffer_lock = threading.Lock()
        self._max_buffer = 1000
        self._setup_file_logger()

    @classmethod
    def get_instance(cls) -> "LogService":
        """Get or create the singleton LogService instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _setup_file_logger(self):
        """Configure the Python logging module for file output."""
        LOG_DIR.mkdir(exist_ok=True)
        self._logger = logging.getLogger("IDMTool")
        self._logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        self._logger.handlers.clear()

        # File handler with daily rotation
        log_file = LOG_DIR / f"idm_manager_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
        )
        self._logger.addHandler(handler)

    def _is_enabled(self) -> bool:
        """Check if logging is enabled in config."""
        try:
            config = load_config()
            return config.get("logging_enabled", True)
        except Exception:
            return True

    def _emit(self, level: str, message: str):
        """Internal: create entry, write to file, notify listeners."""
        entry = LogEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level=level,
            message=message,
        )

        # Write to file if enabled
        if self._is_enabled():
            getattr(self._logger, level.lower(), self._logger.info)(message)

        # Add to in-memory buffer
        with self._buffer_lock:
            self._buffer.append(entry)
            if len(self._buffer) > self._max_buffer:
                self._buffer = self._buffer[-self._max_buffer:]

        # Notify GUI listeners
        for listener in self._listeners:
            try:
                listener(entry)
            except Exception:
                pass  # Never let a listener crash the logger

    def info(self, message: str):
        self._emit("INFO", message)

    def warning(self, message: str):
        self._emit("WARNING", message)

    def error(self, message: str):
        self._emit("ERROR", message)

    def debug(self, message: str):
        self._emit("DEBUG", message)

    def add_listener(self, callback: Callable[[LogEntry], None]):
        """Subscribe to new log entries (for GUI real-time display)."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[LogEntry], None]):
        """Unsubscribe from log entries."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def get_buffer(self) -> List[LogEntry]:
        """Get all entries currently in the in-memory buffer."""
        with self._buffer_lock:
            return list(self._buffer)

    def get_log_files(self) -> List[Path]:
        """List all log files sorted newest first."""
        if not LOG_DIR.exists():
            return []
        return sorted(LOG_DIR.glob("*.log"), reverse=True)

    def read_log_file(self, path: Path, tail: int = 100) -> List[str]:
        """Read the last N lines from a log file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return [line.rstrip() for line in lines[-tail:]]
        except IOError:
            return []

    def clear_logs(self) -> bool:
        """Delete all log files."""
        try:
            for log_file in LOG_DIR.glob("*.log"):
                log_file.unlink()
            self.info("All log files cleared")
            return True
        except Exception as e:
            self.error(f"Failed to clear logs: {e}")
            return False
