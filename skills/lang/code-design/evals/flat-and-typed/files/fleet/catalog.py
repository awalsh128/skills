"""The catalog of services under services/."""

from pathlib import Path


def service_folders(root: Path) -> list[Path]:
    """Every folder under services/, in name order."""
    return sorted(path for path in (root / "services").iterdir() if path.is_dir())
