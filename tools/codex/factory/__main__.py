from __future__ import annotations

import faulthandler
import os
import sys
import traceback

from .cli import main


def _debug_stack_enabled() -> bool:
    value = os.environ.get("HITECH_FACTORY_DEBUG_STACK", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _enable_faulthandler_if_requested() -> None:
    if not _debug_stack_enabled():
        return
    try:
        faulthandler.enable(file=sys.stderr, all_threads=True)
    except Exception:
        # Keep runtime behavior stable; diagnostics must never break command execution.
        pass


def _run() -> int:
    _enable_faulthandler_if_requested()
    try:
        return int(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("HITECH_FACTORY_UNHANDLED_EXCEPTION", file=sys.stderr)
        print(f"exception_repr: {exc!r}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr, end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(_run())
