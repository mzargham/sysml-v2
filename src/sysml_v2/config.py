"""Load project-level configuration from sysml.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILENAME = "sysml.toml"

# Backends supported by ``sysml serve``
BACKENDS = ("flexo", "gearshift")


@dataclass(frozen=True)
class ServerConfig:
    backend: str = "flexo"
    url: str = "http://localhost:8083"


@dataclass(frozen=True)
class LibraryConfig:
    path: str = "lib/SysML-v2-Release"


@dataclass(frozen=True)
class ValidateConfig:
    mode: str = "local"


@dataclass(frozen=True)
class ProjectConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    library: LibraryConfig = field(default_factory=LibraryConfig)
    validate: ValidateConfig = field(default_factory=ValidateConfig)


def find_config(start: Path | None = None) -> Path | None:
    """Walk up from *start* looking for ``sysml.toml``. Return path or None."""
    current = (start or Path.cwd()).resolve()
    for directory in (current, *current.parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_config(start: Path | None = None) -> ProjectConfig:
    """Load project config from the nearest ``sysml.toml``, or return defaults."""
    path = find_config(start)
    if path is None:
        return ProjectConfig()

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    server_raw = raw.get("server", {})
    library_raw = raw.get("library", {})
    validate_raw = raw.get("validate", {})

    return ProjectConfig(
        server=ServerConfig(
            backend=server_raw.get("backend", "flexo"),
            url=server_raw.get("url", "http://localhost:8083"),
        ),
        library=LibraryConfig(
            path=library_raw.get("path", "lib/SysML-v2-Release"),
        ),
        validate=ValidateConfig(
            mode=validate_raw.get("mode", "local"),
        ),
    )
