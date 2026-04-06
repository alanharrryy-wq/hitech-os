param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PassThruArgs
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Root)) {
    throw "Root not found: $Root"
}

$engine = Join-Path $Root '.synapse_hidden\entrypoints\run_engine_real.py'
if (-not (Test-Path -LiteralPath $engine)) {
    throw "Hidden engine entrypoint not found: $engine"
}

$argsList = @($engine, '--root', $Root) + $PassThruArgs

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @argsList
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python @argsList
    exit $LASTEXITCODE
}

throw 'No Python launcher found. Install Python or ensure py/python is on PATH.'
