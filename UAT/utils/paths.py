"""
utils/paths.py
===============
Path resolution helpers.

These helpers make sure config files and other shared resources are
found regardless of what the current working directory is.  This is
important when the automation is launched from an IDE (CWD = project
root), from the command line in a subfolder, or as a scheduled task
(CWD = system32 on Windows).

Usage:
    from utils.paths import get_config_path
    path = get_config_path("email_recipients.txt")
    # → <project-root>/config/email_recipients.txt
"""

from pathlib import Path


# Project root is two levels up from this file:
#   <project_root>/utils/paths.py   →   <project_root>
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


def get_config_path(filename: str) -> str:
    """
    Return the absolute path to a file inside the <project_root>/config/
    directory.

    Args:
        filename: Name of the file inside the config directory
                  (e.g. "email_recipients.txt").

    Returns:
        Absolute path as a string.
    """
    return str(PROJECT_ROOT / "config" / filename)