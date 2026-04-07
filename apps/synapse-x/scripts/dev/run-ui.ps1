
param(
    [string]$Python = "py -3"
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..")
$entry = Join-Path $repoRoot "run_ui.py"
$env:SYNAPSE_X_ROOT = $repoRoot.Path

if ($Python -eq "py -3") {
    py -3 $entry @args
    exit $LASTEXITCODE
}

$parts = $Python.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
& $parts[0] @($parts[1..($parts.Length - 1)]) $entry @args
exit $LASTEXITCODE
