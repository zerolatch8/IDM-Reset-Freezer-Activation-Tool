"""
Administrator privilege management.

Handles checking and requesting admin rights via Windows UAC.
"""

import ctypes
import os
import sys
from typing import Tuple

from app.backend.logger import LogService


def is_admin() -> bool:
    """
    Check if the current process has administrator privileges.

    Returns:
        bool: True if running as admin, False otherwise.
    """
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def request_admin_elevation() -> Tuple[bool, str]:
    """
    Attempt to re-launch the current script with administrator privileges.

    Uses Windows ShellExecuteW with 'runas' verb to trigger UAC prompt.
    If successful, the current process should exit and a new elevated
    process takes over.

    Returns:
        Tuple[bool, str]: (success, message)
            - (True, msg) if elevation was initiated (caller should exit)
            - (False, msg) if elevation was declined or failed
    """
    logger = LogService.get_instance()

    if is_admin():
        return True, "Already running with administrator privileges."

    logger.info("Requesting admin privileges via UAC")

    try:
        script_path = os.path.abspath(sys.argv[0])

        # Use ShellExecuteW to trigger UAC elevation
        result = ctypes.windll.shell32.ShellExecuteW(
            None,               # hwnd
            "runas",            # verb - triggers UAC
            sys.executable,     # executable (python.exe or frozen .exe)
            f'"{script_path}"', # parameters
            None,               # directory
            1,                  # SW_SHOWNORMAL
        )

        # ShellExecuteW returns > 32 on success
        if result > 32:
            logger.info("Admin elevation initiated successfully")
            return True, "Elevation initiated. Restarting with admin privileges."
        else:
            logger.warning("Admin elevation failed or was cancelled by user")
            return False, "UAC was cancelled or elevation failed."

    except Exception as e:
        logger.error(f"Failed to elevate privileges: {e}")
        return False, f"Elevation error: {e}"


def get_admin_status_text() -> str:
    """Get a human-readable admin status string for the status bar."""
    return "Administrator" if is_admin() else "Standard User"
