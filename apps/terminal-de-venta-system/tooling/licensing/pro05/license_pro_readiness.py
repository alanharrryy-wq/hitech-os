#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import py_compile
from pathlib import Path

PROJECT = "terminal_venta_license_pro05"
REQUIRED_04_FILES = [
    "tooling/licensing/prisma_license_canon_ops.py",
    "tooling/licensing/mock_license_server.py",
    "tooling/licensing/PRISMA_LICENSE_CANONICAL_OPS_04_MANIFEST.json",
    "docs/productization/PRISMA_LICENSE_CANONICAL_OPERATIONS_04.md",
    "terminal_de_venta.cmd",
]
REQUIRED_05_FILES = [
    "docs/productization/PRISMA_LICENSE_SYSTEM_PRO_ROADMAP_05.md",
    "docs/productization/PRISMA_LICENSE_SERVER_CONTRACT_05.md",
    "docs/productization/PRISMA_DEVICE_ACTIVATION_CONTRACT_05.md",
    "docs/productization/PRISMA_LICENSE_ADMIN_PORTAL_CONTRACT_05.md",
    "tooling/licensing/pro05/license_system_pro_contract.json",
    "tooling/licensing/pro05/license_e2e_matrix.json",
    "tooling/licensing/pro05/license_admin_portal_map.json",
    "tooling/licensing/pro05/license_pro_readiness.py",
]
CMD_04_MARKER = "PRISMA_LICENSE_CANONICAL_OPERATIONS_04_START"
CMD_05_MARKER = "PRISMA_LICENSE_SYSTEM_PRO_ROADMAP_05_START"

def default_out_dir() -> Path:
    return Path(r"F:\descargasf") if os.name == "nt" else Path("/mnt/data")

def stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")

def log_line(path: Path, msg: str) -> None:
    line = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(msg)

def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA License System Pro Roadmap 05 readiness gate")
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", default=str(default_out_dir()))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    s = stamp()
    log_path = out_dir / f"{PROJECT}_{s}.log"
    report_path = out_dir / f"{PROJECT}_report_{s}.md"
    results: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail))
        log_line(log_path, f"{'OK' if ok else 'FAIL'} {name} {detail}".rstrip())

    if not root.exists():
        add("root exists", False, str(root))
    else:
        add("root exists", True, str(root))

    for label, rels in [("04", REQUIRED_04_FILES), ("05", REQUIRED_05_FILES)]:
        for rel in rels:
            p = root / rel
            add(f"{label} file {rel}", p.exists(), str(p) if not p.exists() else "")

    terminal_cmd = root / "terminal_de_venta.cmd"
    cmd_text = terminal_cmd.read_text(encoding="utf-8", errors="replace") if terminal_cmd.exists() else ""
    add("04 command block marker", CMD_04_MARKER in cmd_text)
    add("05 command block marker", CMD_05_MARKER in cmd_text)
    add("license-full-check command", "license-full-check" in cmd_text)
    add("license-pro-readiness command", "license-pro-readiness" in cmd_text)

    for rel in [
        "tooling/licensing/pro05/license_system_pro_contract.json",
        "tooling/licensing/pro05/license_e2e_matrix.json",
        "tooling/licensing/pro05/license_admin_portal_map.json",
    ]:
        try:
            with (root / rel).open("r", encoding="utf-8") as fh:
                json.load(fh)
            add(f"json parse {rel}", True)
        except Exception as exc:
            add(f"json parse {rel}", False, str(exc))

    try:
        py_compile.compile(str(root / "tooling/licensing/pro05/license_pro_readiness.py"), doraise=True)
        add("py_compile license_pro_readiness", True)
    except Exception as exc:
        add("py_compile license_pro_readiness", False, str(exc))

    verdict = "READY" if all(x[1] for x in results) else "BLOCKED"
    lines = [
        "# PRISMA License System Pro Roadmap 05 Readiness Report",
        "",
        f"## Verdict: {verdict}",
        "",
        f"Root: `{root}`",
        f"Log: `{log_path}`",
        "",
        "| Check | Result | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in results:
        safe_detail = str(detail).replace("|", "\\|")
        lines.append(f"| {name} | {'OK' if ok else 'FAIL'} | {safe_detail} |")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log_line(log_path, f"REPORT {report_path}")
    log_line(log_path, f"FINAL {verdict}")
    print(f"FINAL {verdict}\nReport: {report_path}")
    return 0 if verdict == "READY" else 2

if __name__ == "__main__":
    raise SystemExit(main())
