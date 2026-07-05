#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Fast Ignit Port Commander.

Interactive VS Code-integrated port commander for the PRISMA local stack.
It can status, close, launch, restart, and execute dot-separated command chains
such as C1.C2.L4.A5.R7.  It targets only the PID(s) listening on selected ports
for closes, and delegates launches to Fast Ignit without detached consoles.
"""
from __future__ import annotations

import argparse
import concurrent.futures
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

PRISMA_PORT_COMMANDER_V3 = True
PRISMA_PORT_COMMANDER_DOT_CHAIN_V1 = True
PRISMA_PORT_COMMANDER_PARALLEL_PHASES_V1 = True
PRISMA_PORT_CONTROL_CLOSE_ALL_STRONG_CONFIRM = True

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
INDEX_TO_PORT = {str(i): p for i, p in enumerate(PORTS, 1)}


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


def unique_ports(ports: Iterable[int]) -> List[int]:
    out: List[int] = []
    seen = set()
    for p in ports:
        if p not in PORTS:
            raise ValueError(f"Puerto no soportado por Port Commander: {p}")
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def parse_port_selector(text: str) -> int:
    raw = (text or "").strip().lower()
    if raw in INDEX_TO_PORT:
        return INDEX_TO_PORT[raw]
    if raw.isdigit():
        n = int(raw)
        if n in PORTS:
            return n
    raise ValueError(f"Puerto/opcion no soportado por Port Commander: {text}")


def parse_ports(text: str) -> List[int]:
    """Parse menu positions or real port numbers.

    Supports `1` -> 3000, `2` -> 3110, and real ports such as `3120`.
    Also accepts comma/space/semicolon lists and `all`.
    """
    raw = (text or "").strip().lower()
    if raw in ("all", "todo", "todos", "*"):
        return list(PORTS)
    selected: List[int] = []
    for part in re.split(r"[,;\s]+", raw):
        if not part:
            continue
        selected.append(parse_port_selector(part))
    return unique_ports(selected)


@dataclass
class CommandAction:
    op: str
    port: Optional[int] = None
    raw: str = ""


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


@dataclass
class StartResult:
    ports: List[int]
    command: List[str]
    exit_code: int
    success: bool
    elapsed_sec: float
    log_file: str
    latest_run_zip: str = ""
    error: str = ""


@dataclass
class BatchResult:
    raw: str
    actions: List[CommandAction]
    close_ports: List[int]
    start_ports: List[int]
    kill_results: List[KillResult]
    start_results: List[StartResult]
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
        self.fast_dir = Path(__file__).resolve().parent.parent
        self.fast_ps1 = self.fast_dir / "FastIgnit.ps1"
        self.summary: Dict = {
            "tool": "PRISMA Fast Ignit Port Commander",
            "schemaVersion": "3.0",
            "createdAt": iso_now(),
            "status": "PENDING",
            "runDir": str(self.run_dir),
            "fastDir": str(self.fast_dir),
            "fastIgnitPs1": str(self.fast_ps1),
            "actions": [],
            "errors": [],
            "resultZip": str(self.result_zip),
            "failZip": str(self.fail_zip),
            "policy": {
                "killsOnlyListeningPidsForSelectedPorts": True,
                "noGlobalNodeKill": True,
                "noDetachedConsoles": True,
                "port3160MayBeReset": True,
                "dotSeparatedCommands": True,
                "parallelByPhase": True,
                "closeAllRequiresExactPhrase": "CERRAR TODO",
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
            out = exc.stdout if isinstance(exc.stdout, str) else ""
            return 124, out + "\n[TIMEOUT]"
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
            if not re.search(rf"(?::|\]){port}$", local):
                if not local.endswith(f":{port}"):
                    continue
            if pid_raw.isdigit():
                pids.add(int(pid_raw))
        return sorted(pids)

    def process_info(self, pid: int) -> PidInfo:
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

    def status_map(self, statuses: Optional[List[PortStatus]] = None) -> Dict[int, PortStatus]:
        statuses = statuses if statuses is not None else self.status_all()
        return {s.port: s for s in statuses}

    def print_status_table(self, statuses: Optional[List[PortStatus]] = None) -> None:
        statuses = statuses if statuses is not None else self.status_all()
        print("\nPRISMA FAST IGNIT PORT COMMANDER")
        print("-" * 98)
        print(f"{'#':>2} {'PORT':>5}  {'SERVICIO':<28} {'ESTADO':<10} {'PID(s)':<16} PROCESO")
        print("-" * 98)
        for idx, st in enumerate(statuses, 1):
            pids = ",".join(str(p.pid) for p in st.pids) if st.pids else "-"
            proc = ", ".join((p.name or "?") for p in st.pids) if st.pids else "-"
            state = "READY" if st.listening else "CLOSED"
            print(f"{idx:>2} {st.port:>5}  {st.name:<28} {state:<10} {pids:<16} {proc}")
        print("-" * 98)

    def kill_port(self, port: int) -> KillResult:
        name = PORT_NAMES.get(port, f"Port {port}")
        before = self.port_status(port)
        killed: List[int] = []
        failed: List[str] = []
        if not before.pids:
            return KillResult(port=port, name=name, before_pids=[], after_pids=[], killed=[], failed=[], success=True)
        for info in before.pids:
            self.log(f"[PortCmd] Cerrando puerto {port} {name}: PID {info.pid} {info.name}")
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

    def close_ports_parallel(self, ports: List[int]) -> List[KillResult]:
        ports = unique_ports(ports)
        if not ports:
            return []
        self.log("[PortCmd] Cerrando en paralelo: " + ",".join(map(str, ports)))
        results: List[KillResult] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(ports), 7) or 1) as pool:
            futs = {pool.submit(self.kill_port, p): p for p in ports}
            for fut in concurrent.futures.as_completed(futs):
                results.append(fut.result())
        return sorted(results, key=lambda r: PORTS.index(r.port))

    def which_powershell(self) -> str:
        for name in ("pwsh.exe", "pwsh", "powershell.exe", "powershell"):
            exe = shutil.which(name)
            if exe:
                return exe
        return "powershell.exe"

    def newest_fastignit_run_zip(self, since_ts: float) -> str:
        zips = []
        for pat in ("fastignit run * result.zip", "fastignit run * fail.zip"):
            zips.extend([p for p in self.base.glob(pat) if p.is_file() and p.stat().st_mtime >= since_ts - 3])
        if not zips:
            return ""
        return str(max(zips, key=lambda p: p.stat().st_mtime))

    def start_ports(self, ports: List[int]) -> StartResult:
        ports = unique_ports(ports)
        if not ports:
            return StartResult(ports=[], command=[], exit_code=0, success=True, elapsed_sec=0.0, log_file="")
        if not self.fast_ps1.exists():
            return StartResult(ports=ports, command=[], exit_code=1, success=False, elapsed_sec=0.0, log_file="", error=f"No existe FastIgnit.ps1: {self.fast_ps1}")
        started_ts = time.time()
        started = time.monotonic()
        log_file = self.run_dir / ("launch_" + "_".join(map(str, ports)) + ".log")
        reset_ports = "3160" if 3160 in ports else ""
        cmd = [
            self.which_powershell(), "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(self.fast_ps1),
            "--mode", "start",
            "--ports", ",".join(map(str, ports)),
            "--reset-ports", reset_ports,
            "--concurrency", str(max(1, min(4, len(ports)))),
            "--timeout", "180",
            "--output-dir", str(self.base),
        ]
        self.log("[PortCmd] Levantando con Fast Ignit: " + " ".join(cmd))
        code = 1
        err = ""
        try:
            with log_file.open("w", encoding="utf-8", errors="replace") as log:
                log.write("COMMAND:\n" + " ".join(cmd) + "\n\n")
                log.flush()
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(self.fast_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                while True:
                    line = proc.stdout.readline() if proc.stdout else ""
                    if line:
                        print(line, end="", flush=True)
                        log.write(line)
                        log.flush()
                    if proc.poll() is not None:
                        rest = proc.stdout.read() if proc.stdout else ""
                        if rest:
                            print(rest, end="", flush=True)
                            log.write(rest)
                        break
                    if not line:
                        time.sleep(0.2)
                code = int(proc.returncode or 0)
        except Exception:
            err = traceback.format_exc()
            self.log(err)
            code = 1
        elapsed = round(time.monotonic() - started, 3)
        latest = self.newest_fastignit_run_zip(started_ts)
        # Trust Fast Ignit exit code, then verify selected ports are listening too.
        selected = self.status_map()
        ready = all(selected.get(p) and selected[p].listening for p in ports)
        success = code == 0 and ready
        if code == 0 and not ready:
            missing = [str(p) for p in ports if not (selected.get(p) and selected[p].listening)]
            err = "Fast Ignit salio 0 pero estos puertos no quedaron READY: " + ",".join(missing)
        return StartResult(ports=ports, command=cmd, exit_code=code, success=success, elapsed_sec=elapsed, log_file=str(log_file), latest_run_zip=latest, error=err)

    def parse_command_chain(self, raw: str) -> List[CommandAction]:
        text = (raw or "").strip()
        if not text:
            return []
        # Dot is the main separator requested by the user. Comma/semicolon also work.
        parts = [p.strip() for p in re.split(r"[.;,]+", text) if p.strip()]
        actions: List[CommandAction] = []
        for part in parts:
            low = part.lower().replace(" ", "")
            if low in ("q", "quit", "salir", "0"):
                actions.append(CommandAction(op="quit", raw=part))
                continue
            if low in ("s", "status", "estado"):
                actions.append(CommandAction(op="status", raw=part))
                continue
            if low in ("lt", "levantartodos", "levantarclosed", "lc"):
                actions.append(CommandAction(op="launch-closed", raw=part))
                continue
            if low in ("a", "all", "todo", "todos"):
                actions.append(CommandAction(op="close-all", raw=part))
                continue
            m = re.match(r"^([clera])([0-9]{1,4})$", low)
            if m:
                op_raw, port_raw = m.group(1), m.group(2)
                port = parse_port_selector(port_raw)
                if op_raw in ("c", "a"):
                    op = "close"       # Cerrar / Apagar
                elif op_raw in ("l", "e"):
                    op = "launch"      # Levantar / Encender
                elif op_raw == "r":
                    op = "restart"
                else:
                    raise ValueError(f"Operacion no soportada: {part}")
                actions.append(CommandAction(op=op, port=port, raw=part))
                continue
            # Backward compatibility: plain number closes that menu row.
            if low.isdigit():
                port = parse_port_selector(low)
                actions.append(CommandAction(op="close", port=port, raw=part))
                continue
            raise ValueError(f"Comando no reconocido: {part}. Usa C1, A1, L1, R1, S, LT, A o Q.")
        return actions

    def actions_to_dict(self, actions: List[CommandAction]) -> List[Dict]:
        return [asdict(a) for a in actions]

    def execute_actions(self, raw: str, actions: List[CommandAction]) -> Tuple[List[PortStatus], List[PortStatus], BatchResult]:
        before = self.status_all()
        before_map = self.status_map(before)
        if not actions:
            return before, before, BatchResult(raw=raw, actions=[], close_ports=[], start_ports=[], kill_results=[], start_results=[], success=True)
        close_ports: List[int] = []
        start_ports: List[int] = []
        for a in actions:
            if a.op == "close" and a.port:
                close_ports.append(a.port)
            elif a.op == "launch" and a.port:
                start_ports.append(a.port)
            elif a.op == "restart" and a.port:
                close_ports.append(a.port)
                start_ports.append(a.port)
            elif a.op == "launch-closed":
                start_ports.extend([p for p, st in before_map.items() if not st.listening])
            elif a.op == "close-all":
                close_ports.extend(PORTS)
        close_ports = unique_ports(close_ports)
        start_ports = unique_ports(start_ports)

        kill_results: List[KillResult] = []
        start_results: List[StartResult] = []
        # Safe parallel by phase: first every close/restart close, then every launch/restart launch.
        if close_ports:
            print_progress(2, 6, "cerrando puertos en paralelo")
            kill_results = self.close_ports_parallel(close_ports)
        if start_ports:
            print_progress(4, 6, "levantando puertos en paralelo por Fast Ignit")
            start_results.append(self.start_ports(start_ports))
        after = self.status_all()
        after_map = self.status_map(after)
        success = True
        if kill_results and not all(k.success for k in kill_results):
            success = False
        if start_results and not all(s.success for s in start_results):
            success = False
        for p in close_ports:
            if p not in start_ports and after_map.get(p) and after_map[p].listening:
                success = False
        for p in start_ports:
            if not (after_map.get(p) and after_map[p].listening):
                success = False
        return before, after, BatchResult(raw=raw, actions=actions, close_ports=close_ports, start_ports=start_ports, kill_results=kill_results, start_results=start_results, success=success)

    def write_evidence(
        self,
        mode: str,
        statuses_before: List[PortStatus],
        statuses_after: List[PortStatus],
        kill_results: List[KillResult],
        start_results: Optional[List[StartResult]] = None,
        batch: Optional[BatchResult] = None,
    ) -> Path:
        start_results = start_results or []
        status = "PASS"
        if kill_results and not all(k.success for k in kill_results):
            status = "FAIL"
        if start_results and not all(s.success for s in start_results):
            status = "FAIL"
        if batch and not batch.success:
            status = "FAIL"
        self.summary.update({
            "mode": mode,
            "status": status,
            "finishedAt": iso_now(),
            "portsBefore": [asdict(s) for s in statuses_before],
            "portsAfter": [asdict(s) for s in statuses_after],
            "killResults": [asdict(k) for k in kill_results],
            "startResults": [asdict(s) for s in start_results],
            "batch": asdict(batch) if batch else None,
        })
        self.summary_path.write_text(json.dumps(self.summary, indent=2, ensure_ascii=False), encoding="utf-8")
        self.latest_path.write_text(json.dumps(self.summary, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = [
            "# PRISMA Fast Ignit Port Commander Report",
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
        if batch:
            lines += ["", "## Batch", "", f"Raw: `{batch.raw}`", "", f"Close ports: `{batch.close_ports}`", f"Start ports: `{batch.start_ports}`", ""]
        if kill_results:
            lines += ["", "## Acciones de cierre", "", "| Port | Servicio | Killed | Success | Failed |", "|---:|---|---|---|---|"]
            for k in kill_results:
                lines.append(f"| {k.port} | {k.name} | {','.join(map(str,k.killed)) or '-'} | {k.success} | {'; '.join(k.failed) or '-'} |")
        if start_results:
            lines += ["", "## Acciones de arranque", "", "| Ports | Exit | Success | Seconds | Fast Ignit ZIP | Error |", "|---|---:|---|---:|---|---|"]
            for s in start_results:
                lines.append(f"| {','.join(map(str,s.ports))} | {s.exit_code} | {s.success} | {s.elapsed_sec} | `{s.latest_run_zip or '-'}` | {s.error or '-'} |")
        lines += [
            "",
            "## Comandos soportados",
            "",
            "- `C1` o `A1`: cerrar/apagar el puerto de la fila 1.",
            "- `L1` o `E1`: levantar/encender el puerto de la fila 1.",
            "- `R1`: reiniciar el puerto de la fila 1.",
            "- Separador por punto: `C1.C2.L4.A5.R7`.",
            "- Ejecución por fases paralelas: cierres primero, arranques después.",
            "- `A` sin número cierra todos y exige `CERRAR TODO`.",
            "",
            "## Politica",
            "",
            "- Sólo se cierran PID(s) escuchando en los puertos seleccionados.",
            "- No se mata todo `node.exe` ni todo `powershell.exe`.",
            "- 3160 puede resetearse al arrancar; los demás sólo si el usuario los selecciona.",
        ]
        self.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        zip_path = self.result_zip if status == "PASS" else self.fail_zip
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for p in [self.summary_path, self.report_path, self.log_path]:
                if p.exists():
                    z.write(p, p.relative_to(self.run_dir))
            for s in start_results:
                lp = Path(s.log_file)
                if lp.exists():
                    z.write(lp, lp.relative_to(self.run_dir))
        return zip_path

    def do_status(self) -> int:
        print_progress(1, 3, "escaneando puertos")
        before = self.status_all()
        self.print_status_table(before)
        print_progress(2, 3, "generando evidencia")
        z = self.write_evidence("status", before, before, [])
        print_progress(3, 3, f"PASS: {z}")
        print(f"\n[PortCmd] ZIP: {z}")
        return 0

    def do_close(self, ports: List[int], mode: str = "close") -> int:
        if not ports:
            raise ValueError("No se especificaron puertos para cerrar.")
        print_progress(1, 5, "estado inicial")
        before = self.status_all()
        self.print_status_table(before)
        results = self.close_ports_parallel(ports)
        print_progress(4, 5, "verificando puertos")
        after = self.status_all()
        self.print_status_table(after)
        print_progress(5, 5, "generando evidencia")
        z = self.write_evidence(mode, before, after, results)
        print(f"\n[PortCmd] ZIP: {z}")
        return 0 if all(r.success for r in results) else 1

    def do_start(self, ports: List[int], mode: str = "launch") -> int:
        if not ports:
            raise ValueError("No se especificaron puertos para levantar.")
        print_progress(1, 5, "estado inicial")
        before = self.status_all()
        self.print_status_table(before)
        print_progress(3, 5, "levantando puertos")
        start_result = self.start_ports(ports)
        print_progress(4, 5, "verificando puertos")
        after = self.status_all()
        self.print_status_table(after)
        print_progress(5, 5, "generando evidencia")
        z = self.write_evidence(mode, before, after, [], [start_result])
        print(f"\n[PortCmd] ZIP: {z}")
        return 0 if start_result.success else 1

    def do_batch(self, raw: str) -> int:
        print_progress(1, 6, "parseando cadena de comandos")
        actions = self.parse_command_chain(raw)
        if any(a.op == "quit" for a in actions):
            print("[PortCmd] Salida solicitada.")
            return 0
        if any(a.op == "close-all" for a in actions):
            confirm = input("Vas a cerrar TODOS los puertos 3000,3110,3120,3130,3140,3150,3160. Escribe CERRAR TODO para confirmar: ").strip().upper()
            if confirm != "CERRAR TODO":
                print("Cancelado. No se cerro ningun puerto.")
                return 0
        if actions and all(a.op == "status" for a in actions):
            return self.do_status()
        before, after, batch = self.execute_actions(raw, actions)
        print_progress(5, 6, "estado final")
        self.print_status_table(after)
        print_progress(6, 6, "generando evidencia")
        z = self.write_evidence("batch", before, after, batch.kill_results, batch.start_results, batch)
        print(f"\n[PortCmd] ZIP: {z}")
        return 0 if batch.success else 1

    def menu(self) -> int:
        while True:
            statuses = self.status_all()
            self.print_status_table(statuses)
            print("Opciones:")
            print("  C1-C7 / A1-A7   cerrar/apagar ese puerto")
            print("  L1-L7 / E1-E7   levantar/encender ese puerto")
            print("  R1-R7           reiniciar ese puerto")
            print("  C1.C2.L4.A5     ejecutar varios en paralelo por fases al dar Enter")
            print("  LT              levantar todos los CLOSED")
            print("  S               refrescar status")
            print("  A               cerrar todos los puertos PRISMA locales (requiere: CERRAR TODO)")
            print("  Q               salir")
            choice = input("\nElige opcion/cadena: ").strip()
            if not choice:
                print("Opcion vacia. Escribe S, Q, C1, L4 o una cadena como C1.C2.L4.A5.")
                continue
            try:
                actions = self.parse_command_chain(choice)
                if any(a.op == "quit" for a in actions):
                    print("[PortCmd] Salida sin cambios adicionales.")
                    return 0
                code = self.do_batch(choice)
                input("\nEnter para volver al menu...")
                # Keep menu open even after failures, because this is an operator console.
            except Exception as exc:
                print("Error:", exc)
                input("\nEnter para volver al menu...")


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PRISMA Fast Ignit Port Commander")
    p.add_argument("--mode", choices=["menu", "status", "close", "close-all", "launch", "start", "restart", "batch"], default="menu")
    p.add_argument("--ports", default="")
    p.add_argument("--commands", default="")
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
        if args.mode in ("launch", "start"):
            return ctl.do_start(parse_ports(args.ports), mode="launch")
        if args.mode == "restart":
            ports = parse_ports(args.ports)
            return ctl.do_batch(".".join(f"R{PORTS.index(p)+1}" for p in ports))
        if args.mode == "batch":
            return ctl.do_batch(args.commands or args.ports)
        return ctl.menu()
    except Exception:
        err = traceback.format_exc()
        ctl.summary["status"] = "FAIL"
        ctl.summary["errors"].append(err)
        ctl.summary_path.write_text(json.dumps(ctl.summary, indent=2, ensure_ascii=False), encoding="utf-8")
        ctl.report_path.write_text("# PRISMA Fast Ignit Port Commander Report\n\nStatus: **FAIL**\n\n```text\n" + err + "\n```\n", encoding="utf-8")
        with zipfile.ZipFile(ctl.fail_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for p in [ctl.summary_path, ctl.report_path, ctl.log_path]:
                if p.exists():
                    z.write(p, p.relative_to(ctl.run_dir))
        print(err)
        print(f"\n[PortCmd] FAIL ZIP: {ctl.fail_zip}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
