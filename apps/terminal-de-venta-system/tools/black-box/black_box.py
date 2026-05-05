#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

APP = "PRISMA_BLACK_BOX_RUNTIME_SUPERVISOR_I02"
VER = "20260505_i02_v01"
DEFAULT_ROOT = Path(os.environ.get("PRISMA_ROOT", r"F:\repos\hitech-os\apps\terminal-de-venta-system"))
DEFAULT_OUT = Path(os.environ.get("PRISMA_BLACK_BOX_OUT", r"F:\descargasf"))

APPS: dict[str, dict[str, Any]] = {
    "tablet": {"rel": "products/tablet/app", "port": 3120, "url": "http://127.0.0.1:3120/prisma-dark-pos-reference", "script": "dev"},
    "pc": {"rel": "products/pc/app", "port": 3130, "url": "http://127.0.0.1:3130/", "script": "dev"},
    "mobile": {"rel": "products/mobile/app", "port": 3140, "url": "http://127.0.0.1:3140/prisma-app", "script": "dev"},
}

PATTERNS = [
    ("PRISMA_PREFLIGHT_SCRIPT_NOT_FOUND", r"Prisma preflight script not found|preflight script not found.*repair_prisma_client_pnpm_bridge|not found:\s*.*repair_prisma_client_pnpm_bridge", "restore_prisma_bridge", "Falta el bridge de Prisma que exige terminal_de_venta.cmd.", "FAIL"),
    ("PRISMA_CLIENT_GENERATE_FAILED", r"Could not resolve @prisma/client|Please try to install it with npm install @prisma/client", None, "Prisma generate no pudo resolver @prisma/client.", "WARN"),
    ("PNPM_NO_SCRIPT", r"ERR_PNPM_NO_SCRIPT|Missing script:", None, "Script inexistente o comando pegado mal.", "FAIL"),
    ("PORT_IN_USE", r"EADDRINUSE|address already in use", None, "Puerto ocupado.", "FAIL"),
    ("NODE_MODULE_NOT_FOUND", r"Cannot find module|Module not found|ERR_MODULE_NOT_FOUND", None, "Modulo o dependencia faltante.", "FAIL"),
    ("PRISMA_UNIQUE_CONSTRAINT", r"P2002|Unique constraint failed", None, "Duplicado contra constraint unico de Prisma.", "FAIL"),
    ("PRISMA_TABLE_NOT_FOUND", r"P2021|table .* does not exist", None, "Tabla de DB faltante.", "FAIL"),
    ("TS_BAD_EXPORT", r"TS2305|has no exported member", None, "Import/export roto en TypeScript.", "FAIL"),
    ("TS_IMPLICIT_ANY", r"TS7006|implicitly has an .*any.* type", None, "Parametro sin tipo en TypeScript.", "FAIL"),
    ("COMMAND_COMPOSITION_ERROR", r"typecheckpython|buildpython|devpython", None, "Dos comandos pegados sin separador.", "FAIL"),
    ("NEXT_ROUTE_ERROR", r"Error:\s.*Next|Unhandled Runtime Error|Internal Server Error", None, "Error runtime de Next detectado en logs.", "FAIL"),
]

BRIDGE = r'''param(
  [Parameter(Mandatory=$true)][string]$Root,
  [Parameter(Mandatory=$true)][ValidateSet("tablet","pc")][string]$Product
)
$ErrorActionPreference = "Stop"
$OutDir = "F:\descargasf"
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$Log = Join-Path $OutDir ("prisma_" + $Product + "_dev_preflight_last.log")
Set-Content -LiteralPath $Log -Value ""
function L([string]$m) { ("[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $m) | Tee-Object -FilePath $Log -Append }
function Run-Native([string]$File, [string[]]$NativeArgs) {
  L ("RUN " + $File + " " + ($NativeArgs -join " "))
  $stdoutFile = Join-Path $env:TEMP ("prisma-preflight-out-" + [Guid]::NewGuid().ToString() + ".txt")
  $stderrFile = Join-Path $env:TEMP ("prisma-preflight-err-" + [Guid]::NewGuid().ToString() + ".txt")
  try {
    & $File @NativeArgs 1> $stdoutFile 2> $stderrFile
    $rc = $LASTEXITCODE
    if (Test-Path $stdoutFile) { Get-Content $stdoutFile -ErrorAction SilentlyContinue | ForEach-Object { L ("OUT " + $_) } }
    if (Test-Path $stderrFile) { Get-Content $stderrFile -ErrorAction SilentlyContinue | ForEach-Object { L ("ERR " + $_) } }
    L ("EXIT " + $rc)
    return $rc
  } finally {
    Remove-Item -LiteralPath $stdoutFile,$stderrFile -Force -ErrorAction SilentlyContinue
  }
}
L ("PRISMA DEV PREFLIGHT 00G START product=" + $Product)
L ("Root=" + $Root)
if (-not (Test-Path -LiteralPath $Root)) { L "FAIL root missing"; exit 2 }
if ($Product -eq "tablet") {
  $App = Join-Path $Root "products\tablet\app"
  $Schema = Join-Path $App "prisma\schema.prisma"
  $Db = Join-Path $App "data\tablet-pos.db"
  $env:DATABASE_URL = "file:" + (($Db) -replace "\\","/")
  $env:TABLET_DATABASE_URL = $env:DATABASE_URL
  $env:TABLET_RUNTIME_MODE = "standalone"
  L "Notes=Tablet uses standalone local SQLite DB."
} else {
  $App = Join-Path $Root "products\pc\app"
  $Schema = Join-Path $Root "prisma\schema.prisma"
  $Db = Join-Path $Root "tools\_local\data\terminal-de-venta-system\canonical.db"
  $env:DATABASE_URL = "file:" + (($Db) -replace "\\","/")
  $env:PC_DATABASE_URL = $env:DATABASE_URL
  L "Notes=PC uses canonical root Prisma schema and canonical SQLite DB; generate is non-blocking in dev preflight."
}
L ("App=" + $App)
L ("Schema=" + $Schema)
L ("DatabaseUrl=" + $env:DATABASE_URL)
$env:PRISMA_HIDE_UPDATE_MESSAGE = "1"
if (-not (Test-Path -LiteralPath (Join-Path $App "package.json"))) { L "FAIL app package missing"; exit 3 }
if (-not (Test-Path -LiteralPath $Schema)) { L "WARN schema missing"; exit 0 }
$Pnpm = (Get-Command pnpm.cmd -ErrorAction SilentlyContinue).Source
if (-not $Pnpm) { $Pnpm = (Get-Command pnpm -ErrorAction SilentlyContinue).Source }
if (-not $Pnpm) { L "FAIL pnpm missing"; exit 4 }
L ("pnpm=" + $Pnpm)
$nextCache = Join-Path $App ".next"
if (Test-Path -LiteralPath $nextCache) { L ("Removing stale Next cache: " + $nextCache); Remove-Item -LiteralPath $nextCache -Recurse -Force -ErrorAction SilentlyContinue }
$rc = Run-Native $Pnpm @("-C", $App, "exec", "prisma", "validate", "--schema", $Schema)
if ($rc -ne 0) { L ("FAIL prisma validate " + $rc); exit $rc }
$rc = Run-Native $Pnpm @("-C", $App, "exec", "prisma", "generate", "--schema", $Schema)
if ($rc -ne 0) { L ("WARN Prisma generate failed for " + $Product + ", but this is non-blocking for dev if import succeeds.") } else { L ("Prisma generate OK for " + $Product) }
$rc = Run-Native $Pnpm @("-C", $App, "exec", "prisma", "db", "push", "--schema", $Schema, "--skip-generate")
if ($rc -ne 0) { L ("FAIL prisma db push " + $rc); exit $rc }
$rc = Run-Native "node" @("-e", "const { PrismaClient } = require('@prisma/client'); console.log('OK PrismaClient import:', typeof PrismaClient);")
if ($rc -ne 0) { L ("FAIL PrismaClient import " + $rc); exit $rc }
L ("PRISMA DEV PREFLIGHT 00G OK product=" + $Product)
exit 0
'''

@dataclass
class ProbeResult:
    probe: str
    name: str
    status: str
    summary: str
    evidence: str = ""
    recommendation: str = ""
    app: str = "repo"
    code: str = ""

@dataclass
class ProcessInfo:
    pid: int | None = None
    command_line: str = ""
    source: str = ""


def safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def now_stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M%S")


def resolve_root(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    for candidate in [Path.cwd(), *Path.cwd().parents, DEFAULT_ROOT]:
        try:
            c = candidate.resolve()
        except Exception:
            c = candidate
        if (c / "terminal_de_venta.cmd").exists() and (c / "products").exists():
            return c
    return DEFAULT_ROOT


def out_dir(value: str | None) -> Path:
    p = Path(value).expanduser() if value else DEFAULT_OUT
    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def run_capture(cmd: list[str], cwd: Path | None = None, timeout: float = 8.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, timeout=timeout, shell=False)
        return int(p.returncode), p.stdout or "", p.stderr or ""
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or f"timeout after {timeout}s"
    except Exception as exc:
        return 1, "", f"{type(exc).__name__}: {exc}"


def which(name: str) -> str | None:
    found = shutil.which(name)
    return found


def tcp_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", int(port)), timeout=0.35):
            return True
    except OSError:
        return False


def http_probe(url: str, timeout: float = 1.25) -> tuple[str, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "prisma-black-box/i02"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = int(getattr(resp, "status", 0) or 0)
            if 200 <= code < 500:
                return "OK", f"HTTP {code}"
            return "FAIL", f"HTTP {code}"
    except Exception as exc:
        return "WARN", f"No responde HTTP: {type(exc).__name__}: {exc}"


def candidate_logs(root: Path, out: Path) -> list[Path]:
    dirs = [root / "tools/_local/logs", root / "tools/_local", out]
    if root.name.lower() == "terminal-de-venta-system" and root.parent.name.lower() == "apps":
        dirs.append(root.parent.parent / "tools/_local/logs")
    files: list[Path] = []
    for d in dirs:
        if not d.exists():
            continue
        for pat in ["*.log", "*.txt", "*.err", "*.out", "*.jsonl"]:
            files.extend([p for p in d.glob(pat) if p.is_file()])
    excluded = ("prisma_black_box", "black_box_", "evidence_05a", "install_black_box", "blackbox")
    files = [p for p in files if not any(token in p.name.lower() for token in excluded)]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:60]


def preflight_ok_for_log(text: str) -> bool:
    return "PRISMA DEV PREFLIGHT" in text and " OK product=" in text


def classify_log(text: str, source: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    active: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    preflight_ok = preflight_ok_for_log(text)
    for line_no, line in enumerate(text.splitlines(), 1):
        for pattern_id, regex, safe_fix, message, default_severity in PATTERNS:
            if not re.search(regex, line, re.IGNORECASE):
                continue
            severity = default_severity
            bucket = active
            if preflight_ok and pattern_id in {"PRISMA_CLIENT_GENERATE_FAILED", "NODE_MODULE_NOT_FOUND"}:
                severity = "RESOLVED_WARN"
                bucket = resolved
            bucket.append({
                "pattern_id": pattern_id,
                "severity": severity,
                "summary": message,
                "source": source,
                "line": line_no,
                "text": line[:500],
                "safe_fix": safe_fix,
            })
    return active, resolved


def state_dir(root: Path) -> Path:
    return root / "tools" / "_local" / "black-box"


def state_file(root: Path) -> Path:
    return state_dir(root) / "runtime_state.json"


def load_state(root: Path) -> dict[str, Any]:
    path = state_file(root)
    if not path.exists():
        return {"version": VER, "processes": {}}
    try:
        data = read_json(path)
        if not isinstance(data, dict):
            return {"version": VER, "processes": {}}
        data.setdefault("processes", {})
        return data
    except Exception:
        return {"version": VER, "processes": {}}


def save_state(root: Path, data: dict[str, Any]) -> None:
    data["version"] = VER
    data["updated_at"] = dt.datetime.now().isoformat(timespec="seconds")
    write_json(state_file(root), data)


def normalize_for_compare(path: Path | str) -> str:
    return str(path).replace("/", "\\").lower()


def get_port_owner(port: int) -> ProcessInfo:
    if os.name == "nt":
        ps = (
            "$c=Get-NetTCPConnection -LocalPort " + str(port) + " -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1;"
            "if($c){$p=Get-CimInstance Win32_Process -Filter \"ProcessId = $($c.OwningProcess)\" -ErrorAction SilentlyContinue;"
            "$o=[pscustomobject]@{pid=$c.OwningProcess;commandLine=$p.CommandLine};$o|ConvertTo-Json -Compress}"
        )
        rc, stdout, _ = run_capture(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], timeout=5)
        if rc == 0 and stdout.strip():
            try:
                data = json.loads(stdout.strip())
                return ProcessInfo(pid=int(data.get("pid") or 0), command_line=str(data.get("commandLine") or ""), source="Get-NetTCPConnection")
            except Exception:
                pass
        rc, stdout, _ = run_capture(["netstat", "-ano"], timeout=5)
        if rc == 0:
            for line in stdout.splitlines():
                if f":{port}" in line and "LISTEN" in line.upper():
                    parts = line.split()
                    try:
                        pid = int(parts[-1])
                    except Exception:
                        continue
                    return ProcessInfo(pid=pid, command_line="", source="netstat")
    else:
        rc, stdout, _ = run_capture(["bash", "-lc", f"lsof -nP -iTCP:{port} -sTCP:LISTEN -t 2>/dev/null | head -1"], timeout=3)
        if rc == 0 and stdout.strip().isdigit():
            return ProcessInfo(pid=int(stdout.strip()), source="lsof")
    return ProcessInfo()


def get_pid_command_line(pid: int | None) -> str:
    if not pid:
        return ""
    if os.name == "nt":
        ps = f"$p=Get-CimInstance Win32_Process -Filter \"ProcessId = {pid}\" -ErrorAction SilentlyContinue; if($p){{$p.CommandLine}}"
        rc, stdout, _ = run_capture(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], timeout=5)
        return stdout.strip() if rc == 0 else ""
    try:
        path = Path(f"/proc/{pid}/cmdline")
        if path.exists():
            return path.read_bytes().replace(b"\x00", b" ").decode("utf-8", "replace").strip()
    except Exception:
        pass
    return ""


def process_alive(pid: int | None) -> bool:
    if not pid:
        return False
    if os.name == "nt":
        rc, stdout, _ = run_capture(["tasklist", "/FI", f"PID eq {pid}"], timeout=5)
        return rc == 0 and str(pid) in stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def is_probably_owned(root: Path, app_root: Path, cmdline: str, recorded_pid: bool = False) -> bool:
    if recorded_pid:
        return True
    needle_root = normalize_for_compare(root)
    needle_app = normalize_for_compare(app_root)
    hay = cmdline.replace("/", "\\").lower()
    return bool(hay) and (needle_app in hay or needle_root in hay)


def logs_dir(root: Path) -> Path:
    d = root / "tools" / "_local" / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def app_info(root: Path, app: str) -> dict[str, Any]:
    if app not in APPS:
        raise ValueError(f"app invalida: {app}")
    info = dict(APPS[app])
    info["root"] = root / info["rel"]
    return info


def probe_repo(root: Path) -> list[ProbeResult]:
    checks: list[ProbeResult] = []
    checks.append(ProbeResult("repo", "terminal_de_venta.cmd", "OK" if (root / "terminal_de_venta.cmd").exists() else "FAIL", "Launcher principal existe" if (root / "terminal_de_venta.cmd").exists() else "Falta terminal_de_venta.cmd", str(root / "terminal_de_venta.cmd")))
    checks.append(ProbeResult("repo", "products", "OK" if (root / "products").exists() else "FAIL", "Carpeta products existe" if (root / "products").exists() else "Falta carpeta products", str(root / "products")))
    checks.append(ProbeResult("repo", "black-box", "OK" if (root / "tools/black-box/black_box.py").exists() else "WARN", "black-box instalado" if (root / "tools/black-box/black_box.py").exists() else "black-box no instalado en tools/black-box", str(root / "tools/black-box/black_box.py")))
    bridge = root / "tools/_local/repair_prisma_client_pnpm_bridge.ps1"
    checks.append(ProbeResult("repo", "prisma bridge", "OK" if bridge.exists() else "FAIL", "Bridge Prisma existe" if bridge.exists() else "Falta bridge Prisma requerido por pc-dev/tablet-dev", str(bridge), "repair apply --safe", "repo", "PRISMA_PREFLIGHT_SCRIPT_NOT_FOUND" if not bridge.exists() else ""))
    return checks


def probe_toolchain() -> list[ProbeResult]:
    checks: list[ProbeResult] = []
    for tool in ["python", "node", "pnpm", "pnpm.cmd"]:
        found = which(tool)
        checks.append(ProbeResult("toolchain", tool, "OK" if found else ("WARN" if tool == "pnpm.cmd" else "FAIL"), f"{tool}={'OK' if found else 'no encontrado'}", found or ""))
    return checks


def probe_packages(root: Path) -> list[ProbeResult]:
    checks: list[ProbeResult] = []
    for app, meta in APPS.items():
        app_root = root / meta["rel"]
        pkg = app_root / "package.json"
        if not pkg.exists():
            checks.append(ProbeResult("package", f"{app} package", "FAIL", f"Falta package.json de {app}", str(pkg), app=app))
            continue
        try:
            data = read_json(pkg)
            scripts = data.get("scripts", {}) if isinstance(data.get("scripts"), dict) else {}
            checks.append(ProbeResult("package", f"{app} package", "OK", f"package.json de {app} existe", str(pkg), app=app))
            for script in ["dev", "typecheck"]:
                checks.append(ProbeResult("package", f"{app}:{script}", "OK" if script in scripts else "WARN", f"script {script} {'existe' if script in scripts else 'no existe'}", str(pkg), app=app))
        except Exception as exc:
            checks.append(ProbeResult("package", f"{app} package parse", "FAIL", f"No se pudo leer package.json: {exc}", str(pkg), app=app))
    return checks


def probe_ports_and_http(root: Path) -> list[ProbeResult]:
    checks: list[ProbeResult] = []
    for app, meta in APPS.items():
        port = int(meta["port"])
        owner = get_port_owner(port) if tcp_open(port) else ProcessInfo()
        owner_line = owner.command_line or get_pid_command_line(owner.pid)
        if tcp_open(port):
            checks.append(ProbeResult("port", f"{app}:{port}", "OK", f"Puerto {port} escucha" + (f" PID={owner.pid}" if owner.pid else ""), owner_line, app=app))
        else:
            checks.append(ProbeResult("port", f"{app}:{port}", "WARN", f"Puerto {port} no escucha", "", "start " + app, app=app))
        http_status, summary = http_probe(str(meta["url"]))
        checks.append(ProbeResult("http", f"{app} endpoint", http_status, summary, str(meta["url"]), app=app))
    return checks


def probe_logs(root: Path, out: Path) -> tuple[list[ProbeResult], list[dict[str, Any]], list[dict[str, Any]]]:
    checks: list[ProbeResult] = []
    active: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    logs = candidate_logs(root, out)
    if not logs:
        return [ProbeResult("logs", "recent logs", "WARN", "No encontre logs recientes", str(root / "tools/_local/logs"))], active, resolved
    checks.append(ProbeResult("logs", "recent logs", "OK", f"{len(logs)} logs candidatos revisados", "; ".join(str(p) for p in logs[:8])))
    for path in logs:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[-24000:]
        except Exception:
            continue
        a, r = classify_log(text, str(path))
        active.extend(a)
        resolved.extend(r)
    if active:
        checks.append(ProbeResult("logs", "active known failures", "FAIL", f"{len(active)} patrones activos detectados", active[0].get("source", ""), code=active[0].get("pattern_id", "")))
    elif resolved:
        checks.append(ProbeResult("logs", "resolved known failures", "WARN", f"{len(resolved)} patrones historicos/resueltos detectados", resolved[0].get("source", ""), code=resolved[0].get("pattern_id", "")))
    else:
        checks.append(ProbeResult("logs", "known failure patterns", "OK", "Sin patrones activos conocidos en logs recientes"))
    return checks, active, resolved


def summarize(checks: list[ProbeResult], active: list[dict[str, Any]], resolved: list[dict[str, Any]]) -> dict[str, Any]:
    fail_count = sum(1 for c in checks if c.status == "FAIL")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    ok_count = sum(1 for c in checks if c.status == "OK")
    if active or fail_count:
        status = "BLOCKED"
    elif warn_count or resolved:
        status = "READY_WITH_CAVEATS"
    else:
        status = "READY"
    if active:
        root_cause = active[0]
        active_code = root_cause.get("pattern_id", "ACTIVE_FAILURE")
        active_summary = root_cause.get("summary", "Falla activa detectada")
    else:
        fail = next((c for c in checks if c.status == "FAIL"), None)
        if fail:
            active_code = fail.code or "FAILED_CHECK"
            active_summary = fail.summary
            root_cause = asdict(fail)
        else:
            active_code = "NO_ACTIVE_FAILURE"
            active_summary = "Sin causa raiz activa. El estado actual no esta bloqueado."
            root_cause = {"pattern_id": active_code, "summary": active_summary}
    if resolved:
        primary_caveat = {"pattern_id": resolved[0].get("pattern_id"), "summary": f"{resolved[0].get('pattern_id')} - {len(resolved)} patrones historicos/resueltos detectados.", "evidence": resolved[0].get("source", "")}
    elif warn_count:
        warn = next((c for c in checks if c.status == "WARN"), None)
        primary_caveat = asdict(warn) if warn else None
    else:
        primary_caveat = None
    return {
        "status": status,
        "ok": ok_count,
        "warn": warn_count,
        "fail": fail_count,
        "active_hits": len(active),
        "resolved_hits": len(resolved),
        "active_code": active_code,
        "active_summary": active_summary,
        "active_root_cause": root_cause,
        "primary_caveat": primary_caveat,
    }




def run_probe_snapshot(root: Path, out: Path) -> tuple[dict[str, Any], list[ProbeResult], list[dict[str, Any]], list[dict[str, Any]]]:
    """Run probes without emitting a full markdown/json report.

    This is used by watch mode so it can act like a heartbeat instead of
    wallpapering the output directory with reports every interval. Because
    apparently logs can reproduce like gremlins if you feed them after midnight.
    """
    checks: list[ProbeResult] = []
    active: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    checks.extend(probe_repo(root))
    checks.extend(probe_toolchain())
    checks.extend(probe_packages(root))
    checks.extend(probe_ports_and_http(root))
    log_checks, a, r = probe_logs(root, out)
    checks.extend(log_checks)
    active.extend(a)
    resolved.extend(r)
    summary = summarize(checks, active, resolved)
    return summary, checks, active, resolved


def watch_signature(summary: dict[str, Any]) -> str:
    caveat = summary.get("primary_caveat") or {}
    return "|".join([
        str(summary.get("status")),
        str(summary.get("active_code")),
        str(summary.get("fail")),
        str(summary.get("warn")),
        str(summary.get("active_hits")),
        str(caveat.get("pattern_id") or caveat.get("code") or caveat.get("name") or ""),
    ])

def build_report(root: Path, out: Path, checks: list[ProbeResult], active: list[dict[str, Any]], resolved: list[dict[str, Any]]) -> tuple[dict[str, Any], Path, Path]:
    summary = summarize(checks, active, resolved)
    stamp = now_stamp()
    md_path = out / f"prisma_black_box_i02_{stamp}.md"
    json_path = out / f"prisma_black_box_i02_{stamp}.json"
    lines = [
        f"# PRISMA black-box i02 report",
        "",
        f"- Status: `{summary['status']}`",
        f"- Root: `{root}`",
        f"- Active root cause: `{summary['active_code']}` - {summary['active_summary']}",
    ]
    if summary.get("primary_caveat"):
        pc = summary["primary_caveat"]
        lines.append(f"- Primary caveat: `{pc.get('pattern_id') or pc.get('code') or pc.get('name')}` - {pc.get('summary')}")
    lines.extend([
        f"- Checks: OK={summary['ok']} WARN={summary['warn']} FAIL={summary['fail']} ACTIVE_HITS={summary['active_hits']} RESOLVED_HITS={summary['resolved_hits']}",
        "",
        "## Checks",
        "",
        "| Probe | Name | Status | Summary | Evidence |",
        "|---|---|---:|---|---|",
    ])
    for c in checks:
        ev = (c.evidence or "").replace("|", "\\|")[:240]
        lines.append(f"| {c.probe} | {c.name} | {c.status} | {c.summary.replace('|','/')} | {ev} |")
    if active:
        lines.extend(["", "## Active error hits", ""])
        for h in active[:25]:
            lines.append(f"- `{h.get('pattern_id')}` {h.get('source')}:{h.get('line')} - {h.get('text')}")
    if resolved:
        lines.extend(["", "## Historical/resolved hits", ""])
        for h in resolved[:25]:
            lines.append(f"- `{h.get('pattern_id')}` {h.get('source')}:{h.get('line')} - {h.get('text')}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(json_path, {"app": APP, "version": VER, "root": str(root), "summary": summary, "checks": [asdict(c) for c in checks], "active_hits": active, "resolved_hits": resolved})
    append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "app": APP, "event": "doctor", "status": summary["status"], "root": str(root), "summary": summary, "report": str(md_path)})
    return summary, md_path, json_path


def run_doctor(root: Path, out: Path) -> tuple[dict[str, Any], Path, Path]:
    checks: list[ProbeResult] = []
    active: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    checks.extend(probe_repo(root))
    checks.extend(probe_toolchain())
    checks.extend(probe_packages(root))
    checks.extend(probe_ports_and_http(root))
    log_checks, a, r = probe_logs(root, out)
    checks.extend(log_checks)
    active.extend(a)
    resolved.extend(r)
    return build_report(root, out, checks, active, resolved)


def collect(root: Path, out: Path) -> Path:
    summary, md_path, json_path = run_doctor(root, out)
    stamp = now_stamp()
    zip_path = out / f"prisma_black_box_evidence_i02_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in [md_path, json_path, state_file(root)]:
            if p.exists():
                z.write(p, p.name)
        for p in candidate_logs(root, out)[:20]:
            try:
                z.write(p, "logs/" + p.name)
            except Exception:
                pass
        for app, meta in APPS.items():
            pkg = root / meta["rel"] / "package.json"
            if pkg.exists():
                z.write(pkg, f"packages/{app}-package.json")
        launcher = root / "terminal_de_venta.cmd"
        if launcher.exists():
            z.write(launcher, "terminal_de_venta.cmd")
    append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "app": APP, "event": "collect", "status": summary["status"], "zip": str(zip_path)})
    return zip_path


def repair_plan(root: Path, out: Path) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    bridge = root / "tools/_local/repair_prisma_client_pnpm_bridge.ps1"
    if not bridge.exists():
        plan.append({"id": "restore_prisma_bridge", "risk": "low", "summary": "Restaurar tools/_local/repair_prisma_client_pnpm_bridge.ps1", "target": str(bridge)})
    if not (root / "tools/_local/logs").exists():
        plan.append({"id": "ensure_log_dirs", "risk": "low", "summary": "Crear tools/_local/logs", "target": str(root / "tools/_local/logs")})
    if not plan:
        plan.append({"id": "no_safe_repairs", "risk": "none", "summary": "No hay reparaciones seguras pendientes", "target": str(root)})
    write_json(out / f"prisma_black_box_repair_plan_i02_{now_stamp()}.json", plan)
    return plan


def apply_safe_repairs(root: Path, out: Path) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    bridge = root / "tools/_local/repair_prisma_client_pnpm_bridge.ps1"
    if not bridge.exists():
        bridge.parent.mkdir(parents=True, exist_ok=True)
        bridge.write_text(BRIDGE, encoding="utf-8")
        applied.append({"id": "restore_prisma_bridge", "status": "fixed", "target": str(bridge)})
    logs = root / "tools/_local/logs"
    if not logs.exists():
        logs.mkdir(parents=True, exist_ok=True)
        applied.append({"id": "ensure_log_dirs", "status": "fixed", "target": str(logs)})
    if not applied:
        applied.append({"id": "no_safe_repairs", "status": "noop", "target": str(root)})
    write_json(out / f"prisma_black_box_repair_apply_i02_{now_stamp()}.json", applied)
    return applied


def pnpm_path() -> str | None:
    return which("pnpm.cmd") or which("pnpm")


def app_log_paths(root: Path, app: str) -> tuple[Path, Path]:
    d = logs_dir(root)
    return d / f"terminal-{app}-dev.out.log", d / f"terminal-{app}-dev.err.log"


def check_start_preconditions(root: Path, app: str) -> tuple[bool, str]:
    info = app_info(root, app)
    app_root = info["root"]
    pkg = app_root / "package.json"
    if not pkg.exists():
        return False, f"Falta package.json: {pkg}"
    try:
        data = read_json(pkg)
    except Exception as exc:
        return False, f"package.json invalido: {pkg}: {exc}"
    scripts = data.get("scripts", {}) if isinstance(data.get("scripts"), dict) else {}
    if "dev" not in scripts:
        return False, f"Falta script dev en {pkg}"
    if not pnpm_path():
        return False, "pnpm/pnpm.cmd no encontrado en PATH"
    return True, "OK"


def wait_for_health(url: str, timeout_seconds: int) -> tuple[bool, str]:
    deadline = time.time() + max(1, timeout_seconds)
    last = "not checked"
    while time.time() < deadline:
        status, summary = http_probe(url, timeout=1.5)
        last = summary
        if status == "OK":
            return True, summary
        time.sleep(1.0)
    return False, last


def start_one(root: Path, out: Path, app: str, timeout_seconds: int = 35) -> dict[str, Any]:
    info = app_info(root, app)
    app_root: Path = info["root"]
    port = int(info["port"])
    url = str(info["url"])
    state = load_state(root)
    out_log, err_log = app_log_paths(root, app)
    out_log.parent.mkdir(parents=True, exist_ok=True)

    if tcp_open(port):
        owner = get_port_owner(port)
        cmdline = owner.command_line or get_pid_command_line(owner.pid)
        http_status, http_summary = http_probe(url)
        result = {"app": app, "status": "already_running" if http_status == "OK" else "port_occupied", "port": port, "pid": owner.pid, "command_line": cmdline, "http": http_summary, "url": url}
        append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "event": "start", **result})
        return result

    ok, reason = check_start_preconditions(root, app)
    if not ok:
        return {"app": app, "status": "blocked", "reason": reason, "url": url, "port": port}

    pnpm = pnpm_path()
    assert pnpm is not None
    stdout_f = out_log.open("ab")
    stderr_f = err_log.open("ab")
    env = os.environ.copy()
    env.setdefault("PRISMA_BLACK_BOX_SUPERVISED", "1")
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        proc = subprocess.Popen([pnpm, "-C", str(app_root), "dev"], cwd=str(root), stdout=stdout_f, stderr=stderr_f, stdin=subprocess.DEVNULL, env=env, creationflags=creationflags)
    finally:
        stdout_f.close()
        stderr_f.close()
    state.setdefault("processes", {})[app] = {
        "pid": proc.pid,
        "app": app,
        "root": str(root),
        "app_root": str(app_root),
        "port": port,
        "url": url,
        "out_log": str(out_log),
        "err_log": str(err_log),
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
        "command": [pnpm, "-C", str(app_root), "dev"],
    }
    save_state(root, state)
    healthy, health_summary = wait_for_health(url, timeout_seconds)
    result = {"app": app, "status": "started" if healthy else "started_with_caveats", "pid": proc.pid, "port": port, "url": url, "health": health_summary, "out_log": str(out_log), "err_log": str(err_log)}
    append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "event": "start", **result})
    return result


def stop_one(root: Path, out: Path, app: str) -> dict[str, Any]:
    state = load_state(root)
    rec = state.get("processes", {}).get(app)
    if not rec:
        return {"app": app, "status": "noop", "summary": "No hay PID registrado por black-box"}
    pid = int(rec.get("pid") or 0)
    app_root = Path(str(rec.get("app_root") or (root / APPS[app]["rel"])))
    cmdline = get_pid_command_line(pid)
    if not process_alive(pid):
        state.get("processes", {}).pop(app, None)
        save_state(root, state)
        return {"app": app, "status": "already_stopped", "pid": pid}
    if not is_probably_owned(root, app_root, cmdline, recorded_pid=True):
        return {"app": app, "status": "blocked", "pid": pid, "summary": "PID no parece propio; no se mata", "command_line": cmdline}
    if os.name == "nt":
        rc, stdout, stderr = run_capture(["taskkill", "/PID", str(pid), "/T", "/F"], timeout=10)
        status = "stopped" if rc == 0 else "failed"
        result = {"app": app, "status": status, "pid": pid, "stdout": stdout[-500:], "stderr": stderr[-500:]}
    else:
        try:
            os.kill(pid, 15)
            status = "stopped"
            result = {"app": app, "status": status, "pid": pid}
        except Exception as exc:
            result = {"app": app, "status": "failed", "pid": pid, "error": str(exc)}
    if result["status"] == "stopped":
        state.get("processes", {}).pop(app, None)
        save_state(root, state)
    append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "event": "stop", **result})
    return result


def start_apps(root: Path, out: Path, app: str, timeout: int, watch: bool) -> int:
    names = list(APPS) if app == "all" else [app]
    results = [start_one(root, out, name, timeout) for name in names]
    for r in results:
        safe_print(f"{r.get('app')}: {r.get('status')} port={r.get('port')} pid={r.get('pid','')} url={r.get('url','')} health={r.get('health') or r.get('http') or r.get('reason','')}")
    if watch:
        return watch_apps(root, out, interval=5, cycles=0)
    return 0 if all(r.get("status") in {"started", "already_running", "started_with_caveats"} for r in results) else 2


def stop_apps(root: Path, out: Path, app: str) -> int:
    names = list(APPS) if app == "owned" else [app]
    results = [stop_one(root, out, name) for name in names]
    for r in results:
        safe_print(f"{r.get('app')}: {r.get('status')} pid={r.get('pid','')} {r.get('summary','')}")
    return 0 if all(r.get("status") in {"stopped", "already_stopped", "noop"} for r in results) else 2


def restart_apps(root: Path, out: Path, app: str, timeout: int) -> int:
    names = list(APPS) if app == "all" else [app]
    for name in names:
        stop_one(root, out, name)
        time.sleep(1)
        r = start_one(root, out, name, timeout)
        safe_print(f"{name}: {r.get('status')} pid={r.get('pid','')} health={r.get('health') or r.get('http') or r.get('reason','')}")
    return 0


def watch_apps(root: Path, out: Path, interval: int, cycles: int, emit_report: bool = False, report_every: int = 0) -> int:
    out.mkdir(parents=True, exist_ok=True)
    state_path = out / "black_box_watch_state_i02.json"
    heartbeat_path = out / "black_box_heartbeat.jsonl"
    try:
        last_state = read_json(state_path) if state_path.exists() else {}
    except Exception:
        last_state = {}
    last_signature = str(last_state.get("signature") or "")
    n = 0
    try:
        while True:
            n += 1
            summary, checks, active, resolved = run_probe_snapshot(root, out)
            signature = watch_signature(summary)
            status = str(summary.get("status"))
            active_code = str(summary.get("active_code"))
            should_report = False
            reason = "heartbeat"
            if emit_report:
                should_report = True
                reason = "emit-report"
            elif signature != last_signature:
                should_report = True
                reason = "state-change"
            elif status == "BLOCKED" or int(summary.get("active_hits") or 0) > 0:
                should_report = True
                reason = "active-failure"
            elif report_every and n % max(1, int(report_every)) == 0:
                should_report = True
                reason = f"report-every-{report_every}"

            report_path = ""
            if should_report:
                _, md_path, _ = build_report(root, out, checks, active, resolved)
                report_path = str(md_path)
                last_signature = signature
                write_json(state_path, {
                    "signature": signature,
                    "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
                    "status": status,
                    "active_code": active_code,
                    "report": report_path,
                })

            heartbeat = {
                "ts": dt.datetime.now().isoformat(timespec="seconds"),
                "event": "watch-heartbeat",
                "status": status,
                "active_code": active_code,
                "ok": summary.get("ok"),
                "warn": summary.get("warn"),
                "fail": summary.get("fail"),
                "active_hits": summary.get("active_hits"),
                "resolved_hits": summary.get("resolved_hits"),
                "report_emitted": should_report,
                "report_reason": reason,
                "report": report_path,
            }
            append_jsonl(heartbeat_path, heartbeat)
            report_label = f" report={report_path}" if report_path else f" heartbeat={heartbeat_path}"
            safe_print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {status} active={active_code} checks OK={summary['ok']} WARN={summary['warn']} FAIL={summary['fail']} reason={reason}{report_label}")
            if cycles and n >= cycles:
                return 0
            time.sleep(max(1, interval))
    except KeyboardInterrupt:
        safe_print("watch detenido por usuario")
        return 0

def cmd_status(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    summary, md_path, _ = run_doctor(root, out)
    safe_print(f"PRISMA BLACK-BOX i02: {summary['status']}")
    safe_print(f"Root: {root}")
    safe_print(f"Active root cause: {summary['active_code']} - {summary['active_summary']}")
    if summary.get("primary_caveat"):
        pc = summary["primary_caveat"]
        safe_print(f"Primary caveat: {pc.get('pattern_id') or pc.get('code') or pc.get('name')} - {pc.get('summary')}")
    safe_print(f"Checks: OK={summary['ok']} WARN={summary['warn']} FAIL={summary['fail']} ACTIVE_HITS={summary['active_hits']} RESOLVED_HITS={summary['resolved_hits']}")
    safe_print(f"Report: {md_path}")
    if summary["status"] == "BLOCKED" and not args.allow_blocked:
        return 2
    return 0


def cmd_last_error(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    summary, _, _ = run_doctor(root, out)
    safe_print("PRISMA LAST ERROR")
    safe_print(f"Status: {summary['status']}")
    safe_print(f"Code: {summary['active_code']}")
    safe_print(f"Summary: {summary['active_summary']}")
    if summary.get("primary_caveat"):
        pc = summary["primary_caveat"]
        safe_print(f"Primary caveat: {pc.get('pattern_id') or pc.get('code') or pc.get('name')} - {pc.get('summary')}")
        safe_print(f"Evidence: {pc.get('evidence') or ''}")
    if summary["status"] == "BLOCKED" and not args.allow_blocked:
        return 2
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    z = collect(root, out)
    safe_print(f"Evidence ZIP: {z}")
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    if args.repair_action == "plan":
        plan = repair_plan(root, out)
        safe_print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0
    if args.repair_action == "apply":
        if not args.safe:
            safe_print("BLOCKED: repair apply requiere --safe en i02")
            return 2
        applied = apply_safe_repairs(root, out)
        safe_print(json.dumps(applied, indent=2, ensure_ascii=False))
        return 0
    safe_print("repair action invalida")
    return 2


def cmd_start(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    return start_apps(root, out, args.app, int(args.timeout), bool(args.watch))


def cmd_stop(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    return stop_apps(root, out, args.app)


def cmd_restart(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    return restart_apps(root, out, args.app, int(args.timeout))


def cmd_watch(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    return watch_apps(root, out, int(args.interval), int(args.cycles), bool(args.emit_report), int(args.report_every))


def cmd_cleanup(args: argparse.Namespace) -> int:
    out = out_dir(args.out)
    if args.kind != "reports":
        safe_print("cleanup solo soporta: reports")
        return 2
    days = int(args.days)
    keep_last = int(args.keep_last)
    now = time.time()
    candidates: list[Path] = []
    for pat in ["prisma_black_box_i02_*.md", "prisma_black_box_i02_*.json", "prisma_black_box_05*.md", "prisma_black_box_05*.json"]:
        candidates.extend([p for p in out.glob(pat) if p.is_file()])
    candidates = sorted(set(candidates), key=lambda p: p.stat().st_mtime, reverse=True)
    protected = set(candidates[:max(0, keep_last)])
    removed: list[str] = []
    for p in candidates:
        if p in protected:
            continue
        age_days = (now - p.stat().st_mtime) / 86400
        if age_days >= days:
            try:
                p.unlink()
                removed.append(str(p))
            except Exception:
                pass
    report = {
        "kind": "cleanup-reports",
        "out": str(out),
        "days": days,
        "keep_last": keep_last,
        "removed": removed,
        "removed_count": len(removed),
    }
    write_json(out / f"black_box_cleanup_reports_{now_stamp()}.json", report)
    safe_print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

def cmd_self_test(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    out = out_dir(args.out)
    checks = []
    checks.extend(probe_repo(root))
    ok = (root / "tools/black-box/black_box.py").exists() and (root / "tools/black_box.py").exists()
    state_dir(root).mkdir(parents=True, exist_ok=True)
    append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "event": "self-test", "ok": ok})
    safe_print(json.dumps({"ok": ok, "app": APP, "version": VER, "checks": [asdict(c) for c in checks[:4]]}, indent=2, ensure_ascii=False))
    return 0 if ok else 2


def add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--root", default=None, help="Raiz del proyecto terminal-de-venta-system")
    p.add_argument("--out", default=None, help=r"Directorio de reportes/logs. Default F:\Black-box")
    p.add_argument("--allow-blocked", action="store_true", help="No regresar codigo 2 cuando el diagnostico queda BLOCKED")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="black_box.py", description="PRISMA black-box runtime doctor + supervisor i02")
    add_common_args(parser)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn in [("status", cmd_status), ("doctor", cmd_status), ("last-error", cmd_last_error), ("collect", cmd_collect), ("self-test", cmd_self_test)]:
        p = sub.add_parser(name)
        add_common_args(p)
        p.set_defaults(func=fn)
    p = sub.add_parser("repair")
    add_common_args(p)
    p.add_argument("repair_action", choices=["plan", "apply"])
    p.add_argument("--safe", action="store_true")
    p.set_defaults(func=cmd_repair)
    p = sub.add_parser("start")
    add_common_args(p)
    p.add_argument("app", choices=["tablet", "pc", "mobile", "all"])
    p.add_argument("--timeout", type=int, default=35)
    p.add_argument("--watch", action="store_true")
    p.set_defaults(func=cmd_start)
    p = sub.add_parser("stop")
    add_common_args(p)
    p.add_argument("app", choices=["tablet", "pc", "mobile", "owned"], default="owned", nargs="?")
    p.set_defaults(func=cmd_stop)
    p = sub.add_parser("restart")
    add_common_args(p)
    p.add_argument("app", choices=["tablet", "pc", "mobile", "all"])
    p.add_argument("--timeout", type=int, default=35)
    p.set_defaults(func=cmd_restart)
    p = sub.add_parser("watch")
    add_common_args(p)
    p.add_argument("--interval", type=int, default=5)
    p.add_argument("--cycles", type=int, default=0, help="0 = infinito hasta Ctrl+C")
    p.add_argument("--emit-report", action="store_true", help="Genera reporte completo en cada ciclo. Por default solo heartbeat y reportes por cambio.")
    p.add_argument("--report-every", type=int, default=0, help="Genera reporte completo cada N ciclos aunque no cambie el estado. 0 = desactivado.")
    p.set_defaults(func=cmd_watch)
    p = sub.add_parser("cleanup")
    add_common_args(p)
    p.add_argument("kind", choices=["reports"])
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--keep-last", type=int, default=200)
    p.set_defaults(func=cmd_cleanup)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        safe_print(f"BLACK_BOX_INTERNAL_FAIL: {type(exc).__name__}: {exc}")
        try:
            out = out_dir(getattr(args, "out", None))
            append_jsonl(out / "prisma_black_box_events.jsonl", {"ts": dt.datetime.now().isoformat(timespec="seconds"), "event": "internal_fail", "error": f"{type(exc).__name__}: {exc}"})
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
