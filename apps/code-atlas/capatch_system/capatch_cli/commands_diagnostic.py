#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Any

from diagnostic_runtime import run_diagnostic_command

from .parser import diagnostic_args_requested



def handle(args: Any, *, base_dir: Path) -> int | None:
    if not diagnostic_args_requested(args):
        return None
    return run_diagnostic_command(args, base_dir=base_dir, plugin_state=getattr(__import__('capatch_legacy'), 'CAPATCH_PLUGIN_STATE'))
