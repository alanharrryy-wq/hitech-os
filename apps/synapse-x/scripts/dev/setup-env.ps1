param(
    [switch]$InstallDeps = $true
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$venvDir = Join-Path $appRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    & python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment at $venvDir"
    }
}

if ($InstallDeps) {
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Failed upgrading pip"
    }
    & $venvPython -m pip install -r (Join-Path $appRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "Failed installing requirements"
    }
}

$result = [ordered]@{
    status = "ok"
    app_root = $appRoot
    venv_python = $venvPython
    next = @(
        "$venvPython $appRoot\run_engine.py init-db",
        "$venvPython $appRoot\run_engine.py ingest",
        "$venvPython $appRoot\run_engine.py status"
    )
}
$result | ConvertTo-Json -Depth 4
