"""Load and parse SysML v2 model files via sysml2py."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def find_models(directory: str | Path) -> list[Path]:
    """Recursively find all ``.sysml`` files under *directory*."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    return sorted(directory.rglob("*.sysml"))


def load(path: str | Path) -> Any:
    """Load a ``.sysml`` file and return the parsed model.

    Uses sysml2py's grammar-based parser. Raises on parse errors.
    """
    import sysml2py

    path = Path(path)
    text = path.read_text()
    return sysml2py.loads(text)


def loads(text: str) -> Any:
    """Parse a SysML v2 model from a string.

    Uses sysml2py's grammar-based parser. Raises on parse errors.
    """
    import sysml2py

    return sysml2py.loads(text)
