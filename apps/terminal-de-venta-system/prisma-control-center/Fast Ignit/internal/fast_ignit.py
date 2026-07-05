#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Fast Ignit: parallel local boot sandbox.

Additive launcher, intentionally isolated under prisma-control-center/Fast Ignit.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import datetime as _dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import urllib.error
import zipfile
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

PORTS_ALL = [3000, 3110, 3120, 3130, 3140, 3150, 3160]


def now_stamp() -> str:
    return _dt.datetime.now().strftime("%d%m %H%M%S")


def iso_now() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def norm_path(p: Path) -> str:
    return str(p.resolve()) if p.exists() else str(p)


def print_progress(step: int, total: int, label: str) -> None:
    total = max(total, 1)
    pct = int(round((step / total) * 100))
    width = 24
    done = int(width * step / total)
    bar = "█" * done + "░" * (width - done)
    remain = max(0, 100 - pct)
    print(f"[{bar}] {pct:3d}% listo / {remain:3d}% restante :: {label}", flush=True)


def which_powershell() -> str:
    for name in ("pwsh.exe", "pwsh", "powershell.exe", "powershell"):
        exe = shutil.which(name)
        if exe:
            return exe
    return "powershell.exe"

def which_pnpm() -> str:
    """Return a Windows-safe pnpm executable.

    Fast Ignit launches some repo apps from services.json.  On the user's
    machine, `pnpm -C "..." run dev` is parsed by pnpm as a bad JSON config
    key named `dir`.  Since services.json already carries `cwd`, the canonical
    fast path is: chdir to that cwd, then run `pnpm run <script>` directly.
    """
    names = ("pnpm.cmd", "pnpm.exe", "pnpm") if os.name == "nt" else ("pnpm", "pnpm.cmd", "pnpm.exe")
    for name in names:
        exe = shutil.which(name)
        if exe:
            return exe
    return "pnpm.cmd" if os.name == "nt" else "pnpm"


def normalize_shell_command(command: str, cwd: str) -> Tuple[str, List[str] | str, str]:
    """Normalize known service commands without changing services.json.

    Returns (start_kind, start_command, note).  The important case is
    `pnpm -C <dir> run dev`: we already launch with cwd=<dir>, so pass argv
    directly as `pnpm run dev`. This avoids the user's pnpm config parser
    error and keeps the original architecture intact.
    """
    raw = (command or "").strip()
    m = re.match(r'^pnpm\s+-C\s+(?:"[^"]+"|\S+)\s+run\s+([^\s]+)(.*)$', raw, flags=re.IGNORECASE)
    if m:
        script = m.group(1).strip() or "dev"
        tail = (m.group(2) or "").strip()
        argv: List[str] = [which_pnpm(), "run", script]
        if tail:
            # Keep only simple argument tokens here. Current repo commands do not
            # need extra tail args, but preserving whitespace-split args is safer
            # than dropping them silently.
            argv.extend(tail.split())
        return "argv", argv, "normalized pnpm -C to cwd + pnpm run"
    return "shell", raw, "services.json"


def split_ports(text: str) -> List[int]:
    out: List[int] = []
    for raw in (text or "").replace(";", ",").split(","):
        raw = raw.strip()
        if not raw:
            continue
        if raw.lower() == "all":
            out.extend(PORTS_ALL)
            continue
        out.append(int(raw))
    seen = set()
    result = []
    for p in out:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result or list(PORTS_ALL)


@dataclass
class Service:
    id: str
    name: str
    port: int
    url: str
    cwd: str
    start_kind: str
    start_command: List[str] | str
    health_urls: List[str] = field(default_factory=list)
    source: str = "generated"
    reset_default: bool = False


@dataclass
class ServiceResult:
    id: str
    name: str
    port: int
    url: str
    action: str = "pending"
    ready: bool = False
    ready_url: str = ""
    pid: Optional[int] = None
    log_file: str = ""
    elapsed_sec: float = 0.0
    error: str = ""


class Tee:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.f = self.log_path.open("a", encoding="utf-8", errors="replace")

    def write(self, msg: str) -> None:
        sys.__stdout__.write(msg)
        self.f.write(msg)
        self.f.flush()

    def flush(self) -> None:
        sys.__stdout__.flush()
        self.f.flush()

    def close(self) -> None:
        self.f.close()


class FastIgnit:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.script_dir = Path(__file__).resolve().parent.parent
        self.fast_dir = self.script_dir
        self.control_root = self.fast_dir.parent
        self.terminal_root = self.control_root.parent
        self.repo_root = self.terminal_root.parent.parent
        self.out_base = Path(os.path.expandvars(args.output_dir or r"F:\descargasf"))
        self.stamp = now_stamp()
        self.run_dir = self.out_base / f"fastignit run {self.stamp}"
        self.logs_dir = self.run_dir / "logs"
        self.summary_path = self.run_dir / "summary.json"
        self.report_path = self.run_dir / "FAST_IGNIT_REPORT.md"
        self.latest_path = self.out_base / "latest_FAST_IGNIT_RUN.json"
        self.result_zip = self.out_base / f"fastignit run {self.stamp} result.zip"
        self.fail_zip = self.out_base / f"fastignit run {self.stamp} fail.zip"
        self.services: Dict[int, Service] = {}
        self.results: Dict[int, ServiceResult] = {}
        self.processes: Dict[int, subprocess.Popen] = {}
        self.stream_threads: List[threading.Thread] = []
        self.started_at = time.monotonic()
        self.out_base.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.tee = Tee(self.run_dir / "orchestrator.log")
        sys.stdout = self.tee  # type: ignore[assignment]
        sys.stderr = self.tee  # type: ignore[assignment]

    def close(self) -> None:
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.tee.close()
        except Exception:
            pass

    def load_services(self) -> None:
        cfg_path = self.control_root / "internal" / "config" / "services.json"
        if not cfg_path.exists():
            raise FileNotFoundError(f"No existe services.json: {cfg_path}")
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        services: Dict[int, Service] = {}
        for item in data.get("services", []):
            port = int(item["port"])
            base_url = item.get("localUrl") or f"http://127.0.0.1:{port}/"
            health_urls = []
            hp = item.get("healthPath") or "/"
            health_urls.append(base_url.rstrip("/") + "/" + hp.lstrip("/"))
            for alt in item.get("alternateHealthPaths", []) or []:
                health_urls.append(base_url.rstrip("/") + "/" + str(alt).lstrip("/"))
            health_urls.append(base_url)
            cwd = str(item.get("cwd") or self.terminal_root)
            start_kind, start_command, source_note = normalize_shell_command(str(item.get("startCommand") or ""), cwd)
            services[port] = Service(
                id=str(item.get("id") or f"port-{port}"),
                name=str(item.get("name") or f"PRISMA {port}"),
                port=port,
                url=base_url,
                cwd=cwd,
                start_kind=start_kind,
                start_command=start_command,
                health_urls=health_urls,
                source=source_note,
            )

        ps = which_powershell()
        wrappers = self.control_root / "internal" / "wrappers"
        services[3000] = Service(
            id="chart-lab-3000",
            name="PRISMA Chart Lab",
            port=3000,
            url="http://127.0.0.1:3000/",
            cwd=str(self.terminal_root),
            start_kind="argv",
            start_command=[which_pnpm(), "chart-lab:dev"],
            health_urls=["http://127.0.0.1:3000/"],
            source="vscode-terminal-native pnpm chart-lab:dev",
        )
        services[3150] = Service(
            id="control-center-3150",
            name="PRISMA Control Center",
            port=3150,
            url="http://127.0.0.1:3150/",
            cwd=str(self.control_root),
            start_kind="argv",
            start_command=[ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(wrappers / "_invoke_control_center.ps1"), "-Action", "panel"],
            health_urls=["http://127.0.0.1:3150/"],
            source="vscode-terminal-native _invoke_control_center.ps1 -Action panel",
        )
        services[3160] = Service(
            id="cloud-command-center-3160",
            name="PRISMA Cloud Command Center",
            port=3160,
            url="http://127.0.0.1:3160/unified-shell.html",
            cwd=str(self.control_root),
            start_kind="argv",
            start_command=[ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(wrappers / "cloud_command_center_3160.ps1"), "-Foreground", "-NoBrowser", "-OutputDir", str(self.out_base)],
            health_urls=["http://127.0.0.1:3160/unified-shell.html", "http://127.0.0.1:3160/"],
            source="wrapper cloud_command_center_3160.ps1",
            reset_default=True,
        )
        self.services = services

    def probe_url(self, url: str, timeout: float = 0.75) -> Tuple[bool, str]:
        req = urllib.request.Request(url, headers={"User-Agent": "PRISMA-Fast-Ignit/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = int(getattr(resp, "status", 200))
                return 200 <= code < 500, f"HTTP {code}"
        except Exception as exc:
            return False, str(exc)

    def service_ready(self, svc: Service) -> Tuple[bool, str, str]:
        last = ""
        for url in svc.health_urls or [svc.url]:
            ok, msg = self.probe_url(url)
            if ok:
                return True, url, msg
            last = f"{url}: {msg}"
        return False, "", last

    def _pump_child_output(self, svc: Service, proc: subprocess.Popen, log_file: Path) -> None:
        """Stream child output into the current VS Code integrated terminal.

        This is the important VSCODE_NATIVE_TERMINAL_MODE path: no detached
        PowerShell windows, no hidden external console.  Child stdout is copied
        to the service log and to this terminal with a stable port prefix.
        """
        prefix = f"[{svc.port} {svc.id}] "
        try:
            with log_file.open("a", encoding="utf-8", errors="replace") as log:
                if proc.stdout is None:
                    return
                for line in proc.stdout:
                    if not line:
                        break
                    log.write(line)
                    log.flush()
                    try:
                        print(prefix + line, end="", flush=True)
                    except Exception:
                        pass
        except Exception:
            try:
                with log_file.open("a", encoding="utf-8", errors="replace") as log:
                    log.write("\n[stream-error]\n" + traceback.format_exc() + "\n")
            except Exception:
                pass

    def start_service(self, svc: Service) -> ServiceResult:
        started = time.monotonic()
        log_file = self.logs_dir / f"{svc.port}_{svc.id}.log"
        result = ServiceResult(id=svc.id, name=svc.name, port=svc.port, url=svc.url, log_file=str(log_file))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update({
            "NO_COLOR": "1",
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8:replace",
            "PRISMA_FAST_IGNIT": "1",
            "PRISMA_VSCODE_NATIVE_TERMINAL": "1",
            "PRISMA_OUTPUT_DIR": str(self.out_base),
        })
        cwd = svc.cwd if svc.cwd and Path(svc.cwd).exists() else str(self.terminal_root)
        try:
            if svc.start_kind == "shell":
                cmd = ["cmd.exe", "/d", "/s", "/c", str(svc.start_command)] if os.name == "nt" else ["bash", "-lc", str(svc.start_command)]
            else:
                cmd = list(svc.start_command)  # type: ignore[arg-type]

            header = f"\n=== PRISMA Fast Ignit start {iso_now()} ===\ncmd={cmd!r}\ncwd={cwd}\nsource={svc.source}\nstream={bool(self.args.stream)}\n\n"
            with log_file.open("ab", buffering=0) as out:
                out.write(header.encode("utf-8", errors="replace"))

            creationflags = 0
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

            if bool(self.args.stream):
                proc = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    env=env,
                    creationflags=creationflags,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )
                t = threading.Thread(target=self._pump_child_output, args=(svc, proc, log_file), daemon=True)
                t.start()
                self.stream_threads.append(t)
            else:
                with log_file.open("ab", buffering=0) as out:
                    proc = subprocess.Popen(cmd, cwd=cwd, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env, creationflags=creationflags)

            result.pid = int(proc.pid)
            # Tiny grace period catches immediate CLI failures, so Fast Ignit
            # does not burn the whole readiness timeout when pnpm/node exits
            # in the first seconds.
            time.sleep(0.85)
            exit_code = proc.poll()
            if exit_code is None:
                result.action = "started"
                self.processes[svc.port] = proc
            else:
                result.action = "start-exited"
                result.error = f"process exited early with code {exit_code}"
                try:
                    tail = log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-24:]
                    if tail:
                        result.error += "\n" + "\n".join(tail)
                except Exception:
                    pass
        except Exception:
            result.action = "start-failed"
            result.error = traceback.format_exc()
        result.elapsed_sec = round(time.monotonic() - started, 3)
        return result

    def wait_ready(self, selected: List[Service], timeout_sec: int) -> None:
        deadline = time.monotonic() + timeout_sec
        total = len(selected)
        last_print = 0.0
        while time.monotonic() < deadline:
            ready_count = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(max(total, 1), 12)) as pool:
                future_map = {pool.submit(self.service_ready, svc): svc for svc in selected}
                for fut in concurrent.futures.as_completed(future_map, timeout=5):
                    svc = future_map[fut]
                    res = self.results[svc.port]
                    if res.ready:
                        ready_count += 1
                        continue
                    try:
                        ok, url, msg = fut.result()
                    except Exception as exc:
                        ok, url, msg = False, str(exc), str(exc)
                    if ok:
                        res.ready = True
                        res.ready_url = url
                        res.elapsed_sec = round(time.monotonic() - self.started_at, 3)
                        if res.action == "pending":
                            res.action = "reused"
                    else:
                        res.error = msg
                    if res.ready:
                        ready_count += 1
            if ready_count >= total:
                print_progress(total, total, "todos los puertos listos")
                return
            if time.monotonic() - last_print >= 1.0:
                last_print = time.monotonic()
                label = ", ".join(f"{p}:{'ok' if self.results[p].ready else '...'}" for p in sorted(self.results))
                print_progress(ready_count, total, label)
            time.sleep(0.75)

    def write_outputs(self, status: str, error: str = "") -> Path:
        elapsed = round(time.monotonic() - self.started_at, 3)
        summary = {
            "schemaVersion": "1.0",
            "tool": "PRISMA Fast Ignit",
            "mode": self.args.mode,
            "status": status,
            "startedAt": getattr(self, "started_iso", iso_now()),
            "finishedAt": iso_now(),
            "elapsedSec": elapsed,
            "error": error,
            "fastDir": str(self.fast_dir),
            "controlRoot": str(self.control_root),
            "terminalRoot": str(self.terminal_root),
            "repoRoot": str(self.repo_root),
            "resultZip": str(self.result_zip),
            "failZip": str(self.fail_zip),
            "runDir": str(self.run_dir),
            "selectedPorts": sorted(self.results),
            "services": [asdict(self.results[p]) for p in sorted(self.results)],
            "policy": {
                "parallelSandboxOnly": True,
                "replacesCurrentLaunchers": False,
                "defaultResetPorts": split_ports(self.args.reset_ports),
                "notes": "3160 reset is intentional; other ports use fast-resume unless explicitly reset."
            }
        }
        self.summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        self.latest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = []
        lines.append("# PRISMA Fast Ignit Report")
        lines.append("")
        lines.append(f"Status: **{status}**")
        lines.append(f"Elapsed: `{elapsed}s`")
        lines.append(f"Run dir: `{self.run_dir}`")
        lines.append("")
        lines.append("| Port | Service | Action | Ready | PID | Ready URL | Log |")
        lines.append("|---:|---|---|---|---:|---|---|")
        for p in sorted(self.results):
            r = self.results[p]
            lines.append(f"| {r.port} | {r.name} | {r.action} | {r.ready} | {r.pid or ''} | {r.ready_url} | `{r.log_file}` |")
        lines.append("")
        lines.append("## Policy")
        lines.append("")
        lines.append("- No reemplaza launchers actuales.")
        lines.append("- 3160 conserva reset/liberacion de puerto antes de iniciar.")
        lines.append("- Otros puertos se reutilizan si ya responden.")
        lines.append("- Evidencia completa en fail; evidencia ligera en pass.")
        if error:
            lines.append("")
            lines.append("## Error")
            lines.append("")
            lines.append("```text")
            lines.append(error)
            lines.append("```")
        self.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        zip_path = self.result_zip if status == "PASS" else self.fail_zip
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for path in [self.summary_path, self.report_path, self.run_dir / "orchestrator.log"]:
                if path.exists():
                    z.write(path, path.relative_to(self.run_dir))
            for log in self.logs_dir.glob("*.log"):
                try:
                    z.write(log, log.relative_to(self.run_dir))
                except Exception:
                    pass
        return zip_path

    def hold_terminal(self) -> int:
        """Keep the VS Code terminal attached to the live child processes."""
        if not bool(self.args.hold):
            return 0
        if not self.processes:
            print("\n[Fast Ignit] Hold solicitado, pero no hay procesos nuevos que mantener. Puertos reutilizados.", flush=True)
            return 0
        print("\n[Fast Ignit] VS Code terminal live mode: servicios corriendo dentro de esta terminal.", flush=True)
        print("[Fast Ignit] Ctrl+C apaga los procesos iniciados por Fast Ignit.", flush=True)
        try:
            while True:
                alive = {p: proc for p, proc in self.processes.items() if proc.poll() is None}
                if not alive:
                    print("[Fast Ignit] Todos los procesos hijos terminaron.", flush=True)
                    return 0
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[Fast Ignit] Ctrl+C recibido. Terminando procesos hijos...", flush=True)
            for port, proc in list(self.processes.items()):
                if proc.poll() is None:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                if all(proc.poll() is not None for proc in self.processes.values()):
                    break
                time.sleep(0.25)
            for port, proc in list(self.processes.items()):
                if proc.poll() is None:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            return 130

    def run(self) -> int:
        self.started_iso = iso_now()
        print("PRISMA Fast Ignit :: sandbox paralelo", flush=True)
        print(f"Fast dir: {self.fast_dir}")
        print(f"Control root: {self.control_root}")
        print(f"Salida: {self.run_dir}")
        try:
            print_progress(1, 6, "cargando services.json")
            self.load_services()
            selected_ports = split_ports(self.args.ports)
            selected = []
            for port in selected_ports:
                if port not in self.services:
                    raise ValueError(f"Puerto no soportado por Fast Ignit: {port}")
                selected.append(self.services[port])
                svc = self.services[port]
                self.results[port] = ServiceResult(id=svc.id, name=svc.name, port=svc.port, url=svc.url)
            reset_ports = set(split_ports(self.args.reset_ports or "")) if self.args.reset_ports else set()
            print_progress(2, 6, "probando reutilizacion rapida")
            to_start: List[Service] = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(selected), 12) or 1) as pool:
                futs = {pool.submit(self.service_ready, svc): svc for svc in selected}
                for fut in concurrent.futures.as_completed(futs):
                    svc = futs[fut]
                    res = self.results[svc.port]
                    ok, url, msg = fut.result()
                    if ok and svc.port not in reset_ports and self.args.mode != "clean":
                        res.action = "reused"
                        res.ready = True
                        res.ready_url = url
                        res.elapsed_sec = round(time.monotonic() - self.started_at, 3)
                    else:
                        res.action = "pending-start"
                        res.error = "reset-required" if svc.port in reset_ports else msg
                        to_start.append(svc)
            print_progress(3, 6, f"arranque paralelo: {len(to_start)} servicio(s)")
            if self.args.mode == "status":
                status = "PASS" if all(r.ready for r in self.results.values()) else "FAIL"
                zip_path = self.write_outputs(status)
                print(f"\n[Fast Ignit] Status ZIP: {zip_path}")
                return 0 if status == "PASS" else 1
            # Launch with bounded concurrency.
            max_workers = max(1, int(self.args.concurrency))
            for i in range(0, len(to_start), max_workers):
                batch = to_start[i:i + max_workers]
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
                    for res in pool.map(self.start_service, batch):
                        self.results[res.port] = res
                        print(f"[start] {res.port} {res.name}: {res.action} pid={res.pid or ''} log={res.log_file}", flush=True)
                if i + max_workers < len(to_start):
                    time.sleep(0.75)
            print_progress(4, 6, "esperando HTTP ready")
            self.wait_ready(selected, int(self.args.timeout))
            print_progress(5, 6, "generando evidencia")
            all_ready = all(self.results[p].ready for p in self.results)
            status = "PASS" if all_ready else "FAIL"
            zip_path = self.write_outputs(status)
            print_progress(6, 6, f"{status}: {zip_path}")
            print(f"\n[Fast Ignit] Reporte: {self.report_path}")
            print(f"[Fast Ignit] ZIP: {zip_path}")
            if all_ready:
                hold_code = self.hold_terminal()
                if hold_code:
                    return hold_code
            return 0 if all_ready else 1
        except Exception:
            err = traceback.format_exc()
            print(err, flush=True)
            try:
                zip_path = self.write_outputs("FAIL", error=err)
                print(f"[Fast Ignit] FAIL ZIP: {zip_path}")
            except Exception:
                print("No pude generar FAIL ZIP:\n" + traceback.format_exc(), flush=True)
            return 1
        finally:
            self.close()


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PRISMA Fast Ignit parallel boot sandbox")
    p.add_argument("--mode", choices=["start", "status", "clean"], default="start")
    p.add_argument("--ports", default="3000,3110,3120,3130,3140,3150,3160")
    p.add_argument("--reset-ports", default="3160", help="Ports that should not be reused. Default: 3160.")
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--output-dir", default=r"F:\descargasf")
    p.add_argument("--stream", action="store_true", help="Stream child service logs into the current terminal.")
    p.add_argument("--hold", action="store_true", help="After readiness PASS, keep this terminal attached to child processes.")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    return FastIgnit(args).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
