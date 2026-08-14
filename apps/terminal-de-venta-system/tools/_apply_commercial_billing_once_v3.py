#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
VERIFY = HERE / "verify-commercial-billing-cfdi-01.py"
V2 = HERE / "_apply_commercial_billing_once_v2.py"

text = VERIFY.read_text(encoding="utf-8")
old = '''        require(partial["charge"]["status"] == "partially_paid", f"Charge should be partially paid, got {partial['charge']['status']}")\n        require(partial["charge"]["balanceCents"] == 97084, f"Expected balance 97084, got {partial['charge']['balanceCents']}")\n'''
new = '''        require(partial["charge"]["status"] == "past_due", f"Overdue partially paid charge should remain past_due, got {partial['charge']['status']}")\n        require(partial["charge"]["paidCents"] == 100000, f"Expected paidCents 100000, got {partial['charge']['paidCents']}")\n        require(partial["charge"]["balanceCents"] == 97084, f"Expected balance 97084, got {partial['charge']['balanceCents']}")\n'''
if text.count(old) != 1:
    raise SystemExit(f"v3 verifier anchor expected once, found {text.count(old)}")
VERIFY.write_text(text.replace(old, new, 1), encoding="utf-8")
subprocess.check_call([sys.executable, str(V2)])
