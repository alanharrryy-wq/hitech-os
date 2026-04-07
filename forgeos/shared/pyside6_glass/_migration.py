from __future__ import annotations

"""Migration helpers for legacy import paths and example bridges."""

import warnings

_SEEN: set[str] = set()


def _warn_once(key: str, message: str, *, stacklevel: int = 3) -> None:
    if key in _SEEN:
        return
    warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)
    _SEEN.add(key)


def warn_legacy_root_import(symbol: str, module_name: str) -> None:
    target = f"pyside6_glass{module_name}.{symbol}"
    _warn_once(
        f"root:{symbol}",
        f"Importing '{symbol}' from 'pyside6_glass' is deprecated; import it from '{target}' instead.",
        stacklevel=4,
    )


def warn_legacy_module_access(old_path: str, new_path: str) -> None:
    _warn_once(
        f"module:{old_path}",
        f"Importing from '{old_path}' is deprecated; use '{new_path}' instead.",
        stacklevel=4,
    )


def warn_legacy_symbol_access(old_path: str, new_path: str) -> None:
    _warn_once(
        f"symbol:{old_path}",
        f"Accessing '{old_path}' is deprecated; use '{new_path}' instead.",
        stacklevel=4,
    )
