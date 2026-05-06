#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from capatch_plugins.runtime_core import initialize_plugin_runtime

from .exit_codes import EXIT_GENERAL_ERROR
from .parser import (
    audit_args_requested,
    capability_args_requested,
    build_parser,
    diagnostic_args_requested,
    patch_args_requested,
    resolve_root_dir,
)


def main(argv: list[str] | None = None) -> int:
    base_dir = Path(__file__).resolve().parent.parent
    repo_root = base_dir.parents[2]
    parser = build_parser()
    args = parser.parse_args(argv)
    args.root_dir = str(resolve_root_dir(str(getattr(args, 'root_dir', '')), cwd=Path.cwd(), repo_root=repo_root))

    initialize_plugin_runtime(base_dir)

    handlers = []
    from .commands_plugin import handle as handle_plugin
    handlers.append(lambda: handle_plugin(args))

    # === CAPATCH PROJECT CAPABILITY HANDLER START ===
    if capability_args_requested(args):
        from .commands_capability import handle as handle_capability
        handlers.append(lambda: handle_capability(args, base_dir=base_dir))
    # === CAPATCH PROJECT CAPABILITY HANDLER END ===

    if patch_args_requested(args):
        from .commands_patch import handle as handle_patch
        handlers.append(lambda: handle_patch(args, parser))

    if diagnostic_args_requested(args):
        from .commands_diagnostic import handle as handle_diagnostic
        handlers.append(lambda: handle_diagnostic(args, base_dir=base_dir))

    if audit_args_requested(args):
        from .commands_audit import handle as handle_audit
        handlers.append(lambda: handle_audit(args))

    for handler in handlers:
        result = handler()
        if result is not None:
            return int(result)

    parser.error('Debes pasar --ops-file o --ops-stdin, o usar --self-test o --smoke-test.')
    return EXIT_GENERAL_ERROR
