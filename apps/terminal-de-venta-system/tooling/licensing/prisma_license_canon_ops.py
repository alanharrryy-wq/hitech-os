from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

DEFAULT_OUT_DIR = Path(r"F:\descargasf") if os.name == "nt" else Path("/tmp")
TABLET_PORT = 3120
PC_PORT = 3130

REQUIRED_FILES = [
    "shared/licensing/license-types.ts",
    "shared/licensing/license-loader.ts",
    "shared/licensing/feature-resolver.ts",
    "shared/licensing/license-signature.ts",
    "shared/licensing/license-refresh-client.ts",
    "shared/licensing/local-license-store.ts",
    "local-runtime/license/license.signed.dev.json",
    "tooling/licensing/verify_signed_license.js",
    "terminal_de_venta_license_ops.cmd",
]

PLAN_EXPECTATIONS = {
    "TABLET_SOLO": {"dashboard": 403},
    "TABLET_PRO": {"dashboard": 403},
    "TABLET_PC_REQUIRED": {"dashboard": 200},
    "EXPIRED": {"dashboard": 403},
    "SUSPENDED": {"dashboard": 403},
    "REVOKED": {"dashboard": 403},
    "TAMPERED": {"dashboard": 403},
}

@dataclass
class Result:
    name: str
    ok: bool
    detail: str = ""
    exit_code: int | None = None

@dataclass
class Context:
    root: Path
    out_dir: Path
    stamp: str
    log_path: Path
    report_path: Path
    results: list[Result] = field(default_factory=list)

    def log(self, message: str) -> None:
        line = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        print(message)

    def add(self, name: str, ok: bool, detail: str = "", exit_code: int | None = None) -> None:
        self.results.append(Result(name=name, ok=ok, detail=detail, exit_code=exit_code))
        state = "OK" if ok else "FAIL"
        suffix = f" :: {detail}" if detail else ""
        self.log(f"{state} {name}{suffix}")


def make_context(root: Path, out_dir: Path) -> Context:
    stamp = dt.datetime.now().strftime("%y%m%d_%H%M")
    out_dir.mkdir(parents=True, exist_ok=True)
    return Context(
        root=root.resolve(),
        out_dir=out_dir,
        stamp=stamp,
        log_path=out_dir / f"terminal_venta_license_canon_ops_{stamp}.log",
        report_path=out_dir / f"terminal_venta_license_canon_ops_report_{stamp}.md",
    )


def run(ctx: Context, name: str, cmd: list[str], cwd: Path | None = None, allow_fail: bool = False) -> subprocess.CompletedProcess:
    cwd = cwd or ctx.root
    ctx.log(f"RUN {name}: {' '.join(cmd)} [cwd={cwd}]")
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    output = proc.stdout or ""
    if output:
        with ctx.log_path.open("a", encoding="utf-8", errors="replace") as fh:
            fh.write(output)
            if not output.endswith("\n"):
                fh.write("\n")
        print(output, end="" if output.endswith("\n") else "\n")
    ok = proc.returncode == 0
    ctx.add(name, ok, f"exit={proc.returncode}", proc.returncode)
    if not ok and not allow_fail:
        raise RuntimeError(f"{name} failed with exit={proc.returncode}")
    return proc


def terminal_cmd(ctx: Context) -> Path:
    p = ctx.root / "terminal_de_venta.cmd"
    if not p.exists():
        raise RuntimeError(f"Missing terminal_de_venta.cmd: {p}")
    return p


def ops_cmd(ctx: Context) -> Path:
    p = ctx.root / "terminal_de_venta_license_ops.cmd"
    if not p.exists():
        raise RuntimeError(f"Missing terminal_de_venta_license_ops.cmd: {p}")
    return p


def self_check(ctx: Context) -> None:
    ctx.log("SELF CHECK")
    if not ctx.root.exists():
        raise RuntimeError(f"Root does not exist: {ctx.root}")
    missing = []
    for rel in REQUIRED_FILES:
        path = ctx.root / rel
        if path.exists():
            ctx.add(f"required file {rel}", True)
        else:
            ctx.add(f"required file {rel}", False, str(path))
            missing.append(rel)
    if missing:
        raise RuntimeError("Missing required files: " + ", ".join(missing))

    run(ctx, "py_compile prisma_license_canon_ops", [sys.executable, "-m", "py_compile", str(ctx.root / "tooling/licensing/prisma_license_canon_ops.py")])
    run(ctx, "py_compile mock_license_server", [sys.executable, "-m", "py_compile", str(ctx.root / "tooling/licensing/mock_license_server.py")])

    verifier = ctx.root / "tooling/licensing/verify_signed_license.js"
    if verifier.exists():
        run(ctx, "signed fixture verification", ["node", str(verifier), "--root", str(ctx.root)])


def core_build_gates(ctx: Context) -> None:
    cmd = terminal_cmd(ctx)
    for gate in ["tablet-typecheck", "tablet-build", "pc-typecheck", "pc-build"]:
        run(ctx, gate, [str(cmd), gate])


def http_get(url: str, timeout: int = 12) -> tuple[int, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "prisma-license-canon-ops/0.4"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            return int(resp.status), resp.headers.get("Content-Type", ""), body
    except urllib.error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        return int(exc.code), exc.headers.get("Content-Type", ""), body


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.8)
        return s.connect_ex((host, port)) == 0


def start_dev_servers_if_needed(ctx: Context) -> None:
    cmd = terminal_cmd(ctx)
    if not port_open(TABLET_PORT):
        out = open(ctx.out_dir / f"tablet_dev_{ctx.stamp}.out.log", "w", encoding="utf-8")
        err = open(ctx.out_dir / f"tablet_dev_{ctx.stamp}.err.log", "w", encoding="utf-8")
        subprocess.Popen([str(cmd), "tablet-dev"], cwd=str(ctx.root), stdout=out, stderr=err)
        ctx.add("start tablet dev", True, f"started port {TABLET_PORT}")
    else:
        ctx.add("tablet dev already running", True, f"port {TABLET_PORT}")

    if not port_open(PC_PORT):
        out = open(ctx.out_dir / f"pc_dev_{ctx.stamp}.out.log", "w", encoding="utf-8")
        err = open(ctx.out_dir / f"pc_dev_{ctx.stamp}.err.log", "w", encoding="utf-8")
        subprocess.Popen([str(cmd), "pc-dev"], cwd=str(ctx.root), stdout=out, stderr=err)
        ctx.add("start pc dev", True, f"started port {PC_PORT}")
    else:
        ctx.add("pc dev already running", True, f"port {PC_PORT}")

    deadline = time.time() + 45
    while time.time() < deadline:
        if port_open(TABLET_PORT) and port_open(PC_PORT):
            return
        time.sleep(2)


def set_demo_license(ctx: Context, plan: str) -> None:
    run(ctx, f"set demo license {plan}", [str(ops_cmd(ctx)), "--set-demo-license", plan])


def smoke_endpoint(ctx: Context, name: str, url: str, allowed: Iterable[int] = (200,)) -> tuple[int, str]:
    code, ctype, body = http_get(url)
    allowed_set = set(allowed)
    ok = code in allowed_set
    snippet = body.replace("\n", " ")[:600]
    ctx.add(name, ok, f"{code} {ctype} {url} body={snippet}")
    if not ok:
        raise RuntimeError(f"{name} expected {sorted(allowed_set)}, got {code}")
    return code, body


def live_smoke(ctx: Context, expect_dashboard: int = 200) -> None:
    smoke_endpoint(ctx, "Tablet health", "http://127.0.0.1:3120/api/health")
    smoke_endpoint(ctx, "Tablet license status", "http://127.0.0.1:3120/api/license/status")
    smoke_endpoint(ctx, "Tablet license features", "http://127.0.0.1:3120/api/license/features")
    smoke_endpoint(ctx, "Tablet refresh status", "http://127.0.0.1:3120/api/license/refresh/status")
    smoke_endpoint(ctx, "Tablet license page", "http://127.0.0.1:3120/settings/license")
    smoke_endpoint(ctx, "Tablet POS", "http://127.0.0.1:3120/pos")
    smoke_endpoint(ctx, "PC home", "http://127.0.0.1:3130/")
    smoke_endpoint(ctx, "PC license status", "http://127.0.0.1:3130/api/license/status")
    smoke_endpoint(ctx, "PC license features", "http://127.0.0.1:3130/api/license/features")
    smoke_endpoint(ctx, "PC refresh status", "http://127.0.0.1:3130/api/license/refresh/status")
    smoke_endpoint(ctx, "PC license page", "http://127.0.0.1:3130/settings/license")
    smoke_endpoint(ctx, "PC dashboard API", "http://127.0.0.1:3130/api/backoffice/dashboard", allowed=(expect_dashboard,))


def full_check(ctx: Context, ensure_running: bool) -> None:
    self_check(ctx)
    core_build_gates(ctx)
    set_demo_license(ctx, "TABLET_PC_REQUIRED")
    if ensure_running:
        start_dev_servers_if_needed(ctx)
    live_smoke(ctx, expect_dashboard=200)


def diagnose(ctx: Context, ensure_running: bool) -> None:
    self_check(ctx)
    if ensure_running:
        start_dev_servers_if_needed(ctx)
    for name, url in [
        ("Tablet license status", "http://127.0.0.1:3120/api/license/status"),
        ("Tablet refresh status", "http://127.0.0.1:3120/api/license/refresh/status"),
        ("PC license status", "http://127.0.0.1:3130/api/license/status"),
        ("PC refresh status", "http://127.0.0.1:3130/api/license/refresh/status"),
    ]:
        try:
            smoke_endpoint(ctx, name, url, allowed=(200,))
        except Exception as exc:
            ctx.add(name + " diagnostic", False, str(exc))


def plan_matrix(ctx: Context, ensure_running: bool) -> None:
    self_check(ctx)
    if ensure_running:
        start_dev_servers_if_needed(ctx)
    rows = []
    for plan, expected in PLAN_EXPECTATIONS.items():
        try:
            set_demo_license(ctx, plan)
            time.sleep(1)
            smoke_endpoint(ctx, f"{plan} status", "http://127.0.0.1:3120/api/license/status", allowed=(200,))
            smoke_endpoint(ctx, f"{plan} tablet POS", "http://127.0.0.1:3120/pos", allowed=(200,))
            dash_code, _ = smoke_endpoint(ctx, f"{plan} PC dashboard expectation", "http://127.0.0.1:3130/api/backoffice/dashboard", allowed=(expected["dashboard"],))
            rows.append({"plan": plan, "ok": True, "dashboard": dash_code})
        except Exception as exc:
            rows.append({"plan": plan, "ok": False, "error": str(exc)})
            ctx.add(f"{plan} matrix", False, str(exc))
    matrix_path = ctx.out_dir / f"terminal_venta_license_plan_matrix_{ctx.stamp}.json"
    matrix_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = all(r.get("ok") for r in rows)
    ctx.add("plan matrix artifact", ok, str(matrix_path))
    if not ok:
        raise RuntimeError(f"Plan matrix failed. See {matrix_path}")


def write_report(ctx: Context, verdict: str) -> None:
    lines = [
        "# PRISMA License Canonical Operations 04 Report",
        "",
        f"## Verdict: {verdict}",
        "",
        f"Root: `{ctx.root}`",
        f"Log: `{ctx.log_path}`",
        "",
        "## Results",
        "",
        "| Check | Result | Detail |",
        "|---|---:|---|",
    ]
    for r in ctx.results:
        mark = "OK" if r.ok else "FAIL"
        detail = (r.detail or "").replace("|", "\\|")[:1000]
        lines.append(f"| {r.name} | {mark} | {detail} |")
    lines += ["", "## Notes", "", "Refresh remoto puede permanecer disabled si no hay servidor configurado. Eso no bloquea la operación local firmada."]
    ctx.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.log(f"REPORT {ctx.report_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA canonical license operations 04")
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--full-check", action="store_true")
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--plan-matrix", action="store_true")
    parser.add_argument("--ensure-running", action="store_true")
    parser.add_argument("--set-demo-license", choices=list(PLAN_EXPECTATIONS), default=None)
    args = parser.parse_args()
    ctx = make_context(Path(args.root), Path(args.out_dir))
    try:
        if args.set_demo_license:
            set_demo_license(ctx, args.set_demo_license)
        if args.self_check:
            self_check(ctx)
        if args.full_check:
            full_check(ctx, ensure_running=args.ensure_running)
        if args.diagnose:
            diagnose(ctx, ensure_running=args.ensure_running)
        if args.plan_matrix:
            plan_matrix(ctx, ensure_running=args.ensure_running)
        if not any([args.set_demo_license, args.self_check, args.full_check, args.diagnose, args.plan_matrix]):
            self_check(ctx)
        write_report(ctx, "READY")
        ctx.log("FINAL READY")
        print(f"FINAL READY\nReport: {ctx.report_path}")
        return 0
    except Exception as exc:
        ctx.add("final", False, str(exc))
        write_report(ctx, "BLOCKED")
        ctx.log(f"FINAL BLOCKED: {exc}")
        print(f"FINAL BLOCKED\nReport: {ctx.report_path}\nError: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
