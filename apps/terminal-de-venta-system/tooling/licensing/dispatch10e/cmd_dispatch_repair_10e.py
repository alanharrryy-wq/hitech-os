#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, os, re, subprocess, sys
from pathlib import Path
from typing import Sequence

PACKAGE = "PRISMA_LICENSE_CMD_DISPATCH_REPAIR_10E"
VERSION = "10.0.5"
START = "rem PRISMA_LICENSE_CMD_DISPATCH_REPAIR_10E_START"
END = "rem PRISMA_LICENSE_CMD_DISPATCH_REPAIR_10E_END"
DEFAULT_OUT = Path("F:/descargasf")
CRITICAL = ["license-signature-verify-fixture", "license-private-key-smoke", "license-signature-smoke"]
REQUIRED_COMMANDS = [
    "license-signature-policy", "license-signature-registry", "license-signature-audit",
    "license-signature-verify-fixture", "license-signature-env-smoke", "license-signature-smoke",
    "license-signature-contract", "license-signature-scan", "license-signature-scan-smoke",
    "license-signature-scan-rules", "license-private-key-scan", "license-private-key-audit",
    "license-private-key-quarantine", "license-private-key-generate-dev", "license-private-key-smoke",
    "license-private-key-contract", "license-dispatch-analyze", "license-dispatch-smoke", "license-dispatch-contract"
]

def now_tag(): return dt.datetime.now().strftime("%y%m%d_%H%M")
def root_from(v): return Path(v).expanduser().resolve() if v else Path.cwd().resolve()
def out_from(v):
    p = Path(v).expanduser().resolve() if v else DEFAULT_OUT
    try: p.mkdir(parents=True, exist_ok=True); return p
    except Exception:
        f = Path.cwd() / "local-runtime" / "reports"; f.mkdir(parents=True, exist_ok=True); return f

def cmd_file(root: Path) -> Path: return root / "terminal_de_venta.cmd"
def read_cmd(root: Path) -> str: return cmd_file(root).read_text(encoding="utf-8", errors="ignore")

def line_no(text: str, token: str):
    i = text.lower().find(token.lower())
    return None if i < 0 else text.count("\n", 0, i) + 1

def analyze_text(text: str):
    findings = []
    if START not in text or END not in text:
        findings.append(("error", "missing_10e_block", "10E direct dispatch block is missing", None, None))
    goto = line_no(text, "goto unknown")
    unknown = line_no(text, ":unknown")
    if goto and not unknown:
        findings.append(("error", "missing_unknown_label", "goto unknown exists but :unknown label is missing", None, goto))
    goto_guard = goto or 10**9
    for cmd in REQUIRED_COMMANDS:
        ln = line_no(text, '"%~1"=="' + cmd + '"')
        if ln is None:
            findings.append(("error", "missing_command_dispatch", "missing dispatcher", cmd, None))
        elif ln > goto_guard:
            findings.append(("error", "unreachable_command_dispatch", "dispatcher appears after goto unknown", cmd, ln))
    if "private_key_quarantine_10d.py" in text and "license-private-key-smoke" in text:
        if not re.search(r'private_key_quarantine_10d\.py"\s+--root\s+"%~dp0\."\s+--out\s+"F:\\\\descargasf"\s+smoke', text, re.I):
            findings.append(("error", "private_key_smoke_missing_subcommand", "private-key smoke must pass smoke subcommand", "license-private-key-smoke", None))
    return findings

def report(root, out, name, findings, smoke=None):
    smoke = smoke or []
    blocked = any(f[0] == "error" for f in findings) or any(x[1] != 0 for x in smoke)
    lines = ["# PRISMA CMD Dispatch Repair 10E Report", "", f"Package: `{PACKAGE}`", f"Version: `{VERSION}`", f"Root: `{root}`", f"Status: `{'BLOCKED' if blocked else 'FINAL READY'}`", "", "## Static analysis"]
    if findings:
        for sev, code, msg, cmd, ln in findings:
            bits = [f"- {sev.upper()} `{code}`"]
            if cmd: bits.append(f"command `{cmd}`")
            if ln: bits.append(f"line `{ln}`")
            bits.append(msg)
            lines.append(" :: ".join(bits))
    else:
        lines.append("- OK: dispatch commands are reachable before legacy fallback.")
    if smoke:
        lines += ["", "## Runtime smoke"]
        for c, code, tail in smoke:
            lines.append(f"- `{c}`: `{'OK' if code == 0 else 'FAIL'}` exit=`{code}` tail=`{tail}`")
    p = out / f"terminal_venta_cmd_dispatch_10e_{name}_{now_tag()}.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p, blocked

def print_findings(findings):
    if not findings:
        print("OK dispatch analysis clean")
    for sev, code, msg, cmd, ln in findings:
        extra = (f" command={cmd}" if cmd else "") + (f" line={ln}" if ln else "")
        print(f"{sev.upper()} {code}{extra} :: {msg}")

def run_cmd(root: Path, command: str, timeout: int):
    if os.name == "nt":
        proc = subprocess.run(["cmd.exe", "/c", str(cmd_file(root)), command], cwd=str(root), capture_output=True, text=True, timeout=timeout)
        text = (proc.stdout or "") + (proc.stderr or "")
        tail = " | ".join([x.strip() for x in text.splitlines()[-8:] if x.strip()])[:900]
        return proc.returncode, tail
    return 0, "SKIPPED non-Windows"

def cmd_analyze(args):
    root, out = root_from(args.root), out_from(args.out)
    findings = analyze_text(read_cmd(root))
    print_findings(findings)
    p, blocked = report(root, out, "analyze", findings)
    print(f"REPORT {p}")
    print("BLOCKED" if blocked else "FINAL READY")
    return 2 if blocked else 0

def cmd_smoke(args):
    root, out = root_from(args.root), out_from(args.out)
    findings = analyze_text(read_cmd(root))
    smoke = []
    if args.runtime:
        for c in CRITICAL:
            code, tail = run_cmd(root, c, args.timeout)
            print(f"{c}: {'OK' if code == 0 else 'FAIL'} exit={code} {tail}")
            smoke.append((c, code, tail))
    else:
        print("Runtime smoke skipped. Use --runtime.")
    p, blocked = report(root, out, "smoke", findings, smoke)
    print(f"REPORT {p}")
    print("BLOCKED" if blocked else "FINAL READY")
    return 2 if blocked else 0

def cmd_contract(args):
    print(json.dumps({"schemaVersion":"10E.cmd-dispatch-repair.v1","package":PACKAGE,"version":VERSION,"criticalRuntimeSmoke":CRITICAL,"commands":REQUIRED_COMMANDS}, indent=2, ensure_ascii=False))
    return 0

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["analyze", "smoke", "contract"])
    p.add_argument("--root", default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--runtime", action="store_true")
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args(argv)
    try:
        if args.command == "analyze": return cmd_analyze(args)
        if args.command == "smoke": return cmd_smoke(args)
        if args.command == "contract": return cmd_contract(args)
    except subprocess.TimeoutExpired as exc:
        print(f"ERROR timeout: {exc}", file=sys.stderr); return 1
    except Exception as exc:
        print(f"ERROR {type(exc).__name__}: {exc}", file=sys.stderr); return 1
    return 1
if __name__ == "__main__": raise SystemExit(main())
