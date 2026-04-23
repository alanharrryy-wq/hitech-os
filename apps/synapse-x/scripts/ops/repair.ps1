param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
if (-not $Root) {
    $Root = $appRoot
}

$runner = Join-Path $appRoot "run_engine.py"
& python $runner --root $Root repair
if ($LASTEXITCODE -ne 0) {
    throw "repair failed with exit code $LASTEXITCODE"
}
