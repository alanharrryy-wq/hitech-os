#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOUD_PY = ROOT / "Prisma Cloud Ctr" / "internal" / "py"
if str(CLOUD_PY) not in sys.path:
    sys.path.insert(0, str(CLOUD_PY))

import command_center_store as store  # noqa: E402


class VerifyFailure(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyFailure(message)


def verify() -> dict:
    checks: list[dict] = []
    original_data_dir = store.DATA_DIR
    original_db_path = store.DB_PATH
    try:
        with tempfile.TemporaryDirectory(prefix="prisma-command-billing-") as tmp:
            temp_root = Path(tmp)
            store.DATA_DIR = temp_root
            store.DB_PATH = temp_root / "command-center-billing.sqlite"

            boot = store.command_center_payload("/api/command-center/bootstrap", method="GET")
            require(boot.get("ok") is True, "Bootstrap failed")
            billing = boot.get("billing") or {}
            require(billing.get("moneyProcessing") is False, "Command Center claims money processing")
            require(billing.get("bankValidation") is False, "Command Center claims bank validation")
            require(billing.get("liveStampingAllowed") is not True, "Unexpected root live stamping flag")
            require((billing.get("gateway") or {}).get("liveStampingAllowed") is False, "Gateway live stamping must remain false")
            checks.append({"name": "bootstrap_billing_boundary", "status": "PASS"})

            client = store.command_center_payload(
                "/api/command-center/draft-client",
                method="POST",
                body={
                    "displayName": "Command Billing Sandbox",
                    "email": "billing-sandbox@example.invalid",
                    "vertical": "abarrotes",
                    "subvertical": "minisuper",
                    "businessSize": "small",
                    "operationMode": "counter",
                    "acquisitionChannel": "unknown",
                    "country": "MX",
                    "state": "ciudad_de_mexico",
                    "city": "Ciudad de México",
                    "clientRequestId": "billing-command-center-customer-01",
                },
            )
            require(client.get("ok") is True, f"Client draft failed: {client}")
            client_code = client["client"]["humanCode"]
            checks.append({"name": "draft_client_via_store", "status": "PASS", "clientCode": client_code})

            license_result = store.command_center_payload(
                "/api/command-center/draft-license",
                method="POST",
                body={
                    "clientCode": client_code,
                    "plan": "TABLET_SOLO",
                    "billingPeriod": "monthly",
                    "priceTreatment": "canonical_list",
                    "validFrom": "2026-08-14",
                },
            )
            require(license_result.get("ok") is True, f"License/contract draft failed: {license_result}")
            contract = license_result.get("contract") or {}
            require(contract.get("humanCode", "").startswith("CTR-"), "Contract CTR identity missing")
            require(contract.get("agreedPriceMxn") == 399, f"Canonical TABLET_SOLO price drifted: {contract}")
            contract_code = contract["humanCode"]
            checks.append({"name": "license_contract_via_store", "status": "PASS", "contractCode": contract_code})

            charge = store.command_center_payload(
                "/api/command-center/billing/create-charge",
                method="POST",
                body={
                    "contractCode": contract_code,
                    "taxRateBps": 1600,
                    "taxRateSource": "LIVA_ART_1_GENERAL_RATE_OPERATOR_CONFIRMED",
                    "confirmTax": True,
                    "asOf": "2026-08-14",
                },
            )
            require(charge.get("ok") is True, f"Charge creation failed: {charge}")
            charge_row = charge.get("charge") or {}
            require(charge_row.get("subtotalCents") == 39900, "Charge did not derive contract price")
            require(charge_row.get("taxCents") == 6384, "16% tax cents mismatch")
            require(charge_row.get("totalCents") == 46284, "Charge total mismatch")
            charge_code = charge_row["humanCode"]
            checks.append({"name": "charge_via_billing_route", "status": "PASS", "chargeCode": charge_code})

            missing_evidence = store.command_center_payload(
                "/api/command-center/billing/register-payment",
                method="POST",
                body={
                    "chargeCode": charge_code,
                    "amountMxn": "100.00",
                    "paymentForm": "03",
                    "idempotencyKey": "command-e2e-pay-0001",
                },
            )
            require(missing_evidence.get("ok") is False, "Payment without evidence should fail")
            require(missing_evidence.get("resultCode") == "BILLING_PAYMENT_EVIDENCE_REQUIRED", f"Wrong evidence error: {missing_evidence}")
            require(missing_evidence.get("_httpStatus") == 400, f"Structured HTTP status missing: {missing_evidence}")
            checks.append({"name": "structured_error_status_via_store", "status": "PASS"})

            payment_body = {
                "chargeCode": charge_code,
                "amountMxn": "100.00",
                "paymentForm": "03",
                "idempotencyKey": "command-e2e-pay-0002",
                "externalReference": "SANDBOX-TRANSFER-0002",
            }
            payment = store.command_center_payload(
                "/api/command-center/billing/register-payment",
                method="POST",
                body=payment_body,
            )
            require(payment.get("ok") is True, f"Payment registration failed: {payment}")
            require(payment.get("payment", {}).get("amountCents") == 10000, "Payment cents mismatch")
            require(payment.get("receipt", {}).get("nonFiscal") == 1, "Receipt must be non-fiscal")
            require(payment.get("charge", {}).get("balanceCents") == 36284, "Balance after payment mismatch")
            payment_id = payment["payment"]["id"]
            received_at = payment["payment"]["receivedAt"]

            retry = store.command_center_payload(
                "/api/command-center/billing/register-payment",
                method="POST",
                body=payment_body,
            )
            require(retry.get("ok") is True and retry.get("idempotent") is True, f"Retry not idempotent: {retry}")
            require(retry.get("payment", {}).get("id") == payment_id, "Retry created different payment")
            require(retry.get("payment", {}).get("receivedAt") == received_at, "Retry changed implicit receivedAt")
            checks.append({"name": "payment_and_retry_via_store", "status": "PASS"})

            snapshot = store.command_center_payload("/api/command-center/billing/snapshot", method="GET")
            require(snapshot.get("ok") is True, "Billing snapshot failed")
            require(snapshot.get("counts", {}).get("charges") == 1, f"Unexpected charge count: {snapshot.get('counts')}")
            require(snapshot.get("counts", {}).get("payments") == 1, f"Unexpected payment count: {snapshot.get('counts')}")
            require(snapshot.get("reconciliation", {}).get("outstandingCents") == 36284, "Snapshot outstanding mismatch")
            require(snapshot.get("licenseAutoSuspension") is False, "Snapshot enables license auto-suspension")
            checks.append({"name": "billing_snapshot_via_store", "status": "PASS"})

            not_found = store.command_center_payload(
                "/api/command-center/billing/create-charge",
                method="POST",
                body={"contractCode": "CTR-NOT-FOUND", "taxRateBps": 1600, "confirmTax": True},
            )
            require(not_found.get("resultCode") == "BILLING_CONTRACT_NOT_FOUND", f"Wrong missing contract result: {not_found}")
            require(not_found.get("_httpStatus") == 404, f"Missing contract did not preserve 404 semantics: {not_found}")
            checks.append({"name": "not_found_status_via_store", "status": "PASS"})

            require(store.DB_PATH == temp_root / "command-center-billing.sqlite", "Verifier escaped temporary DB")
            require(store.DB_PATH.exists(), "Temporary DB was not created")
            require(original_db_path != store.DB_PATH, "Verifier used configured real DB path")
            checks.append({"name": "temporary_db_only", "status": "PASS"})

        return {
            "status": "PASS_COMMERCIAL_BILLING_COMMAND_CENTER_E2E",
            "checkedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "checkCount": len(checks),
            "checks": checks,
            "realDbTouched": False,
            "moneyProcessed": False,
            "liveFiscalMutation": False,
        }
    finally:
        store.DATA_DIR = original_data_dir
        store.DB_PATH = original_db_path


def write_report(out_dir: Path, report: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "COMMERCIAL_BILLING_COMMAND_CENTER_E2E.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".governance/current")
    args = parser.parse_args()
    try:
        report = verify()
        write_report(Path(args.out_dir), report)
        print(report["status"])
        print(f"checks={report['checkCount']}")
        return 0
    except Exception as exc:
        report = {
            "status": "FAIL_COMMERCIAL_BILLING_COMMAND_CENTER_E2E",
            "checkedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "realDbTouched": False,
        }
        write_report(Path(args.out_dir), report)
        print(report["status"], file=sys.stderr)
        print(report["error"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
