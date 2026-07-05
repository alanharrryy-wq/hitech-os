#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Fast Ignit Port Control.

Interactive VS Code-integrated port control for the PRISMA local stack.
No detached consoles, no global node.exe/powershell.exe massacre. It targets
only the PID(s) listening on selected ports and writes result/fail evidence.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

PRISMA_PORT_CONTROL_V1 = True
PORTS = [3000, 3110, 3120, 3130, 3140, 3150, 3160]
PORT_NAMES = {
    3000: "Chart Lab",
    3110: "PRISMA Web / EIT",
    3120: "Tablet Core",
    3130: "PC Backoffice",
    3140: "Mobile Adder",
    3150: "Control Center",
    3160: "Cloud Command Center",
}


def stamp() -> str:
    return _dt.datetime.now().strftime("%d%m %H%M%S")


def iso_now() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def print_progress(step: int, total: int, label: str) -> None:
    total = max(total, 1)
    pct = int(round((step / total) * 100))
    width = 24
    done = int(width * step / total)
    bar = "█" * done + "░" * (width - done)
    print(f"[{bar}] {pct:3d}% listo / {100-pct:3d}% restante :: {label}", flush=True)


def parse_ports(text: str) -> List[int]:
    raw = (text or "").strip().lower()
    if raw in ("all", "todo", "todos", "*"):
        return list(PORTS)
    selected: List[int] = []
    for part in re.split(r"[,;\s]+", raw):
        if not part:
            continue
        if part.isdigit():
            selected.append(int(part))
            continue
        # menu number 1..7 support
        if part in [str(i) for i in range(1, 8)]:
            idx = int(part) - 1
            if 0 <= idx < len(PORTS):
                selected.append(PORTS[idx])
    out: List[int] = []
    seen = set()
    for p in selected:
        if p not in PORTS:
            raise ValueError(f"Puerto no soportado por Port Control: {p}")
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


@dataclass
class PidInfo:
    pid: int
    name: str = ""
    command_line: str = ""


@dataclass
class PortStatus:
    port: int
    name: str
    listening: bool
    pids: List[PidInfo]


@dataclass
class KillResult:
    port: int
    name: str
    before_pids: List[PidInfo]
    after_pids: List[PidInfo]
    killed: List[int]
    failed: List[str]
    success: bool


class PortControl:
    def __init__(self, output_dir: str):
        self.base = Path(os.path.expandvars(output_dir or r"F:\descargasf"))
        self.stamp = stamp()
        self.run_dir = self.base / f"fastignit portctl {self.stamp}"
        self.log_path = self.run_dir / "action.log"
        self.summary_path = self.run_dir / "PORT_CONTROL_SUMMARY.json"
        self.report_path = self.run_dir / "PORT_CONTROL_REPORT.md"
        self.latest_path = self.base / "latest_FAST_IGNIT_PORT_CONTROL.json"
        self.result_zip = self.base / f"fastignit portctl {self.stamp} result.zip"
        self.fail_zip = self.base / f"fastignit portctl {self.stamp} fail.zip"
        self.summary: Dict = {
            "tool": "PRISMA Fast Ignit Port Control",
            "schemaVersion": "1.0",
            "createdAt": iso_now(),
            "status": "PENDING",
            "runDir": str(self.run_dir),
            "actions": [],
            "errors": [],
            "resultZip": str(self.result_zip),
            "failZip": str(self.fail_zip),
            "policy": {
                "killsOnlyListeningPidsForSelectedPorts": True,
                "noGlobalNodeKill": True,
                "noDetachedConsoles": True,
                "port3160MayBeReset": True,
            },
        }
        self.base.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def log(self, text: str) -> None:
        print(text, flush=True)
        with self.log_path.open("a", encoding="utf-8", errors="replace") as f:
            f.write(text + "\n")

    def run_cmd(self, cmd: List[str], timeout: int = 20) -> Tuple[int, str]:
        try:
            p = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            return int(p.returncode), p.stdout or ""
        except subprocess.TimeoutExpired as exc:
            return 124, (exc.stdout or "") + "\n[TIMEOUT]"
        except Exception:
            return 1, traceback.format_exc()

    def listen_pids_netstat(self, port: int) -> List[int]:
        rc, out = self.run_cmd(["netstat", "-ano", "-p", "tcp"], timeout=25)
        pids = set()
        if rc != 0 and not out:
            return []
        for line in out.splitlines():
            s = " ".join(line.split())
            if not s:
                continue
            upper = s.upper()
            if "LISTEN" not in upper:
                continue
            cols = s.split()
            if len(cols) < 5:
                continue
            local = cols[1]
            state = cols[3].upper() if len(cols) >= 5 else ""
            pid_raw = cols[-1]
            if "LISTEN" not in state and "LISTEN" not in upper:
                continue
            # matches 127.0.0.1:3000, 0.0.0.0:3000, [::]:3000
            if not re.search(rf"(?::|\]){port}$", local):
                if not local.endswith(f":{port}"):
                    continue
            if pid_raw.isdigit():
                pids.add(int(pid_raw))
        return sorted(pids)

    def process_info(self, pid: int) -> PidInfo:
        # Prefer PowerShell CIM for command line, fallback to tasklist.
        ps = shutil.which("pwsh.exe") or shutil.which("pwsh") or shutil.which("powershell.exe") or shutil.which("powershell")
        if ps:
            script = (
                f"$p=Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\" -ErrorAction SilentlyContinue; "
                "if($p){ [pscustomobject]@{ ProcessId=$p.ProcessId; Name=$p.Name; CommandLine=$p.CommandLine } | ConvertTo-Json -Compress -Depth 4 }"
            )
            rc, out = self.run_cmd([ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], timeout=12)
            if out.strip().startswith("{"):
                try:
                    data = json.loads(out.strip())
                    return PidInfo(pid=int(data.get("ProcessId") or pid), name=str(data.get("Name") or ""), command_line=str(data.get("CommandLine") or ""))
                except Exception:
                    pass
        rc, out = self.run_cmd(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], timeout=12)
        name = ""
        try:
            rows = list(csv.reader(io.StringIO(out)))
            if rows and rows[0] and not rows[0][0].startswith("INFO:"):
                name = rows[0][0]
        except Exception:
            pass
        return PidInfo(pid=pid, name=name, command_line="")

    def port_status(self, port: int) -> PortStatus:
        pids = self.listen_pids_netstat(port)
        infos = [self.process_info(pid) for pid in pids]
        return PortStatus(port=port, name=PORT_NAMES.get(port, f"Port {port}"), listening=bool(infos), pids=infos)

    def status_all(self) -> List[PortStatus]:
        return [self.port_status(p) for p in PORTS]

    def print_status_table(self, statuses: Optional[List[PortStatus]] = None) -> None:
        statuses = statuses if statuses is not None else self.status_all()
        print("\nPRISMA FAST IGNIT PORT CONTROL")
        print("-" * 92)
        print(f"{'#':>2} {'PORT':>5}  {'SERVICIO':<28} {'ESTADO':<10} {'PID(s)':<16} PROCESO")
        print("-" * 92)
        for idx, st in enumerate(statuses, 1):
            pids = ",".join(str(p.pid) for p in st.pids) if st.pids else "-"
            proc = ", ".join((p.name or "?") for p in st.pids) if st.pids else "-"
            state = "READY" if st.listening else "CLOSED"
            print(f"{idx:>2} {st.port:>5}  {st.name:<28} {state:<10} {pids:<16} {proc}")
        print("-" * 92)

    def kill_port(self, port: int) -> KillResult:
        name = PORT_NAMES.get(port, f"Port {port}")
        before = self.port_status(port)
        killed: List[int] = []
        failed: List[str] = []
        if not before.pids:
            return KillResult(port=port, name=name, before_pids=[], after_pids=[], killed=[], failed=[], success=True)
        for info in before.pids:
            self.log(f"[PortCtl] Cerrando puerto {port} {name}: PID {info.pid} {info.name}")
            rc, out = self.run_cmd(["taskkill", "/PID", str(info.pid), "/T", "/F"], timeout=20)
            self.log(out.strip() or f"taskkill exit={rc}")
            if rc == 0:
                killed.append(info.pid)
            else:
                failed.append(f"PID {info.pid}: taskkill exit {rc}: {out.strip()[:500]}")
        time.sleep(1.2)
        after = self.port_status(port)
        success = not after.pids
        if after.pids:
            failed.append("Puerto sigue ocupado despues de taskkill: " + ",".join(str(p.pid) for p in after.pids))
        return KillResult(port=port, name=name, before_pids=before.pids, after_pids=after.pids, killed=killed, failed=failed, success=success)

    def write_evidence(self, mode: str, statuses_before: List[PortStatus], statuses_after: List[PortStatus], kill_results: List[KillResult]) -> Path:
        status = "PASS" if all(k.success for k in kill_results) else "FAIL"
        if not kill_results and mode == "status":
            status = "PASS"
        self.summary.update({
            "mode": mode,
            "status": status,
            "finishedAt": iso_now(),
            "portsBefore": [asdict(s) for s in statuses_before],
            "portsAfter": [asdict(s) for s in statuses_after],
            "killResults": [asdict(k) for k in kill_results],
        })
        self.summary_path.write_text(json.dumps(self.summary, indent=2, ensure_ascii=False), encoding="utf-8")
        self.latest_path.write_text(json.dumps(self.summary, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = [
            "# PRISMA Fast Ignit Port Control Report",
            "",
            f"Status: **{status}**",
            f"Mode: `{mode}`",
            f"Run dir: `{self.run_dir}`",
            "",
            "## Puertos despues",
            "",
            "| Port | Servicio | Estado | PID(s) | Proceso |",
            "|---:|---|---|---|---|",
        ]
        for st in statuses_after:
            pids = ", ".join(str(p.pid) for p in st.pids) if st.pids else "-"
            proc = ", ".join(p.name or "?" for p in st.pids) if st.pids else "-"
            lines.append(f"| {st.port} | {st.name} | {'READY' if st.listening else 'CLOSED'} | {pids} | {proc} |")
        if kill_results:
            lines += ["", "## Acciones de cierre", "", "| Port | Servicio | Killed | Success | Failed |", "|---:|---|---|---|---|"]
            for k in kill_results:
                lines.append(f"| {k.port} | {k.name} | {','.join(map(str,k.killed)) or '-'} | {k.success} | {'; '.join(k.failed) or '-'} |")
        lines += ["", "## Politica", "", "- Sólo se cierran PID(s) escuchando en los puertos seleccionados.", "- No se mata todo `node.exe` ni todo `powershell.exe`.", "- 3160 puede resetearse; los demás sólo si el usuario los selecciona."]
        self.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        zip_path = self.result_zip if status == "PASS" else self.fail_zip
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for p in [self.summary_path, self.report_path, self.log_path]:
                if p.exists():
                    z.write(p, p.relative_to(self.run_dir))
        return zip_path

    def do_status(self) -> int:
        print_progress(1, 3, "escaneando puertos")
        before = self.status_all()
        self.print_status_table(before)
        print_progress(2, 3, "generando evidencia")
        z = self.write_evidence("status", before, before, [])
        print_progress(3, 3, f"PASS: {z}")
        print(f"\n[PortCtl] ZIP: {z}")
        return 0

    def do_close(self, ports: List[int], mode: str = "close") -> int:
        if not ports:
            raise ValueError("No se especificaron puertos para cerrar.")
        print_progress(1, 5, "estado inicial")
        before = self.status_all()
        self.print_status_table(before)
        results: List[KillResult] = []
        total = len(ports)
        for idx, port in enumerate(ports, 1):
            print_progress(1 + idx, max(5, total + 4), f"cerrando {port} {PORT_NAMES.get(port,'')}")
            results.append(self.kill_port(port))
        print_progress(4, 5, "verificando puertos")
        after = self.status_all()
        self.print_status_table(after)
        print_progress(5, 5, "generando evidencia")
        z = self.write_evidence(mode, before, after, results)
        print(f"\n[PortCtl] ZIP: {z}")
        return 0 if all(r.success for r in results) else 1

    def menu(self) -> int:
        while True:
            statuses = self.status_all()
            self.print_status_table(statuses)
            print("Opciones:")
            print("  1-7  cerrar ese puerto")
            print("  S    refrescar status")
            print("  A    cerrar todos los puertos PRISMA locales")
            print("  Q    salir")
            choice = input("\nElige opcion: ").strip().lower()
            if choice in ("q", "quit", "salir", "0"):
                print("[PortCtl] Salida sin cambios adicionales.")
                return 0
            if choice in ("s", "status", "estado"):
                self.do_status()
                input("\nEnter para volver al menu...")
                continue
            if choice in ("a", "all", "todo", "todos"):
                confirm = input("Vas a cerrar TODOS los puertos 3000,3110,3120,3130,3140,3150,3160. Escribe SI para confirmar: ").strip().upper()
                if confirm != "SI":
                    print("Cancelado.")
                    continue
                self.do_close(PORTS, mode="close-all")
                input("\nEnter para volver al menu...")
                continue
            try:
                ports = parse_ports(choice)
                if not ports and choice.isdigit() and 1 <= int(choice) <= len(PORTS):
                    ports = [PORTS[int(choice)-1]]
                if not ports:
                    print("Opcion no reconocida.")
                    continue
                self.do_close(ports, mode="menu-close")
                input("\nEnter para volver al menu...")
            except Exception as exc:
                print("Error:", exc)
                input("\nEnter para volver al menu...")


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PRISMA Fast Ignit Port Control")
    p.add_argument("--mode", choices=["menu", "status", "close", "close-all"], default="menu")
    p.add_argument("--ports", default="")
    p.add_argument("--output-dir", default=r"F:\descargasf")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    ctl = PortControl(args.output_dir)
    try:
        if args.mode == "status":
            return ctl.do_status()
        if args.mode == "close-all":
            return ctl.do_close(PORTS, mode="close-all")
        if args.mode == "close":
            return ctl.do_close(parse_ports(args.ports), mode="close")
        return ctl.menu()
    except Exception:
        err = traceback.format_exc()
        ctl.summary["status"] = "FAIL"
        ctl.summary["errors"].append(err)
        ctl.summary_path.write_text(json.dumps(ctl.summary, indent=2, ensure_ascii=False), encoding="utf-8")
        ctl.report_path.write_text("# PRISMA Fast Ignit Port Control Report\n\nStatus: **FAIL**\n\n```text\n" + err + "\n```\n", encoding="utf-8")
        with zipfile.ZipFile(ctl.fail_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for p in [ctl.summary_path, ctl.report_path, ctl.log_path]:
                if p.exists():
                    z.write(p, p.relative_to(ctl.run_dir))
        print(err)
        print(f"\n[PortCtl] FAIL ZIP: {ctl.fail_zip}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
