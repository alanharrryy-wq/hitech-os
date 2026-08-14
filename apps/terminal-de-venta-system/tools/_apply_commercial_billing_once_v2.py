#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
TARGET = HERE / "_apply_commercial_billing_once.py"
text = TARGET.read_text(encoding="utf-8")
old = '''        'surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo")',
        'surfaceButton("entitlements","Asignar licencia"),surfaceButton("billing","Cobranza & CFDI"),surfaceButton("fleet","Agregar dispositivo")',
        "command billing action",
'''
new = '''        'surfaceButton("customer-setup","Prisma Customer Setup"),surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo")',
        'surfaceButton("customer-setup","Prisma Customer Setup"),surfaceButton("entitlements","Asignar licencia"),surfaceButton("billing","Cobranza & CFDI"),surfaceButton("fleet","Agregar dispositivo")',
        "command billing action",
'''
if text.count(old) != 1:
    raise SystemExit(f"v2 patch-script anchor expected once, found {text.count(old)}")
TARGET.write_text(text.replace(old, new, 1), encoding="utf-8")
subprocess.check_call([sys.executable, str(TARGET)])
