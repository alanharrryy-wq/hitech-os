from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
from typing import Any


def is_port_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _powershell_executable() -> str | None:
    for candidate in ["powershell.exe", "pwsh.exe", "powershell", "pwsh"]:
        found = shutil.which(candidate)
        if found:
            return found
    return None


def _run_powershell_json(script: str, timeout: int = 10) -> Any:
    ps = _powershell_executable()
    if ps is None:
        return []
    completed = subprocess.run(
        [ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []


def inspect_port(port: int) -> dict[str, Any]:
    script = f"""
$items = @()
$connections = @(Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue)
foreach ($connection in $connections) {{
  $pidValue = [int]$connection.OwningProcess
  $proc = Get-CimInstance Win32_Process -Filter ("ProcessId={{0}}" -f $pidValue) -ErrorAction SilentlyContinue
  $items += [pscustomobject]@{{
    pid = $pidValue
    localAddress = [string]$connection.LocalAddress
    localPort = [int]$connection.LocalPort
    state = [string]$connection.State
    processName = if ($proc) {{ [string]$proc.Name }} else {{ "" }}
    executablePath = if ($proc) {{ [string]$proc.ExecutablePath }} else {{ "" }}
    commandLine = if ($proc) {{ [string]$proc.CommandLine }} else {{ "" }}
    parentPid = if ($proc) {{ [int]$proc.ParentProcessId }} else {{ 0 }}
    creationDate = if ($proc) {{ [string]$proc.CreationDate }} else {{ "" }}
    cwd = $null
    cwdSource = "unavailable-win32-process"
  }}
}}
$items | ConvertTo-Json -Depth 5
"""
    owners = _run_powershell_json(script)
    if isinstance(owners, dict):
        owners = [owners]
    if not isinstance(owners, list):
        owners = []
    return {
        "port": port,
        "open": bool(owners) or is_port_open("127.0.0.1", port, timeout=0.4),
        "owners": owners,
    }


def inspect_ports(ports: list[int]) -> dict[int, dict[str, Any]]:
    return {port: inspect_port(port) for port in ports}


def process_exists(pid: int) -> bool:
    if not pid:
        return False
    if _powershell_executable() is None:
        try:
            os.kill(int(pid), 0)
            return True
        except OSError:
            return False
    script = f"""
$proc = Get-CimInstance Win32_Process -Filter "ProcessId={int(pid)}" -ErrorAction SilentlyContinue
if ($proc) {{ "true" }} else {{ "false" }}
"""
    completed = subprocess.run(
        [_powershell_executable() or "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        timeout=8,
    )
    return completed.stdout.strip().lower() == "true"


def command_exists(command: str) -> dict[str, Any]:
    if _powershell_executable() is None:
        found = shutil.which(command)
        return {"found": bool(found), "source": found or "", "name": command}
    script = f"""
$cmd = Get-Command {json.dumps(command)} -ErrorAction SilentlyContinue
if ($cmd) {{
  [pscustomobject]@{{ found = $true; source = [string]$cmd.Source; name = [string]$cmd.Name }} | ConvertTo-Json -Depth 3
}} else {{
  [pscustomobject]@{{ found = $false; source = ""; name = {json.dumps(command)} }} | ConvertTo-Json -Depth 3
}}
"""
    result = _run_powershell_json(script)
    return result if isinstance(result, dict) else {"found": False, "source": "", "name": command}
