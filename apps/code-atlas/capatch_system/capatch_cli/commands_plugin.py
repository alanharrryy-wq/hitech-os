#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

import capatch_legacy



def handle(args: Any) -> int | None:
    if capatch_legacy.handle_plugin_cli_actions(args):
        return 0
    return None
