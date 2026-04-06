from __future__ import annotations

from importlib import import_module

from .primitives import make_panel_heading, make_placeholder, make_separator


def __getattr__(name: str):
    if name == "charts":
        return import_module(".charts", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["make_separator", "make_panel_heading", "make_placeholder", "charts"]
