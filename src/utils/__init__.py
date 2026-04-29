"""
Utility functions for the project.
"""

from pathlib import Path


def get_project_root() -> Path:
    """Return project root directory."""
    return Path(__file__).parent.parent.parent


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not."""
    path.mkdir(parents=True, exist_ok=True)
    return path