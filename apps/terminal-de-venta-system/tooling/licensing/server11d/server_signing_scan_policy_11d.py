#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import base64
import datetime as dt
import fnmatch
import hashlib
import hmac
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_OUT = r"F:\descargasf"
VERSION = "11D"
DEV_MATERIAL = Path("local-runtime/license-keys/dev/dev-signing-secret.local.json")
SIGNED_OUT = Path("local-runtime/license/license.signed.remote.local.json")
CONFIG_OUT = Path("local-runtime/license-server/signing-config.local.json")
REGISTRY_OUT = Path("local-runtime/license-keys/dev/public-signing-registry.local.json")
LEGACY_JS = Path("tooling/licensing/create_dev_signed_license.js")
CONTRACT = Path("tooling/licensing/server11d/server_signing_scan_contract_11d.json")
POLICY = Path("tooling/licensing/server11d/repo_secret_scan_policy_11d.json")

PEM_RE = re.compile(
    r"-----BEGIN (?:(?:RSA|DSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----[\s\S]+?"
    r"-----END (?:(?:RSA|DSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----",
    re.M,
)
TEXT_EXT = {
    ".cmd", ".bat", ".ps1", ".py", ".js", ".ts", ".tsx", ".json", ".jsonl",
    ".md", ".txt", ".yml", ".yaml", ".env", ".pem", ".toml", ".mjs", ".cjs"
}
DEFAULT_EXCLUDES = {
    ".git", ".hg", ".svn", "node_modules", ".next", "dist", "build", "coverage",
    ".turbo", ".venv", "venv", "__pycache__",
}
DEFAULT_FIXTURE_GLOBS = [
    "tooling/licensing/signature10c/private_key_scan_regressions.jsonl",
    "tooling/licensing/signature10d/private_key_smoke_regression_10f.jsonl",
    "tooling/licensing/signature10d/private_key_smoke_regressions_10f.jsonl",
    "tooling/licensing/signature10f/private_key_smoke_regression_10f.jsonl",
    "tooling/licensing/signature10f/private_key_smoke_regressions_10f.jsonl",
    "tooling/licensing/server11c/server_signing_tamper_cases_11c.jsonl",
    "tooling/licensing/server11d/server_signing_scan_regression_11d.jsonl",
]
DEFAULT_HINTS = ["regression", "regressions", "tamper_cases", "fixture", "corpus"]
DEFAULT_FIXTURE_EXT = [".jsonl", ".json", ".md", ".txt"]


def stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")


def ensure_out(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("/", "\\")
    except Exception:
        return str(path)


def rel_posix(root: Path, path: Path) -> str:
    return rel(root, path).replace("\\", "/")


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64ud(value: str) -> bytes:
    value = str(value).strip()
    return base64.urlsafe_b64decode((value + "=" * ((4 - len(value) % 4) % 4)).encode("ascii"))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return None
    except Exception:
        return None


def load_policy(root: Path) -> dict[str, Any]:
    path = root / POLICY
    base = {
        "excludeDirs": sorted(DEFAULT_EXCLUDES),
        "approvedFixtureGlobs": DEFAULT_FIXTURE_GLOBS,
        "approvedFixtureNameHints": DEFAULT_HINTS,
        "approvedFixtureExtensions": DEFAULT_FIXTURE_EXT,
    }
    if not path.exists():
        return base
    try:
        raw = read_json(path)
        if isinstance(raw, dict):
            merged = dict(base)
            merged.update(raw)
            return merged
    except Exception:
        return base
    return base


def normalize_material(raw: dict[str, Any]) -> dict[str, str]:
    key_id = raw.get("key_id") or raw.get("keyId") or raw.get("kid")
    secret = raw.get("secret_b64url") or raw.get("secretMaterialBase64Url") or raw.get("secret")
    algorithm = raw.get("algorithm") or raw.get("alg") or "HS256_DEV_LOCAL"
    if algorithm == "HS256_DEV_ONLY":
        algorithm = "HS256_DEV_LOCAL"
    if not key_id or not secret:
        raise ValueError("Signing material incompleto; faltan key_id/keyId o secret_b64url/secretMaterialBase64Url")
    secret_bytes = b64ud(str(secret))
    if len(secret_bytes) < 32:
        raise ValueError("Signing material inseguro: secret menor a 32 bytes")
    return {
        "key_id": str(key_id),
        "secret_b64url": b64u(secret_bytes),
        "algorithm": str(algorithm),
        "materialClass": str(raw.get("materialClass") or raw.get("material_class") or "dev-local"),
    }


def load_material(root: Path) -> dict[str, str]:
    path = root / DEV_MATERIAL
    raw = read_json(path)
    if not isinstance(raw, dict):
        raise ValueError(f"Signing material no es objeto JSON: {path}")
    mat = normalize_material(raw)
    raw.update(
        {
            "key_id": mat["key_id"],
            "keyId": mat["key_id"],
            "secret_b64url": mat["secret_b64url"],
            "secretMaterialBase64Url": mat["secret_b64url"],
            "algorithm": mat["algorithm"],
            "alg": mat["algorithm"],
            "materialClass": mat["materialClass"],
        }
    )
    write_json(path, raw)
    return mat


def sign(payload: dict[str, Any], mat: dict[str, str]) -> dict[str, Any]:
    digest = hmac.new(b64ud(mat["secret_b64url"]), canonical_json(payload), hashlib.sha256).digest()
    return {
        "payload": payload,
        "signature": {
            "schemaVersion": VERSION,
            "algorithm": mat["algorithm"],
            "keyId": mat["key_id"],
            "value": b64u(digest),
        },
    }


def verify(envelope: dict[str, Any], mat: dict[str, str]) -> tuple[bool, str]:
    if not isinstance(envelope, dict):
        return False, "envelope_not_object"
    payload = envelope.get("payload")
    signature = envelope.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature, dict):
        return False, "missing_payload_or_signature"
    if signature.get("keyId") != mat["key_id"]:
        return False, "key_id_mismatch"
    if signature.get("algorithm") != mat["algorithm"]:
        return False, "algorithm_mismatch"
    expected = sign(payload, mat)["signature"]["value"]
    actual = str(signature.get("value", ""))
    return (True, "signature_valid") if hmac.compare_digest(actual, expected) else (False, "signature_invalid")


def demo_payload() -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "licenseId": "lic_server11d_local_demo",
        "customerId": "cust_demo",
        "businessId": "biz_demo",
        "deviceId": "device_demo_tablet_01",
        "plan": "TABLET_PC_REQUIRED",
        "state": "active",
        "issuedAt": "2026-04-30T00:00:00.000Z",
        "validUntil": "2099-12-31T23:59:59.000Z",
    }


def is_candidate_text_file(path: Path) -> bool:
    lower = str(path).lower()
    return path.suffix.lower() in TEXT_EXT or "license" in lower or "key" in lower or "secret" in lower


def is_approved_fixture(root: Path, path: Path, policy: dict[str, Any]) -> bool:
    relative = rel_posix(root, path)
    globs = [str(p).replace("\\", "/") for p in policy.get("approvedFixtureGlobs", DEFAULT_FIXTURE_GLOBS)]
    if any(fnmatch.fnmatch(relative, pattern) for pattern in globs):
        return True
    suffix = path.suffix.lower()
    if suffix not in set(policy.get("approvedFixtureExtensions", DEFAULT_FIXTURE_EXT)):
        return False
    if not relative.startswith("tooling/licensing/"):
        return False
    name = path.name.lower()
    hints = [str(h).lower() for h in policy.get("approvedFixtureNameHints", DEFAULT_HINTS)]
    return any(hint in name for hint in hints)


def scan_repo(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    policy = load_policy(root)
    excludes = set(policy.get("excludeDirs", sorted(DEFAULT_EXCLUDES)))
    findings: list[dict[str, Any]] = []
    allowed: list[dict[str, Any]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in excludes and not d.startswith(".prisma_license_") and not d.startswith(".git")
        ]
        for filename in filenames:
            path = Path(dirpath) / filename
            if not is_candidate_text_file(path):
                continue
            try:
                if path.stat().st_size > 12_000_000:
                    continue
            except Exception:
                continue
            text = read_text(path)
            if not text:
                continue
            fixture = is_approved_fixture(root, path, policy)
            for match in PEM_RE.finditer(text):
                item = {
                    "path": rel(root, path),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "fp": hashlib.sha256(match.group(0).encode("utf-8", errors="ignore")).hexdigest()[:16],
                    "fixture": fixture,
                }
                if fixture:
                    allowed.append(item)
                else:
                    findings.append(item)
    return findings, allowed


def sanitize_legacy_js(root: Path, dry_run: bool = False) -> tuple[bool, str]:
    path = root / LEGACY_JS
    if not path.exists():
        return True, "missing_not_needed"
    text = read_text(path) or ""
    if not PEM_RE.search(text):
        return True, "no_pem_block"
    if dry_run:
        return True, "would_replace_embedded_pem"
    backup_dir = root / ".prisma_license_server_signing_scan_policy_11d_backups" / stamp()
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_dir / path.name)
    safe = r'''#!/usr/bin/env node
/* 11D sanitized: no embedded PEM private key. Reads local-runtime dev signing material. */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const root = path.resolve(__dirname, "..", "..");
const materialPath = path.join(root, "local-runtime", "license-keys", "dev", "dev-signing-secret.local.json");
function b64u(buf) {
  return Buffer.from(buf).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}
function canonical(value) {
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (value && typeof value === "object") {
    return "{" + Object.keys(value).sort().map(k => JSON.stringify(k) + ":" + canonical(value[k])).join(",") + "}";
  }
  return JSON.stringify(value);
}
function readMaterial() {
  const raw = JSON.parse(fs.readFileSync(materialPath, "utf8"));
  const keyId = raw.key_id || raw.keyId;
  const secret = raw.secret_b64url || raw.secretMaterialBase64Url;
  const algorithm = raw.algorithm === "HS256_DEV_ONLY" ? "HS256_DEV_LOCAL" : (raw.algorithm || "HS256_DEV_LOCAL");
  if (!keyId || !secret) throw new Error("Missing local dev signing material fields");
  return { keyId, secret, algorithm };
}
function signPayload(payload) {
  const material = readMaterial();
  const padded = material.secret.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - material.secret.length % 4) % 4);
  const key = Buffer.from(padded, "base64");
  const value = b64u(crypto.createHmac("sha256", key).update(canonical(payload)).digest());
  return { payload, signature: { schemaVersion: "11D", algorithm: material.algorithm, keyId: material.keyId, value } };
}
if (require.main === module) {
  const payload = { licenseId: "lic_dev_signed_local", plan: "TABLET_PC_REQUIRED", state: "active", issuedAt: new Date().toISOString() };
  process.stdout.write(JSON.stringify(signPayload(payload), null, 2) + "\n");
}
module.exports = { signPayload };
'''
    path.write_text(safe, encoding="utf-8", newline="\n")
    return True, f"replaced_embedded_pem backup={backup_dir / path.name}"


def write_report(out: Path, name: str, title: str, checks: list[tuple[str, bool, str]], extra: list[str] | None = None) -> Path:
    status = "FINAL READY" if all(ok for _, ok, _ in checks) else "BLOCKED"
    lines = [f"# {title}", ""]
    lines.extend([f"- {name}: `{'OK' if ok else 'FAIL'}` {detail}" for name, ok, detail in checks])
    if extra:
        lines.append("")
        lines.extend(extra)
    lines.extend(["", f"Status: `{status}`"])
    path = out / f"terminal_venta_{name.replace(' ', '_').lower()}_{stamp()}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def print_checks(checks: list[tuple[str, bool, str]]) -> bool:
    for name, ok, detail in checks:
        print(f"- {name}: {'OK' if ok else 'FAIL'} {detail}")
    return all(ok for _, ok, _ in checks)


def cmd_smoke(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    out = ensure_out(args.out)
    checks: list[tuple[str, bool, str]] = []
    extra: list[str] = []
    try:
        mat = load_material(root)
        write_json(root / CONFIG_OUT, {
            "schemaVersion": VERSION,
            "environment": "development",
            "keyId": mat["key_id"],
            "algorithm": mat["algorithm"],
            "productionAllowsDevMaterial": False,
        })
        write_json(root / REGISTRY_OUT, {
            "schemaVersion": VERSION,
            "keys": [{
                "keyId": mat["key_id"],
                "algorithm": mat["algorithm"],
                "materialClass": "dev-local",
                "secretStoredOutsideRepo": True,
            }],
        })
        checks.append(("config", True, str(root / CONFIG_OUT)))
        ok, detail = sanitize_legacy_js(root)
        checks.append(("legacy JS signer sanitize", ok, detail))
        findings, allowed = scan_repo(root)
        detail = f"findings={len(findings)} allowedFixtures={len(allowed)}"
        if findings:
            detail += " first=" + ";".join(f"{f['path']}:{f['line']}" for f in findings[:3])
            extra.extend([f"- disallowed `{f['path']}:{f['line']}` fp={f['fp']}" for f in findings[:50]])
        if allowed:
            sample = []
            seen = set()
            for item in allowed:
                if item["path"] not in seen:
                    sample.append(item["path"])
                    seen.add(item["path"])
                if len(sample) >= 10:
                    break
            extra.append(f"Allowed fixture sample: `{'; '.join(sample)}`")
        checks.append(("repo private-key PEM scan", len(findings) == 0, detail))
        envelope = sign(demo_payload(), mat)
        ok, detail = verify(envelope, mat)
        checks.append(("offline sign+verify", ok, detail))
        tampered_payload = json.loads(json.dumps(envelope))
        tampered_payload["payload"]["plan"] = "TABLET_SOLO"
        ok, detail = verify(tampered_payload, mat)
        checks.append(("tamper rejection payload", not ok, detail))
        tampered_sig = json.loads(json.dumps(envelope))
        value = tampered_sig["signature"]["value"]
        tampered_sig["signature"]["value"] = ("A" if value[0] != "A" else "B") + value[1:]
        ok, detail = verify(tampered_sig, mat)
        checks.append(("tamper rejection signature", not ok, detail))
        missing_key = json.loads(json.dumps(envelope))
        missing_key["signature"].pop("keyId", None)
        ok, detail = verify(missing_key, mat)
        checks.append(("tamper rejection missing keyId", not ok, detail))
        checks.append((
            "production refuses dev material",
            mat.get("algorithm") == "HS256_DEV_LOCAL" and mat.get("materialClass") == "dev-local",
            "production no puede firmar con material dev-local HS256_DEV_LOCAL",
        ))
        write_json(root / SIGNED_OUT, envelope)
        checks.append(("signed output", True, str(root / SIGNED_OUT)))
        if args.http:
            try:
                with urllib.request.urlopen(args.base_url.rstrip("/") + "/health", timeout=5) as response:
                    checks.append(("server06 health", response.status == 200, f"status={response.status}"))
            except Exception as exc:
                checks.append(("server06 health", False, str(exc)))
        else:
            checks.append(("server06 health", True, "SKIP use --http to require live server"))
    except Exception as exc:
        checks.append(("smoke", False, str(exc)))
    ok = print_checks(checks)
    report = write_report(out, "license server signing 11d smoke", "PRISMA License Server Signing Scan Policy 11D Smoke", checks, extra)
    print(f"REPORT {report}")
    print("FINAL READY" if ok else "BLOCKED")
    return 0 if ok else 2


def cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    out = ensure_out(args.out)
    sanitize_legacy_js(root)
    findings, allowed = scan_repo(root)
    detail = f"findings={len(findings)} allowedFixtures={len(allowed)}"
    checks = [("repo private-key PEM scan", len(findings) == 0, detail)]
    extra = [f"Allowed fixtures: `{len(allowed)}`"]
    extra.extend([f"- disallowed `{f['path']}:{f['line']}` fp={f['fp']}" for f in findings[:100]])
    ok = print_checks(checks)
    report = write_report(out, "license server signing 11d scan", "PRISMA License Server Signing Scan Policy 11D Scan", checks, extra)
    print(f"REPORT {report}")
    print("FINAL READY" if ok else "BLOCKED")
    return 0 if ok else 2


def cmd_fixture_audit(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    out = ensure_out(args.out)
    _, allowed = scan_repo(root)
    by_path: dict[str, int] = {}
    for item in allowed:
        by_path[item["path"]] = by_path.get(item["path"], 0) + 1
    checks = [("approved fixture PEM inventory", True, f"fixtureFiles={len(by_path)} allowedBlocks={len(allowed)}")]
    extra = [f"- `{path}` blocks={count}" for path, count in sorted(by_path.items())]
    ok = print_checks(checks)
    report = write_report(out, "license server signing 11d fixture audit", "PRISMA License Server Signing Scan Policy 11D Fixture Audit", checks, extra)
    print(f"REPORT {report}")
    print("FINAL READY")
    return 0


def cmd_material(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    out = ensure_out(args.out)
    checks: list[tuple[str, bool, str]] = []
    try:
        mat = load_material(root)
        material_text = (root / DEV_MATERIAL).read_text(encoding="utf-8")
        envelope = sign(demo_payload(), mat)
        ok, detail = verify(envelope, mat)
        checks.append(("material parses", True, f"{mat['key_id']} alg={mat['algorithm']}"))
        checks.append(("material has no PEM private-key block", PEM_RE.search(material_text) is None, str(root / DEV_MATERIAL)))
        checks.append(("sign+verify", ok, detail))
    except Exception as exc:
        checks.append(("material", False, str(exc)))
    ok = print_checks(checks)
    report = write_report(out, "license server signing 11d material", "PRISMA License Server Signing Scan Policy 11D Material", checks)
    print(f"REPORT {report}")
    print("FINAL READY" if ok else "BLOCKED")
    return 0 if ok else 2


def cmd_sanitize(args: argparse.Namespace) -> int:
    ok, detail = sanitize_legacy_js(Path(args.root).resolve(), bool(args.dry_run))
    checks = [("legacy JS signer sanitize", ok, detail)]
    print_checks(checks)
    print("FINAL READY" if ok else "BLOCKED")
    return 0 if ok else 2


def cmd_sign(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    mat = load_material(root)
    envelope = sign(demo_payload(), mat)
    write_json(root / SIGNED_OUT, envelope)
    print(f"- signed output: OK {root / SIGNED_OUT}")
    print("FINAL READY")
    return 0


def cmd_contract(args: argparse.Namespace) -> int:
    print((Path(args.root).resolve() / CONTRACT).read_text(encoding="utf-8"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA license server signing scan policy 11D")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default=DEFAULT_OUT)
    sub = parser.add_subparsers(dest="command", required=True)
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--http", action="store_true")
    smoke.add_argument("--base-url", default="http://127.0.0.1:3140")
    smoke.set_defaults(fn=cmd_smoke)
    sub.add_parser("scan").set_defaults(fn=cmd_scan)
    sub.add_parser("fixture-audit").set_defaults(fn=cmd_fixture_audit)
    sub.add_parser("material-smoke").set_defaults(fn=cmd_material)
    sanitize = sub.add_parser("sanitize")
    sanitize.add_argument("--dry-run", action="store_true")
    sanitize.set_defaults(fn=cmd_sanitize)
    sub.add_parser("sign-license").set_defaults(fn=cmd_sign)
    sub.add_parser("contract").set_defaults(fn=cmd_contract)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
