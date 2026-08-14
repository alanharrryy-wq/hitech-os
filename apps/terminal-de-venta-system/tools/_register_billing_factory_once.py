#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
APP = REPO / "apps" / "terminal-de-venta-system"
LEDGER_DIR = REPO / "PRISMA Factory Ledger"
LEDGER = LEDGER_DIR / "PRISMA_FACTORY_LEDGER.json"
EVIDENCE = LEDGER_DIR / "PRISMA_EVIDENCE_INDEX.json"
REG = LEDGER_DIR / "PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json"
DNR = LEDGER_DIR / "PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json"
LEDGER_MD = LEDGER_DIR / "PRISMA_FACTORY_LEDGER.md"
DOC = APP / "docs" / "productization" / "PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md"
VERIFY = APP / "tools" / "verify-commercial-billing-cfdi-01.py"

MX = timezone(timedelta(hours=-6))
NOW = datetime.now(MX).replace(microsecond=0).isoformat()
DOC_SHA = hashlib.sha256(DOC.read_bytes()).hexdigest().upper()
VERIFY_SHA = hashlib.sha256(VERIFY.read_bytes()).hexdigest().upper()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_capability(items, capability):
    matches = [i for i, item in enumerate(items) if item.get("id") == capability["id"]]
    if len(matches) > 1:
        raise SystemExit(f"Duplicate capability before patch: {capability['id']}")
    if matches:
        items[matches[0]] = capability
    else:
        items.append(capability)


def main() -> int:
    ledger = load(LEDGER)
    caps = ledger.setdefault("capabilities", [])

    collections = {
        "id": "commercial.billing.collections",
        "displayName": "PRISMA commercial collections and accounts receivable ledger",
        "domain": "commercial",
        "surfaces": ["cloud_center", "commercial_contract", "billing", "governance", "quality"],
        "classification": "DONE",
        "status": "LOCAL_VERIFIED",
        "stateLabel": "PASS_COMMERCIAL_BILLING_CFDI_LOCAL_VERIFIED",
        "doNotRebuild": True,
        "nextGate": "Runtime operator verification in Prisma Cloud Center with sandbox/test customer data, then supervised real-client operational use. Do not rebuild the collections ledger.",
        "evidence": [
            "apps/terminal-de-venta-system/docs/productization/PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
            "apps/terminal-de-venta-system/tools/verify-commercial-billing-cfdi-01.py",
            "PR #245 Commercial Billing Authority + behavioral verification",
        ],
        "doesNotProve": [
            "Bank payment processing or bank reconciliation",
            "Live SAT/PAC stamping or cancellation",
            "Runtime/visual certification of Cloud Center",
            "Tax/legal compliance for a specific taxpayer",
            "Historical fiscal data for Prisma Original Customer",
        ],
        "allowedActions": [
            "read-only evidence review",
            "runtime operator verification",
            "sandbox billing exercises",
            "fix demonstrated drift",
            "advance to external fiscal gateway",
        ],
        "forbiddenActions": [
            "rebuild collections ledger from scratch",
            "move payment processing into licensing",
            "auto-suspend licenses from past-due state",
            "store banking/card credentials",
        ],
    }
    fiscal = {
        "id": "commercial.billing.cfdi_external_gateway",
        "displayName": "PRISMA CFDI 4.0 and Payment Complement 2.0 external gateway boundary",
        "domain": "commercial",
        "surfaces": ["cloud_center", "billing", "fiscal_gateway", "governance", "quality"],
        "classification": "EXTERNAL",
        "status": "EXTERNAL_BLOCKED",
        "stateLabel": "SOURCE_READY_LOCAL_DRAFTS_EXTERNAL_SAT_PAC_REQUIRED",
        "doNotRebuild": True,
        "nextGate": "Configure real issuer fiscal identity and SAT/PAC integration with CSD/secrets managed outside repo/ledger, then run explicitly authorized live stamping and cancellation E2E with secret-safe evidence.",
        "evidence": [
            "apps/terminal-de-venta-system/docs/productization/PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
            "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py/cfdi_gateway.py",
            "apps/terminal-de-venta-system/tools/verify-commercial-billing-cfdi-01.py",
            "PR #245 Commercial Billing Authority + behavioral verification",
        ],
        "doesNotProve": [
            "XML XSD validation by SAT/PAC",
            "Real CSD validity",
            "Live UUID issuance",
            "Live SAT/PAC cancellation",
            "Fiscal catalog compatibility for a real taxpayer",
            "Legal/accounting certification",
        ],
        "allowedActions": [
            "prepare external provider ceremony",
            "validate source locally",
            "register external UUID/cancellation evidence",
            "run live fiscal E2E only with explicit authorization",
        ],
        "forbiddenActions": [
            "store CSD private key or password in repo/database/logs",
            "store PAC token in repo/database/logs",
            "claim live stamping from local draft verification",
            "claim cancellation from cancel_requested",
        ],
    }
    replace_capability(caps, collections)
    replace_capability(caps, fiscal)
    save(LEDGER, ledger)

    evidence = load(EVIDENCE)
    artifacts = evidence.setdefault("artifacts", [])
    artifacts[:] = [a for a in artifacts if a.get("artifact") not in {"PR #245 Commercial Billing local verification", "PR #245 CFDI external gateway source verification"}]
    artifacts.extend([
        {
            "artifact": "PR #245 Commercial Billing local verification",
            "type": "commercial_collections_local_verification",
            "scope": ["commercial", "cloud_center", "collections", "billing", "quality"],
            "status": "PASS_LOCAL_VERIFIED",
            "proves": [
                "CommercialContract-to-charge projection works in temporary SQLite",
                "Aging, past-due, partial payment, paid, void, idempotency and non-fiscal receipt behaviors are verified",
                "Payments are recorded as external facts and do not mutate licensing",
                "No real database, bank, card, SPEI, Prisma schema, Tablet, PC or Mobile surface was mutated",
                "Behavioral verifier completed 21 checks",
            ],
            "doesNotProve": [
                "Runtime visual certification",
                "Bank payment processing",
                "Live fiscal stamping/cancellation",
                "Tax/legal compliance for a real taxpayer",
            ],
        },
        {
            "artifact": "PR #245 CFDI external gateway source verification",
            "type": "cfdi_external_gateway_source_verification",
            "scope": ["commercial", "cfdi_4_0", "pagos_2_0", "external_sat_pac"],
            "status": "SOURCE_READY_EXTERNAL_BLOCKED",
            "proves": [
                "CFDI 4.0 income drafts fail closed on missing fiscal prerequisites",
                "PUE/PPD and Payment Complement 2.0 local behavior is verified",
                "External UUID and cancellation-result registration is auditable",
                "Live stamping and cancellation flags remain false",
                "Secrets are not part of the billing schema",
            ],
            "doesNotProve": [
                "SAT/PAC XML acceptance",
                "Real UUID issuance",
                "CSD validity",
                "Live cancellation",
                "Legal/accounting certification",
            ],
        },
    ])
    evidence["updatedAt"] = NOW
    entries = evidence.setdefault("entries", [])
    entries[:] = [entry for entry in entries if entry.get("capabilityId") not in {collections["id"], fiscal["id"]}]
    entries.extend([
        {
            "capabilityId": collections["id"],
            "status": collections["status"],
            "runId": "PR245_COMMERCIAL_BILLING_LOCAL_VERIFIED",
            "evidence": [
                "PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
                "verify-commercial-billing-cfdi-01.py",
                "COMMERCIAL_BILLING_VERIFY.json",
            ],
        },
        {
            "capabilityId": fiscal["id"],
            "status": fiscal["status"],
            "runId": "PR245_CFDI_EXTERNAL_GATEWAY_SOURCE_READY",
            "evidence": [
                "PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
                "cfdi_gateway.py",
                "COMMERCIAL_BILLING_VERIFY.json",
            ],
        },
    ])
    save(EVIDENCE, evidence)

    reg = load(REG)
    regs = reg.setdefault("registrations", {})
    regs[collections["id"]] = {
        "status": "DONE_LOCAL_VERIFIED",
        "updatedAt": NOW,
        "evidence": "apps/terminal-de-venta-system/docs/productization/PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
        "sourceEvidenceSha256": DOC_SHA,
        "verifierSha256": VERIFY_SHA,
        "doNotRebuild": True,
        "nextGate": "RUNTIME_OPERATOR_VERIFICATION",
    }
    regs[fiscal["id"]] = {
        "status": "EXTERNAL_BLOCKED_SOURCE_READY",
        "updatedAt": NOW,
        "evidence": "apps/terminal-de-venta-system/docs/productization/PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
        "sourceEvidenceSha256": DOC_SHA,
        "verifierSha256": VERIFY_SHA,
        "doNotRebuild": True,
        "nextGate": "EXPLICIT_SAT_PAC_LIVE_FISCAL_E2E",
    }
    reg["updatedAt"] = NOW
    save(REG, reg)

    dnr = load(DNR)
    protected = dnr.setdefault("doNotRebuild", {})
    protected[collections["id"]] = {
        "value": True,
        "reason": "Collections ledger passed 21 behavioral checks in temporary SQLite; advance to runtime verification, do not rebuild.",
        "evidence": "apps/terminal-de-venta-system/tools/verify-commercial-billing-cfdi-01.py",
        "updatedAt": NOW,
    }
    protected[fiscal["id"]] = {
        "value": True,
        "reason": "CFDI local draft/external-result gateway source is ready; the next gate is external SAT/PAC, not source rebuild.",
        "evidence": "apps/terminal-de-venta-system/docs/productization/PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md",
        "updatedAt": NOW,
    }
    dnr["updatedAt"] = NOW
    save(DNR, dnr)

    md = LEDGER_MD.read_text(encoding="utf-8")
    begin = "<!-- PRISMA:COMMERCIAL_BILLING:BEGIN -->"
    end = "<!-- PRISMA:COMMERCIAL_BILLING:END -->"
    block = f'''{begin}\n## Commercial billing and CFDI\n\n- `commercial.billing.collections`: `DONE / LOCAL_VERIFIED / doNotRebuild=true`.\n- State: `PASS_COMMERCIAL_BILLING_CFDI_LOCAL_VERIFIED`.\n- Next gate: runtime operator verification, not a rebuild.\n- `commercial.billing.cfdi_external_gateway`: `EXTERNAL / EXTERNAL_BLOCKED / doNotRebuild=true`.\n- State: `SOURCE_READY_LOCAL_DRAFTS_EXTERNAL_SAT_PAC_REQUIRED`.\n- Next gate: explicitly authorized SAT/PAC live fiscal E2E with secrets managed outside repo/ledger.\n- Local PASS does **not** mean bank processing, live CFDI stamping, live cancellation, or legal/tax certification.\n{end}'''
    if begin in md and end in md:
        prefix, rest = md.split(begin, 1)
        _, suffix = rest.split(end, 1)
        md = prefix.rstrip() + "\n\n" + block + suffix
    else:
        md = md.rstrip() + "\n\n" + block + "\n"
    LEDGER_MD.write_text(md, encoding="utf-8")

    print("PASS_COMMERCIAL_BILLING_FACTORY_LEDGER_REGISTERED")
    print(f"doc_sha256={DOC_SHA}")
    print(f"verifier_sha256={VERIFY_SHA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
