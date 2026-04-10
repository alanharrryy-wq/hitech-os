#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import capatch_legacy



def handle(args: Any, parser: Any) -> int | None:
    if getattr(args, 'self_test', False):
        return capatch_legacy.print_self_test()
    if getattr(args, 'smoke_test', False):
        return capatch_legacy.run_smoke_tests()

    if not args.ops_file and not args.ops_stdin:
        return None

    root_dir = Path(args.root_dir).expanduser().resolve()
    backup_dir = root_dir / capatch_legacy.BACKUP_DIR_NAME
    checkpoint_label = capatch_legacy.sanitize_checkpoint_label(args.checkpoint_label)
    checkpoint_dir = backup_dir / checkpoint_label
    ctx = capatch_legacy.PatchContext(
        root_dir=root_dir,
        backup_dir=backup_dir,
        checkpoint_dir=checkpoint_dir,
        dry_run=bool(args.dry_run),
        auto_support=not bool(args.no_auto_support),
    )

    try:
        operations = (
            capatch_legacy.load_operations_from_file(Path(args.ops_file).expanduser().resolve())
            if args.ops_file
            else capatch_legacy.load_operations_from_stdin()
        )
        capatch_legacy.apply_operations(ctx, operations)
        capatch_legacy.ok('Cambios aplicados chido.')
        return 0
    except capatch_legacy.CapatchError as exc:
        print(f'[ERROR] {exc}', file=__import__('sys').stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f'[ERROR] JSON invalido: {exc}', file=__import__('sys').stderr)
        return 1
    except Exception as exc:
        print(f'[ERROR] Error inesperado: {exc}', file=__import__('sys').stderr)
        return 1
