"""SysML v2 toolchain — CLI and Python library for model development and analysis."""

__version__ = "0.1.0"

from sysml_v2.api.client import SysMLClient
from sysml_v2.parsing.loader import load, loads, find_models

__all__ = ["SysMLClient", "load", "loads", "find_models", "__version__"]
