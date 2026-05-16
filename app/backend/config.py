"""
Configuration management service.

Handles loading, saving, and accessing application configuration.
All paths are resolved relative to the project root for PyInstaller compatibility.
"""

import json
from pathlib import Path
from typing import Any, Optional


# Resolve project root: works both in dev and PyInstaller frozen mode
if getattr(__import__('sys'), 'frozen', False):
    # Running as PyInstaller bundle
    PROJECT_ROOT = Path(__import__('sys').executable).parent
else:
    # Running as script - project root is two levels up from app/backend/
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

VERSION = "1.0.0"

# Path constants
CONFIG_FILE = PROJECT_ROOT / "config.json"
LOG_DIR = PROJECT_ROOT / "logs"
BACKUP_DIR = PROJECT_ROOT / "IDM_Backup"
BATCH_FILE = PROJECT_ROOT / "zerolatch.cmd"

# Default configuration
DEFAULT_CONFIG = {
    "language": "en",
    "auto_backup": True,
    "logging_enabled": True,
}


def ensure_directories():
    """Create required directories if they don't exist."""
    LOG_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)


def load_config() -> dict:
    """
    Load configuration from disk, merging with defaults for missing keys.

    Returns:
        dict: Complete configuration with all keys guaranteed present.
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                return {**DEFAULT_CONFIG, **user_config}
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """
    Save configuration to disk.

    Args:
        config: Configuration dictionary to persist.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except IOError:
        return False


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a single configuration value."""
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> bool:
    """Set a single configuration value and save."""
    config = load_config()
    config[key] = value
    return save_config(config)
