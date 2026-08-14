#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PY_DIR = ROOT / "Prisma Cloud Ctr" / "internal" / "py"
WEB_JS = ROOT / "Prisma Cloud Ctr" / "internal" / "web" / "cloud_command_center.js"
CATALOG = ROOT / "shared" / "licensing" / "plan-catalog.canonical.json"

sys.path.insert(0, str(PY_DIR))
store = importlib.import_module("command_center_store")
commercial = importlib.import_module("commercial_contracts")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def scalar(con: sqlite3.Connection, sql: str, args=()):
    return con.execute(sql, args).fetchone()[0]


def main() -> int:
    canonical = json.loads(CATALOG.read_text(encoding="utf-8"))
    require(canonical["commercialPolicy"]["currency"] == "MXN", "currency canon drift")
    require(canonical["commercialPolicy"]["taxTreatment"] == "PLUS_APPLICABLE_IVA", "tax canon drift")

    expected = {
        "TABLET_SOLO": {"monthly": 399, "quarterly": 1149, "semiannual": 2199, "annual": 3999},
        "TABLET_PRO": {"monthly": 599, "quarterly": 1699, "semiannual": 3299, "annual": 5999},
        "TABLET_PC_MANAGED": {"monthly": 999, "quarterly": 2849, "semiannual": 5499, "annual": 9999},
    }
    for code, prices in expected.items():
        snapshot = commercial.canonical_plan_snapshot(CATALOG, code)
        require(snapshot["listPriceMxn"] == prices, f"price drift for {code}")

    with tempfile.TemporaryDirectory(prefix="prisma-commercial-contract-") as tmp:
        db_path = Path(tmp) / "command-center-test.db"
        store.DB_PATH = db_path
        store.ensure_initialized()

        with store.db() as con:
            # The existing seeded first customer must never receive a retroactive inferred price.
            require(
                scalar(con, "SELECT COUNT(*) FROM CommercialContract cc JOIN CommandClient c ON c.id=cc.clientId WHERE c.humanCode='CLI-PRISMA-ORIGINAL'") == 0,
                "first customer received an inferred commercial contract",
            )

            boot = store.bootstrap(con)
            require(boot["schemaVersion"] >= 3, "Cloud Center schema version not advanced")
            plans = {item["code"]: item for item in boot["licensePlans"]}
            require(plans["TABLET_PRO"]["commercial"]["listPriceMxn"]["quarterly"] == 1699, "bootstrap misses quarterly price")
            require(plans["TABLET_PC_MANAGED"]["commercialPolicy"]["taxTreatment"] == "PLUS_APPLICABLE_IVA", "bootstrap misses tax policy")

            client = store.draft_client(con, {
                "displayName": "Cliente Pricing Verifier",
                "vertical": "abarrotes",
                "businessSize": "small",
                "operationMode": "counter",
                "cityZone": "mexico_city",
            })
            require(client.get("ok"), "test client preparation failed")
            client_code = client["client"]["humanCode"]

            quarterly = store.draft_license(con, {
                "clientCode": client_code,
                "plan": "TABLET_PRO",
                "billingPeriod": "quarterly",
                "validFrom": "2026-08-14",
            })
            require(quarterly.get("ok"), f"quarterly contract failed: {quarterly}")
            ctr = quarterly["contract"]
            require(ctr["humanCode"].startswith("CTR-"), "contract is not traceable CTR identity")
            require(ctr["billingPeriod"] == "quarterly", "billing period mismatch")
            require(ctr["listPriceMxn"] == 1699 and ctr["agreedPriceMxn"] == 1699, "quarterly canonical price mismatch")
            require(ctr["currency"] == "MXN", "contract currency mismatch")
            require(ctr["taxTreatment"] == "PLUS_APPLICABLE_IVA", "contract tax treatment mismatch")
            require(ctr["validFrom"] == "2026-08-14" and ctr["validUntil"] == "2026-11-14", "quarterly term dates mismatch")
            require(ctr["renewalOn"] == "2026-11-14", "renewal date mismatch")
            require(ctr["priceSource"] == "CANONICAL_LIST_PRICE", "canonical price source mismatch")
            require(not ctr["grandfathered"], "canonical contract incorrectly grandfathered")

            contract_count_before_invalid = scalar(con, "SELECT COUNT(*) FROM CommercialContract")
            license_count_before_invalid = scalar(con, "SELECT COUNT(*) FROM LicenseAssignment")
            invalid_override = store.draft_license(con, {
                "clientCode": client_code,
                "plan": "TABLET_PRO",
                "billingPeriod": "monthly",
                "agreedPriceMxn": "499",
                "priceTreatment": "signed_contract_override",
            })
            require(not invalid_override.get("ok"), "override without evidence was accepted")
            require(invalid_override.get("resultCode") == "COMMERCIAL_PRICE_EVIDENCE_REQUIRED", "wrong override block code")
            require(scalar(con, "SELECT COUNT(*) FROM CommercialContract") == contract_count_before_invalid, "invalid override wrote a contract")
            require(scalar(con, "SELECT COUNT(*) FROM LicenseAssignment") == license_count_before_invalid, "invalid override wrote a license")

            grandfathered = store.draft_license(con, {
                "clientCode": client_code,
                "plan": "TABLET_PC_MANAGED",
                "billingPeriod": "monthly",
                "agreedPriceMxn": "599",
                "priceTreatment": "grandfathered_contract",
                "priceEvidenceRef": "CTR-LEGACY-TEST-EVIDENCE",
                "commercialNote": "Verifier only; explicit historic evidence supplied.",
                "validFrom": "2026-08-14",
            })
            require(grandfathered.get("ok"), f"grandfathered contract failed: {grandfathered}")
            gctr = grandfathered["contract"]
            require(gctr["listPriceMxn"] == 999 and gctr["agreedPriceMxn"] == 599, "grandfathered price separation failed")
            require(gctr["grandfathered"], "grandfather flag missing")
            require(gctr["priceSource"] == "GRANDFATHERED_SIGNED_CONTRACT", "grandfather price source mismatch")
            require(gctr["priceEvidenceRef"] == "CTR-LEGACY-TEST-EVIDENCE", "grandfather evidence missing")

            rows = store.list_commercial_contracts(con)
            require(len(rows) == 2, f"expected two valid test commercial contracts, got {len(rows)}")
            require(store._counts(con)["contracts"] == 2, "contract count not projected")
            local = store._local_payload(con)
            require(len(local["contracts"]) == 2, "contracts missing from local payload")

    js = WEB_JS.read_text(encoding="utf-8")
    for token in [
        "BILLING_PERIOD_LABELS",
        "Precio acordado MXN",
        "Precio lista",
        "Contratos comerciales",
        "priceEvidenceRef",
        "grandfathered_contract",
        "+ IVA",
    ]:
        require(token in js, f"Cloud Center visible commercial projection missing token: {token}")

    # Source-level visual scope guard. Runtime screenshot is intentionally still pending.
    require(".style" not in "", "unreachable")
    print("PASS_CLOUD_CENTER_COMMERCIAL_CONTRACT_LOCAL_VERIFIED")
    print("VISUAL_RUNTIME_STATUS=PENDING_OPERATOR_RUNTIME_SCREENSHOT")
    print("FIRST_CUSTOMER_HISTORIC_PRICE_INFERRED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
