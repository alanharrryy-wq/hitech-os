#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_patch_audit import list_checkpoint_rows, load_patch_run, rollback_checkpoint, rollback_last



def handle(args: Any) -> int | None:
    root_dir = Path(args.root_dir).expanduser().resolve()
    if getattr(args, 'list_checkpoints', False):
        print(json.dumps(list_checkpoint_rows(root_dir), indent=2, ensure_ascii=False))
        return 0
    if getattr(args, 'rollback_checkpoint', None):
        print(json.dumps(rollback_checkpoint(root_dir, str(args.rollback_checkpoint)), indent=2, ensure_ascii=False))
        return 0
    if getattr(args, 'rollback_last', False):
        print(json.dumps(rollback_last(root_dir), indent=2, ensure_ascii=False))
        return 0
    if getattr(args, 'show_run', None):
        print(json.dumps(load_patch_run(root_dir, str(args.show_run)), indent=2, ensure_ascii=False))
        return 0
    if getattr(args, 'show_rollback_command', None):
        payload = load_patch_run(root_dir, str(args.show_rollback_command))
        print(str(payload.get('rollback_command') or ''))
        return 0
    return None
