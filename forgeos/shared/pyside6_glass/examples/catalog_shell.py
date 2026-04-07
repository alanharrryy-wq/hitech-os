from __future__ import annotations

"""Compatibility wrapper. Real implementation moved to `pyside6_glass.examples._catalog_shell_impl`."""

from importlib import import_module as _import_module
from .._migration import warn_legacy_module_access as _warn_module_access
from .._migration import warn_legacy_symbol_access as _warn_symbol_access

_IMPL_MODULE = "pyside6_glass.examples._catalog_shell_impl"
_impl = _import_module(_IMPL_MODULE)
__all__ = list(getattr(_impl, "__all__", [name for name in dir(_impl) if not name.startswith("_")]))


def __getattr__(name: str):
    if hasattr(_impl, name):
        _warn_symbol_access(f"pyside6_glass.examples.catalog_shell.{name}", f"{_IMPL_MODULE}.{name}")
        value = getattr(_impl, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


_warn_module_access("pyside6_glass.examples.catalog_shell", _IMPL_MODULE)
__migration_bridge_generated__ = True
