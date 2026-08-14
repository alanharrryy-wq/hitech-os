#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOUD_PY = ROOT / "Prisma Cloud Ctr" / "internal" / "py"
if str(CLOUD_PY) not in sys.path:
    sys.path.insert(0, str(CLOUD_PY))

from commercial_contracts import ensure_commercial_schema, insert_commercial_contract, resolve_commercial_terms  # noqa: E402
from commercial_billing import (  # noqa: E402
    BillingError,
    billing_snapshot,
    create_charge,
    ensure_billing_schema,
    prepare_income_cfdi,
    prepare_payment_complement,
    reconcile_billing,
    register_external_cancellation_result,
    register_external_payment,
    register_external_stamp,
    request_cfdi_cancellation,
    reverse_external_payment,
    save_issuer_profile,
    save_receiver_profile,
    void_charge,
)


PLAN_CATALOG = ROOT / "shared" / "licensing" / "plan-catalog.canonical.json"
DOC_CONTRACT = ROOT / "docs" / "productization" / "PRISMA_COMMERCIAL_BILLING_CFDI_CONTRACT.md"
NO_PAYMENT_DOC = ROOT / "docs" / "productization" / "PRISMA_LICENSE_NO_PAYMENT_PROCESSING_ADDENDUM.md"
JS_PATH = ROOT / "Prisma Cloud Ctr" / "internal" / "web" / "cloud_command_center.js"
BILLING_SOURCE = CLOUD_PY / "commercial_billing.py"
CFDI_SOURCE = CLOUD_PY / "cfdi_gateway.py"


class VerifyFailure(AssertionError):
    pass


class IdFactory:
    PREFIX = {"charge": "COB", "payment": "PAY", "receipt": "RCP", "fiscal": "CFD"}

    def __init__(self) -> None:
        self.seq: dict[str, int] = {}

    def __call__(self, _con, kind, meta=None):
        self.seq[kind] = self.seq.get(kind, 0) + 1
        n = self.seq[kind]
        prefix = self.PREFIX.get(kind, kind[:3].upper())
        return {
            "kind": kind,
            "internalId": f"{kind}_test_{n:04d}",
            "humanCode": f"{prefix}-2026-{n:06d}",
            "sequence": n,
            "metadata": meta or {},
        }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyFailure(message)


def expect_billing_error(code: str, fn, *args, **kwargs) -> BillingError:
    try:
        fn(*args, **kwargs)
    except BillingError as exc:
        require(exc.code == code, f"Expected {code}, got {exc.code}: {exc}")
        return exc
    raise VerifyFailure(f"Expected BillingError {code}, but call succeeded")


def seed_minimal_core(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE CommandClient(
          id TEXT PRIMARY KEY,
          humanCode TEXT NOT NULL UNIQUE,
          displayName TEXT NOT NULL,
          status TEXT NOT NULL
        );
        CREATE TABLE LicenseAssignment(
          id TEXT PRIMARY KEY,
          humanCode TEXT NOT NULL UNIQUE,
          clientId TEXT NOT NULL,
          status TEXT NOT NULL
        );
        """
    )
    con.executemany(
        "INSERT INTO CommandClient(id,humanCode,displayName,status) VALUES(?,?,?,?)",
        [
            ("client_original", "CLI-PRISMA-ORIGINAL", "Prisma Original Customer", "active_local_signed"),
            ("client_test", "CLI-2026-900001", "Cliente Fiscal Sandbox", "active"),
        ],
    )
    for index in range(1, 8):
        con.execute(
            "INSERT INTO LicenseAssignment(id,humanCode,clientId,status) VALUES(?,?,?,?)",
            (f"license_{index}", f"LIC-2026-9{index:05d}", "client_test", "active"),
        )
    ensure_commercial_schema(con)
    ensure_billing_schema(con)


def make_contract(con: sqlite3.Connection, plan: str, period: str, license_index: int, contract_index: int, valid_from: str = "2026-08-01") -> dict:
    terms = resolve_commercial_terms(
        PLAN_CATALOG,
        plan,
        billing_period=period,
        valid_from=valid_from,
    )
    identity = {
        "internalId": f"contract_test_{contract_index}",
        "humanCode": f"CTR-2026-9{contract_index:05d}",
        "kind": "contract",
    }
    return insert_commercial_contract(
        con,
        identity=identity,
        client_id="client_test",
        license_assignment_id=f"license_{license_index}",
        terms=terms,
    )


def active_doc(con: sqlite3.Connection, *, charge_id=None, payment_id=None, kind: str) -> dict | None:
    if charge_id:
        row = con.execute(
            "SELECT * FROM CommercialFiscalDocument WHERE chargeId=? AND kind=? ORDER BY createdAt DESC,id DESC LIMIT 1",
            (charge_id, kind),
        ).fetchone()
    else:
        row = con.execute(
            "SELECT * FROM CommercialFiscalDocument WHERE paymentId=? AND kind=? ORDER BY createdAt DESC,id DESC LIMIT 1",
            (payment_id, kind),
        ).fetchone()
    return dict(row) if row else None


def verify() -> dict:
    checks: list[dict] = []

    def ok(name: str, evidence=None):
        checks.append({"name": name, "status": "PASS", "evidence": evidence})

    ids = IdFactory()
    with tempfile.TemporaryDirectory(prefix="prisma-billing-verify-") as tmp:
        db_path = Path(tmp) / "billing-sandbox.sqlite"
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        seed_minimal_core(con)
        con.commit()
        ok("sandbox_sqlite_only", str(db_path))

        table_names = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for expected in {
            "CommercialFiscalProfile", "CommercialIssuerProfile", "CommercialCharge", "CommercialPayment",
            "CommercialPaymentAllocation", "CommercialReceipt", "CommercialFiscalDocument", "CommercialBillingEvent",
        }:
            require(expected in table_names, f"Missing table {expected}")
        ok("billing_schema_complete", sorted(name for name in table_names if name.startswith("Commercial")))

        require(con.execute("SELECT COUNT(*) FROM CommercialFiscalProfile WHERE clientId='client_original'").fetchone()[0] == 0, "First customer received inferred fiscal profile")
        require(con.execute("SELECT COUNT(*) FROM CommercialCharge WHERE clientId='client_original'").fetchone()[0] == 0, "First customer received inferred charge")
        ok("first_customer_no_fiscal_or_charge_inference")

        contract_q = make_contract(con, "TABLET_PRO", "quarterly", 1, 1)
        require(contract_q["agreedPriceMxn"] == 1699, f"Expected Tablet Pro quarterly 1699, got {contract_q['agreedPriceMxn']}")
        charge_q = create_charge(
            con,
            {"contractCode": contract_q["humanCode"], "taxRateBps": 1600, "confirmTax": True, "dueOn": "2026-08-01", "asOf": "2026-08-01"},
            ids,
        )["charge"]
        require(charge_q["subtotalCents"] == 169900, "Quarterly subtotal cents incorrect")
        require(charge_q["taxCents"] == 27184, f"Expected IVA 27184 cents, got {charge_q['taxCents']}")
        require(charge_q["totalCents"] == 197084, f"Expected total 197084 cents, got {charge_q['totalCents']}")
        require(charge_q["dueOn"] == "2026-08-01", "Charge due date did not preserve contract/prepaid policy")
        ok("charge_from_contract_and_tax_cents", {"subtotal": 169900, "tax": 27184, "total": 197084})

        before_license = con.execute("SELECT status FROM LicenseAssignment WHERE id='license_1'").fetchone()[0]
        aged = reconcile_billing(con, as_of="2026-09-05", mutate_status=True)
        require(aged["overdueCents"] == 197084, f"Expected overdue total 197084, got {aged['overdueCents']}")
        require(con.execute("SELECT status FROM CommercialCharge WHERE id=?", (charge_q["id"],)).fetchone()[0] == "past_due", "Past due state not derived")
        require(con.execute("SELECT status FROM LicenseAssignment WHERE id='license_1'").fetchone()[0] == before_license, "Past due mutated licensing status")
        require(aged["pastDueDoesNotSuspendLicense"] is True, "Reconciliation missing no-auto-suspension contract")
        ok("aging_past_due_without_license_mutation", aged)

        blocked_pre_profiles = prepare_income_cfdi(con, {"chargeCode": charge_q["humanCode"]}, ids)
        require(blocked_pre_profiles["document"]["status"] == "draft_blocked", "CFDI should be blocked before fiscal profiles")
        require(blocked_pre_profiles["missingPrerequisites"], "Blocked CFDI did not report missing prerequisites")
        ok("cfdi_fail_closed_without_profiles", blocked_pre_profiles["missingPrerequisites"])

        receiver = save_receiver_profile(
            con,
            {
                "clientCode": "CLI-2026-900001",
                "rfc": "AAA010101AAA",
                "legalName": "CLIENTE FISCAL SANDBOX SA DE CV",
                "postalCode": "06000",
                "fiscalRegime": "601",
                "cfdiUse": "G03",
                "email": "facturacion@example.invalid",
                "sourceRef": "sandbox://receiver-fiscal-source",
                "confirmFiscalData": True,
            },
        )["profile"]
        require(receiver["status"] == "operator_confirmed", "Receiver profile not confirmed")
        issuer_result = save_issuer_profile(
            con,
            {
                "issuerRfc": "BBB010101BBB",
                "legalName": "PRISMA SANDBOX SA DE CV",
                "postalCode": "06000",
                "fiscalRegime": "601",
                "productServiceCode": "81112100",
                "unitCode": "E48",
                "unitName": "Unidad de servicio",
                "taxObjectCode": "02",
                "taxCode": "002",
                "exportCode": "01",
                "providerMode": "pac_external",
                "providerName": "PAC_SANDBOX_EXTERNAL",
                "csdState": "externally_managed",
                "sourceRef": "sandbox://issuer-fiscal-source",
                "confirmIssuerData": True,
            },
        )
        require(issuer_result["gateway"]["liveStampingAllowed"] is False, "Gateway falsely enabled live stamping")
        require(issuer_result["gateway"]["liveCancellationAllowed"] is False, "Gateway falsely enabled live cancellation")
        require(issuer_result["gateway"]["secretsExposed"] is False, "Gateway claims secret exposure")
        expect_billing_error(
            "BILLING_FISCAL_SECRET_FORBIDDEN",
            save_issuer_profile,
            con,
            {"issuerRfc": "BBB010101BBB", "privateKey": "NOPE"},
        )
        ok("fiscal_profiles_confirmed_without_secrets")

        income_q = prepare_income_cfdi(con, {"chargeCode": charge_q["humanCode"]}, ids)
        require(income_q["document"]["status"] == "ready_to_stamp", f"Income CFDI not ready after profiles: {income_q['document']['status']}")
        require(income_q["document"]["methodCode"] == "PPD", "Unpaid invoice must prepare as PPD")
        require(income_q["document"]["paymentForm"] == "99", "PPD invoice must prepare with form 99")
        ok("income_cfdi_ppd_99_before_payment")

        income_uuid = "123E4567-E89B-42D3-A456-426614174000"
        income_stamp = register_external_stamp(
            con,
            {
                "documentCode": income_q["document"]["humanCode"],
                "uuid": income_uuid,
                "provider": "PAC_SANDBOX_EXTERNAL",
                "providerEvidenceRef": "sandbox://stamp/income-q",
                "xmlSha256": "a" * 64,
            },
        )["document"]
        require(income_stamp["status"] == "external_stamped", "Income external stamp state not recorded")
        require(income_stamp["uuid"] == income_uuid, "Income UUID not preserved")
        ok("external_income_stamp_recorded_not_executed", income_uuid)

        partial_body = {
            "chargeCode": charge_q["humanCode"],
            "amountMxn": "1000.00",
            "currency": "MXN",
            "paymentForm": "03",
            "receivedAt": "2026-08-15T15:30:00+00:00",
            "externalReference": "EXT-PAY-0001",
            "evidenceRef": "sandbox://payment/0001",
            "idempotencyKey": "pay-quarterly-0001",
        }
        partial = register_external_payment(con, partial_body, ids)
        require(partial["charge"]["status"] == "past_due", f"Overdue partially paid charge should remain past_due, got {partial['charge']['status']}")
        require(partial["charge"]["paidCents"] == 100000, f"Expected paidCents 100000, got {partial['charge']['paidCents']}")
        require(partial["charge"]["balanceCents"] == 97084, f"Expected balance 97084, got {partial['charge']['balanceCents']}")
        require(partial["receipt"]["nonFiscal"] == 1, "Receipt must be explicitly non-fiscal")
        require("NO FISCAL" in partial["receipt"]["disclaimer"], "Receipt disclaimer missing NO FISCAL")
        alloc = partial["allocations"][0]
        require(alloc["partialityNumber"] == 1, "First partiality number should be 1")
        require(alloc["balanceBeforeCents"] == 197084 and alloc["amountCents"] == 100000 and alloc["balanceAfterCents"] == 97084, "Partiality balances incorrect")
        retry = register_external_payment(con, partial_body, ids)
        require(retry["idempotent"] is True and retry["payment"]["id"] == partial["payment"]["id"], "Identical retry duplicated payment")
        conflict = dict(partial_body)
        conflict["amountMxn"] = "1000.01"
        expect_billing_error("BILLING_IDEMPOTENCY_CONFLICT", register_external_payment, con, conflict, ids)
        require(con.execute("SELECT COUNT(*) FROM CommercialPayment WHERE idempotencyKey='pay-quarterly-0001'").fetchone()[0] == 1, "Idempotency conflict created duplicate row")
        ok("partial_payment_receipt_and_idempotency")

        complement = prepare_payment_complement(con, {"paymentCode": partial["payment"]["humanCode"]}, ids)
        require(complement["document"]["status"] == "ready_to_stamp", f"Payment complement not ready: {complement['missingPrerequisites']}")
        complement_payload = complement["document"]["draftPayload"]
        require(complement_payload["TipoDeComprobante"] == "P", "Payment complement top CFDI type must be P")
        require(complement_payload["Total"] == "0.00" and complement_payload["SubTotal"] == "0.00", "Payment CFDI top totals must be zero")
        require("MetodoPago" not in complement_payload and "FormaPago" not in complement_payload, "Payment CFDI must not use top-level MetodoPago/FormaPago")
        require(complement_payload["Receptor"]["UsoCFDI"] == "CP01", f"Payment complement must use CP01, got {complement_payload['Receptor'].get('UsoCFDI')}")
        related = complement_payload["Complemento"]["Pagos20"]["Pago"][0]["DoctoRelacionado"][0]
        require(related["IdDocumento"] == income_uuid, "Payment complement did not relate parent CFDI UUID")
        require(related["NumParcialidad"] == "1", "Payment complement partiality incorrect")
        require(related["ImpSaldoAnt"] == "1970.84", "Payment complement prior balance incorrect")
        require(related["ImpPagado"] == "1000.00", "Payment complement paid amount incorrect")
        require(related["ImpSaldoInsoluto"] == "970.84", "Payment complement remaining balance incorrect")
        ok("payment_complement_20_draft_trace", related)

        complement_uuid = "223E4567-E89B-42D3-A456-426614174001"
        complement_stamp = register_external_stamp(
            con,
            {
                "documentCode": complement["document"]["humanCode"],
                "uuid": complement_uuid,
                "provider": "PAC_SANDBOX_EXTERNAL",
                "providerEvidenceRef": "sandbox://stamp/payment-q",
            },
        )["document"]
        require(complement_stamp["status"] == "external_stamped", "Payment complement stamp state missing")
        expect_billing_error(
            "BILLING_PAYMENT_REVERSE_BLOCKED_BY_CFDI",
            reverse_external_payment,
            con,
            {"paymentCode": partial["payment"]["humanCode"], "confirmReverse": True, "reason": "sandbox correction"},
        )
        ok("payment_reversal_blocked_by_stamped_complement")

        expect_billing_error(
            "CFDI_UUID_INVALID",
            request_cfdi_cancellation,
            con,
            {"documentCode": complement["document"]["humanCode"], "reason": "01", "confirmCancellationRequest": True},
        )
        replacement_uuid = "323E4567-E89B-42D3-A456-426614174002"
        cancel_request = request_cfdi_cancellation(
            con,
            {"documentCode": complement["document"]["humanCode"], "reason": "01", "replacementUuid": replacement_uuid, "confirmCancellationRequest": True},
        )["document"]
        require(cancel_request["status"] == "cancel_requested", "Cancellation request state missing")
        require(cancel_request["replacementUuid"] == replacement_uuid, "Replacement UUID not preserved")
        cancelled = register_external_cancellation_result(
            con,
            {"documentCode": complement["document"]["humanCode"], "cancelled": True, "evidenceRef": "sandbox://cancel/payment-q"},
        )["document"]
        require(cancelled["status"] == "cancelled", "External cancellation result not recorded")
        reversed_after_cancel = reverse_external_payment(
            con,
            {"paymentCode": partial["payment"]["humanCode"], "confirmReverse": True, "reason": "sandbox correction after fiscal cancellation"},
        )
        require(reversed_after_cancel["payment"]["status"] == "reversed", "Payment could not be reversed after fiscal complement cancellation")
        ok("fiscal_cancellation_reason_01_and_post_cancel_reversal")

        contract_pue = make_contract(con, "TABLET_SOLO", "monthly", 2, 2, "2026-08-10")
        charge_pue = create_charge(con, {"contractCode": contract_pue["humanCode"], "taxRateBps": 1600, "confirmTax": True, "asOf": "2026-08-10"}, ids)["charge"]
        full_amount = f"{charge_pue['totalCents'] // 100}.{charge_pue['totalCents'] % 100:02d}"
        full_payment = register_external_payment(
            con,
            {
                "chargeCode": charge_pue["humanCode"],
                "amountMxn": full_amount,
                "paymentForm": "01",
                "receivedAt": "2026-08-10T18:00:00+00:00",
                "externalReference": "CASH-TEST-0001",
                "idempotencyKey": "pay-pue-full-0001",
            },
            ids,
        )
        require(full_payment["charge"]["status"] == "paid", "Full payment did not close charge")
        income_pue = prepare_income_cfdi(con, {"chargeCode": charge_pue["humanCode"]}, ids)
        require(income_pue["document"]["methodCode"] == "PUE", "Fully paid one-payment invoice should be PUE")
        require(income_pue["document"]["paymentForm"] == "01", "PUE did not preserve actual payment form")
        ok("income_cfdi_pue_after_single_full_payment")

        income_pue_stamp = register_external_stamp(
            con,
            {
                "documentCode": income_pue["document"]["humanCode"],
                "uuid": "423E4567-E89B-42D3-A456-426614174003",
                "provider": "PAC_SANDBOX_EXTERNAL",
                "providerEvidenceRef": "sandbox://stamp/income-pue",
            },
        )["document"]
        request_cfdi_cancellation(con, {"documentCode": income_pue_stamp["humanCode"], "reason": "02", "confirmCancellationRequest": True})
        register_external_cancellation_result(con, {"documentCode": income_pue_stamp["humanCode"], "cancelled": True, "evidenceRef": "sandbox://cancel/income-pue"})
        replacement = prepare_income_cfdi(con, {"chargeCode": charge_pue["humanCode"]}, ids)["document"]
        require(replacement["humanCode"] != income_pue_stamp["humanCode"], "Cancelled CFDI history was overwritten instead of creating replacement attempt")
        require(con.execute("SELECT COUNT(*) FROM CommercialFiscalDocument WHERE chargeId=? AND kind='CFDI_INGRESO'", (charge_pue["id"],)).fetchone()[0] == 2, "Cancelled fiscal document history not preserved")
        ok("cancelled_cfdi_is_immutable_and_replacement_is_new_document")

        contract_over = make_contract(con, "TABLET_SOLO", "monthly", 3, 3, "2026-08-12")
        charge_over = create_charge(con, {"contractCode": contract_over["humanCode"], "taxRateBps": 1600, "confirmTax": True}, ids)["charge"]
        income_over = prepare_income_cfdi(con, {"chargeCode": charge_over["humanCode"]}, ids)["document"]
        register_external_stamp(
            con,
            {"documentCode": income_over["humanCode"], "uuid": "523E4567-E89B-42D3-A456-426614174004", "provider": "PAC_SANDBOX_EXTERNAL", "providerEvidenceRef": "sandbox://stamp/income-over"},
        )
        over_amount_cents = charge_over["totalCents"] + 10000
        over_amount = f"{over_amount_cents // 100}.{over_amount_cents % 100:02d}"
        overpay = register_external_payment(
            con,
            {"chargeCode": charge_over["humanCode"], "amountMxn": over_amount, "paymentForm": "03", "receivedAt": "2026-08-12T18:00:00+00:00", "externalReference": "OVERPAY-TEST", "idempotencyKey": "pay-over-0001"},
            ids,
        )
        require(overpay["payment"]["unappliedCents"] == 10000, "Overpayment unapplied credit incorrect")
        over_complement = prepare_payment_complement(con, {"paymentCode": overpay["payment"]["humanCode"]}, ids)
        require(over_complement["document"]["status"] == "draft_blocked", "Payment complement must block when payment contains unapplied amount")
        require(any("unapplied" in item.lower() for item in over_complement["missingPrerequisites"]), f"Missing unapplied prerequisite: {over_complement['missingPrerequisites']}")
        ok("overpayment_unapplied_credit_blocks_payment_complement", overpay["payment"]["unappliedCents"])

        contract_void = make_contract(con, "TABLET_SOLO", "monthly", 4, 4, "2026-08-20")
        charge_void = create_charge(con, {"contractCode": contract_void["humanCode"], "taxRateBps": 1600, "confirmTax": True}, ids)["charge"]
        voided = void_charge(con, {"chargeCode": charge_void["humanCode"], "confirmVoid": True, "reason": "sandbox void without payment"})["charge"]
        require(voided["status"] == "void", "Unpaid charge void failed")
        ok("void_preserves_history")

        snap = billing_snapshot(con, as_of="2026-09-05")
        for key in ("moneyProcessing", "bankValidation", "cardCapture", "speiValidation", "automaticBankReconciliation", "licenseAutoSuspension"):
            require(snap[key] is False, f"Boundary flag {key} must be false")
        require(snap["gateway"]["liveStampingAllowed"] is False and snap["gateway"]["liveCancellationAllowed"] is False, "Fiscal gateway must remain external/fail-closed")
        ok("financial_and_fiscal_external_boundaries", {k: snap[k] for k in ("moneyProcessing", "bankValidation", "cardCapture", "speiValidation", "automaticBankReconciliation", "licenseAutoSuspension")})

        secret_terms = ("password", "privatekey", "private_key", "token", "cvv", "pan", "clabe", "bankaccount", "accountnumber")
        schema_text = "\n".join(row[0] for row in con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"))
        source_text = (BILLING_SOURCE.read_text(encoding="utf-8") + "\n" + CFDI_SOURCE.read_text(encoding="utf-8")).lower()
        for term in secret_terms:
            require(term not in schema_text.lower(), f"Forbidden secret/bank field found in schema: {term}")
        require("liveStampingAllowed\": True".lower() not in source_text, "Source enables live stamping")
        ok("no_secret_or_bank_storage_schema")

        doc_text = DOC_CONTRACT.read_text(encoding="utf-8")
        no_pay_text = NO_PAYMENT_DOC.read_text(encoding="utf-8")
        require("RECIBO INTERNO NO FISCAL" in doc_text, "Productization contract missing non-fiscal receipt boundary")
        require("liveStampingAllowed=false" in doc_text, "Productization contract missing live stamping fail-closed state")
        require("no procesa pagos bancarios" in no_pay_text, "Existing no-payment addendum boundary missing")
        ok("productization_contract_boundaries")

        js = JS_PATH.read_text(encoding="utf-8")
        for marker in (
            '["billing", "Cobranza"',
            'function renderBilling()',
            'billing-register-payment',
            'billing-prepare-income-cfdi',
            'billing-prepare-payment-complement',
            'billing-request-cancellation',
            'Registrar pago externo',
            'RECIBO INTERNO NO FISCAL',
        ):
            require(marker in js, f"Cloud Center billing UI missing marker: {marker}")
        for forbidden_copy in ("Pagar ahora", "Ingresar tarjeta", "Confirmar pago bancario"):
            require(forbidden_copy not in js, f"Forbidden payment-processing UI copy found: {forbidden_copy}")
        ok("cloud_center_billing_surface_and_copy_boundary")

        con.commit()
        con.close()

    return {
        "status": "PASS_COMMERCIAL_BILLING_CFDI_LOCAL_VERIFIED",
        "checkedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "checks": checks,
        "checkCount": len(checks),
        "liveStampingCertified": False,
        "liveCancellationCertified": False,
        "bankPaymentProcessing": False,
        "realDbTouched": False,
        "firstCustomerFiscalDataInferred": False,
    }


def write_report(out_dir: Path, report: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "COMMERCIAL_BILLING_VERIFY.json"
    md_path = out_dir / "COMMERCIAL_BILLING_VERIFY.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# PRISMA Commercial Billing & CFDI Verification",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Checked at: `{report.get('checkedAt')}`",
        f"- Check count: `{report.get('checkCount', 0)}`",
        f"- Live stamping certified: `{str(report.get('liveStampingCertified')).lower()}`",
        f"- Live cancellation certified: `{str(report.get('liveCancellationCertified')).lower()}`",
        f"- Bank payment processing: `{str(report.get('bankPaymentProcessing')).lower()}`",
        f"- Real DB touched: `{str(report.get('realDbTouched')).lower()}`",
        "",
        "## Checks",
        "",
    ]
    for item in report.get("checks", []):
        lines.append(f"- `{item.get('status')}` **{item.get('name')}**")
    if report.get("error"):
        lines.extend(["", "## Error", "", "```text", str(report["error"]), "```"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".governance/current")
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    try:
        report = verify()
        write_report(out_dir, report)
        print(report["status"])
        print(f"checks={report['checkCount']}")
        return 0
    except Exception as exc:
        report = {
            "status": "FAIL_COMMERCIAL_BILLING_CFDI_VERIFY",
            "checkedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "checkCount": 0,
            "checks": [],
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "liveStampingCertified": False,
            "liveCancellationCertified": False,
            "bankPaymentProcessing": False,
            "realDbTouched": False,
        }
        write_report(out_dir, report)
        print(report["status"], file=sys.stderr)
        print(report["error"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
