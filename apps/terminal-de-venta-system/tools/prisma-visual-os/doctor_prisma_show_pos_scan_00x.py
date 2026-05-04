#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA_SHOW_POS_DOCTOR_SMART_00X.

Smarter Visual POS diagnostic doctor.
- Separates current failures from historical log noise.
- Parses JSON reports structurally instead of grepping old error strings blindly.
- Produces release verdicts, health score, action plan, and machine-readable gates.
- Does not mutate repo files.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

PACKAGE = "PRISMA_SHOW_POS_DOCTOR_SMART_00X"
VERSION = "20260504_v01"
DEFAULT_TARGET_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_OUT_DIR = Path(r"F:\descargasf")
TABLET_BASE = "http://127.0.0.1:3120"
REALTIME_BASE = "http://127.0.0.1:4177"

ERROR_PATTERNS = [
    "Build Error",
    "Internal Server Error",
    "Transforming CSS failed",
    "Unhandled Runtime Error",
    "Module not found",
    "Cannot find module",
    "SyntaxError",
    "TypeError",
    "ReferenceError",
    "EADDRINUSE",
    "ECONNREFUSED",
    "VERIFY FAILED",
    "500",
]

@dataclass
class Check:
    name: str
    ok: bool
    critical: bool = False
    detail: str = ""
    data: Any = None
    skipped: bool = False

@dataclass
class Report:
    package: str
    version: str
    createdAt: str
    runStartedAt: str
    targetRoot: str
    systemRoot: str
    tabletRoot: str
    log: str
    json: str
    mode: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    criticalFailures: list[dict[str, Any]] = field(default_factory=list)
    fragilePoints: list[dict[str, Any]] = field(default_factory=list)
    historicalSignals: list[dict[str, Any]] = field(default_factory=list)
    suppressedSignals: list[dict[str, Any]] = field(default_factory=list)
    started: list[dict[str, Any]] = field(default_factory=list)
    gates: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    releaseVerdict: str = "unknown"
    healthScore: int = 0
    status: str = "unknown"
    finishedAt: str | None = None

class Doctor:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.run_started = datetime.now(timezone.utc)
        self.stamp = datetime.now().strftime("%y%m%d_%H%M")
        self.target_root = Path(args.target_root).resolve()
        self.out_dir = Path(args.out_dir).resolve()
        self.system_root = self.target_root / "apps" / "terminal-de-venta-system"
        self.tablet_root = self.system_root / "products" / "tablet" / "app"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.out_dir / f"prisma_show_pos_doctor_smart_00x_{self.stamp}.log"
        self.json_path = self.out_dir / f"prisma_show_pos_doctor_smart_00x_{self.stamp}.json"
        self.log_path.write_text("", encoding="utf-8")
        self.report = Report(
            package=PACKAGE,
            version=VERSION,
            createdAt=datetime.now().isoformat(timespec="seconds"),
            runStartedAt=self.run_started.isoformat(),
            targetRoot=str(self.target_root),
            systemRoot=str(self.system_root),
            tabletRoot=str(self.tablet_root),
            log=str(self.log_path),
            json=str(self.json_path),
            mode=self.mode_name(),
        )
        self.node = self.find_tool(["node.exe", "node"])
        self.pnpm = self.find_tool(["pnpm.cmd", "pnpm"])
        self.git = self.find_tool(["git.exe", "git"])

    def mode_name(self) -> str:
        if self.args.self_check:
            return "self-check"
        if self.args.scan:
            return "scan"
        return "inspect"

    def log(self, msg: str) -> None:
        line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
        print(line)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def add_check(self, name: str, ok: bool, detail: str = "", data: Any = None, critical: bool = False, skipped: bool = False) -> None:
        row = Check(name=name, ok=ok, critical=critical, detail=detail, data=data, skipped=skipped).__dict__
        self.report.checks.append(row)
        if skipped:
            self.log(f"SKIP {'CRIT ' if critical else ''}{name}: {detail}")
            return
        if not ok and critical:
            self.report.criticalFailures.append(row)
        elif not ok:
            self.report.warnings.append(row)
        self.log(f"{'OK' if ok else 'FAIL'} {'CRIT ' if critical else ''}{name}: {detail}")

    def add_fragile(self, name: str, detail: str, data: Any = None) -> None:
        row = {"name": name, "detail": detail, "data": data}
        self.report.fragilePoints.append(row)
        self.log(f"FRAGILE {name}: {detail}")

    def add_historical(self, name: str, detail: str, data: Any = None) -> None:
        row = {"name": name, "detail": detail, "data": data}
        self.report.historicalSignals.append(row)
        self.log(f"HISTORY {name}: {detail}")

    def add_suppressed(self, name: str, detail: str, data: Any = None) -> None:
        row = {"name": name, "detail": detail, "data": data}
        self.report.suppressedSignals.append(row)
        self.log(f"SUPPRESS {name}: {detail}")

    def find_tool(self, names: list[str]) -> str | None:
        for n in names:
            p = shutil.which(n)
            if p:
                return p
        return None

    def save_report(self) -> None:
        self.report.finishedAt = datetime.now().isoformat(timespec="seconds")
        self.compute_verdict()
        self.json_path.write_text(json.dumps(self.report.__dict__, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"JSON {self.json_path}")

    def compute_verdict(self) -> None:
        critical_count = len(self.report.criticalFailures)
        warning_count = len(self.report.warnings)
        fragile_count = len(self.report.fragilePoints)
        score = 100 - critical_count * 35 - warning_count * 8 - fragile_count * 4
        score = max(0, min(100, score))
        self.report.healthScore = score
        if critical_count:
            verdict = "blocked"
            status = "blocked"
        elif warning_count or fragile_count:
            verdict = "ready_with_warnings"
            status = "ready_with_warnings"
        else:
            verdict = "ready"
            status = "ready"
        self.report.releaseVerdict = verdict
        self.report.status = status
        if critical_count:
            self.report.recommendations.append("No cerrar release: primero atender criticalFailures.")
        elif warning_count or fragile_count:
            self.report.recommendations.append("Base operable. Revisar warnings/fragilePoints si se va a cerrar release final.")
        else:
            self.report.recommendations.append("Base lista: sin fallas criticas, warnings ni fragilidad activa detectada.")
        if self.report.historicalSignals and not self.report.warnings:
            self.report.recommendations.append("Los errores historicos fueron clasificados como historial y no bloquean el estado actual.")

    def http_text(self, url: str, timeout: int = 10) -> dict[str, Any]:
        req = urllib.request.Request(url, headers={"Accept": "text/html,application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
            return {"status": r.status, "contentType": r.headers.get("content-type", ""), "text": text}

    def http_json(self, url: str, timeout: int = 10) -> dict[str, Any]:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "json": json.loads(r.read().decode("utf-8", errors="replace"))}

    def post_json(self, url: str, payload: dict[str, Any], timeout: int = 10) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "json": json.loads(r.read().decode("utf-8", errors="replace"))}

    def run_cmd(self, name: str, cmd: list[str], cwd: Path, timeout: int = 45, critical: bool = False) -> dict[str, Any] | None:
        if not cmd[0]:
            self.add_check(name, False, "missing executable", critical=critical)
            return None
        try:
            self.log("RUN " + " ".join(cmd))
            cp = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout, shell=False)
            data = {
                "cmd": cmd,
                "cwd": str(cwd),
                "exitCode": cp.returncode,
                "stdoutTail": cp.stdout[-6000:],
                "stderrTail": cp.stderr[-6000:],
            }
            self.add_check(name, cp.returncode == 0, f"exit={cp.returncode}", data, critical=critical)
            return data
        except Exception as exc:
            self.add_check(name, False, str(exc), critical=critical)
            return None

    def file_exists(self, name: str, path: Path, critical: bool = False) -> bool:
        ok = path.exists()
        self.add_check(name, ok, str(path), critical=critical)
        return ok

    def scan_text(self, name: str, path: Path, must: list[str], must_not: list[str], critical: bool = False) -> None:
        if not path.exists():
            self.add_check(name, False, f"missing {path}", critical=critical)
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            missing = [m for m in must if m not in text]
            forbidden = [m for m in must_not if m in text]
            data = {"path": str(path), "length": len(text), "missing": missing, "presentForbidden": forbidden}
            ok = not missing and not forbidden
            self.add_check(name, ok, str(path), data, critical=critical)
        except Exception as exc:
            self.add_check(name, False, str(exc), critical=critical)

    def get_port_owner(self, port: int) -> dict[str, Any]:
        ps = f"""
$ErrorActionPreference='SilentlyContinue'
$conn = Get-NetTCPConnection -LocalPort {port} -State Listen | Select-Object -First 1
if ($conn) {{
  $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $($conn.OwningProcess)"
  [pscustomobject]@{{ Port={port}; Listening=$true; Pid=$conn.OwningProcess; CommandLine=$proc.CommandLine }} | ConvertTo-Json -Compress
}} else {{
  [pscustomobject]@{{ Port={port}; Listening=$false; Pid=$null; CommandLine=$null }} | ConvertTo-Json -Compress
}}
"""
        try:
            cp = subprocess.run(["powershell", "-NoProfile", "-Command", ps], text=True, capture_output=True, timeout=10)
            return json.loads(cp.stdout.strip())
        except Exception as exc:
            return {"Port": port, "Listening": False, "Pid": None, "CommandLine": None, "error": str(exc)}

    def start_process_logged(self, name: str, file: str, args: list[str], cwd: Path) -> None:
        out = self.out_dir / f"prisma_doctor_00x_{name}_{self.stamp}.out.log"
        err = self.out_dir / f"prisma_doctor_00x_{name}_{self.stamp}.err.log"
        try:
            with out.open("w", encoding="utf-8") as fo, err.open("w", encoding="utf-8") as fe:
                p = subprocess.Popen([file] + args, cwd=str(cwd), stdout=fo, stderr=fe, shell=False)
            row = {"name": name, "pid": p.pid, "stdout": str(out), "stderr": str(err)}
            self.report.started.append(row)
            self.add_check(f"start {name}", True, f"pid={p.pid}", row)
        except Exception as exc:
            self.add_check(f"start {name}", False, str(exc), critical=True)

    def wait_http(self, url: str, seconds: int = 80) -> bool:
        deadline = time.time() + seconds
        while time.time() < deadline:
            try:
                r = self.http_text(url, timeout=8)
                if 200 <= int(r["status"]) < 500:
                    return True
            except Exception:
                time.sleep(2)
        return False

    def self_check(self) -> None:
        self.log(f"START {PACKAGE} self-check")
        self.add_check("doctor package marker", True, PACKAGE, critical=True)
        self.add_check("python version", True, sys.version, critical=True)
        self.file_exists("target root", self.target_root, critical=True)
        self.file_exists("system root", self.system_root, critical=True)
        self.file_exists("tablet root", self.tablet_root, critical=True)
        self.file_exists("doctor file", Path(__file__), critical=True)

    def scan_structure(self) -> None:
        self.add_check("tool node", bool(self.node), self.node or "missing", critical=True)
        self.add_check("tool pnpm", bool(self.pnpm), self.pnpm or "missing", critical=True)
        self.add_check("tool git", bool(self.git), self.git or "missing")
        if self.node:
            self.run_cmd("node version", [self.node, "--version"], self.target_root, timeout=10)
        if self.pnpm:
            self.run_cmd("pnpm version", [self.pnpm, "--version"], self.target_root, timeout=10)

        paths = {
            "repo root": self.target_root,
            "terminal system root": self.system_root,
            "tablet app root": self.tablet_root,
            "terminal cmd": self.system_root / "terminal_de_venta.cmd",
            "tablet package json": self.tablet_root / "package.json",
            "pos screen": self.tablet_root / "components/pos/pos-screen.tsx",
            "pos ticket panel": self.tablet_root / "components/pos/pos-ticket-panel.tsx",
            "pos binding": self.tablet_root / "components/pos/pos-live-binding.tsx",
            "pos css": self.tablet_root / "components/pos/pos.module.css",
            "doctor 00X installed": self.system_root / "tools/prisma-visual-os/doctor_prisma_show_pos_scan_00x.py",
            "doctor 00X launcher": self.system_root / "tools/prisma-visual-os/run_prisma_show_pos_doctor_00x.cmd",
            "doctor canonical launcher": self.system_root / "tools/prisma-visual-os/run_prisma_show_pos_doctor.cmd",
            "verify doctor 00X": self.system_root / "tools/prisma-visual-os/verify_prisma_show_pos_doctor_00x.mjs",
            "visual realtime server": self.system_root / "tools/prisma-visual-os/live-preview-server-00q.mjs",
            "verify 00T": self.system_root / "tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs",
            "verify readme 00W": self.system_root / "tools/prisma-visual-os/verify_prisma_visual_os_readme_status_00w.mjs",
            "architecture doc": self.system_root / "docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md",
            "pos golden flow": self.system_root / "docs/pos/PRISMA_POS_GOLDEN_FLOW_01.md",
        }
        for n, p in paths.items():
            self.file_exists(n, p, critical=n in {"repo root", "terminal system root", "tablet app root", "pos binding", "pos css", "doctor 00X installed", "verify doctor 00X"})

        self.scan_text(
            "00T binding safe",
            self.tablet_root / "components/pos/pos-live-binding.tsx",
            ["new EventSource", "prisma.visual.controls", "setProperty", "data-prisma-pos-live-badge", "export default PosLiveBinding"],
            ["applyFallbackVars()", "POS_POS500_AUTOFIX_BOMB_TEST_00T"],
            critical=True,
        )
        self.scan_text(
            "00T css no-layout markers",
            self.tablet_root / "components/pos/pos.module.css",
            ["PRISMA 00T SAFE NO-LAYOUT LIVE MARKER"],
            ["PRISMA 00T POS500 SAFE LIVE POS MAPPING", "PRISMA 00T AUTOPILOT HARD GLOBAL POS MAPPING", "PRISMA 00T HARD LIVE POS MAPPING", "FORCE VISIBLE LIVE POS MAPPING", "posWorkspace[data-prisma-pos-live=\"00T\"]", ".posLiveBadge"],
            critical=True,
        )

    def scan_runtime(self) -> None:
        if self.args.skip_runtime:
            self.add_check("runtime probes", True, "skipped by --skip-runtime", skipped=True)
            return
        owner3120 = self.get_port_owner(3120)
        owner4177 = self.get_port_owner(4177)
        self.add_check("port 3120 owner", True, "checked", owner3120)
        self.add_check("port 4177 owner", True, "checked", owner4177)

        if self.args.start_missing:
            if not owner4177.get("Listening") and self.node:
                server = self.system_root / "tools/prisma-visual-os/live-preview-server-00q.mjs"
                if server.exists():
                    self.start_process_logged("realtime", self.node, [str(server), "--port", "4177"], self.system_root)
                    self.wait_http(f"{REALTIME_BASE}/health", 35)
            if not owner3120.get("Listening") and self.pnpm:
                self.start_process_logged("tablet", self.pnpm, ["-C", str(self.tablet_root), "dev"], self.target_root)
                self.wait_http(f"{TABLET_BASE}/pos", 90)

        try:
            h = self.http_json(f"{REALTIME_BASE}/health", timeout=8)
            self.add_check("realtime health", 200 <= h["status"] < 400 and h["json"].get("ok") is True, f"status={h['status']}", h, critical=True)
        except Exception as exc:
            self.add_check("realtime health", False, str(exc), critical=True)
        try:
            st = self.http_json(f"{REALTIME_BASE}/state", timeout=8)
            self.add_check("realtime state", 200 <= st["status"] < 400, f"status={st['status']}", st)
        except Exception as exc:
            self.add_check("realtime state", False, str(exc))

        for route, crit in [("/pos", True), ("/visual-os", False), ("/visual-os/pro", True), ("/visual-os/realtime", False)]:
            try:
                r = self.http_text(f"{TABLET_BASE}{route}", timeout=14)
                text = r["text"]
                build_error = any(s in text for s in ["Build Error", "Internal Server Error", "Transforming CSS failed", "Unhandled Runtime Error"])
                data = {"url": f"{TABLET_BASE}{route}", "status": r["status"], "contentType": r["contentType"], "buildError": build_error, "hasCobrar": "COBRAR" in text or "Cobrar" in text or "cobrar" in text, "hasTocar": "Tocar" in text, "has00T": "00T" in text, "snippet": text[:700]}
                ok = 200 <= int(r["status"]) < 400 and not build_error
                self.add_check(f"route {route}", ok, f"status={r['status']}", data, critical=crit)
            except Exception as exc:
                self.add_check(f"route {route}", False, str(exc), critical=crit)

        if self.args.broadcast_neutral:
            payload = {
                "type": "prisma.visual.controls",
                "sourceClientId": "doctor-smart-00x",
                "surface": "tablet_pos",
                "recipeName": "POS_DOCTOR_SMART_00X_NEUTRAL_NO_LAYOUT",
                "liveEnabled": True,
                "debugLayers": False,
                "mode": "doctor-smart-neutral-no-layout",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "cssVars": {
                    "--prisma-live-glass": "0",
                    "--prisma-live-blur": "0px",
                    "--prisma-live-panel-alpha": "1",
                    "--prisma-live-glow": "none",
                    "--prisma-live-neon": "none",
                    "--prisma-live-depth": "0",
                    "--prisma-live-contrast": "0",
                    "--prisma-live-density": "0",
                    "--prisma-live-motion": "0",
                    "--prisma-live-radius": "0px",
                    "--prisma-live-shadow": "none",
                    "--prisma-live-saturation": "100%",
                    "--prisma-live-shine": "0",
                    "--prisma-live-grain": "0",
                    "--prisma-live-edge": "transparent",
                },
                "score": {"overall": 0, "verdict": "doctor_smart_neutral_no_layout"},
            }
            try:
                post = self.post_json(f"{REALTIME_BASE}/broadcast", payload, timeout=10)
                state = self.http_json(f"{REALTIME_BASE}/state", timeout=10)
                ok = state.get("json", {}).get("lastPayload", {}).get("recipeName") == "POS_DOCTOR_SMART_00X_NEUTRAL_NO_LAYOUT"
                self.add_check("broadcast neutral no-layout", ok, "POST /broadcast + GET /state", {"post": post, "state": state})
            except Exception as exc:
                self.add_check("broadcast neutral no-layout", False, str(exc))

    def run_verifiers(self) -> None:
        if not self.node:
            self.add_check("node verifiers", False, "node missing", critical=True)
            return
        verifiers: list[tuple[str, Path, bool]] = [
            ("verify doctor 00X", self.system_root / "tools/prisma-visual-os/verify_prisma_show_pos_doctor_00x.mjs", True),
            ("verify doctor 00U", self.system_root / "tools/prisma-visual-os/verify_prisma_show_pos_doctor_00u.mjs", False),
            ("verify readme 00W", self.system_root / "tools/prisma-visual-os/verify_prisma_visual_os_readme_status_00w.mjs", False),
            ("verify 00T", self.system_root / "tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs", True),
            ("verify 00R 00S", self.system_root / "tools/prisma-visual-os/verify_prisma_visual_os_studio_pro_qa_00r_00s.mjs", False),
            ("verify tablet pos light 00Q", self.tablet_root / "tools/verify_prisma_tablet_pos_light_operational_00q.mjs", False),
            ("verify checkout 00R", self.tablet_root / "tools/verify_prisma_tablet_pos_real_checkout_flow_00r.mjs", False),
            ("verify checkout shift 00S", self.tablet_root / "tools/verify_prisma_tablet_pos_checkout_shift_autofix_00s.mjs", False),
            ("verify hold carts 04G", self.tablet_root / "tools/verify_pos_golden_flow_hold_carts_04g.mjs", False),
            ("verify touch only 04H", self.tablet_root / "tools/verify_pos_touch_only_actions_04h.mjs", False),
        ]
        for name, path, crit in verifiers:
            if path.exists():
                self.run_cmd(name, [self.node, str(path)], self.system_root, timeout=55, critical=crit)
            else:
                self.add_check(name, True, f"not installed: {path}", skipped=True)
        score = self.system_root / "tools/prisma-visual-os/score_prisma_studio_pro_00s.mjs"
        recipe = self.system_root / "config/prisma-visual-os/recipes/CRYSTAL_POS_ANGEL_LIVE_v01.json"
        if score.exists() and recipe.exists():
            self.run_cmd("score crystal recipe", [self.node, str(score), str(recipe)], self.system_root, timeout=40)

    def classify_json_report(self, path: Path, mtime: datetime) -> dict[str, Any] | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return None
        status = data.get("status") or data.get("releaseVerdict") or "unknown"
        criticals = data.get("criticalFailures") or []
        warnings = data.get("warnings") or []
        package = data.get("package", "unknown")
        active_window = self.run_started - timedelta(minutes=self.args.active_log_grace_minutes)
        is_current_window = mtime >= active_window
        is_current_doctor = str(path) == str(self.json_path)
        if criticals:
            return {"kind": "active" if is_current_window else "historical", "reason": "json criticalFailures", "package": package, "status": status, "criticalFailures": len(criticals), "warnings": len(warnings)}
        if status in {"ready", "ok", "READY"}:
            return {"kind": "suppressed", "reason": "structured JSON ready despite embedded old strings", "package": package, "status": status}
        if status == "ready_with_warnings":
            kind = "active" if (is_current_window or is_current_doctor) else "historical"
            return {"kind": kind, "reason": "structured JSON ready_with_warnings", "package": package, "status": status, "warnings": len(warnings)}
        return None

    def scan_logs_smart(self) -> None:
        if not self.out_dir.exists():
            self.add_check("smart log scan", True, "out dir missing, nothing to scan")
            return
        max_files = int(self.args.max_log_files)
        files = [p for p in self.out_dir.iterdir() if p.is_file() and p.suffix.lower() in {".log", ".json", ".err", ".out"}]
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        files = files[:max_files]
        active = []
        historical = []
        suppressed = []
        for p in files:
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
                text = p.read_text(encoding="utf-8", errors="replace")[-20000:]
            except Exception:
                continue
            json_class = self.classify_json_report(p, mtime) if p.suffix.lower() == ".json" else None
            if json_class:
                item = {"file": str(p), "mtime": mtime.isoformat(), **json_class}
                if json_class["kind"] == "active":
                    active.append(item)
                elif json_class["kind"] == "historical":
                    historical.append(item)
                else:
                    suppressed.append(item)
                continue
            hits = [pat for pat in ERROR_PATTERNS if pat in text]
            if not hits:
                continue
            active_window = self.run_started - timedelta(minutes=self.args.active_log_grace_minutes)
            item = {"file": str(p), "mtime": mtime.isoformat(), "patterns": hits[:12]}
            if mtime >= active_window:
                active.append(item)
            else:
                historical.append(item)
        self.add_check("smart log scan", len(active) == 0, f"active={len(active)} historical={len(historical)} suppressed={len(suppressed)}", {"active": active[:20], "historicalCount": len(historical), "suppressedCount": len(suppressed)}, critical=False)
        if active:
            self.add_fragile("active log signals", "New/current logs contain failure strings or structured warnings.", active[:12])
        if historical:
            self.add_historical("historical log signals", "Old logs contain failures but are not counted against current runtime.", historical[:12])
        for item in suppressed[:12]:
            self.add_suppressed("structured report noise", "JSON report was ready; embedded historical strings ignored.", item)

    def build_gates(self) -> None:
        gate_names = {
            "runtime_pos": ["route /pos"],
            "runtime_visual_os": ["route /visual-os/pro", "realtime health"],
            "safe_no_layout": ["scan 00T binding", "scan 00T css no-layout markers", "verify 00T"],
            "doctor": ["verify doctor 00X"],
            "touch_pos": ["verify touch only 04H"],
        }
        gates: dict[str, Any] = {}
        for gate, names in gate_names.items():
            rows = [c for c in self.report.checks if c["name"] in names]
            ok = bool(rows) and all(r.get("ok") or r.get("skipped") for r in rows)
            gates[gate] = {"ok": ok, "checks": rows}
        self.report.gates = gates

    def run(self) -> int:
        try:
            self.log(f"START {PACKAGE} {VERSION} mode={self.mode_name()}")
            if self.args.self_check:
                self.self_check()
                self.save_report()
                return 0 if not self.report.criticalFailures else 2
            self.scan_structure()
            if self.args.scan:
                self.scan_runtime()
                self.run_verifiers()
                self.scan_logs_smart()
            self.build_gates()
            self.save_report()
            if self.report.criticalFailures:
                return 2
            if self.report.warnings or self.report.fragilePoints:
                return 1
            return 0
        except Exception as exc:
            self.add_check("fatal", False, str(exc), critical=True)
            self.save_report()
            return 99

def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="PRISMA smart Visual POS diagnostic doctor 00X")
    ap.add_argument("--target-root", default=str(DEFAULT_TARGET_ROOT), help="Repo root, default F:\\repos\\hitech-os")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output dir for logs/reports, default F:\\descargasf")
    ap.add_argument("--self-check", action="store_true", help="Verify doctor can resolve paths and write report")
    ap.add_argument("--scan", action="store_true", help="Run full smart scan")
    ap.add_argument("--start-missing", action="store_true", help="Start missing Tablet/realtime services if ports are closed")
    ap.add_argument("--skip-runtime", action="store_true", help="Skip HTTP route/runtime probes")
    ap.add_argument("--broadcast-neutral", action="store_true", default=True, help="Broadcast neutral no-layout payload during runtime scan")
    ap.add_argument("--no-broadcast-neutral", action="store_false", dest="broadcast_neutral", help="Do not broadcast neutral payload")
    ap.add_argument("--active-log-grace-minutes", type=int, default=3, help="Only logs newer than run start minus this grace are active")
    ap.add_argument("--max-log-files", type=int, default=80, help="Max recent output files to inspect")
    return ap.parse_args(argv)

if __name__ == "__main__":
    raise SystemExit(Doctor(parse_args(sys.argv[1:])).run())
