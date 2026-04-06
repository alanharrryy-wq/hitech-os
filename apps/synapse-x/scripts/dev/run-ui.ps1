param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [switch]$Demo,
    [switch]$ShowConsole
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Root)) {
    throw "Root not found: $Root"
}

$starter = Join-Path $Root 'starter.py'
if (-not (Test-Path -LiteralPath $starter)) {
    throw "starter.py not found: $starter"
}

$argsList = @($starter, '--root', $Root)
if ($Demo) { $argsList += '--demo' }
if ($ShowConsole) { $argsList += '--show-console' }

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @argsList
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python @argsList
    exit $LASTEXITCODE
}

throw 'No Python launcher found. Install Python or ensure py/python is on PATH.'
