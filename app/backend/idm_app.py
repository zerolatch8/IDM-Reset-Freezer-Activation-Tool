"""
IDM Application control.

Handles restarting the IDM process.
"""

import subprocess
import time
from pathlib import Path
from app.backend.process_manager import OperationResult, OperationState
from app.backend.status import get_idm_status

def restart_idm(on_output=None) -> OperationResult:
    """Kill and relaunch the IDM process."""
    if on_output:
        on_output("Restarting IDM...")
        on_output("Killing IDMan.exe process if running...")

    try:
        # Kill the process
        subprocess.run(
            ["taskkill", "/F", "/IM", "IDMan.exe"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(1)

        # Find the path
        status = get_idm_status()
        idm_path = status.install_path

        if not idm_path or not Path(idm_path).exists():
            default_path = Path("C:\\Program Files (x86)\\Internet Download Manager\\IDMan.exe")
            if default_path.exists():
                idm_path = str(default_path)
            else:
                msg = "Could not find IDMan.exe to restart."
                if on_output:
                    on_output(msg)
                return OperationResult(False, msg, OperationState.FAILED)

        if on_output:
            on_output(f"Launching IDM from: {idm_path}")

        # Start the process
        subprocess.Popen(
            [idm_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return OperationResult(True, "IDM Restarted Successfully", OperationState.COMPLETED)
    except Exception as e:
        return OperationResult(False, f"Failed to restart IDM: {e}", OperationState.FAILED, str(e))
