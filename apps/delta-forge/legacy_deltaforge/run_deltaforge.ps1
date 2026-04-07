$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RunnableRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$EntryPoint = Join-Path -Path $RunnableRoot -ChildPath "apps\deltaforge\deltaforge_app.py"
$SharedPath = Join-Path -Path $RunnableRoot -ChildPath "forgeos\shared\pyside6_glass"

if (-not (Test-Path -LiteralPath $EntryPoint -PathType Leaf)) {
    throw "No existe el entrypoint esperado: $EntryPoint"
}
if (-not (Test-Path -LiteralPath $SharedPath -PathType Container)) {
    throw "No existe el shared esperado: $SharedPath"
}

try {
    $escapedEntry = [Regex]::Escape($EntryPoint)
    $existingProcess = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -and $_.CommandLine -match $escapedEntry } |
        Select-Object -First 1
    if ($existingProcess) {
        Write-Output "DELTAFORGE_RUNNING PID=$($existingProcess.ProcessId)"
        exit 0
    }
} catch {
    # Continue without process de-duplication if process metadata is unavailable.
}

$PythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCommand) {
    throw "No se encontro python en PATH."
}
$PythonExe = $PythonCommand.Source

$validationScript = @'
from __future__ import annotations

import importlib
import sys
from pathlib import Path

runnable_root = Path(sys.argv[1]).resolve()
entrypoint = Path(sys.argv[2]).resolve()
shared_path = Path(sys.argv[3]).resolve()

if not entrypoint.is_file():
    raise FileNotFoundError(f"EntryPoint no existe: {entrypoint}")
if not shared_path.is_dir():
    raise FileNotFoundError(f"Shared path no existe: {shared_path}")

app_root = entrypoint.parent
for candidate in (runnable_root, app_root):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

importlib.import_module("PySide6")
importlib.import_module("forgeos.shared.pyside6_glass")
importlib.import_module("bootstrap")
'@

& $PythonExe -c $validationScript $RunnableRoot $EntryPoint $SharedPath

$Process = Start-Process -FilePath $PythonExe -ArgumentList @($EntryPoint) -WorkingDirectory $RunnableRoot -PassThru
Start-Sleep -Seconds 2
$Process.Refresh()
if ($Process.HasExited) {
    throw "DeltaForge termino inmediatamente con codigo $($Process.ExitCode)."
}

Write-Output "DELTAFORGE_RUNNING PID=$($Process.Id)"
