
from pathlib import Path

def get_project_root(marker=".project_root") -> Path:
    """Return the project root Path by searching upward for a marker file."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"Marker '{marker}' not found.")


ROOT = get_project_root()
