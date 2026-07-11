"""Closer to whom public-data policy model."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("closer-to-whom")
except PackageNotFoundError:  # pragma: no cover - editable source without metadata
    __version__ = "0.2.0"

__all__ = ["__version__"]
