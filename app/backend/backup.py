"""
Backup and restore service for IDM registry settings.

Handles exporting and importing registry keys via reg.exe,
with backup file management.
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.backend.config import BACKUP_DIR, PROJECT_ROOT
from app.backend.logger import LogService
from app.backend.process_manager import OperationResult, OperationState


@dataclass
class BackupInfo:
    """Metadata about a backup file."""
    path: Path
    name: str
    date: str
    size_kb: float


def list_backups() -> List[BackupInfo]:
    """
    List all available backup files, sorted newest first.

    Returns:
        List of BackupInfo objects.
    """
    BACKUP_DIR.mkdir(exist_ok=True)

    backup_files = sorted(
        [f for f in BACKUP_DIR.iterdir()
         if f.name.startswith("IDM_Settings_") and f.suffix == ".reg"],
        reverse=True,
    )

    results = []
    for f in backup_files:
        stat = f.stat()
        results.append(BackupInfo(
            path=f,
            name=f.name,
            date=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            size_kb=stat.st_size / 1024,
        ))

    return results


def create_backup() -> OperationResult:
    """
    Export current IDM registry settings to a .reg file.

    Returns:
        OperationResult with backup file path in the output field.
    """
    logger = LogService.get_instance()
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"IDM_Settings_{timestamp}.reg"

    logger.info(f"Creating backup: {backup_file}")

    # Create temp batch for reg export with UTF-8
    temp_batch = PROJECT_ROOT / "backup_idm_temp.bat"

    try:
        with open(temp_batch, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("chcp 65001 >nul\n")
            f.write(
                f'reg export "HKCU\\Software\\DownloadManager" "{backup_file}" /y\n'
            )

        result = subprocess.run(
            ["cmd.exe", "/c", str(temp_batch)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode == 0 and backup_file.exists():
            logger.info(f"Backup created: {backup_file}")
            return OperationResult(
                success=True,
                message=f"Backup saved to: {backup_file.name}",
                output=str(backup_file),
                state=OperationState.COMPLETED,
            )
        else:
            logger.error("Backup command failed")
            return OperationResult(
                success=False,
                message="Failed to create backup. Are admin privileges active?",
                error=result.stderr or "",
                state=OperationState.FAILED,
            )

    except Exception as e:
        logger.error(f"Backup error: {e}")
        return OperationResult(
            success=False,
            message=f"Backup error: {e}",
            state=OperationState.FAILED,
        )
    finally:
        if temp_batch.exists():
            try:
                temp_batch.unlink()
            except OSError:
                pass


def restore_backup(backup_path: Path) -> OperationResult:
    """
    Import a .reg backup file to restore IDM settings.

    Args:
        backup_path: Path to the .reg file to restore.

    Returns:
        OperationResult indicating success or failure.
    """
    logger = LogService.get_instance()

    if not backup_path.exists():
        return OperationResult(
            success=False,
            message=f"Backup file not found: {backup_path}",
            state=OperationState.FAILED,
        )

    logger.info(f"Restoring from: {backup_path}")

    try:
        result = subprocess.run(
            ["reg", "import", str(backup_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode == 0:
            logger.info("Restore completed successfully")
            return OperationResult(
                success=True,
                message=f"Restored from: {backup_path.name}",
                state=OperationState.COMPLETED,
            )
        else:
            logger.error("Restore command failed")
            return OperationResult(
                success=False,
                message="Failed to restore backup.",
                error=result.stderr or "",
                state=OperationState.FAILED,
            )

    except Exception as e:
        logger.error(f"Restore error: {e}")
        return OperationResult(
            success=False,
            message=f"Restore error: {e}",
            state=OperationState.FAILED,
        )


def delete_backup(backup_path: Path) -> OperationResult:
    """Delete a specific backup file."""
    logger = LogService.get_instance()

    try:
        if backup_path.exists():
            backup_path.unlink()
            logger.info(f"Deleted backup: {backup_path.name}")
            return OperationResult(
                success=True,
                message=f"Deleted: {backup_path.name}",
                state=OperationState.COMPLETED,
            )
        return OperationResult(
            success=False,
            message="File not found.",
            state=OperationState.FAILED,
        )
    except Exception as e:
        logger.error(f"Delete backup error: {e}")
        return OperationResult(
            success=False,
            message=f"Error: {e}",
            state=OperationState.FAILED,
        )
