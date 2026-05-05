#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKAGE = "PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09"
VERSION = "0.9.0"
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".next", "dist", "build", ".venv", "venv", "__pycache__", ".turbo", ".cache"}
TEXT_SUFFIXES = {".cmd", ".ps1", ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".env", ".yml", ".yaml", ".toml"}


def now_stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")


def default_out_dir() -> Path:
    return Path(r"F:\descargasf") if os.name == "nt" else Path(tempfile.gettempdir())


@dataclass
class Ctx:
    root: Path
    out_dir: Path

    @property
    def base(self) -> Path:
        return self.root / "tooling" / "licensing" / "keys09"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_report(out_dir: Path, stem: str, content: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}_{now_stamp()}.md"
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return path


def resolve_ctx(args: argparse.Namespace) -> Ctx:
    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else default_out_dir()
    if not (root / "terminal_de_venta.cmd").exists():
        raise SystemExit(f"Root invalida, falta terminal_de_venta.cmd: {root}")
    return Ctx(root=root, out_dir=out_dir)


def policy_path(ctx: Ctx) -> Path:
    return ctx.base / "key_policy.json"


def registry_path(ctx: Ctx) -> Path:
    return ctx.base / "public_key_registry.example.json"


def env_contract_path(ctx: Ctx) -> Path:
    return ctx.base / "license_env_contract_09.json"


def command_policy(ctx: Ctx, args: argparse.Namespace) -> int:
    policy = load_json(policy_path(ctx))
    print(json.dumps(policy, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def validate_registry_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schemaVersion") != "09.public-key-registry.1":
        errors.append("schemaVersion invalido")
    keys = data.get("keys")
    if not isinstance(keys, list) or not keys:
        errors.append("registry sin keys")
        return errors
    for idx, key in enumerate(keys):
        prefix = f"keys[{idx}]"
        for field in ["keyId", "environment", "algorithm", "state", "publicKeyPem"]:
            if not key.get(field):
                errors.append(f"{prefix} falta {field}")
        pem = str(key.get("publicKeyPem", ""))
        if "PRIVATE KEY" in pem:
            errors.append(f"{prefix} contiene private key")
        if key.get("algorithm") in {"HS256_DEV_ONLY", "HS256", "none", "UNSIGNED"}:
            errors.append(f"{prefix} algoritmo no permitido para public registry: {key.get('algorithm')}")
    return errors


def command_registry(ctx: Ctx, args: argparse.Namespace) -> int:
    data = load_json(registry_path(ctx))
    errors = validate_registry_data(data)
    if errors:
        print("REGISTRY BLOCKED")
        for e in errors:
            print(f"- {e}")
        return 2
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
    print("FINAL READY")
    return 0


def env_lines(env: str, contract: dict[str, Any]) -> list[str]:
    if env not in {"development", "staging", "production"}:
        raise ValueError("--env debe ser development, staging o production")
    lines = [f"# PRISMA license env template 09", f"PRISMA_LICENSE_ENV={env}"]
    if env == "development":
        lines.extend([
            "PRISMA_LICENSE_SERVER_URL=http://127.0.0.1:3140",
            "PRISMA_LICENSE_ALLOW_UNSIGNED_DEV=1",
            "PRISMA_LICENSE_DEV_KEY_ID=dev-local-09",
            "# PRISMA_LICENSE_DEV_SIGNING_SECRET se define localmente; no commitear.",
        ])
    elif env == "staging":
        lines.extend([
            "PRISMA_LICENSE_SERVER_URL=https://licensing-staging.example.invalid",
            "PRISMA_LICENSE_PUBLIC_KEY_REGISTRY_PATH=tooling/licensing/keys09/public_key_registry.example.json",
            "PRISMA_LICENSE_ACTIVE_KEY_ID=prisma-staging-rs256-2026-01",
            "PRISMA_LICENSE_SIGNING_KEY_REF=secret-manager://prisma/staging/license-signing-key",
            "PRISMA_LICENSE_ALLOW_UNSIGNED_DEV=0",
        ])
    else:
        lines.extend([
            "PRISMA_LICENSE_SERVER_URL=https://licensing.example.invalid",
            "PRISMA_LICENSE_PUBLIC_KEY_REGISTRY_PATH=tooling/licensing/keys09/public_key_registry.example.json",
            "PRISMA_LICENSE_ACTIVE_KEY_ID=prisma-prod-eddsa-2026-01",
            "PRISMA_LICENSE_SIGNING_KEY_REF=kms://prisma/prod/license-signing-key",
            "PRISMA_LICENSE_ALLOW_UNSIGNED_DEV=0",
            "PRISMA_LICENSE_ALLOW_DEV_SIGNATURE_IN_STAGING=0",
        ])
    return lines


def command_env_template(ctx: Ctx, args: argparse.Namespace) -> int:
    contract = load_json(env_contract_path(ctx))
    lines = env_lines(args.env, contract)
    content = "\n".join(lines) + "\n"
    report = write_report(ctx.out_dir, f"terminal_venta_license_key_env_{args.env}_09", "# Env template 09\n\n```text\n" + content + "```\n")
    print(content)
    print(f"REPORT {report}")
    print("FINAL READY")
    return 0


def iter_candidate_files(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            suffix = path.suffix.lower()
            lower_name = name.lower()
            if suffix in TEXT_SUFFIXES or suffix in {".pem", ".key", ".p8", ".p12", ".pfx"} or ".env" in lower_name:
                yield path


def scan_private_key_risks(root: Path, policy: dict[str, Any]) -> tuple[list[str], list[str]]:
    blocked: list[str] = []
    warnings: list[str] = []
    suffixes = set(str(s).lower() for s in policy.get("forbiddenFileSuffixesForCommittedSecrets", []))
    private_key_re = re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")
    private_env_re = re.compile(r"^\s*(?:export\s+)?PRISMA_LICENSE_[A-Z0-9_]*PRIVATE[A-Z0-9_]*\s*=\s*\S+", re.MULTILINE)
    allowlisted = {
        "tooling/licensing/keys09/key_policy.json",
        "tooling/licensing/keys09/license_key_management_09.py",
        "docs/productization/PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09.md",
        "docs/productization/PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09_RUNBOOK.md",
        "docs/productization/PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09_ACCEPTANCE.md",
    }
    for path in iter_candidate_files(root):
        rel = str(path.relative_to(root)).replace("\\", "/")
        suffix = path.suffix.lower()
        if rel in allowlisted:
            continue
        if suffix in suffixes:
            warnings.append(f"archivo con sufijo sensible: {rel}")
        try:
            if path.stat().st_size > 1024 * 512:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if private_key_re.search(text):
            blocked.append(f"private key PEM detectada en {rel}")
        if private_env_re.search(text):
            blocked.append(f"variable privada de licencia con valor detectada en {rel}")
    return blocked, warnings


def command_audit(ctx: Ctx, args: argparse.Namespace) -> int:
    policy = load_json(policy_path(ctx))
    blocked, warnings = scan_private_key_risks(ctx.root, policy)
    status = "BLOCKED" if blocked else "READY"
    lines = [
        "# PRISMA License Key Audit 09",
        "",
        f"Root: `{ctx.root}`",
        f"Status: **{status}**",
        "",
        "## Blockers",
    ]
    lines += [f"- {b}" for b in blocked] or ["- ninguno"]
    lines += ["", "## Warnings"]
    lines += [f"- {w}" for w in warnings[:100]] or ["- ninguno"]
    if len(warnings) > 100:
        lines.append(f"- ... {len(warnings) - 100} warnings adicionales truncados")
    report = write_report(ctx.out_dir, "terminal_venta_license_key_audit_09", "\n".join(lines))
    print(f"REPORT {report}")
    if blocked:
        print("BLOCKED")
        return 2
    print("FINAL READY")
    return 0


def command_rotation_plan(ctx: Ctx, args: argparse.Namespace) -> int:
    policy = load_json(policy_path(ctx))
    overlap = int(policy.get("rotation", {}).get("overlapDays", 14))
    lines = [
        "# PRISMA License Key Rotation Plan 09",
        "",
        f"Environment: `{args.env}`",
        f"Current keyId: `{args.current_key_id}`",
        f"Next keyId: `{args.next_key_id}`",
        f"Overlap days: `{overlap}`",
        "",
        "## Steps",
        "1. Publicar la nueva llave publica como `next`.",
        "2. Verificar que clientes acepten `current` y `next`.",
        "3. Cambiar emision del servidor al nuevo `keyId`.",
        f"4. Mantener `{args.current_key_id}` en verify-only por {overlap} dias.",
        "5. Marcar llave anterior como `retired`.",
        "6. Si hay sospecha de fuga, marcar como `revoked` y cortar sin ceremonia.",
        "",
        "## Stop conditions",
        "- Se detecta private key en repo.",
        "- Clientes no validan el nuevo `keyId`.",
        "- Produccion intenta aceptar `HS256_DEV_ONLY`.",
    ]
    report = write_report(ctx.out_dir, "terminal_venta_license_key_rotation_plan_09", "\n".join(lines))
    print(f"REPORT {report}")
    print("FINAL READY")
    return 0


def command_smoke(ctx: Ctx, args: argparse.Namespace) -> int:
    policy = load_json(policy_path(ctx))
    registry = load_json(registry_path(ctx))
    env_contract = load_json(env_contract_path(ctx))
    failures: list[str] = []
    prod = policy.get("environments", {}).get("production", {})
    if prod.get("allowUnsigned") is not False:
        failures.append("production debe rechazar unsigned")
    if "HS256_DEV_ONLY" in prod.get("allowedAlgorithms", []):
        failures.append("production no debe permitir HS256_DEV_ONLY")
    if "HS256_DEV_ONLY" not in policy.get("environments", {}).get("development", {}).get("allowedAlgorithms", []):
        failures.append("development debe documentar HS256_DEV_ONLY")
    failures.extend(validate_registry_data(registry))
    if "PRISMA_LICENSE_SIGNING_KEY_REF" not in env_contract.get("variables", {}):
        failures.append("env contract sin PRISMA_LICENSE_SIGNING_KEY_REF")
    blocked, warnings = scan_private_key_risks(ctx.base, policy)
    failures.extend(blocked)
    lines = ["# PRISMA License Key Management 09 Smoke", "", f"Root: `{ctx.root}`", "", "## Results"]
    if failures:
        lines += [f"- FAIL {f}" for f in failures]
    else:
        lines += ["- policy: OK", "- registry: OK", "- env contract: OK", "- private key scan on keys09: OK"]
    if warnings:
        lines += ["", "## Warnings"] + [f"- {w}" for w in warnings]
    report = write_report(ctx.out_dir, "terminal_venta_license_key_management_09_smoke", "\n".join(lines))
    print(f"REPORT {report}")
    if failures:
        print("BLOCKED")
        return 2
    print("FINAL READY")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRISMA license production key management 09")
    parser.add_argument("--root", default=".", help="Raiz de apps/terminal-de-venta-system")
    parser.add_argument("--out-dir", default=None, help="Directorio de reportes; default F:\\descargasf en Windows")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("policy")
    sub.add_parser("registry")
    p_env = sub.add_parser("env-template")
    p_env.add_argument("--env", choices=["development", "staging", "production"], default="production")
    sub.add_parser("audit")
    p_rot = sub.add_parser("rotation-plan")
    p_rot.add_argument("--env", choices=["staging", "production"], default="production")
    p_rot.add_argument("--current-key-id", required=True)
    p_rot.add_argument("--next-key-id", required=True)
    sub.add_parser("smoke")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ctx = resolve_ctx(args)
    if args.cmd == "policy":
        return command_policy(ctx, args)
    if args.cmd == "registry":
        return command_registry(ctx, args)
    if args.cmd == "env-template":
        return command_env_template(ctx, args)
    if args.cmd == "audit":
        return command_audit(ctx, args)
    if args.cmd == "rotation-plan":
        return command_rotation_plan(ctx, args)
    if args.cmd == "smoke":
        return command_smoke(ctx, args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    _code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_code)
