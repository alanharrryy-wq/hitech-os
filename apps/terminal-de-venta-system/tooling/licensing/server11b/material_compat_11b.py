#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""PRISMA License Server Signing Material Compatibility 11B.

This helper exists because 10D generated local dev material with camelCase fields
and the first 11 signer expected snake_case fields. That mismatch blocked signing
without any security benefit, like a bouncer rejecting you because your name tag
uses Arial instead of Calibri. The tool normalizes local runtime material only.
It never creates or commits PEM private keys.
"""
from __future__ import annotations
import argparse, base64, datetime as dt, hashlib, hmac, json, re, secrets, sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----", re.I)
DEV_KEY_ID = "dev-local-hs256-10d"
DEV_ALGORITHM = "HS256_DEV_LOCAL"
LEGACY_ALGORITHMS = {"HS256_DEV_ONLY", "HS256_DEV_LOCAL"}
DEFAULT_OUT = Path("F:/descargasf")

class ToolError(RuntimeError):
    def __init__(self, msg: str, code: int = 2):
        super().__init__(msg); self.code = code

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")

def now_tag() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def b64decode(text: str) -> bytes:
    return base64.urlsafe_b64decode((text + "=" * (-len(text) % 4)).encode("ascii"))

def canonical(v: Any) -> bytes:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def root_path(raw: str) -> Path:
    p = Path(raw).expanduser().resolve()
    if not (p / "terminal_de_venta.cmd").exists():
        raise ToolError(f"root invalido; falta terminal_de_venta.cmd: {p}")
    return p

def material_path(root: Path) -> Path:
    return root / "local-runtime" / "license-keys" / "dev" / "dev-signing-secret.local.json"

def report(out: Path, name: str, lines: Sequence[str]) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"terminal_venta_{name}_{now_tag()}.md"
    p.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return p

def first(data: Mapping[str, Any], names: Sequence[str]) -> str | None:
    for n in names:
        if n in data and str(data[n]).strip():
            return str(data[n])
    return None

def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ToolError(f"no existe material: {path}")
    except json.JSONDecodeError as e:
        raise ToolError(f"json invalido {path}: {e}")

def parse(data: Mapping[str, Any], path: Path) -> dict[str, Any]:
    key_id = first(data, ["key_id", "keyId", "kid"]) or DEV_KEY_ID
    alg = first(data, ["algorithm", "alg"]) or DEV_ALGORITHM
    secret = first(data, ["secret_b64url", "secretMaterialBase64Url", "secret", "secretBase64Url"])
    if alg not in LEGACY_ALGORITHMS:
        raise ToolError(f"algoritmo local no soportado {path}: {alg}")
    if not secret:
        raise ToolError(f"material incompleto {path}; falta secret_b64url o secretMaterialBase64Url")
    raw = b64decode(secret)
    if len(raw) < 32:
        raise ToolError(f"secret demasiado corto {path}; bytes={len(raw)}")
    return {
        "key_id": key_id,
        "algorithm": DEV_ALGORITHM,
        "secret_b64url": secret,
        "created_at": first(data, ["created_at", "createdAt"]) or now(),
        "scope": first(data, ["scope", "storagePolicy"]) or "local-dev-only",
        "note": first(data, ["note", "description"]) or "Local dev signing material normalized by 11B. Not a PEM private key.",
    }

def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def ensure_material(root: Path) -> dict[str, Any]:
    p = material_path(root)
    if not p.exists():
        mat = {
            "key_id": DEV_KEY_ID,
            "algorithm": DEV_ALGORITHM,
            "secret_b64url": b64url(secrets.token_bytes(32)),
            "created_at": now(),
            "scope": "local-dev-only",
            "note": "Local dev signing material created by 11B. Not a PEM private key.",
        }
        write_json(p, mat)
        return mat
    mat = parse(read_json(p), p)
    write_json(p, mat)
    return mat

def sign_verify(mat: Mapping[str, Any]) -> tuple[bool, str]:
    header = {"alg": mat["algorithm"], "kid": mat["key_id"], "typ": "PRISMA-LICENSE-JWS"}
    payload = {"licenseId": "lic_11b_smoke", "plan": "TABLET_PC_REQUIRED", "state": "active"}
    h = b64url(canonical(header)); p = b64url(canonical(payload))
    sig = hmac.new(b64decode(str(mat["secret_b64url"])), f"{h}.{p}".encode("ascii"), hashlib.sha256).digest()
    compact = f"{h}.{p}.{b64url(sig)}"
    hh, pp, ss = compact.split(".")
    expected = hmac.new(b64decode(str(mat["secret_b64url"])), f"{hh}.{pp}".encode("ascii"), hashlib.sha256).digest()
    return hmac.compare_digest(expected, b64decode(ss)), "signature_valid"

def cmd_migrate(args: argparse.Namespace) -> int:
    root = root_path(args.root); out = Path(args.out).expanduser().resolve()
    p = material_path(root); before = read_json(p) if p.exists() else {}
    mat = ensure_material(root); pem = bool(PRIVATE_KEY_RE.search(p.read_text(encoding="utf-8", errors="ignore")))
    r = report(out, "license_server_signing_material_11b_migrate", [
        "# PRISMA License Server Signing Material 11B Migrate", "",
        f"Material: `{p}`", f"Legacy before: `{bool(before and before != mat)}`",
        f"Key ID: `{mat['key_id']}`", f"Algorithm: `{mat['algorithm']}`", f"PEM private key block: `{pem}`",
        f"Status: `{'BLOCKED' if pem else 'FINAL READY'}`",
    ])
    print(f"MATERIAL {p}"); print(f"REPORT {r}"); print("FINAL READY" if not pem else "BLOCKED")
    return 0 if not pem else 2

def cmd_smoke(args: argparse.Namespace) -> int:
    root = root_path(args.root); out = Path(args.out).expanduser().resolve(); p = material_path(root)
    mat = ensure_material(root); ok, reason = sign_verify(mat); pem = bool(PRIVATE_KEY_RE.search(p.read_text(encoding="utf-8", errors="ignore")))
    status = ok and not pem
    r = report(out, "license_server_signing_material_11b_smoke", [
        "# PRISMA License Server Signing Material 11B Smoke", "",
        f"Material: `{p}`", f"Key ID: `{mat['key_id']}`", f"Algorithm: `{mat['algorithm']}`",
        f"Sign verify: `{'OK' if ok else 'FAIL'} {reason}`", f"PEM private key block: `{'FAIL' if pem else 'OK'}`",
        f"Status: `{'FINAL READY' if status else 'BLOCKED'}`",
    ])
    print(f"- material parses and normalizes: OK {mat['key_id']} alg={mat['algorithm']}")
    print(f"- sign+verify: {'OK' if ok else 'FAIL'} {reason}")
    print(f"- material PEM private-key block: {'FAIL' if pem else 'OK'}")
    print(f"REPORT {r}"); print("FINAL READY" if status else "BLOCKED")
    return 0 if status else 2

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate").set_defaults(func=cmd_migrate)
    sub.add_parser("smoke").set_defaults(func=cmd_smoke)
    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ToolError as e:
        print(f"[ERROR] {e}", file=sys.stderr); return e.code

if __name__ == "__main__":
    raise SystemExit(main())
