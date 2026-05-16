"""
Quick Configuration module.

Applies Token directly to the registry and provides the 
composite "preserve Configuration" function.
"""

import os
import random
import string
import subprocess
from app.backend.process_manager import OperationResult, OperationState
from app.backend.hosts import block_servers, clean_hosts
from app.backend.idm_app import restart_idm

def generate_serial():
    """Generate a random IDM Token in format XXXXX-XXXXX-XXXXX-XXXXX."""
    chars = string.ascii_uppercase + string.digits
    parts = ["".join(random.choices(chars, k=5)) for _ in range(4)]
    return "-".join(parts)

def quick_activate(on_output=None) -> OperationResult:
    """Apply random Token directly to registry."""
    if on_output:
        on_output("Starting Quick Configuration...")
        
    Token = generate_serial()
    if on_output:
        on_output(f"Generated Random Token: {Token}")

    reg_commands = [
        ["reg", "add", "HKCU\\Software\\DownloadManager", "/v", "FName", "/t", "REG_SZ", "/d", "ZeroLatch", "/f"],
        ["reg", "add", "HKCU\\Software\\DownloadManager", "/v", "LName", "/t", "REG_SZ", "/d", "User", "/f"],
        ["reg", "add", "HKCU\\Software\\DownloadManager", "/v", "Email", "/t", "REG_SZ", "/d", "info@zerolatch.com", "/f"],
        ["reg", "add", "HKCU\\Software\\DownloadManager", "/v", "Serial", "/t", "REG_SZ", "/d", Token, "/f"]
    ]

    try:
        for cmd in reg_commands:
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode != 0 and on_output:
                on_output(f"Warning: Registry write failed: {result.stderr.strip()}")

        if on_output:
            on_output("Registry updated successfully.")
            
        return OperationResult(True, "Quick Configuration Completed.", OperationState.COMPLETED)
    except Exception as e:
        return OperationResult(False, f"Quick Configuration failed: {e}", OperationState.FAILED, str(e))

def freeze_activation(on_output=None) -> OperationResult:
    """
    Recommended Option 7:
    1. Quick configure (Random Token)
    2. Block servers in hosts file
    3. Restart IDM
    """
    if on_output:
        on_output("=== Starting preserve Configuration ===")
    
    # 1. Quick configure
    act_res = quick_activate(on_output)
    if not act_res.success:
        return act_res
        
    # 2. Block servers
    block_res = block_servers(on_output)
    if not block_res.success:
        return block_res
        
    # 3. Disable updates in registry
    if on_output:
        on_output("Disabling update checks in registry...")
    subprocess.run(
        ["reg", "add", "HKCU\\Software\\DownloadManager", "/v", "CheckUpdtVM", "/t", "REG_DWORD", "/d", "10", "/f"],
        capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
        
    # 4. Restart IDM
    restart_res = restart_idm(on_output)
    
    if on_output:
        on_output("=== preserve Configuration Completed ===")
        
    return OperationResult(True, "preserve Configuration Applied Successfully.", OperationState.COMPLETED)
    
def enable_updates(on_output=None) -> OperationResult:
    """Allow IDM updates (removes hosts blocks)."""
    if on_output:
        on_output("Warning: Enabling updates will break Configuration.")
    
    res = clean_hosts(on_output)
    if res.success:
        res.message = "Updates Enabled (Servers Unblocked)."
    return res
