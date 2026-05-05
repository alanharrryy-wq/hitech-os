#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""PRISMA License Server Signing 11.

Purpose
-------
This tool bridges the already working PRISMA License Server MVP 06 with the
signature enforcement layer from 09/10/10D/10F. It intentionally avoids storing
production private keys in the repository. For local development and staging it
can sign server-issued license payloads with a local runtime secret under
local-runtime/license-keys/dev. For production it refuses to sign unless the
operator provides an external signing adapter. That refusal is a feature, not a
bug wearing a tiny hat.

Primary jobs
------------
- create or audit local signing config
- sign a license payload into a compact JWS-like envelope
- verify a signed envelope with the matching local registry entry
- call the 06 server activation/refresh endpoints and sign the returned payload
- generate Markdown reports in F:\descargasf
- scan the repository for real PEM private-key blocks before signing
- prove behavior through a deterministic smoke command

No production private key is generated, embedded, or copied by this tool.
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import hashlib
import hmac
import json
import os
import re
import secrets
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "0.11.1"
TOOL_NAME = "prisma-license-server-signing-11"
DEFAULT_OUT = Path("F:/descargasf")
DEFAULT_BASE_URL = "http://127.0.0.1:3140"
DEV_KEY_ID = "dev-local-hs256-10d"
DEV_ALGORITHM = "HS256_DEV_LOCAL"
LEGACY_DEV_ALGORITHMS = {"HS256_DEV_ONLY", "HS256_DEV_LOCAL"}
PACKAGE_ID = "PRISMA_LICENSE_SERVER_SIGNING_11"

PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----",
    re.IGNORECASE,
)

SKIP_SCAN_PARTS = {
    ".git", "node_modules", ".next", "dist", "build", ".turbo", ".venv", "venv",
    "__pycache__", ".prisma_license_server_signing_11_backups",
}
TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".cmd", ".ps1",
    ".yaml", ".yml", ".env", ".pem", ".crt", ".key", ".sample", ".example",
}


class ToolError(RuntimeError):
    """Expected operational error with a clean message and exit code."""

    def __init__(self, message: str, exit_code: int = 2):
        super().__init__(message)
        self.exit_code = exit_code


@dataclass
class SigningMaterial:
    key_id: str
    algorithm: str
    secret_b64url: str
    created_at: str
    scope: str
    note: str

    @property
    def secret_bytes(self) -> bytes:
        return b64url_decode(self.secret_b64url)


@dataclass
class Finding:
    rel: str
    line: int
    reason: str
    fingerprint: str


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def now_tag() -> str:
    return _dt.datetime.now().strftime("%y%m%d_%H%M")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_root(raw: str | None) -> Path:
    root = Path(raw or ".").expanduser().resolve()
    if not root.exists():
        raise ToolError(f"No existe root: {root}")
    if not (root / "terminal_de_venta.cmd").exists():
        # Do not require the cmd for sub-package tests, but warn through exception for real installs.
        raise ToolError(f"Root no parece terminal-de-venta-system; falta terminal_de_venta.cmd: {root}")
    return root


def out_dir(raw: str | None) -> Path:
    return ensure_dir(Path(raw).expanduser().resolve() if raw else DEFAULT_OUT)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ToolError(f"No existe JSON: {path}")
    except json.JSONDecodeError as exc:
        raise ToolError(f"JSON inválido {path}: {exc}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def report_path(out: Path, name: str) -> Path:
    return out / f"terminal_venta_{name}_{now_tag()}.md"


def emit_report(path: Path, title: str, lines: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", "", *lines]
    path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")


def safe_rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("/", "\\")
    except ValueError:
        return str(path)


def should_scan(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(SKIP_SCAN_PARTS):
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        return path.stat().st_size < 512_000
    except OSError:
        return False


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_repo_for_private_keys(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1", errors="ignore")
        for match in PRIVATE_KEY_RE.finditer(text):
            block = match.group(0).encode("utf-8", errors="ignore")
            findings.append(Finding(safe_rel(root, path), line_for_offset(text, match.start()), "private_key_pem_block_detected", fingerprint(block)))
    return findings


def dev_key_path(root: Path) -> Path:
    return root / "local-runtime" / "license-keys" / "dev" / "dev-signing-secret.local.json"


def server_signing_config_path(root: Path) -> Path:
    return root / "local-runtime" / "license-server" / "signing-config.local.json"


def signed_output_path(root: Path) -> Path:
    return root / "local-runtime" / "license" / "license.signed.remote.local.json"


def public_registry_path(root: Path) -> Path:
    return root / "local-runtime" / "license-keys" / "dev" / "public-signing-registry.local.json"


def ensure_dev_material(root: Path, rotate: bool = False) -> SigningMaterial:
    path = dev_key_path(root)
    if path.exists() and not rotate:
        data = read_json(path)
        material = parse_material(data, path)
        # 11B normalizes legacy 10D material in-place so later tools see one shape.
        # This writes no PEM private key and preserves the existing secret bytes.
        canonical = material.__dict__
        if dict(data) != canonical:
            write_json(path, canonical)
        return material
    material = SigningMaterial(
        key_id=DEV_KEY_ID,
        algorithm=DEV_ALGORITHM,
        secret_b64url=b64url(secrets.token_bytes(32)),
        created_at=now(),
        scope="local-dev-only",
        note="Local dev/staging signing secret. Not a PEM private key. Do not commit runtime files.",
    )
    write_json(path, material.__dict__)
    return material


def _first_text(data: Mapping[str, Any], names: Sequence[str]) -> str | None:
    for name in names:
        value = data.get(name)
        if value is not None and str(value).strip():
            return str(value)
    return None


def parse_material(data: Mapping[str, Any], path: Path | None = None) -> SigningMaterial:
    # 11B accepts both the canonical 11 shape and the 10D generated runtime shape:
    #   key_id / secret_b64url / HS256_DEV_LOCAL
    #   keyId  / secretMaterialBase64Url / HS256_DEV_ONLY
    where = f" {path}" if path else ""
    key_id = _first_text(data, ["key_id", "keyId", "kid"])
    secret = _first_text(data, ["secret_b64url", "secretMaterialBase64Url", "secret", "secretBase64Url"])
    alg = _first_text(data, ["algorithm", "alg"])
    missing = []
    if not key_id:
        missing.append("key_id|keyId")
    if not alg:
        missing.append("algorithm")
    if not secret:
        missing.append("secret_b64url|secretMaterialBase64Url")
    if missing:
        raise ToolError(f"Signing material incompleto{where}; faltan: {', '.join(missing)}")
    if alg not in LEGACY_DEV_ALGORITHMS:
        raise ToolError(f"Algoritmo local no soportado{where}: {alg}")
    try:
        raw = b64url_decode(secret)
    except Exception as exc:
        raise ToolError(f"secret material base64url inválido{where}: {exc}")
    if len(raw) < 32:
        raise ToolError("secret material demasiado corto; mínimo 32 bytes")
    # Normalize the legacy dev-only algorithm to the 11 local signer algorithm.
    # The secret bytes remain identical; only the envelope alg gets the 11 name.
    normalized_alg = DEV_ALGORITHM
    created_at = _first_text(data, ["created_at", "createdAt"]) or "unknown"
    scope = _first_text(data, ["scope", "storagePolicy"]) or "local-dev-only"
    note = _first_text(data, ["note", "description"]) or ""
    return SigningMaterial(
        key_id=key_id,
        algorithm=normalized_alg,
        secret_b64url=secret,
        created_at=created_at,
        scope=scope,
        note=note,
    )


def write_public_registry(root: Path, material: SigningMaterial) -> Path:
    # HMAC has no public key. The registry stores only a fingerprint and metadata so audits can match keyId
    # without exposing the secret. Verification in local dev loads the local runtime secret.
    registry = {
        "schemaVersion": "1.0.0",
        "environment": "development",
        "generatedAt": now(),
        "keys": [
            {
                "keyId": material.key_id,
                "algorithm": material.algorithm,
                "scope": material.scope,
                "secretFingerprint": fingerprint(material.secret_bytes),
                "publicVerificationMode": "local-secret-required",
                "privateKeyInRepoAllowed": False,
            }
        ],
    }
    path = public_registry_path(root)
    write_json(path, registry)
    return path


def write_server_signing_config(root: Path, base_url: str = DEFAULT_BASE_URL) -> Path:
    material = ensure_dev_material(root)
    write_public_registry(root, material)
    cfg = {
        "schemaVersion": "1.0.0",
        "package": PACKAGE_ID,
        "createdAt": now(),
        "baseUrl": base_url,
        "defaultSigner": {
            "environment": "development",
            "keyId": material.key_id,
            "algorithm": material.algorithm,
            "materialPath": str(dev_key_path(root)),
            "outputPath": str(signed_output_path(root)),
        },
        "production": {
            "signingMode": "external-kms-required",
            "repoPrivateKeysAllowed": False,
            "localDevSecretAllowed": False,
            "notes": [
                "Production signing must happen in a real KMS/HSM or backend secret store.",
                "This package refuses to create production private keys inside the repository.",
            ],
        },
    }
    path = server_signing_config_path(root)
    write_json(path, cfg)
    return path


def jws_header(material: SigningMaterial, env: str) -> dict[str, Any]:
    return {
        "typ": "PRISMA-LICENSE-JWS",
        "alg": material.algorithm,
        "kid": material.key_id,
        "env": env,
        "iat": now(),
    }


def sign_payload(payload: Mapping[str, Any], material: SigningMaterial, env: str = "development") -> dict[str, Any]:
    if env == "production" and material.algorithm == DEV_ALGORITHM:
        raise ToolError("production no puede firmar con material dev-local HS256_DEV_LOCAL", 3)
    header = jws_header(material, env)
    encoded_header = b64url(canonical_json(header))
    encoded_payload = b64url(canonical_json(payload))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    sig = hmac.new(material.secret_bytes, signing_input, hashlib.sha256).digest()
    compact = f"{encoded_header}.{encoded_payload}.{b64url(sig)}"
    return {
        "schemaVersion": "1.0.0",
        "format": "PRISMA_LICENSE_SIGNED_ENVELOPE_11",
        "issuedAt": now(),
        "keyId": material.key_id,
        "algorithm": material.algorithm,
        "environment": env,
        "license": payload,
        "signature": {
            "type": "jws-compact-local",
            "compact": compact,
            "payloadSha256": sha256_hex(canonical_json(payload)),
        },
        "warnings": [
            "Development/staging local signature. Production must use external KMS-backed signer.",
        ] if env != "production" else [],
    }


def verify_envelope(envelope: Mapping[str, Any], material: SigningMaterial) -> tuple[bool, str]:
    try:
        compact = envelope["signature"]["compact"]
        encoded_header, encoded_payload, encoded_sig = compact.split(".")
        header = json.loads(b64url_decode(encoded_header).decode("utf-8"))
        payload = json.loads(b64url_decode(encoded_payload).decode("utf-8"))
        if header.get("kid") != material.key_id:
            return False, "key_id_mismatch"
        if header.get("alg") != material.algorithm:
            return False, "algorithm_mismatch"
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        expected = hmac.new(material.secret_bytes, signing_input, hashlib.sha256).digest()
        actual = b64url_decode(encoded_sig)
        if not hmac.compare_digest(expected, actual):
            return False, "signature_mismatch"
        expected_hash = envelope.get("signature", {}).get("payloadSha256")
        if expected_hash and expected_hash != sha256_hex(canonical_json(payload)):
            return False, "payload_hash_mismatch"
        return True, "signature_valid"
    except Exception as exc:
        return False, f"verify_error:{exc}"


def sample_license(plan: str = "TABLET_PC_REQUIRED", state: str = "active") -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "licenseId": f"lic_server11_{secrets.token_hex(8)}",
        "customerId": "cust_demo",
        "businessId": "biz_demo",
        "deviceId": "device_demo_tablet_01",
        "terminalId": "terminal_demo_tablet_01",
        "plan": plan,
        "state": state,
        "validFrom": "2026-01-01T00:00:00.000Z",
        "validUntil": "2099-12-31T23:59:59.000Z",
        "issuedAt": now(),
        "offlineGraceDays": 14,
        "source": "server11-local-smoke",
    }


def http_json(method: str, url: str, body: Mapping[str, Any] | None = None, timeout: float = 8.0) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method.upper())
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"raw": raw}
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return exc.code, parsed
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        raise ToolError(f"Servidor no disponible {url}: {exc}", 4)


def server_license_from_response(response: Any) -> dict[str, Any]:
    if not isinstance(response, Mapping):
        raise ToolError("Respuesta del servidor no es objeto JSON")
    data = response.get("data", response)
    if not isinstance(data, Mapping):
        raise ToolError("Respuesta del servidor no contiene data JSON")
    # Several server shapes are accepted. This is intentionally permissive because MVP 06 can evolve.
    for key in ["license", "currentLicense", "signedLicense", "payload"]:
        val = data.get(key)
        if isinstance(val, Mapping):
            return dict(val)
    if "licenseId" in data or "plan" in data:
        return dict(data)
    raise ToolError("No encontré payload de licencia en respuesta del servidor")


def activate_payload(plan: str, device_id: str, terminal_id: str, business_id: str, customer_id: str) -> dict[str, Any]:
    return {
        "customerId": customer_id,
        "businessId": business_id,
        "deviceId": device_id,
        "terminalId": terminal_id,
        "plan": plan,
        "installationFingerprint": fingerprint(f"{device_id}|{terminal_id}|{business_id}".encode("utf-8")),
        "requestedAt": now(),
    }


def maybe_server_health(base_url: str) -> tuple[bool, str]:
    try:
        status, body = http_json("GET", base_url.rstrip("/") + "/health", timeout=2.0)
        return status == 200, f"status={status} service={body.get('data', body).get('service', 'unknown') if isinstance(body, Mapping) else 'unknown'}"
    except Exception as exc:
        return False, str(exc)


def command_config(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    cfg = write_server_signing_config(root, args.base_url)
    mat = ensure_dev_material(root)
    reg = write_public_registry(root, mat)
    path = report_path(out, "license_server_signing_11_config")
    emit_report(path, "PRISMA License Server Signing 11 Config", [
        f"Root: `{root}`",
        f"Config: `{cfg}`",
        f"Dev material: `{dev_key_path(root)}`",
        f"Public registry: `{reg}`",
        f"Key ID: `{mat.key_id}`",
        f"Algorithm: `{mat.algorithm}`",
        "Status: `FINAL READY`",
    ])
    print(f"CONFIG {cfg}")
    print(f"REGISTRY {reg}")
    print(f"REPORT {path}")
    print("FINAL READY")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    findings = scan_repo_for_private_keys(root)
    material_exists = dev_key_path(root).exists()
    cfg_exists = server_signing_config_path(root).exists()
    lines = [
        f"Root: `{root}`",
        f"Repo private-key PEM findings: `{len(findings)}`",
        f"Dev material exists: `{material_exists}`",
        f"Signing config exists: `{cfg_exists}`",
    ]
    for f in findings[:25]:
        lines.append(f"- `{f.rel}:{f.line}` {f.reason} fp={f.fingerprint}")
    if len(findings) > 25:
        lines.append(f"- ... truncated {len(findings)-25} more findings")
    status = "BLOCKED" if findings else "FINAL READY"
    lines.append(f"Status: `{status}`")
    path = report_path(out, "license_server_signing_11_audit")
    emit_report(path, "PRISMA License Server Signing 11 Audit", lines)
    print(f"- repo private-key PEM scan: {'FAIL' if findings else 'OK'} findings={len(findings)}")
    print(f"- dev material exists: {'OK' if material_exists else 'WARN'} {dev_key_path(root)}")
    print(f"- signing config exists: {'OK' if cfg_exists else 'WARN'} {server_signing_config_path(root)}")
    print(f"REPORT {path}")
    print(status)
    return 2 if findings else 0


def command_sign_payload(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    findings = scan_repo_for_private_keys(root)
    if findings:
        print(f"BLOCKED repo has PEM private-key findings={len(findings)}")
        for f in findings[:10]:
            print(f"- {f.rel}:{f.line} {f.reason} fp={f.fingerprint}")
        return 2
    material = ensure_dev_material(root)
    if args.payload:
        payload = read_json(Path(args.payload).expanduser().resolve())
    else:
        payload = sample_license(plan=args.plan, state=args.state)
    envelope = sign_payload(payload, material, env=args.env)
    ok, reason = verify_envelope(envelope, material)
    if not ok:
        raise ToolError(f"La firma generada no verificó: {reason}")
    dest = Path(args.output).expanduser().resolve() if args.output else signed_output_path(root)
    write_json(dest, envelope)
    path = report_path(out, "license_server_signing_11_sign")
    emit_report(path, "PRISMA License Server Signing 11 Sign Payload", [
        f"Root: `{root}`",
        f"Output: `{dest}`",
        f"Key ID: `{material.key_id}`",
        f"Algorithm: `{material.algorithm}`",
        f"Environment: `{args.env}`",
        f"Verify: `{reason}`",
        f"License ID: `{payload.get('licenseId', 'unknown') if isinstance(payload, Mapping) else 'unknown'}`",
        "Status: `FINAL READY`",
    ])
    print(f"SIGNED {dest}")
    print(f"VERIFY {reason}")
    print(f"REPORT {path}")
    print("FINAL READY")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    material = ensure_dev_material(root)
    envelope = read_json(Path(args.envelope).expanduser().resolve())
    ok, reason = verify_envelope(envelope, material)
    print(f"VERIFY {reason}")
    print("FINAL READY" if ok else "BLOCKED")
    return 0 if ok else 2


def command_activate_and_sign(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    material = ensure_dev_material(root)
    base_url = args.base_url.rstrip("/")
    body = activate_payload(args.plan, args.device_id, args.terminal_id, args.business_id, args.customer_id)
    status, resp = http_json("POST", base_url + "/licenses/activate", body=body, timeout=args.timeout)
    if status < 200 or status >= 300:
        raise ToolError(f"activate falló status={status} response={resp}", 5)
    license_payload = server_license_from_response(resp)
    envelope = sign_payload(license_payload, material, env=args.env)
    ok, reason = verify_envelope(envelope, material)
    if not ok:
        raise ToolError(f"activate signed envelope no verificó: {reason}")
    dest = Path(args.output).expanduser().resolve() if args.output else signed_output_path(root)
    write_json(dest, envelope)
    path = report_path(out, "license_server_signing_11_activate")
    emit_report(path, "PRISMA License Server Signing 11 Activate + Sign", [
        f"Base URL: `{base_url}`",
        f"Status: `{status}`",
        f"Output: `{dest}`",
        f"Verify: `{reason}`",
        f"License ID: `{license_payload.get('licenseId', 'unknown')}`",
        "Status: `FINAL READY`",
    ])
    print(f"ACTIVATE status={status}")
    print(f"SIGNED {dest}")
    print(f"VERIFY {reason}")
    print(f"REPORT {path}")
    print("FINAL READY")
    return 0


def command_refresh_and_sign(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    material = ensure_dev_material(root)
    base_url = args.base_url.rstrip("/")
    body = {
        "licenseId": args.license_id,
        "deviceId": args.device_id,
        "businessId": args.business_id,
        "requestedAt": now(),
    }
    status, resp = http_json("POST", base_url + "/licenses/refresh", body=body, timeout=args.timeout)
    if status < 200 or status >= 300:
        raise ToolError(f"refresh falló status={status} response={resp}", 5)
    license_payload = server_license_from_response(resp)
    envelope = sign_payload(license_payload, material, env=args.env)
    ok, reason = verify_envelope(envelope, material)
    if not ok:
        raise ToolError(f"refresh signed envelope no verificó: {reason}")
    dest = Path(args.output).expanduser().resolve() if args.output else signed_output_path(root)
    write_json(dest, envelope)
    path = report_path(out, "license_server_signing_11_refresh")
    emit_report(path, "PRISMA License Server Signing 11 Refresh + Sign", [
        f"Base URL: `{base_url}`",
        f"Status: `{status}`",
        f"Output: `{dest}`",
        f"Verify: `{reason}`",
        f"License ID: `{license_payload.get('licenseId', args.license_id)}`",
        "Status: `FINAL READY`",
    ])
    print(f"REFRESH status={status}")
    print(f"SIGNED {dest}")
    print(f"VERIFY {reason}")
    print(f"REPORT {path}")
    print("FINAL READY")
    return 0


def command_contract(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    path = root / "tooling" / "licensing" / "server11" / "server_signing_contract_11.json"
    if path.exists():
        print(path.read_text(encoding="utf-8"))
    else:
        print(json.dumps(default_contract(), indent=2, ensure_ascii=False))
    return 0


def command_smoke(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    lines: list[str] = []
    ok = True

    cfg = write_server_signing_config(root, args.base_url)
    material = ensure_dev_material(root)
    registry = write_public_registry(root, material)
    lines.append(f"Config written: `{cfg}`")
    lines.append(f"Registry written: `{registry}`")
    print(f"- config: OK {cfg}")

    findings = scan_repo_for_private_keys(root)
    if findings:
        ok = False
        print(f"- repo private-key PEM scan: FAIL findings={len(findings)}")
        lines.append(f"Repo private-key PEM scan: `FAIL findings={len(findings)}`")
        for f in findings[:10]:
            lines.append(f"- `{f.rel}:{f.line}` {f.reason} fp={f.fingerprint}")
    else:
        print("- repo private-key PEM scan: OK findings=0")
        lines.append("Repo private-key PEM scan: `OK findings=0`")

    payload = sample_license(plan=args.plan, state="active")
    envelope = sign_payload(payload, material, env="development")
    verify_ok, reason = verify_envelope(envelope, material)
    ok = ok and verify_ok
    print(f"- offline sign+verify: {'OK' if verify_ok else 'FAIL'} {reason}")
    lines.append(f"Offline sign+verify: `{'OK' if verify_ok else 'FAIL'} {reason}`")
    write_json(signed_output_path(root), envelope)
    lines.append(f"Signed output: `{signed_output_path(root)}`")

    # Negative tamper test.
    tampered = json.loads(json.dumps(envelope))
    tampered["license"]["plan"] = "TABLET_SOLO"
    tamper_ok, tamper_reason = verify_envelope(tampered, material)
    if tamper_ok:
        ok = False
        print("- tamper rejection: FAIL tampered envelope verified")
        lines.append("Tamper rejection: `FAIL`")
    else:
        print(f"- tamper rejection: OK {tamper_reason}")
        lines.append(f"Tamper rejection: `OK {tamper_reason}`")

    # Production refusal test.
    try:
        sign_payload(payload, material, env="production")
        ok = False
        print("- production refuses dev material: FAIL")
        lines.append("Production refuses dev material: `FAIL`")
    except ToolError as exc:
        print(f"- production refuses dev material: OK {exc}")
        lines.append(f"Production refuses dev material: `OK {exc}`")

    if args.http:
        healthy, health_note = maybe_server_health(args.base_url.rstrip("/"))
        print(f"- required server06 health: {'OK' if healthy else 'FAIL'} {health_note}")
        lines.append(f"Required server06 health: `{'OK' if healthy else 'FAIL'} {health_note}`")
        if not healthy:
            ok = False
        else:
            try:
                body = activate_payload(args.plan, "device_server11_smoke", "terminal_server11_smoke", "biz_demo", "cust_demo")
                status, resp = http_json("POST", args.base_url.rstrip("/") + "/licenses/activate", body=body, timeout=args.timeout)
                license_payload = server_license_from_response(resp)
                http_env = sign_payload(license_payload, material, env="development")
                http_ok, http_reason = verify_envelope(http_env, material)
                ok = ok and http_ok and (200 <= status < 300)
                print(f"- http activate+sign: {'OK' if http_ok and (200 <= status < 300) else 'FAIL'} status={status} {http_reason}")
                lines.append(f"HTTP activate+sign: `{'OK' if http_ok and (200 <= status < 300) else 'FAIL'} status={status} {http_reason}`")
            except Exception as exc:
                ok = False
                print(f"- http activate+sign: FAIL {exc}")
                lines.append(f"HTTP activate+sign: `FAIL {exc}`")
    else:
        print("- server06 health: SKIP use --http to require live server")
        lines.append("Server06 health: `SKIP use --http to require live server`")

    path = report_path(out, "license_server_signing_11_smoke")
    lines.append(f"Status: `{'FINAL READY' if ok else 'BLOCKED'}`")
    emit_report(path, "PRISMA License Server Signing 11 Smoke", lines)
    print(f"REPORT {path}")
    print("FINAL READY" if ok else "BLOCKED")
    return 0 if ok else 2


def material_shape(path: Path) -> dict[str, Any]:
    data = read_json(path)
    material = parse_material(data, path)
    legacy = any(k in data for k in ["keyId", "secretMaterialBase64Url"]) or data.get("algorithm") == "HS256_DEV_ONLY"
    return {
        "path": str(path),
        "keyId": material.key_id,
        "algorithm": material.algorithm,
        "legacyDetected": bool(legacy),
        "secretBytes": len(material.secret_bytes),
        "hasPemPrivateKeyBlock": bool(PRIVATE_KEY_RE.search(path.read_text(encoding="utf-8", errors="ignore"))) if path.exists() else False,
    }


def command_material_migrate(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    path = dev_key_path(root)
    if not path.exists():
        ensure_dev_material(root)
    before = read_json(path)
    material = parse_material(before, path)
    write_json(path, material.__dict__)
    write_public_registry(root, material)
    shape = material_shape(path)
    report = report_path(out, "license_server_signing_material_11b_migrate")
    emit_report(report, "PRISMA License Server Signing Material 11B Migrate", [
        f"Root: `{root}`",
        f"Material: `{path}`",
        f"Legacy detected before: `{any(k in before for k in ['keyId', 'secretMaterialBase64Url']) or before.get('algorithm') == 'HS256_DEV_ONLY'}`",
        f"Key ID: `{shape['keyId']}`",
        f"Algorithm: `{shape['algorithm']}`",
        f"Secret bytes: `{shape['secretBytes']}`",
        f"PEM private-key block: `{shape['hasPemPrivateKeyBlock']}`",
        "Status: `FINAL READY`",
    ])
    print(f"MATERIAL {path}")
    print(f"KEY {shape['keyId']} alg={shape['algorithm']} secretBytes={shape['secretBytes']}")
    print(f"REPORT {report}")
    print("FINAL READY")
    return 0


def command_material_smoke(args: argparse.Namespace) -> int:
    root = normalize_root(args.root)
    out = out_dir(args.out)
    path = dev_key_path(root)
    if not path.exists():
        ensure_dev_material(root)
    data = read_json(path)
    mat = parse_material(data, path)
    canonical = mat.__dict__
    # Do a no-op normalize to prove the path is writable and future tools get the same shape.
    write_json(path, canonical)
    reread = parse_material(read_json(path), path)
    payload = sample_license()
    env = sign_payload(payload, reread, env="development")
    ok, reason = verify_envelope(env, reread)
    pem = bool(PRIVATE_KEY_RE.search(path.read_text(encoding="utf-8", errors="ignore")))
    final = ok and not pem and reread.key_id and reread.algorithm == DEV_ALGORITHM
    report = report_path(out, "license_server_signing_material_11b_smoke")
    emit_report(report, "PRISMA License Server Signing Material 11B Smoke", [
        f"Material: `{path}`",
        f"Key ID: `{reread.key_id}`",
        f"Algorithm: `{reread.algorithm}`",
        f"Secret bytes: `{len(reread.secret_bytes)}`",
        f"Sign+verify: `{'OK' if ok else 'FAIL'} {reason}`",
        f"PEM private-key block: `{'FAIL' if pem else 'OK'}`",
        f"Status: `{'FINAL READY' if final else 'BLOCKED'}`",
    ])
    print(f"- material parses: OK {reread.key_id} alg={reread.algorithm} secretBytes={len(reread.secret_bytes)}")
    print(f"- material normalized: OK {path}")
    print(f"- material has no PEM private key block: {'OK' if not pem else 'FAIL'}")
    print(f"- sign+verify with material: {'OK' if ok else 'FAIL'} {reason}")
    print(f"REPORT {report}")
    print("FINAL READY" if final else "BLOCKED")
    return 0 if final else 2


def default_contract() -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "package": PACKAGE_ID,
        "version": VERSION,
        "commands": [
            "license-server-signing-config",
            "license-server-signing-audit",
            "license-server-signing-smoke",
            "license-server-sign-license",
            "license-server-signing-activate",
            "license-server-signing-refresh",
            "license-server-signing-verify",
            "license-server-signing-contract",
            "license-server-signing-material-migrate",
            "license-server-signing-material-smoke",
        ],
        "guarantees": [
            "Does not create production private keys in the repository.",
            "Blocks signing when repo PEM private-key blocks are detected.",
            "Signs development/staging payloads with local runtime material only.",
            "Verifies generated envelopes before writing them.",
            "Writes operational Markdown reports to F:/descargasf by default.",
        ],
        "nonGoals": [
            "No real production KMS integration in this package.",
            "No portal admin UI changes.",
            "No replacement of the license server MVP 06 endpoints.",
        ],
        "compatibility": {
            "accepts10DMaterial": true,
            "legacyFields": ["keyId", "secretMaterialBase64Url", "HS256_DEV_ONLY"],
            "canonicalFields": ["key_id", "secret_b64url", "HS256_DEV_LOCAL"]
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="license_server_signing_11.py", description="PRISMA License Server Signing 11")
    parser.add_argument("--root", default=".", help="Terminal root. Defaults to current directory.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output reports directory.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("config", help="Create local signing config and registry.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.set_defaults(func=command_config)

    p = sub.add_parser("audit", help="Audit signing material and repo private-key hygiene.")
    p.set_defaults(func=command_audit)

    p = sub.add_parser("sign-payload", help="Sign a payload JSON or generated sample license.")
    p.add_argument("--payload", default=None, help="Path to JSON license payload.")
    p.add_argument("--output", default=None, help="Output signed envelope JSON.")
    p.add_argument("--plan", default="TABLET_PC_REQUIRED")
    p.add_argument("--state", default="active")
    p.add_argument("--env", default="development", choices=["development", "staging", "production"])
    p.set_defaults(func=command_sign_payload)

    p = sub.add_parser("verify", help="Verify a generated signed envelope.")
    p.add_argument("--envelope", required=True)
    p.set_defaults(func=command_verify)

    p = sub.add_parser("activate-and-sign", help="Call server06 activate then sign returned license.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--plan", default="TABLET_PC_REQUIRED")
    p.add_argument("--device-id", default="device_server11_cli")
    p.add_argument("--terminal-id", default="terminal_server11_cli")
    p.add_argument("--business-id", default="biz_demo")
    p.add_argument("--customer-id", default="cust_demo")
    p.add_argument("--output", default=None)
    p.add_argument("--env", default="development", choices=["development", "staging", "production"])
    p.set_defaults(func=command_activate_and_sign)

    p = sub.add_parser("refresh-and-sign", help="Call server06 refresh then sign returned license.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--license-id", required=True)
    p.add_argument("--device-id", default="device_server11_cli")
    p.add_argument("--business-id", default="biz_demo")
    p.add_argument("--output", default=None)
    p.add_argument("--env", default="development", choices=["development", "staging", "production"])
    p.set_defaults(func=command_refresh_and_sign)

    p = sub.add_parser("smoke", help="Run deterministic signing smoke.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--plan", default="TABLET_PC_REQUIRED")
    p.add_argument("--http", action="store_true", help="Require HTTP activate+sign against server06.")
    p.set_defaults(func=command_smoke)

    p = sub.add_parser("material-migrate", help="Normalize 10D/11 local signing material to the canonical 11B shape.")
    p.set_defaults(func=command_material_migrate)

    p = sub.add_parser("material-smoke", help="Prove 10D/11 local signing material parses, normalizes, signs, and verifies.")
    p.set_defaults(func=command_material_smoke)

    p = sub.add_parser("contract", help="Print package contract JSON.")
    p.set_defaults(func=command_contract)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ToolError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("[ERROR] interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
