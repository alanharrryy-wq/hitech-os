#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Historical shim for capatch Phase 0.

This module intentionally stays tiny. Real CLI ownership lives in capatch_cli.main,
while legacy patch-engine behavior remains preserved in capatch_legacy until the
engine/fs/ops split is fully materialized.
"""

from capatch_cli.main import main


if __name__ == '__main__':
    raise SystemExit(main())
