"""Backward-compatible neutral module entrypoint for Code Atlas Operational Evidence."""
from __future__ import annotations

from typing import Any, Sequence

from .cli import main as _cli_main
from .cli import run_operational_atlas


def run_operational_evidence(*args: Any, **kwargs: Any) -> Any:
    return run_operational_atlas(*args, **kwargs)


def run_operational_evidence_atlas(*args: Any, **kwargs: Any) -> Any:
    return run_operational_atlas(*args, **kwargs)


def run(*args: Any, **kwargs: Any) -> Any:
    return run_operational_atlas(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> Any:
    if argv is None:
        return _cli_main()
    try:
        return _cli_main(argv)
    except TypeError:
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
