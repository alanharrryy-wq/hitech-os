#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

import capatch_legacy

from .commands_audit import handle as handle_audit
from .commands_diagnostic import handle as handle_diagnostic
from .commands_patch import handle as handle_patch
from .commands_plugin import handle as handle_plugin
from .exit_codes import EXIT_GENERAL_ERROR, EXIT_OK
from .parser import build_parser



def emit_deprecation_warning() -> None:
    print('[WARN] capatch.py opera como shim de compatibilidad. El entrypoint real ya es capatch_cli.main.', file=sys.stderr)



def main(argv: list[str] | None = None) -> int:
    base_dir = Path(__file__).resolve().parent.parent
    parser = build_parser()
    args = parser.parse_args(argv)

    capatch_legacy.initialize_plugin_runtime(base_dir)
    emit_deprecation_warning()

    for handler in (
        lambda: handle_audit(args),
        lambda: handle_plugin(args),
        lambda: handle_patch(args, parser),
        lambda: handle_diagnostic(args, base_dir=base_dir),
    ):
        result = handler()
        if result is not None:
            return int(result)

    parser.error('Debes pasar --ops-file o --ops-stdin, o usar --self-test o --smoke-test.')
    return EXIT_GENERAL_ERROR
