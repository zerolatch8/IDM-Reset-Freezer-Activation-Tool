"""
Hosts file management.

Handles blocking and unblocking IDM validation servers.
"""

import os
from pathlib import Path
from app.backend.process_manager import OperationResult, OperationState

HOSTS_PATH = Path(os.environ.get("WINDIR", "C:\\Windows")) / "System32" / "drivers" / "etc" / "hosts"

IDM_SERVERS = [
    "registeridm.com",
    "www.registeridm.com",
    "internetdownloadmanager.com",
    "www.internetdownloadmanager.com",
    "internetdownloadmanager.net",
    "www.internetdownloadmanager.net",
    "star.internetdownloadmanager.com",
    "secure.internetdownloadmanager.com",
    "tonec.com",
    "www.tonec.com",
]

def clean_hosts(on_output=None) -> OperationResult:
    """Remove IDM servers from the hosts file."""
    if on_output:
        on_output("Cleaning IDM entries from hosts file...")

    try:
        if not HOSTS_PATH.exists():
            return OperationResult(True, "Hosts file not found. Nothing to clean.", OperationState.COMPLETED)

        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        new_lines = []
        cleaned_count = 0
        for line in lines:
            if any(server in line for server in IDM_SERVERS):
                cleaned_count += 1
                continue
            new_lines.append(line)

        if cleaned_count > 0:
            # Check if read-only
            if not os.access(HOSTS_PATH, os.W_OK):
                os.chmod(HOSTS_PATH, 0o666)
            
            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            if on_output:
                on_output(f"Removed {cleaned_count} IDM entries from hosts file.")

        return OperationResult(True, "Hosts file cleaned successfully.", OperationState.COMPLETED)
    except Exception as e:
        return OperationResult(False, f"Failed to clean hosts file: {e}", OperationState.FAILED, str(e))

def block_servers(on_output=None) -> OperationResult:
    """Add IDM servers to hosts file pointing to localhost."""
    clean_result = clean_hosts(on_output)
    if not clean_result.success:
        return clean_result

    if on_output:
        on_output("Blocking IDM validation servers in hosts file...")

    try:
        with open(HOSTS_PATH, "a", encoding="utf-8") as f:
            f.write("\n# Block IDM Validation Servers\n")
            for server in IDM_SERVERS:
                f.write(f"127.0.0.1\t{server}\n")
        
        if on_output:
            on_output(f"Blocked {len(IDM_SERVERS)} servers.")
            
        return OperationResult(True, "Servers blocked successfully.", OperationState.COMPLETED)
    except Exception as e:
        return OperationResult(False, f"Failed to block servers: {e}", OperationState.FAILED, str(e))
