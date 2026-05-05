#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "0.8.0"
PACKAGE = "PRISMA_LICENSE_DEVICE_ACTIVATION_HARDENING_08"
PLAN_LIMITS = {
    "TABLET_SOLO": {"terminalLimit": 1, "branchLimit": 1},
    "TABLET_PRO": {"terminalLimit": 2, "branchLimit": 1},
    "TABLET_PC_REQUIRED": {"terminalLimit": 6, "branchLimit": 3},
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")


def default_out_dir() -> Path:
    return Path(r"F:\descargasf") if os.name == "nt" else Path(tempfile.gettempdir())


def resolve_root(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path.cwd().resolve()


def default_store(root: Path) -> Path:
    return root / "local-runtime" / "license-server" / "license-server-store.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON raíz inválido: {path}")
    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def read_policy(root: Path) -> dict[str, Any]:
    path = root / "tooling" / "licensing" / "device08" / "device_activation_policy.json"
    return load_json(path)


def read_matrix(root: Path) -> dict[str, Any]:
    path = root / "tooling" / "licensing" / "device08" / "device_activation_matrix.json"
    return load_json(path)


def active_devices(store: dict[str, Any]) -> list[dict[str, Any]]:
    devices = store.get("devices", {})
    if not isinstance(devices, dict):
        return []
    return [d for d in devices.values() if isinstance(d, dict) and d.get("status") == "active"]


def branch_id(device: dict[str, Any]) -> str:
    return str(device.get("branchId") or device.get("businessId") or "default")


def evaluate_counts(plan: str, terminal_count: int, branch_count: int) -> str:
    limits = PLAN_LIMITS.get(plan)
    if not limits:
        return "block_unknown_plan"
    if terminal_count > limits["terminalLimit"]:
        return "block_terminal_limit"
    if branch_count > limits["branchLimit"]:
        return "block_branch_limit"
    return "allow"


def audit_store(store: dict[str, Any], strict: bool = False) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    devices = store.get("devices", {}) if isinstance(store.get("devices", {}), dict) else {}
    licenses = store.get("licenses", {}) if isinstance(store.get("licenses", {}), dict) else {}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for device in devices.values():
        if not isinstance(device, dict):
            warnings.append("Dispositivo inválido no dict en store.devices")
            continue
        if device.get("status") != "active":
            continue
        business_id = str(device.get("businessId") or "missing_business")
        plan = str(device.get("plan") or "missing_plan")
        groups.setdefault((business_id, plan), []).append(device)
        for field in ["customerId", "businessId", "deviceId", "terminalId", "plan", "activatedAt", "status", "licenseId"]:
            if not device.get(field):
                errors.append(f"Device {device.get('deviceId') or '<sin id>'} sin campo requerido {field}")
        if not device.get("installationFingerprint"):
            warnings.append(f"Device {device.get('deviceId')} sin installationFingerprint; 06 lo permite, 08 lo recomienda")
        lic_id = device.get("licenseId")
        if lic_id and lic_id not in licenses:
            errors.append(f"Device {device.get('deviceId')} apunta a licencia inexistente {lic_id}")
    for (business_id, plan), items in sorted(groups.items()):
        branches = {branch_id(item) for item in items}
        decision = evaluate_counts(plan, len(items), len(branches))
        if decision != "allow":
            errors.append(f"{business_id}/{plan}: {decision} terminales={len(items)} sucursales={len(branches)}")
        else:
            notes.append(f"{business_id}/{plan}: OK terminales={len(items)} sucursales={len(branches)}")
    if strict and warnings:
        errors.extend("STRICT " + w for w in warnings)
    return errors, warnings, notes


def write_report(out_dir: Path, prefix: str, title: str, body_lines: list[str]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{prefix}_{now_stamp()}.md"
    text = "\n".join([f"# {title}", "", f"Generado: {utc_now()}", "", *body_lines, ""])
    path.write_text(text, encoding="utf-8")
    return path


def cmd_policy(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    policy = read_policy(root)
    print(json.dumps(policy, ensure_ascii=False, indent=2))
    print("FINAL READY")
    return 0


def cmd_matrix(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    matrix = read_matrix(root)
    rows = []
    errors = []
    for case in matrix.get("cases", []):
        plan = str(case.get("plan"))
        terminals = int(case.get("activeTerminals", 0))
        branches = int(case.get("branches", 0))
        expected = str(case.get("expected"))
        actual = evaluate_counts(plan, terminals, branches)
        ok = actual == expected
        if not ok:
            errors.append(f"{case.get('caseId')}: esperado={expected} actual={actual}")
        rows.append(f"| {case.get('caseId')} | {plan} | {terminals} | {branches} | {expected} | {actual} | {'OK' if ok else 'FAIL'} |")
    body = [
        "## Matriz",
        "",
        "| Caso | Plan | Terminales | Sucursales | Esperado | Actual | Resultado |",
        "|---|---|---:|---:|---|---|---|",
        *rows,
    ]
    if errors:
        body += ["", "## Errores", *[f"- {e}" for e in errors]]
    report = write_report(Path(args.out_dir or default_out_dir()), "prisma_license_device_matrix_08", "PRISMA License Device Matrix 08", body)
    print(f"REPORT {report}")
    if errors:
        print("FINAL BLOCKED")
        return 2
    print("FINAL READY")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    store_path = Path(args.store).resolve() if args.store else default_store(root)
    if not store_path.exists():
        raise RuntimeError(f"No existe store del servidor 06: {store_path}")
    store = load_json(store_path)
    errors, warnings, notes = audit_store(store, strict=bool(args.strict))
    body = [
        f"Store: `{store_path}`",
        "",
        "## Resumen",
        "",
        f"- customers: {len(store.get('customers', {}) if isinstance(store.get('customers', {}), dict) else {})}",
        f"- businesses: {len(store.get('businesses', {}) if isinstance(store.get('businesses', {}), dict) else {})}",
        f"- devices: {len(store.get('devices', {}) if isinstance(store.get('devices', {}), dict) else {})}",
        f"- licenses: {len(store.get('licenses', {}) if isinstance(store.get('licenses', {}), dict) else {})}",
        f"- events: {len(store.get('events', []) if isinstance(store.get('events', []), list) else [])}",
        "",
        "## OK",
        *([f"- {n}" for n in notes] or ["- Sin grupos activos detectados."]),
        "",
        "## Advertencias",
        *([f"- {w}" for w in warnings] or ["- Sin advertencias."]),
        "",
        "## Errores",
        *([f"- {e}" for e in errors] or ["- Sin errores."]),
    ]
    report = write_report(Path(args.out_dir or default_out_dir()), "prisma_license_device_audit_08", "PRISMA License Device Audit 08", body)
    print(f"REPORT {report}")
    if errors:
        print("FINAL BLOCKED")
        return 2
    print("FINAL READY")
    return 0


def append_event(store: dict[str, Any], event_type: str, payload: dict[str, Any]) -> None:
    events = store.setdefault("events", [])
    if not isinstance(events, list):
        store["events"] = []
        events = store["events"]
    events.append({
        "eventId": "evt_" + hashlib.sha256((event_type + utc_now() + json.dumps(payload, sort_keys=True)).encode("utf-8")).hexdigest()[:16],
        "type": event_type,
        "occurredAt": utc_now(),
        "payload": payload,
        "source": PACKAGE,
    })


def cmd_reset(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    store_path = Path(args.store).resolve() if args.store else default_store(root)
    if not store_path.exists():
        raise RuntimeError(f"No existe store del servidor 06: {store_path}")
    if not args.device_id:
        raise RuntimeError("--device-id es obligatorio")
    store = load_json(store_path)
    devices = store.setdefault("devices", {})
    licenses = store.setdefault("licenses", {})
    device = devices.get(args.device_id)
    if not isinstance(device, dict):
        raise RuntimeError(f"No existe deviceId en store.devices: {args.device_id}")
    backup_dir = root / ".prisma_license_device_activation_08_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"license-server-store.before-device-reset.{now_stamp()}.json"
    shutil.copy2(store_path, backup_path)
    old_status = device.get("status")
    reason = args.reason or "support_reset"
    operator = args.operator or "support"
    device["previousStatus"] = old_status
    device["status"] = "reset"
    device["supportResetAt"] = utc_now()
    device["supportResetBy"] = operator
    device["supportResetReason"] = reason
    license_id = device.get("licenseId")
    if license_id and isinstance(licenses.get(license_id), dict):
        lic = licenses[license_id]
        lic["state"] = "suspended"
        lic["statusReason"] = "support_reset"
        lic["statusChangedAt"] = utc_now()
    append_event(store, "device.support_reset", {"deviceId": args.device_id, "reason": reason, "operator": operator, "backup": str(backup_path)})
    save_json(store_path, store)
    print(f"BACKUP {backup_path}")
    print(f"RESET deviceId={args.device_id} previous={old_status} current=reset")
    print("FINAL READY")
    return 0


def cmd_fingerprint(args: argparse.Namespace) -> int:
    parts = [args.customer_id or "", args.business_id or "", args.terminal_id or "", args.device_id or ""]
    raw = "|".join(parts).encode("utf-8")
    print(hashlib.sha256(raw).hexdigest())
    print("FINAL READY")
    return 0


def sample_store() -> dict[str, Any]:
    return {
        "schemaVersion": "06.mvp.1",
        "createdAt": utc_now(),
        "customers": {"cust_demo": {"customerId": "cust_demo", "status": "active"}},
        "businesses": {"biz_demo": {"businessId": "biz_demo", "customerId": "cust_demo", "status": "active"}},
        "devices": {
            "device_demo_tablet_01": {"customerId": "cust_demo", "businessId": "biz_demo", "deviceId": "device_demo_tablet_01", "terminalId": "tablet_01", "plan": "TABLET_PRO", "activatedAt": utc_now(), "status": "active", "licenseId": "lic_demo_01", "branchId": "sucursal_01", "installationFingerprint": "fp_demo_01"},
            "device_demo_tablet_02": {"customerId": "cust_demo", "businessId": "biz_demo", "deviceId": "device_demo_tablet_02", "terminalId": "tablet_02", "plan": "TABLET_PRO", "activatedAt": utc_now(), "status": "active", "licenseId": "lic_demo_02", "branchId": "sucursal_01", "installationFingerprint": "fp_demo_02"},
        },
        "licenses": {"lic_demo_01": {"licenseId": "lic_demo_01", "deviceId": "device_demo_tablet_01", "state": "active"}, "lic_demo_02": {"licenseId": "lic_demo_02", "deviceId": "device_demo_tablet_02", "state": "active"}},
        "events": [],
    }


def cmd_smoke_offline(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir or default_out_dir())
    with tempfile.TemporaryDirectory(prefix="prisma_device08_") as tmp:
        root = Path(tmp)
        store_path = root / "local-runtime" / "license-server" / "license-server-store.json"
        save_json(store_path, sample_store())
        store = load_json(store_path)
        errors, warnings, notes = audit_store(store)
        if errors:
            print("SMOKE audit errors before reset:", errors)
            return 2
        ns = argparse.Namespace(root=str(root), store=str(store_path), device_id="device_demo_tablet_01", reason="smoke_reset", operator="smoke")
        code = cmd_reset(ns)
        if code != 0:
            return code
        store2 = load_json(store_path)
        if store2["devices"]["device_demo_tablet_01"].get("status") != "reset":
            print("SMOKE failed: reset status not persisted")
            return 2
        errors2, warnings2, notes2 = audit_store(store2)
        if errors2:
            print("SMOKE audit errors after reset:", errors2)
            return 2
    report = write_report(out_dir, "prisma_license_device_smoke_08", "PRISMA License Device Smoke 08", ["- audit before reset: OK", "- support reset: OK", "- audit after reset: OK"])
    print(f"REPORT {report}")
    print("FINAL READY")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PRISMA License Device Activation Hardening 08")
    p.add_argument("--root", default=None, help="Raíz de terminal-de-venta-system")
    p.add_argument("--out-dir", default=None, help="Directorio de reportes; default F:\\descargasf en Windows")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("policy")
    sub.add_parser("matrix")

    audit = sub.add_parser("audit")
    audit.add_argument("--store", default=None)
    audit.add_argument("--strict", action="store_true")

    reset = sub.add_parser("reset")
    reset.add_argument("--store", default=None)
    reset.add_argument("--device-id", required=True)
    reset.add_argument("--reason", default="support_reset")
    reset.add_argument("--operator", default="support")

    fp = sub.add_parser("fingerprint")
    fp.add_argument("--customer-id", required=True)
    fp.add_argument("--business-id", required=True)
    fp.add_argument("--terminal-id", required=True)
    fp.add_argument("--device-id", required=True)

    sub.add_parser("smoke-offline")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "policy":
            return cmd_policy(args)
        if args.command == "matrix":
            return cmd_matrix(args)
        if args.command == "audit":
            return cmd_audit(args)
        if args.command == "reset":
            return cmd_reset(args)
        if args.command == "fingerprint":
            return cmd_fingerprint(args)
        if args.command == "smoke-offline":
            return cmd_smoke_offline(args)
        raise RuntimeError(f"Comando no soportado: {args.command}")
    except Exception as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
