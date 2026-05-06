#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

PACKAGE = "PRISMA_LICENSE_PRODUCTION_SIGNATURE_10"
VERSION = "1.0.0"
DIGESTINFO_SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def now_stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")


def repo_root_from_arg(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def downloads_dir(root: Path) -> Path:
    preferred = Path("F:/descargasf")
    if preferred.exists() or preferred.drive:
        try:
            preferred.mkdir(parents=True, exist_ok=True)
            return preferred
        except Exception:
            pass
    fallback = root / "local-runtime" / "reports"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_report(root: Path, name: str, lines: list[str]) -> Path:
    out = downloads_dir(root) / f"terminal_venta_license_signature_10_{name}_{now_stamp()}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def base_dir(root: Path) -> Path:
    return root / "tooling" / "licensing" / "signature10"


def b64u_decode(value: str) -> bytes:
    value = value.strip()
    pad = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + pad).encode("ascii"))


def b64u_to_int(value: str) -> int:
    return int.from_bytes(b64u_decode(value), "big")


def canonical_payload(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def find_key(registry: dict[str, Any], key_id: str) -> dict[str, Any] | None:
    for key in registry.get("keys", []):
        if key.get("keyId") == key_id:
            return key
    return None


def verify_rs256_pkcs1v15(message: bytes, signature: bytes, jwk: dict[str, Any]) -> tuple[bool, str]:
    try:
        n = b64u_to_int(jwk["n"])
        e = b64u_to_int(jwk["e"])
    except Exception as exc:
        return False, f"invalid_jwk: {exc}"

    k = (n.bit_length() + 7) // 8
    if len(signature) != k:
        return False, f"bad_signature_length expected={k} actual={len(signature)}"

    encoded = pow(int.from_bytes(signature, "big"), e, n).to_bytes(k, "big")
    digest = hashlib.sha256(message).digest()
    expected_suffix = DIGESTINFO_SHA256_PREFIX + digest

    if not encoded.startswith(b"\x00\x01"):
        return False, "bad_pkcs1_prefix"

    try:
        sep = encoded.index(b"\x00", 2)
    except ValueError:
        return False, "bad_pkcs1_separator"

    padding = encoded[2:sep]
    if len(padding) < 8 or any(byte != 0xFF for byte in padding):
        return False, "bad_pkcs1_padding"

    if encoded[sep + 1 :] != expected_suffix:
        return False, "digest_mismatch"

    return True, "signature_valid"


def env_policy(policy: dict[str, Any], env: str) -> dict[str, Any]:
    environments = policy.get("environments", {})
    if env not in environments:
        raise ValueError(f"Unknown PRISMA_LICENSE_ENV: {env}")
    return environments[env]


def verify_envelope(envelope: dict[str, Any], registry: dict[str, Any], policy: dict[str, Any], env: str) -> tuple[bool, list[str]]:
    messages: list[str] = []
    p = env_policy(policy, env)

    if "signature" not in envelope:
        if p.get("allowUnsigned"):
            messages.append("unsigned_allowed_for_environment")
            return True, messages
        messages.append("unsigned_rejected")
        return False, messages

    sig = envelope.get("signature") or {}
    alg = sig.get("alg")
    key_id = sig.get("keyId")
    value = sig.get("value")

    if not alg or not key_id or not value:
        messages.append("missing_signature_fields")
        return False, messages

    if alg not in p.get("allowedAlgorithms", []):
        messages.append(f"algorithm_not_allowed env={env} alg={alg}")
        return False, messages

    key = find_key(registry, key_id)
    if not key:
        messages.append(f"unknown_keyId {key_id}")
        return False, messages

    if key.get("status") not in policy.get("keyStatusesAllowedForVerification", ["active"]):
        messages.append(f"key_status_not_allowed status={key.get('status')}")
        return False, messages

    if key.get("alg") != alg:
        messages.append(f"algorithm_key_mismatch keyAlg={key.get('alg')} sigAlg={alg}")
        return False, messages

    payload = envelope.get("payload")
    if payload is None:
        messages.append("missing_payload")
        return False, messages

    if alg == "RS256_PROD" or alg == "RS256_STAGING":
        ok, reason = verify_rs256_pkcs1v15(canonical_payload(payload), b64u_decode(value), key.get("jwk", {}))
        messages.append(reason)
        return ok, messages

    if alg == "HS256_DEV_ONLY" and env == "development":
        messages.append("hs256_dev_only_not_verified_by_signature10")
        return True, messages

    messages.append(f"unsupported_algorithm {alg}")
    return False, messages


def command_policy(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    path = base_dir(root) / "signature_policy.json"
    data = read_json(path)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def command_registry(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    path = base_dir(root) / "public_key_registry.fixture.json"
    data = read_json(path)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def command_contract(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    path = base_dir(root) / "license_signature_contract_10.json"
    data = read_json(path)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def command_verify_fixture(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    bd = base_dir(root)
    policy = read_json(bd / "signature_policy.json")
    registry = read_json(bd / "public_key_registry.fixture.json")
    envelope = read_json(bd / "signed_license.fixture.rs256.json")
    env = args.env or "production"
    ok, messages = verify_envelope(envelope, registry, policy, env)
    for m in messages:
        print(m)
    if ok:
        print("FINAL READY")
        return 0
    print("BLOCKED")
    return 2


def command_env_smoke(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    bd = base_dir(root)
    policy = read_json(bd / "signature_policy.json")
    registry = read_json(bd / "public_key_registry.fixture.json")
    signed = read_json(bd / "signed_license.fixture.rs256.json")
    unsigned = {"schemaVersion": "1.0.0", "payload": signed["payload"]}
    hs_dev = {"schemaVersion": "1.0.0", "payload": signed["payload"], "signature": {"alg": "HS256_DEV_ONLY", "keyId": "dev-local", "value": "abc"}}

    cases = [
        ("production_accepts_rs256_fixture", signed, "production", True),
        ("production_rejects_unsigned", unsigned, "production", False),
        ("production_rejects_hs256_dev", hs_dev, "production", False),
        ("development_accepts_unsigned", unsigned, "development", True),
    ]
    failures: list[str] = []
    for name, envlp, env, expected in cases:
        ok, messages = verify_envelope(envlp, registry, policy, env)
        result = "OK" if ok == expected else "FAIL"
        print(f"{name}: {result} expected={expected} actual={ok} details={';'.join(messages)}")
        if ok != expected:
            failures.append(name)
    if failures:
        print("BLOCKED " + ", ".join(failures))
        return 2
    print("FINAL READY")
    return 0


# PRISMA_SIGNATURE_10C_SCAN_PATCH_START
def scan_for_private_key_markers(root: Path) -> list[str]:
    # Scan for real private-key PEM blocks, not policy strings that merely name forbidden markers.
    try:
        scanner_dir = root / "tooling" / "licensing" / "signature10c"
        scanner_path = str(scanner_dir.resolve())
        if scanner_path not in sys.path:
            sys.path.insert(0, scanner_path)
        from license_signature_scanner_10c import scan_root_for_private_key_pems
        findings = scan_root_for_private_key_pems(root)
        return [f"{item.path}:{item.line} {item.label} {item.reason} fp={item.fingerprint}" for item in findings]
    except Exception as exc:
        return [f"scanner10c_runtime_error: {exc}"]
# PRISMA_SIGNATURE_10C_SCAN_PATCH_END


def command_audit(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    env = args.env or os.environ.get("PRISMA_LICENSE_ENV", "development")
    bd = base_dir(root)
    policy = read_json(bd / "signature_policy.json")
    p = env_policy(policy, env)
    findings = scan_for_private_key_markers(root)

    lines = [
        f"# PRISMA License Signature 10 Audit",
        "",
        f"Root: `{root}`",
        f"Environment: `{env}`",
        "",
        "## Policy",
        f"- allowUnsigned: `{p.get('allowUnsigned')}`",
        f"- allowedAlgorithms: `{', '.join(p.get('allowedAlgorithms', []))}`",
        "",
        "## Private key scan",
    ]
    if findings:
        lines += ["BLOCKED: private key markers found:"] + [f"- `{f}`" for f in findings]
    else:
        lines.append("OK: no private key PEM markers found in licensing runtime/tooling scan.")
    report = write_report(root, "audit", lines)
    print(f"REPORT {report}")
    if findings:
        print("BLOCKED")
        return 2
    print("FINAL READY")
    return 0


def command_smoke(args: argparse.Namespace) -> int:
    root = repo_root_from_arg(args.root)
    lines = ["# PRISMA License Signature 10 Smoke", ""]
    exit_code = 0

    bd = base_dir(root)
    required = [
        bd / "signature_policy.json",
        bd / "public_key_registry.fixture.json",
        bd / "signed_license.fixture.rs256.json",
        bd / "license_signature_contract_10.json",
    ]
    for path in required:
        try:
            read_json(path)
            line = f"- json {path.relative_to(root)}: OK"
        except Exception as exc:
            line = f"- json {path.relative_to(root)}: FAIL {exc}"
            exit_code = 2
        print(line)
        lines.append(line)

    policy = read_json(bd / "signature_policy.json")
    registry = read_json(bd / "public_key_registry.fixture.json")
    signed = read_json(bd / "signed_license.fixture.rs256.json")
    ok, messages = verify_envelope(signed, registry, policy, "production")
    line = f"- verify RS256 production fixture: {'OK' if ok else 'FAIL'} details={';'.join(messages)}"
    print(line)
    lines.append(line)
    if not ok:
        exit_code = 2

    unsigned = {"schemaVersion": "1.0.0", "payload": signed["payload"]}
    hs_dev = {"schemaVersion": "1.0.0", "payload": signed["payload"], "signature": {"alg": "HS256_DEV_ONLY", "keyId": "dev-local", "value": "abc"}}
    checks = [
        ("production rejects unsigned", unsigned, "production", False),
        ("production rejects HS256_DEV_ONLY", hs_dev, "production", False),
        ("development accepts unsigned", unsigned, "development", True),
    ]
    for label, envlp, env, expected in checks:
        actual, msgs = verify_envelope(envlp, registry, policy, env)
        passed = actual == expected
        line = f"- {label}: {'OK' if passed else 'FAIL'} actual={actual} expected={expected} details={';'.join(msgs)}"
        print(line)
        lines.append(line)
        if not passed:
            exit_code = 2

    findings = scan_for_private_key_markers(root)
    if findings:
        line = "- private key scan: FAIL " + ", ".join(findings)
        exit_code = 2
    else:
        line = "- private key scan: OK"
    print(line)
    lines.append(line)

    report = write_report(root, "smoke", lines + ["", "FINAL READY" if exit_code == 0 else "BLOCKED"])
    print(f"REPORT {report}")
    if exit_code == 0:
        print("FINAL READY")
    else:
        print("BLOCKED")
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRISMA License Production Signature 10 tooling")
    parser.add_argument("command", choices=["policy", "registry", "contract", "audit", "verify-fixture", "env-smoke", "smoke"])
    parser.add_argument("--root", default=None, help="Terminal de venta root. Defaults to repo root inferred from this script.")
    parser.add_argument("--env", default=None, help="development, staging, or production")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "policy":
        return command_policy(args)
    if args.command == "registry":
        return command_registry(args)
    if args.command == "contract":
        return command_contract(args)
    if args.command == "audit":
        return command_audit(args)
    if args.command == "verify-fixture":
        return command_verify_fixture(args)
    if args.command == "env-smoke":
        return command_env_smoke(args)
    if args.command == "smoke":
        return command_smoke(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
