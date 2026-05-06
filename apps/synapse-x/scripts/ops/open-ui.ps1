param(
    [string]$Root = "",
    [switch]$Wait = $false
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
if (-not $Root) {
    $Root = $appRoot
}

$venvPython = Join-Path $appRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }
$runner = Join-Path $appRoot "run_engine.py"
$args = @($runner, "--root", $Root, "ui")

if ($Wait) {
    & $python @args
    exit $LASTEXITCODE
}

$process = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $appRoot -PassThru
Start-Sleep -Milliseconds 300
if ($process.HasExited) {
    throw "open-ui failed: process exited immediately (code $($process.ExitCode))"
}

$result = [ordered]@{
    status = "ok"
    pid = $process.Id
    python = $python
    root = $Root
    command = "$python $runner --root $Root ui"
}
$result | ConvertTo-Json -Depth 4
