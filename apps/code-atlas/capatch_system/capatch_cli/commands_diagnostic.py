#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Any

from capatch_diagnostics.runtime import run_diagnostic_command
from capatch_plugins.runtime_core import get_plugin_state

from .parser import diagnostic_args_requested



def handle(args: Any, *, base_dir: Path) -> int | None:
    if not diagnostic_args_requested(args):
        return None
    return run_diagnostic_command(args, base_dir=base_dir, plugin_state=get_plugin_state())
