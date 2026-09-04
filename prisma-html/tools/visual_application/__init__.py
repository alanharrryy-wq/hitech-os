"""PRISMA Generic Visual Application Engine V1.

Source/static application machinery only. Runtime visual certification is deliberately outside this package.

Public engine callables are imported lazily so module CLIs such as
`python -m visual_application.target_index` do not preload their own dependency
graph and emit runpy duplicate-module warnings.
"""
from __future__ import annotations

from typing import Any

__all__ = ["preview", "apply", "verify", "rollback_transaction"]


def preview(*args: Any, **kwargs: Any) -> Any:
    from .engine import preview as _preview
    return _preview(*args, **kwargs)


def apply(*args: Any, **kwargs: Any) -> Any:
    from .engine import apply as _apply
    return _apply(*args, **kwargs)


def verify(*args: Any, **kwargs: Any) -> Any:
    from .engine import verify as _verify
    return _verify(*args, **kwargs)


def rollback_transaction(*args: Any, **kwargs: Any) -> Any:
    from .engine import rollback_transaction as _rollback_transaction
    return _rollback_transaction(*args, **kwargs)
