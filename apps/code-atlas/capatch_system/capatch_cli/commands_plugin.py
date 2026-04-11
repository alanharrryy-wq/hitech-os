#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

from capatch_plugins.runtime_core import handle_plugin_cli_actions



def handle(args: Any) -> int | None:
    if handle_plugin_cli_actions(args):
        return 0
    return None
