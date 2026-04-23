"""Compatibility package exposing the moved bundle under its canonical archive import name."""

from __future__ import annotations

from pathlib import Path

_BUNDLE_ROOT = Path(__file__).resolve().parent.parent
__path__ = [str(_BUNDLE_ROOT)]
PACKAGE_ROOT = _BUNDLE_ROOT
