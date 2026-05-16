"""
IDM status checking service.

Queries the Windows registry directly (via batch subprocess) to determine
the current IDM installation and Configuration state.
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.backend.config import PROJECT_ROOT
from app.backend.logger import LogService
from app.backend.process_manager import OperationResult, OperationState


@dataclass
class IDMStatus:
    """Structured representation of IDM's current state."""
    installed: bool
    install_path: Optional[str] = None
    version: Optional[str] = None
    is_registered: bool = False
    is_trial: bool = False
    Token: Optional[str] = None
    trial_data: Optional[str] = None
    status_text: str = "Unknown"


def check_idm_installed() -> Optional[str]:
    """
    Check if IDM is installed by looking for IDMan.exe.

    Returns:
        Path string to IDMan.exe if found, None otherwise.
    """
    paths = [
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", ""),
            "Internet Download Manager", "IDMan.exe"
        ),
        os.path.join(
            os.environ.get("PROGRAMFILES", ""),
            "Internet Download Manager", "IDMan.exe"
        ),
    ]

    for path in paths:
        if os.path.exists(path):
            return path
    return None


def get_idm_status() -> IDMStatus:
    """
    Get the complete current status of IDM by querying the registry.

    Creates a temporary batch file that queries relevant registry keys
    and parses the structured output. This mirrors the original
    check_idm_status() logic exactly.

    Returns:
        IDMStatus dataclass with all detected information.
    """
    logger = LogService.get_instance()
    logger.info("Checking IDM status")

    # Check installation
    idm_path = check_idm_installed()
    if not idm_path:
        logger.info("IDM not found on system")
        return IDMStatus(
            installed=False,
            status_text="IDM is not installed on this system.",
        )

    # Query registry for Configuration state
    temp_batch = PROJECT_ROOT / "check_idm_temp.bat"

    try:
        with open(temp_batch, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("chcp 65001 >nul\n")
            f.write("setlocal\n")
            f.write(
                "for /f \"tokens=2*\" %%a in "
                "('reg query \"HKCU\\Software\\DownloadManager\" /v Serial 2^>nul') "
                "do set \"Token=%%b\"\n"
            )
            f.write(
                "for /f \"tokens=2*\" %%a in "
                "('reg query \"HKCU\\Software\\DownloadManager\" /v tvfrdt 2^>nul') "
                "do set \"trial=%%b\"\n"
            )
            f.write(
                "for /f \"tokens=2*\" %%a in "
                "('reg query \"HKCU\\Software\\DownloadManager\" /v idmvers 2^>nul') "
                "do set \"version=%%b\"\n"
            )
            f.write("echo IDM_STATUS_BEGIN\n")
            f.write("if defined version echo Version: %version%\n")
            f.write("if defined Token echo Token: %Token%\n")
            f.write("if defined trial echo Trial: %trial%\n")
            f.write(
                "if not defined Token if not defined trial "
                "echo Status: Unknown\n"
            )
            f.write("echo IDM_STATUS_END\n")

        result = subprocess.run(
            ["cmd.exe", "/c", str(temp_batch)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output = result.stdout

        # Parse structured output
        status = IDMStatus(installed=True, install_path=idm_path)

        if "IDM_STATUS_BEGIN" in output:
            section = output.split("IDM_STATUS_BEGIN")[1].split("IDM_STATUS_END")[0]

            for line in section.strip().split("\n"):
                line = line.strip()
                if line.startswith("Version:"):
                    status.version = line.split(":", 1)[1].strip()
                elif line.startswith("Token:"):
                    status.Token = line.split(":", 1)[1].strip()
                    status.is_registered = True
                elif line.startswith("Trial:"):
                    status.trial_data = line.split(":", 1)[1].strip()
                    status.is_trial = True

        # Set human-readable status
        if status.is_registered:
            status.status_text = "Registered"
            logger.info("IDM is registered")
        elif status.is_trial:
            status.status_text = "Trial Mode"
            logger.info("IDM is in trial mode")
        else:
            status.status_text = "Unknown"
            logger.warning("IDM status could not be determined")

        return status

    except Exception as e:
        logger.error(f"Error checking IDM status: {e}")
        return IDMStatus(
            installed=True,
            install_path=idm_path,
            status_text=f"Error: {e}",
        )
    finally:
        # Always clean up temp file
        if temp_batch.exists():
            try:
                temp_batch.unlink()
            except OSError:
                pass
