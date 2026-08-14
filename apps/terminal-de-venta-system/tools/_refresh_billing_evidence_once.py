#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
INDEX = REPO / "PRISMA Factory Ledger" / "PRISMA_EVIDENCE_INDEX.json"
MX = timezone(timedelta(hours=-6))


def main() -> int:
    payload = json.loads(INDEX.read_text(encoding="utf-8"))
    artifacts = payload.get("artifacts", [])
    target = next((item for item in artifacts if item.get("artifact") == "PR #245 Commercial Billing local verification"), None)
    if not target:
        raise SystemExit("Missing PR #245 Commercial Billing local verification artifact")
    proves = list(target.get("proves", []))
    old = "Behavioral verifier completed 21 checks"
    new = "Behavioral verifier completed all declared local checks (22 on PR #245 final suite)"
    if old in proves:
        proves[proves.index(old)] = new
    elif new not in proves:
        raise SystemExit("Expected stale behavioral-check evidence not found")
    e2e = "Command Center store E2E completed 9 additional temporary-DB integration checks"
    if e2e not in proves:
        proves.append(e2e)
    target["proves"] = proves

    entries = payload.get("entries", [])
    entry = next((item for item in entries if item.get("capabilityId") == "commercial.billing.collections"), None)
    if not entry:
        raise SystemExit("Missing commercial.billing.collections evidence entry")
    evidence = list(entry.get("evidence", []))
    for name in ("COMMERCIAL_BILLING_VERIFY.json", "COMMERCIAL_BILLING_COMMAND_CENTER_E2E.json"):
        if name not in evidence:
            evidence.append(name)
    entry["evidence"] = evidence
    payload["updatedAt"] = datetime.now(MX).replace(microsecond=0).isoformat()
    INDEX.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS_BILLING_EVIDENCE_REFRESH")
    print("behavioral_checks=22")
    print("command_center_e2e_checks=9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
