param(
    [string[]]$Path = @(),
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
$args = @($runner, "--root", $Root, "full-ingest")
foreach ($item in $Path) {
    $args += @("--path", $item)
}

& python @args
if ($LASTEXITCODE -ne 0) {
    throw "full-ingest failed with exit code $LASTEXITCODE"
}
