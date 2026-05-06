from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE = "PRISMA_SHOW_POS_DOCTOR_00U"
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


def now_stamp() -> str:
    return datetime.now().strftime("%y%m%d_%H%M")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Doctor:
    def __init__(self, target_root: Path, out_dir: Path, strict: bool = False) -> None:
        self.target_root = target_root
        self.system_root = target_root / "apps" / "terminal-de-venta-system"
        self.tablet_root = self.system_root / "products" / "tablet" / "app"
        self.out_dir = out_dir
        self.strict = strict
        self.stamp = now_stamp()
        self.log_path = out_dir / f"prisma_show_pos_doctor_00u_{self.stamp}.log"
        self.json_path = out_dir / f"prisma_show_pos_doctor_00u_{self.stamp}.json"
        self.report: dict[str, Any] = {
            "package": PACKAGE,
            "version": VERSION,
            "createdAt": datetime.now().isoformat(timespec="seconds"),
            "targetRoot": str(target_root),
            "systemRoot": str(self.system_root),
            "tabletRoot": str(self.tablet_root),
            "log": str(self.log_path),
            "json": str(self.json_path),
            "started": [],
            "checks": [],
            "warnings": [],
            "criticalFailures": [],
            "fragilePoints": [],
            "recommendations": [],
            "status": "running",
        }

    def ensure_out_dir(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def log(self, message: str) -> None:
        line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
        print(line)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def add_check(
        self,
        name: str,
        ok: bool,
        detail: str = "",
        data: Any = None,
        critical: bool = False,
    ) -> None:
        row = {
            "name": name,
            "ok": bool(ok),
            "critical": bool(critical),
            "detail": detail,
            "data": data,
        }
        self.report["checks"].append(row)
        prefix = "OK" if ok else "FAIL"
        self.log(f"{prefix} {'CRIT ' if critical else ''}{name}: {detail}")
        if not ok:
            if critical:
                self.report["criticalFailures"].append(row)
            else:
                self.report["warnings"].append(row)

    def add_fragile(self, name: str, detail: str, data: Any = None) -> None:
        row = {"name": name, "detail": detail, "data": data}
        self.report["fragilePoints"].append(row)
        self.log(f"FRAGILE {name}: {detail}")

    def add_recommendation(self, text: str) -> None:
        self.report["recommendations"].append(text)
        self.log(f"RECOMMENDATION {text}")

    def save_report(self) -> None:
        self.json_path.write_text(json.dumps(self.report, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"JSON {self.json_path}")

    def path(self, *parts: str) -> Path:
        return self.system_root.joinpath(*parts)

    def tablet_path(self, *parts: str) -> Path:
        return self.tablet_root.joinpath(*parts)

    def find_tool(self, names: list[str]) -> str | None:
        for name in names:
            found = shutil.which(name)
            if found:
                return found
        return None

    def run(self, name: str, cmd: list[str], cwd: Path, timeout: int = 45, critical: bool = False) -> dict[str, Any]:
        self.log("RUN " + " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                text=True,
                capture_output=True,
                timeout=timeout,
                shell=False,
            )
            data = {
                "cmd": cmd,
                "cwd": str(cwd),
                "exitCode": proc.returncode,
                "stdoutTail": proc.stdout[-5000:],
                "stderrTail": proc.stderr[-5000:],
            }
            self.add_check(name, proc.returncode == 0, f"exit={proc.returncode}", data, critical=critical)
            return data
        except Exception as exc:
            data = {"cmd": cmd, "cwd": str(cwd), "error": str(exc)}
            self.add_check(name, False, str(exc), data, critical=critical)
            return data

    def http_text(self, url: str, timeout: int = 8) -> dict[str, Any]:
        req = urllib.request.Request(url, headers={"Accept": "text/html,application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return {
                "status": response.status,
                "contentType": response.headers.get("content-type", ""),
                "text": text,
            }

    def http_json(self, url: str, timeout: int = 8) -> dict[str, Any]:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return {"status": response.status, "json": json.loads(text)}

    def post_json(self, url: str, payload: dict[str, Any], timeout: int = 8) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return {"status": response.status, "json": json.loads(text)}

    def wait_http(self, url: str, seconds: int = 80) -> bool:
        deadline = time.time() + seconds
        last = None
        while time.time() < deadline:
            try:
                result = self.http_text(url, timeout=8)
                if 200 <= int(result["status"]) < 500:
                    return True
            except Exception as exc:
                last = str(exc)
            time.sleep(2)
        self.log(f"WAIT FAIL {url}: {last}")
        return False

    def get_port_owner(self, port: int) -> dict[str, Any]:
        if os.name != "nt":
            return {"Port": port, "Listening": None, "Pid": None, "CommandLine": None, "note": "non-windows"}
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
            cp = subprocess.run(["powershell", "-NoProfile", "-Command", ps], text=True, capture_output=True, timeout=12)
            return json.loads(cp.stdout.strip())
        except Exception as exc:
            return {"Port": port, "Listening": False, "Pid": None, "CommandLine": None, "error": str(exc)}

    def start_process_logged(self, name: str, file_path: str, args: list[str], cwd: Path) -> None:
        out = self.out_dir / f"prisma_show_pos_doctor_00u_{name}_{self.stamp}.out.log"
        err = self.out_dir / f"prisma_show_pos_doctor_00u_{name}_{self.stamp}.err.log"
        try:
            with out.open("w", encoding="utf-8") as stdout, err.open("w", encoding="utf-8") as stderr:
                proc = subprocess.Popen([file_path, *args], cwd=str(cwd), stdout=stdout, stderr=stderr, shell=False)
            row = {"name": name, "pid": proc.pid, "stdout": str(out), "stderr": str(err)}
            self.report["started"].append(row)
            self.add_check(f"start {name}", True, f"pid={proc.pid}", row)
        except Exception as exc:
            self.add_check(f"start {name}", False, str(exc), critical=True)

    def check_file(self, name: str, path: Path, critical: bool = True) -> bool:
        exists = path.exists()
        self.add_check(name, exists, str(path), critical=critical)
        return exists

    def scan_file(self, name: str, path: Path, must: list[str], forbidden: list[str], critical: bool = True) -> None:
        if not path.exists():
            self.add_check(f"scan {name}", False, f"missing {path}", critical=critical)
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [m for m in must if m not in text]
        present = [m for m in forbidden if m in text]
        ok = not missing and not present
        data = {"path": str(path), "length": len(text), "missing": missing, "presentForbidden": present}
        self.add_check(f"scan {name}", ok, str(path), data, critical=critical)
        for item in missing:
            self.add_fragile(f"{name} missing marker", item, {"path": str(path)})
        for item in present:
            self.add_fragile(f"{name} forbidden marker present", item, {"path": str(path)})

    def probe_route(self, name: str, url: str, critical: bool) -> None:
        try:
            result = self.http_text(url, timeout=14)
            text = result["text"]
            build_error = any(pattern in text for pattern in ["Build Error", "Internal Server Error", "Transforming CSS failed", "Unhandled Runtime Error"])
            data = {
                "url": url,
                "status": result["status"],
                "contentType": result["contentType"],
                "buildError": build_error,
                "hasCobrar": any(word in text for word in ["COBRAR", "Cobrar", "cobrar"]),
                "has00T": "00T" in text,
                "snippet": text[:700],
            }
            ok = 200 <= int(result["status"]) < 400 and not build_error
            self.add_check(name, ok, f"status={result['status']}", data, critical=critical)
            if build_error:
                self.add_fragile(f"{name} build/runtime error", "Route contains Next/CSS/runtime error text", data)
        except Exception as exc:
            self.add_check(name, False, f"{url}: {exc}", critical=critical)

    def scan_recent_logs(self) -> None:
        if not self.out_dir.exists():
            self.add_check("scan recent logs", False, f"missing {self.out_dir}")
            return
        files = sorted(
            [p for p in self.out_dir.iterdir() if p.is_file() and p.suffix.lower() in {".log", ".json", ".out", ".err"}],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:70]
        hits: list[dict[str, Any]] = []
        for file in files:
            try:
                text = file.read_text(encoding="utf-8", errors="replace")[-9000:]
            except Exception:
                continue
            for pattern in ERROR_PATTERNS:
                if pattern in text:
                    hits.append({"file": str(file), "pattern": pattern, "mtime": datetime.fromtimestamp(file.stat().st_mtime).isoformat(timespec="seconds")})
        self.add_check("scan recent logs", len(hits) == 0, f"hits={len(hits)}", hits, critical=False)
        if hits:
            self.add_fragile("recent log history", "Recent logs contain previous failure strings. Check timestamps before blaming current runtime.", hits[:12])

    def broadcast_neutral(self) -> None:
        payload = {
            "type": "prisma.visual.controls",
            "sourceClientId": "doctor-prisma-show-pos-scan-00u",
            "surface": "tablet_pos",
            "recipeName": "POS_DOCTOR_00U_NEUTRAL_NO_LAYOUT",
            "liveEnabled": True,
            "debugLayers": False,
            "mode": "doctor-neutral-no-layout",
            "createdAt": utc_now(),
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
            "score": {"overall": 0, "verdict": "doctor_neutral_no_layout"},
        }
        try:
            post = self.post_json(f"{REALTIME_BASE}/broadcast", payload, timeout=8)
            state = self.http_json(f"{REALTIME_BASE}/state", timeout=8)
            ok = state.get("json", {}).get("lastPayload", {}).get("recipeName") == payload["recipeName"]
            self.add_check("broadcast neutral no-layout", ok, "POST /broadcast + GET /state", {"post": post, "state": state}, critical=False)
        except Exception as exc:
            self.add_check("broadcast neutral no-layout", False, str(exc), critical=False)

    def self_check(self) -> int:
        self.ensure_out_dir()
        self.log(f"START {PACKAGE} self-check")
        self.check_file("doctor file", Path(__file__), critical=True)
        self.add_check("python version", sys.version_info >= (3, 10), sys.version.replace("\n", " "), critical=True)
        self.add_check("target root path resolved", bool(str(self.target_root)), str(self.target_root), critical=True)
        self.check_file("system root", self.system_root, critical=False)
        self.check_file("tablet root", self.tablet_root, critical=False)
        self.report["status"] = "ready" if not self.report["criticalFailures"] else "blocked"
        self.save_report()
        return 0 if not self.report["criticalFailures"] else 2

    def scan(self, start_missing: bool, run_node_verifiers: bool, broadcast_neutral: bool, scan_logs: bool) -> int:
        self.ensure_out_dir()
        self.log(f"START {PACKAGE} scan")
        node = self.find_tool(["node.exe", "node"])
        pnpm = self.find_tool(["pnpm.cmd", "pnpm"])
        git = self.find_tool(["git.exe", "git"])
        self.add_check("tool node", bool(node), node or "not found", critical=True)
        self.add_check("tool pnpm", bool(pnpm), pnpm or "not found", critical=True)
        self.add_check("tool git", bool(git), git or "not found", critical=False)
        if node:
            self.run("node version", [node, "--version"], self.target_root, timeout=10)
        if pnpm:
            self.run("pnpm version", [pnpm, "--version"], self.target_root, timeout=10)

        required = {
            "repo root": self.target_root,
            "terminal system root": self.system_root,
            "tablet app root": self.tablet_root,
            "terminal cmd": self.system_root / "terminal_de_venta.cmd",
            "tablet package json": self.tablet_root / "package.json",
            "pos screen": self.tablet_root / "components" / "pos" / "pos-screen.tsx",
            "pos binding": self.tablet_root / "components" / "pos" / "pos-live-binding.tsx",
            "pos css": self.tablet_root / "components" / "pos" / "pos.module.css",
            "doctor installed": self.system_root / "tools" / "prisma-visual-os" / "doctor_prisma_show_pos_scan_00u.py",
            "doctor launcher": self.system_root / "tools" / "prisma-visual-os" / "run_prisma_show_pos_doctor_00u.cmd",
            "visual realtime server": self.system_root / "tools" / "prisma-visual-os" / "live-preview-server-00q.mjs",
            "verify 00R 00S": self.system_root / "tools" / "prisma-visual-os" / "verify_prisma_visual_os_studio_pro_qa_00r_00s.mjs",
            "verify 00T": self.system_root / "tools" / "prisma-visual-os" / "verify_prisma_visual_os_pos_live_binding_00t.mjs",
            "verify doctor 00U": self.system_root / "tools" / "prisma-visual-os" / "verify_prisma_show_pos_doctor_00u.mjs",
            "score 00S": self.system_root / "tools" / "prisma-visual-os" / "score_prisma_studio_pro_00s.mjs",
            "crystal recipe": self.system_root / "config" / "prisma-visual-os" / "recipes" / "CRYSTAL_POS_ANGEL_LIVE_v01.json",
            "architecture doc": self.system_root / "docs" / "architecture" / "PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md",
            "pos golden flow": self.system_root / "docs" / "pos" / "PRISMA_POS_GOLDEN_FLOW_01.md",
        }
        for name, path in required.items():
            self.check_file(name, path, critical=name in {"repo root", "terminal system root", "tablet app root", "pos binding", "pos css"})

        self.scan_file(
            "00T binding",
            required["pos binding"],
            ["new EventSource", "prisma.visual.controls", "setProperty", "data-prisma-pos-live-badge", "export default PosLiveBinding"],
            ["applyFallbackVars()", "POS_POS500_AUTOFIX_BOMB_TEST_00T"],
            critical=True,
        )
        self.scan_file(
            "00T css no-layout markers",
            required["pos css"],
            ["PRISMA 00T SAFE NO-LAYOUT LIVE MARKER"],
            [
                "PRISMA 00T POS500 SAFE LIVE POS MAPPING",
                "PRISMA 00T AUTOPILOT HARD GLOBAL POS MAPPING",
                "PRISMA 00T HARD LIVE POS MAPPING",
                "FORCE VISIBLE LIVE POS MAPPING",
                "posWorkspace[data-prisma-pos-live=\"00T\"]",
                ".posLiveBadge",
            ],
            critical=True,
        )

        owner_3120 = self.get_port_owner(3120)
        owner_4177 = self.get_port_owner(4177)
        self.add_check("port 3120 owner", True, "checked", owner_3120)
        self.add_check("port 4177 owner", True, "checked", owner_4177)

        if start_missing and node and not bool(owner_4177.get("Listening")):
            server = required["visual realtime server"]
            if server.exists():
                self.start_process_logged("realtime", node, [str(server), "--port", "4177"], self.system_root)
                self.wait_http(f"{REALTIME_BASE}/health", seconds=30)
        if start_missing and pnpm and not bool(owner_3120.get("Listening")):
            self.start_process_logged("tablet", pnpm, ["-C", str(self.tablet_root), "dev"], self.target_root)
            self.wait_http(f"{TABLET_BASE}/pos", seconds=90)

        try:
            health = self.http_json(f"{REALTIME_BASE}/health", timeout=8)
            self.add_check("realtime health", 200 <= int(health["status"]) < 400, f"status={health['status']}", health, critical=True)
        except Exception as exc:
            self.add_check("realtime health", False, str(exc), critical=True)
        try:
            state = self.http_json(f"{REALTIME_BASE}/state", timeout=8)
            self.add_check("realtime state", 200 <= int(state["status"]) < 400, f"status={state['status']}", state, critical=False)
        except Exception as exc:
            self.add_check("realtime state", False, str(exc), critical=False)

        self.probe_route("route /pos", f"{TABLET_BASE}/pos", critical=True)
        self.probe_route("route /visual-os", f"{TABLET_BASE}/visual-os", critical=False)
        self.probe_route("route /visual-os/pro", f"{TABLET_BASE}/visual-os/pro", critical=True)
        self.probe_route("route /visual-os/realtime", f"{TABLET_BASE}/visual-os/realtime", critical=False)

        if broadcast_neutral:
            self.broadcast_neutral()

        if run_node_verifiers and node:
            verifiers = [
                ("verify doctor 00U", required["verify doctor 00U"], True),
                ("verify 00T", required["verify 00T"], True),
                ("verify 00R 00S", required["verify 00R 00S"], False),
                ("verify tablet pos light 00Q", self.tablet_root / "tools" / "verify_prisma_tablet_pos_light_operational_00q.mjs", False),
                ("verify checkout 00R", self.tablet_root / "tools" / "verify_prisma_tablet_pos_real_checkout_flow_00r.mjs", False),
                ("verify checkout shift 00S", self.tablet_root / "tools" / "verify_prisma_tablet_pos_checkout_shift_autofix_00s.mjs", False),
                ("verify hold carts 04G", self.tablet_root / "tools" / "verify_pos_golden_flow_hold_carts_04g.mjs", False),
                ("verify touch only 04H", self.tablet_root / "tools" / "verify_pos_touch_only_actions_04h.mjs", False),
            ]
            for name, path, critical in verifiers:
                if path.exists():
                    self.run(name, [node, str(path)], self.system_root, timeout=50, critical=critical)
                else:
                    self.add_check(name, False, f"missing {path}", critical=critical)
            score = required["score 00S"]
            recipe = required["crystal recipe"]
            if score.exists() and recipe.exists():
                self.run("score crystal recipe", [node, str(score), str(recipe)], self.system_root, timeout=40, critical=False)

        if scan_logs:
            self.scan_recent_logs()

        if self.report["criticalFailures"]:
            self.report["status"] = "blocked"
            self.add_recommendation("No empaquetar ni avanzar. Resolver criticalFailures primero.")
        elif self.report["warnings"] or self.report["fragilePoints"]:
            self.report["status"] = "ready_with_warnings"
            self.add_recommendation("Base operable con advertencias. Revisar warnings antes de cerrar release final.")
        else:
            self.report["status"] = "ready"
            self.add_recommendation("Base lista para cierre 00T safe y siguiente inyeccion funcional.")
        self.save_report()
        if self.report["criticalFailures"]:
            return 2
        if self.strict and (self.report["warnings"] or self.report["fragilePoints"]):
            return 1
        return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PRISMA Show POS Doctor 00U. Escanea Visual OS, POS, realtime, verifiers y logs sin modificar repo.",
    )
    parser.add_argument("--target-root", default=str(DEFAULT_TARGET_ROOT), help="Repo root. Default: F:\\repos\\hitech-os")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Directorio de logs/reportes. Default: F:\\descargasf")
    parser.add_argument("--self-check", action="store_true", help="Valida que el doctor arranca y puede escribir reporte.")
    parser.add_argument("--scan", action="store_true", help="Ejecuta scan completo. Es el modo default si no pasas --self-check.")
    parser.add_argument("--start-missing", action="store_true", help="Si faltan realtime/tablet, intenta arrancarlos con node/pnpm.")
    parser.add_argument("--no-node-verifiers", action="store_true", help="No correr verificadores node.")
    parser.add_argument("--no-broadcast", action="store_true", help="No mandar broadcast neutral no-layout.")
    parser.add_argument("--no-log-scan", action="store_true", help="No escanear logs recientes de F:\\descargasf.")
    parser.add_argument("--strict", action="store_true", help="Devuelve exit 1 si hay warnings o puntos fragiles.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    doctor = Doctor(Path(args.target_root), Path(args.out_dir), strict=bool(args.strict))
    try:
        if args.self_check:
            return doctor.self_check()
        return doctor.scan(
            start_missing=bool(args.start_missing),
            run_node_verifiers=not bool(args.no_node_verifiers),
            broadcast_neutral=not bool(args.no_broadcast),
            scan_logs=not bool(args.no_log_scan),
        )
    except Exception as exc:
        doctor.ensure_out_dir()
        doctor.log(f"FATAL {exc}")
        doctor.report["status"] = "fatal"
        doctor.report["criticalFailures"].append({"name": "fatal", "ok": False, "critical": True, "detail": str(exc)})
        doctor.save_report()
        return 99


if __name__ == "__main__":
    raise SystemExit(main())
