"""
Network connectivity and update checking services.
"""

import subprocess
from typing import Optional

from app.backend.config import VERSION
from app.backend.logger import LogService
from app.backend.process_manager import OperationResult, OperationState


GITHUB_REPO_URL = "https://github.com/zerolatch8/IDM-Reset-Freezer-Activation-Tool"
IDM_DOWNLOAD_URL = "https://www.internetdownloadmanager.com/download.html"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/zerolatch38/IDM-Preserver-Configuration-Tool/main/version.txt"


def check_connectivity(host: str = "github.com") -> OperationResult:
    """
    Check network connectivity by pinging a host.

    Args:
        host: Hostname to ping.

    Returns:
        OperationResult indicating connectivity status.
    """
    logger = LogService.get_instance()

    try:
        result = subprocess.run(
            ["ping", "-n", "1", host],
            capture_output=True,
            timeout=5,
        )

        if result.returncode == 0:
            return OperationResult(
                success=True,
                message="Network connection OK",
                state=OperationState.COMPLETED,
            )
        else:
            logger.warning(f"Ping to {host} failed")
            return OperationResult(
                success=False,
                message=f"Cannot reach {host}. Check your internet connection.",
                state=OperationState.FAILED,
            )

    except subprocess.TimeoutExpired:
        logger.warning(f"Ping to {host} timed out")
        return OperationResult(
            success=False,
            message="Network check timed out.",
            state=OperationState.FAILED,
        )
    except Exception as e:
        logger.error(f"Network check error: {e}")
        return OperationResult(
            success=False,
            message=f"Network error: {e}",
            state=OperationState.FAILED,
        )


def check_for_updates() -> OperationResult:
    """
    Check GitHub for newer version.

    Returns:
        OperationResult with version comparison in the message and
        the latest version string in the output field.
    """
    logger = LogService.get_instance()
    logger.info("Checking for updates")

    # First check connectivity
    net = check_connectivity()
    if not net.success:
        return net

    try:
        result = subprocess.run(
            [
                "powershell", "-Command",
                f"(Invoke-WebRequest -Uri '{VERSION_CHECK_URL}' "
                f"-UseBasicParsing).Content.Trim()"
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            latest = result.stdout.strip()
            is_up_to_date = (VERSION == latest)

            if is_up_to_date:
                msg = f"You are running the latest version ({VERSION})."
                logger.info(f"Up to date: v{VERSION}")
            else:
                msg = f"Update available! Current: {VERSION}, Latest: {latest}"
                logger.info(f"Update available: v{latest}")

            return OperationResult(
                success=True,
                message=msg,
                output=latest,  # Latest version string
                state=OperationState.COMPLETED,
            )
        else:
            logger.warning("Failed to fetch version from GitHub")
            return OperationResult(
                success=False,
                message="Failed to check for updates.",
                state=OperationState.FAILED,
            )

    except subprocess.TimeoutExpired:
        logger.warning("Update check timed out")
        return OperationResult(
            success=False,
            message="Update check timed out.",
            state=OperationState.FAILED,
        )
    except Exception as e:
        logger.error(f"Update check error: {e}")
        return OperationResult(
            success=False,
            message=f"Error: {e}",
            state=OperationState.FAILED,
        )


