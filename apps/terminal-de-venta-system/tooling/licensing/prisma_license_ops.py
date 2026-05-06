#!/usr/bin/env python3
"""PRISMA license operations console.

Operational helper for PRISMA license runtime checks, live smoke tests,
demo-license switching, and evidence reports.

This script is intentionally stdlib-only. It does not mutate operational data
except when --set-demo-license is explicitly requested, and then it backs up the
previous license first.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

PROJECT_NAME = "terminal_venta_license_ops"
DEFAULT_TABLET_BASE = "http://127.0.0.1:3120"
DEFAULT_PC_BASE = "http://127.0.0.1:3130"

REQUIRED_02ABCD_FILES = [
    "shared/licensing/license-types.ts",
    "shared/licensing/license-schema.ts",
    "shared/licensing/license-loader.ts",
    "shared/licensing/feature-resolver.ts",
    "shared/licensing/license-gate.ts",
    "shared/licensing/license-signature.ts",
    "shared/licensing/local-license-store.ts",
    "shared/licensing/license-refresh-client.ts",
    "shared/licensing/license-refresh-state.ts",
    "products/tablet/app/app/api/license/status/route.ts",
    "products/tablet/app/app/api/license/features/route.ts",
    "products/tablet/app/app/api/license/refresh/route.ts",
    "products/tablet/app/app/api/license/refresh/status/route.ts",
    "products/tablet/app/app/settings/license/page.tsx",
    "products/pc/app/app/api/license/status/route.ts",
    "products/pc/app/app/api/license/features/route.ts",
    "products/pc/app/app/api/license/refresh/route.ts",
    "products/pc/app/app/api/license/refresh/status/route.ts",
    "products/pc/app/app/settings/license/page.tsx",
    "tooling/licensing/verify_signed_license.js",
    "local-runtime/license/license.signed.dev.json",
]

BUILD_GATES = [
    ("tablet-typecheck", ["tablet-typecheck"]),
    ("tablet-build", ["tablet-build"]),
    ("pc-typecheck", ["pc-typecheck"]),
    ("pc-build", ["pc-build"]),
]

TABLET_ENDPOINTS = [
    ("Tablet health", "/api/health"),
    ("Tablet license status", "/api/license/status"),
    ("Tablet license features", "/api/license/features"),
    ("Tablet license refresh status", "/api/license/refresh/status"),
    ("Tablet license page", "/settings/license"),
    ("Tablet POS", "/pos"),
]

PC_ENDPOINTS = [
    ("PC home", "/"),
    ("PC license status", "/api/license/status"),
    ("PC license features", "/api/license/features"),
    ("PC license refresh status", "/api/license/refresh/status"),
    ("PC license page", "/settings/license"),
    ("PC dashboard API", "/api/backoffice/dashboard"),
]

LICENSE_FIXTURE_CANDIDATES = {
    "TABLET_SOLO": [
        "tooling/licensing/fixtures/tablet-solo.active.signed.license.json",
        "tooling/productization/examples/licenses/tablet-solo.active.signed.license.json",
    ],
    "TABLET_PRO": [
        "tooling/licensing/fixtures/tablet-pro.active.signed.license.json",
        "tooling/productization/examples/licenses/tablet-pro.active.signed.license.json",
    ],
    "TABLET_PC_REQUIRED": [
        "tooling/licensing/fixtures/tablet-pc-required.active.signed.license.json",
        "tooling/productization/examples/licenses/tablet-pc-required.active.signed.license.json",
    ],
    "EXPIRED": [
        "tooling/licensing/fixtures/expired.signed.license.json",
        "tooling/productization/examples/licenses/expired.signed.license.json",
    ],
    "SUSPENDED": [
        "tooling/licensing/fixtures/suspended.signed.license.json",
        "tooling/productization/examples/licenses/suspended.signed.license.json",
    ],
    "REVOKED": [
        "tooling/licensing/fixtures/revoked.signed.license.json",
        "tooling/productization/examples/licenses/revoked.signed.license.json",
    ],
    "TAMPERED": [
        "tooling/licensing/fixtures/tampered.signed.license.json",
        "tooling/productization/examples/licenses/tampered.signed.license.json",
    ],
}


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str = ""
    elapsed_s: float = 0.0


@dataclass
class OpsContext:
    root: Path
    out_dir: Path
    stamp: str
    log_path: Path
    report_path: Path | None = None
    results: list[CheckResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        line = f"{_dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        print(message)

    def add(self, name: str, status: str, detail: str = "", elapsed_s: float = 0.0) -> None:
        self.results.append(CheckResult(name=name, status=status, detail=detail, elapsed_s=elapsed_s))
        icon = {"OK": "OK", "FAIL": "FAIL", "SKIP": "SKIP", "WARN": "WARN"}.get(status, status)
        suffix = f" :: {detail}" if detail else ""
        self.log(f"{icon} {name}{suffix}")


def now_stamp() -> str:
    return _dt.datetime.now().strftime("%y%m%d_%H%M")


def resolve_root(raw: str | None) -> Path:
    if raw:
        root = Path(raw).expanduser().resolve()
    else:
        root = Path.cwd().resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")
    return root


def default_out_dir() -> Path:
    if os.name == "nt":
        return Path("F:/descargasf")
    return Path("/mnt/data")


def make_ctx(args: argparse.Namespace) -> OpsContext:
    root = resolve_root(args.root)
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else default_out_dir()
    stamp = now_stamp()
    return OpsContext(
        root=root,
        out_dir=out_dir,
        stamp=stamp,
        log_path=out_dir / f"{PROJECT_NAME}_{stamp}.log",
    )


def run_cmd(ctx: OpsContext, name: str, cmd: list[str], cwd: Path | None = None, timeout: int | None = None) -> bool:
    start = time.monotonic()
    cwd = cwd or ctx.root
    ctx.log(f"RUN {name}: {' '.join(cmd)} [cwd={cwd}]")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except Exception as exc:
        elapsed = time.monotonic() - start
        ctx.add(name, "FAIL", str(exc), elapsed)
        return False

    if proc.stdout:
        with ctx.log_path.open("a", encoding="utf-8") as fh:
            fh.write(proc.stdout)
            if not proc.stdout.endswith("\n"):
                fh.write("\n")
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")

    elapsed = time.monotonic() - start
    if proc.returncode == 0:
        ctx.add(name, "OK", f"exit=0", elapsed)
        return True
    ctx.add(name, "FAIL", f"exit={proc.returncode}", elapsed)
    return False


def terminal_cmd(root: Path) -> Path:
    cmd = root / "terminal_de_venta.cmd"
    if not cmd.exists():
        raise FileNotFoundError(f"Missing terminal_de_venta.cmd at {cmd}")
    return cmd


def check_required_files(ctx: OpsContext) -> bool:
    ok = True
    for rel in REQUIRED_02ABCD_FILES:
        path = ctx.root / rel
        if path.exists():
            ctx.add(f"required file {rel}", "OK")
        else:
            ctx.add(f"required file {rel}", "FAIL", "missing")
            ok = False
    return ok


def verify_signed_fixtures(ctx: OpsContext) -> bool:
    script = ctx.root / "tooling/licensing/verify_signed_license.js"
    if not script.exists():
        ctx.add("signed fixture verification", "FAIL", f"missing {script}")
        return False
    return run_cmd(ctx, "signed fixture verification", ["node", str(script), "--root", str(ctx.root)], cwd=ctx.root, timeout=120)


def run_build_gates(ctx: OpsContext) -> bool:
    try:
        cmd = terminal_cmd(ctx.root)
    except FileNotFoundError as exc:
        ctx.add("build gates", "FAIL", str(exc))
        return False

    ok = True
    for name, args in BUILD_GATES:
        if not run_cmd(ctx, name, [str(cmd), *args], cwd=ctx.root, timeout=900):
            ok = False
            break
    return ok


def http_get(url: str, timeout: int = 12) -> tuple[int, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "PRISMA-License-Ops/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("content-type", "")
        data = resp.read(1_000_000).decode("utf-8", errors="replace")
        return resp.status, content_type, data


def endpoint(ctx: OpsContext, name: str, base: str, path: str) -> bool:
    url = base.rstrip("/") + path
    start = time.monotonic()
    try:
        status, content_type, body = http_get(url)
        elapsed = time.monotonic() - start
        excerpt = body[:1200].replace("\n", " ")
        detail = f"{status} {content_type} {url}"
        if excerpt:
            detail += f" body={excerpt[:240]}"
        if 200 <= status < 400:
            ctx.add(name, "OK", detail, elapsed)
            return True
        ctx.add(name, "FAIL", detail, elapsed)
        return False
    except Exception as exc:
        elapsed = time.monotonic() - start
        ctx.add(name, "FAIL", f"{url} :: {exc}", elapsed)
        return False


def probe_base(base: str, path: str = "/") -> bool:
    try:
        status, _, _ = http_get(base.rstrip("/") + path, timeout=4)
        return 200 <= status < 500
    except Exception:
        return False


def start_app(ctx: OpsContext, app_name: str, command_name: str, out_name: str) -> None:
    cmd = terminal_cmd(ctx.root)
    out_log = ctx.out_dir / f"{PROJECT_NAME}_{out_name}_{ctx.stamp}.out.log"
    err_log = ctx.out_dir / f"{PROJECT_NAME}_{out_name}_{ctx.stamp}.err.log"
    ctx.log(f"START {app_name}: {cmd} {command_name}")
    out_fh = out_log.open("a", encoding="utf-8")
    err_fh = err_log.open("a", encoding="utf-8")
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        creationflags = 0
    subprocess.Popen(
        [str(cmd), command_name],
        cwd=str(ctx.root),
        stdout=out_fh,
        stderr=err_fh,
        text=True,
        creationflags=creationflags,
    )
    ctx.notes.append(f"Started {app_name}. stdout={out_log} stderr={err_log}")


def ensure_running(ctx: OpsContext, tablet_base: str, pc_base: str, start_missing: bool) -> None:
    tablet_ok = probe_base(tablet_base, "/api/health")
    pc_ok = probe_base(pc_base, "/")

    if tablet_ok:
        ctx.add("Tablet server running", "OK", tablet_base)
    elif start_missing:
        ctx.add("Tablet server running", "WARN", "not responding; starting tablet-dev")
        start_app(ctx, "Tablet", "tablet-dev", "tablet_dev")
    else:
        ctx.add("Tablet server running", "WARN", "not responding; use --ensure-running to start")

    if pc_ok:
        ctx.add("PC server running", "OK", pc_base)
    elif start_missing:
        ctx.add("PC server running", "WARN", "not responding; starting pc-dev")
        start_app(ctx, "PC", "pc-dev", "pc_dev")
    else:
        ctx.add("PC server running", "WARN", "not responding; use --ensure-running to start")

    if start_missing and (not tablet_ok or not pc_ok):
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            tablet_ok = probe_base(tablet_base, "/api/health")
            pc_ok = probe_base(pc_base, "/")
            if tablet_ok and pc_ok:
                break
            time.sleep(3)
        ctx.add("Tablet server after start", "OK" if tablet_ok else "FAIL", tablet_base)
        ctx.add("PC server after start", "OK" if pc_ok else "FAIL", pc_base)


def smoke_live(ctx: OpsContext, tablet_base: str, pc_base: str) -> bool:
    ok = True
    for name, path in TABLET_ENDPOINTS:
        if not endpoint(ctx, name, tablet_base, path):
            ok = False
    for name, path in PC_ENDPOINTS:
        if not endpoint(ctx, name, pc_base, path):
            ok = False
    return ok


def find_fixture(root: Path, key: str) -> Path:
    candidates = LICENSE_FIXTURE_CANDIDATES.get(key.upper())
    if not candidates:
        valid = ", ".join(sorted(LICENSE_FIXTURE_CANDIDATES))
        raise SystemExit(f"Unknown demo license '{key}'. Valid: {valid}")
    for rel in candidates:
        path = root / rel
        if path.exists():
            return path
    raise SystemExit(f"No fixture found for {key}. Tried: {candidates}")


def set_demo_license(ctx: OpsContext, key: str) -> bool:
    source = find_fixture(ctx.root, key)
    dest = ctx.root / "local-runtime/license/license.signed.dev.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        backup = dest.with_name(f"{dest.name}.bak.{ctx.stamp}")
        shutil.copy2(dest, backup)
        ctx.add("backup current license", "OK", str(backup))
    shutil.copy2(source, dest)
    ctx.add("set demo license", "OK", f"{key.upper()} <- {source}")
    return True


def collect_current_status(ctx: OpsContext, tablet_base: str, pc_base: str) -> None:
    for name, url in [
        ("Tablet current license", tablet_base.rstrip("/") + "/api/license/status"),
        ("PC current license", pc_base.rstrip("/") + "/api/license/status"),
    ]:
        try:
            status, _, body = http_get(url, timeout=6)
            payload = json.loads(body)
            data = payload.get("data", payload)
            summary = json.dumps(data, ensure_ascii=False)[:900]
            ctx.add(name, "OK" if status == 200 else "WARN", summary)
        except Exception as exc:
            ctx.add(name, "WARN", f"not available live: {exc}")


def verdict(results: Iterable[CheckResult]) -> str:
    items = list(results)
    if any(r.status == "FAIL" for r in items):
        return "BLOCKED"
    if any(r.status == "WARN" for r in items):
        return "READY WITH CAVEATS"
    return "READY"


def write_report(ctx: OpsContext, title: str) -> Path:
    report = ctx.out_dir / f"{PROJECT_NAME}_report_{ctx.stamp}.md"
    v = verdict(ctx.results)
    lines = [
        f"# {title}",
        "",
        f"**Verdict:** `{v}`",
        f"**Generated:** `{_dt.datetime.now().isoformat(timespec='seconds')}`",
        f"**Root:** `{ctx.root}`",
        f"**Log:** `{ctx.log_path}`",
        "",
        "## Results",
        "",
        "| Check | Status | Detail | Seconds |",
        "|---|---:|---|---:|",
    ]
    for r in ctx.results:
        detail = r.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {r.name} | {r.status} | {detail} | {r.elapsed_s:.1f} |")
    lines.extend(["", "## Notes", ""])
    if ctx.notes:
        for note in ctx.notes:
            lines.append(f"- {note}")
    else:
        lines.append("- No additional notes.")
    lines.extend([
        "",
        "## Operator summary",
        "",
        "This report checks the PRISMA license runtime, signed license fixtures, optional refresh surface, live routes, and build gates when requested.",
        "Basic Tablet sale capability must remain independent from remote license refresh.",
    ])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.report_path = report
    ctx.log(f"REPORT {report}")
    return report


def self_check(ctx: OpsContext) -> bool:
    ok = check_required_files(ctx)
    script = ctx.root / "tooling/licensing/prisma_license_ops.py"
    ok = run_cmd(ctx, "py_compile prisma_license_ops", [sys.executable, "-m", "py_compile", str(script)], cwd=ctx.root) and ok
    verifier = ctx.root / "tooling/licensing/verify_signed_license.js"
    if verifier.exists():
        ok = verify_signed_fixtures(ctx) and ok
    else:
        ctx.add("signed fixture verification", "WARN", "verify_signed_license.js missing; maybe 02CD not installed")
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PRISMA license operations automation")
    parser.add_argument("--root", help="Terminal de Venta project root")
    parser.add_argument("--out-dir", help="Output directory for logs and reports")
    parser.add_argument("--tablet-base", default=DEFAULT_TABLET_BASE)
    parser.add_argument("--pc-base", default=DEFAULT_PC_BASE)
    parser.add_argument("--self-check", action="store_true", help="Verify package files and local script health")
    parser.add_argument("--verify-builds", action="store_true", help="Run Tablet/PC typecheck and build gates")
    parser.add_argument("--smoke-live", action="store_true", help="Probe live Tablet and PC license endpoints")
    parser.add_argument("--ensure-running", action="store_true", help="Start tablet-dev/pc-dev if live endpoints are down")
    parser.add_argument("--set-demo-license", choices=sorted(LICENSE_FIXTURE_CANDIDATES), help="Switch local signed demo license")
    parser.add_argument("--report", action="store_true", help="Generate current report without forcing all gates")
    parser.add_argument("--full-check", action="store_true", help="Run self-check, signed fixtures, builds, live smoke, and report")
    parser.add_argument("--skip-build", action="store_true", help="Skip build gates during full-check")
    parser.add_argument("--skip-live", action="store_true", help="Skip live smoke during full-check")

    args = parser.parse_args(argv)
    ctx = make_ctx(args)
    ctx.log(f"Root: {ctx.root}")

    ok = True

    try:
        if args.set_demo_license:
            ok = set_demo_license(ctx, args.set_demo_license) and ok

        if args.full_check or args.self_check:
            ok = self_check(ctx) and ok

        if args.full_check and not args.skip_build:
            ok = run_build_gates(ctx) and ok
        elif args.verify_builds:
            ok = run_build_gates(ctx) and ok

        if args.full_check and not args.skip_live:
            ensure_running(ctx, args.tablet_base, args.pc_base, args.ensure_running)
            ok = smoke_live(ctx, args.tablet_base, args.pc_base) and ok
            collect_current_status(ctx, args.tablet_base, args.pc_base)
        elif args.smoke_live:
            ensure_running(ctx, args.tablet_base, args.pc_base, args.ensure_running)
            ok = smoke_live(ctx, args.tablet_base, args.pc_base) and ok
            collect_current_status(ctx, args.tablet_base, args.pc_base)
        elif args.report:
            collect_current_status(ctx, args.tablet_base, args.pc_base)

        if args.full_check or args.report or args.smoke_live or args.verify_builds or args.self_check or args.set_demo_license:
            write_report(ctx, "PRISMA License Operations Report")
        else:
            parser.print_help()
            return 2

        final = verdict(ctx.results)
        ctx.log(f"FINAL {final}")
        if ctx.report_path:
            print(f"Report: {ctx.report_path}")
        return 0 if ok and final != "BLOCKED" else 1
    except KeyboardInterrupt:
        ctx.log("Interrupted")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
