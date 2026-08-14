#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
V1 = HERE / "_harden_commercial_billing_integrity_once.py"
text = V1.read_text(encoding="utf-8")
old = '''    discarded_drafts = con.execute(\\n        \"UPDATE CommercialFiscalDocument SET status='discarded',lastErrorCode='PAYMENT_REVERSED_BEFORE_EXTERNAL_STAMP',updatedAt=CURRENT_TIMESTAMP \"\\n        \"WHERE paymentId=? AND kind='CFDI_PAGO' AND status IN ('draft_blocked','ready_to_stamp')\",\\n        (payment[\"id\"],),\\n    ).rowcount\\n    con.execute(\"UPDATE CommercialPaymentAllocation SET status='reversed',updatedAt=CURRENT_TIMESTAMP WHERE paymentId=? AND status='posted'\", (payment[\"id\"],))\\n'''
new = '''    discarded_payment_drafts = con.execute(\\n        \"UPDATE CommercialFiscalDocument SET status='discarded',lastErrorCode='PAYMENT_REVERSED_BEFORE_EXTERNAL_STAMP',updatedAt=CURRENT_TIMESTAMP \"\\n        \"WHERE paymentId=? AND kind='CFDI_PAGO' AND status IN ('draft_blocked','ready_to_stamp')\",\\n        (payment[\"id\"],),\\n    ).rowcount\\n    discarded_income_drafts = 0\\n    for allocation in allocations:\\n        discarded_income_drafts += con.execute(\\n            \"UPDATE CommercialFiscalDocument SET status='discarded',lastErrorCode='PAYMENT_REVERSED_BEFORE_EXTERNAL_STAMP',updatedAt=CURRENT_TIMESTAMP \"\\n            \"WHERE chargeId=? AND kind='CFDI_INGRESO' AND status IN ('draft_blocked','ready_to_stamp')\",\\n            (allocation[\"chargeId\"],),\\n        ).rowcount\\n    discarded_drafts = discarded_payment_drafts + discarded_income_drafts\\n    con.execute(\"UPDATE CommercialPaymentAllocation SET status='reversed',updatedAt=CURRENT_TIMESTAMP WHERE paymentId=? AND status='posted'\", (payment[\"id\"],))\\n'''
count = text.count(old)
if count != 1:
    raise SystemExit(f"v2 reverse invalidation anchor expected once, found {count}")
V1.write_text(text.replace(old, new, 1), encoding="utf-8")
subprocess.check_call([sys.executable, str(V1)])
