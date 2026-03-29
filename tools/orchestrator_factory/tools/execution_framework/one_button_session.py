#!/usr/bin/env python3
"""Human entrypoint for the one-button runtime launcher (wave 4)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR / 'lib'
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from session_cli import CLIValidationError, build_runtime_context, format_console_result, parse_args  # type: ignore  # noqa: E402
from session_flow import RuntimeFlowError, run_runtime_core  # type: ignore  # noqa: E402

EXIT_SUCCESS = 0
EXIT_BLOCKED_BY_LOCK = 10
EXIT_INVALID_ARGUMENTS = 30
EXIT_INVALID_POLICY_TRANSITION = 31
EXIT_EXPORT_CONTRACT_FAILED = 40
EXIT_RUNTIME_ERROR = 50


STATUS_TO_EXIT = {
    'blocked_by_lock': EXIT_BLOCKED_BY_LOCK,
    'invalid_policy_transition': EXIT_INVALID_POLICY_TRANSITION,
    'export_contract_failed': EXIT_EXPORT_CONTRACT_FAILED,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        args = parse_args(argv)
        runtime_context = build_runtime_context(args)
        result = run_runtime_core(runtime_context)
        print(format_console_result(result))
        return EXIT_SUCCESS
    except CLIValidationError as exc:
        payload = {'status': 'invalid_arguments', 'error': str(exc), 'exit_code': EXIT_INVALID_ARGUMENTS}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return EXIT_INVALID_ARGUMENTS
    except RuntimeFlowError as exc:
        exit_code = STATUS_TO_EXIT.get(exc.status, EXIT_RUNTIME_ERROR)
        payload = {'status': exc.status, 'error': exc.message, 'details': exc.details, 'exit_code': exit_code}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code
    except KeyboardInterrupt:
        payload = {'status': 'cancelled', 'error': 'Operator cancelled the session before completion.', 'exit_code': EXIT_RUNTIME_ERROR}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return EXIT_RUNTIME_ERROR
    except Exception as exc:  # pragma: no cover
        payload = {'status': 'unexpected_runtime_error', 'error': str(exc), 'type': exc.__class__.__name__, 'exit_code': EXIT_RUNTIME_ERROR}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return EXIT_RUNTIME_ERROR


if __name__ == '__main__':
    raise SystemExit(main())
