param(
  [Parameter(Mandatory = $true)]
  [string]$Action,

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$Entry = Join-Path $ControlRoot "internal\py\prisma_control_center.py"

if (-not (Test-Path -LiteralPath $Entry)) {
  throw "No encontre prisma_control_center.py en $Entry"
}

$env:PYTHONDONTWRITEBYTECODE = "1"

if ($env:PYTHON_EXE) {
  & $env:PYTHON_EXE $Entry $Action @ForwardArgs
  exit $LASTEXITCODE
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  & py -3 $Entry $Action @ForwardArgs
  exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  & python $Entry $Action @ForwardArgs
  exit $LASTEXITCODE
}

$python3 = Get-Command python3 -ErrorAction SilentlyContinue
if ($python3) {
  & python3 $Entry $Action @ForwardArgs
  exit $LASTEXITCODE
}

throw "No encontre Python. Instala Python 3 o define PYTHON_EXE."
