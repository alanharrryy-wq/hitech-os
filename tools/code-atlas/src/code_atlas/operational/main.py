"""Backward-compatible module entrypoint for Code Atlas Operational Evidence.

The implementation remains in ``code_atlas.operational.cli``.  This shim keeps
``code_atlas.operational.main`` imports and module execution stable.
"""

from __future__ import annotations

from typing import Any, Sequence

from .cli import main as _cli_main
from .cli import run_operational_atlas


def run_operational_evidence(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for older imports."""
    return run_operational_atlas(*args, **kwargs)


def run_operational_evidence_atlas(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for previous operational atlas callers."""
    return run_operational_atlas(*args, **kwargs)


def run(*args: Any, **kwargs: Any) -> Any:
    """Legacy shorthand alias."""
    return run_operational_atlas(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> Any:
    """Delegate to the modular operational CLI without assuming its signature."""
    if argv is None:
        return _cli_main()
    try:
        return _cli_main(argv)
    except TypeError:
        # Some internal CLI builds read sys.argv directly.
        return _cli_main()


__all__ = [
    "main",
    "run_operational_atlas",
    "run_operational_evidence",
    "run_operational_evidence_atlas",
    "run",
]


if __name__ == "__main__":
    raise SystemExit(main())
