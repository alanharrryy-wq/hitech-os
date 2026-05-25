param(
  [Parameter(Mandatory = $true)]
  [string]$Action,

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $Utf8NoBom
$OutputEncoding = $Utf8NoBom
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8:replace"
$env:NO_COLOR = "1"

function ConvertTo-ExitCode {
  param([object]$Value, [int]$Default = 1)
  if ($null -eq $Value) { return [int]$Default }
  if ($Value -is [System.Array]) {
    $items = @($Value)
    for ($i = $items.Count - 1; $i -ge 0; $i--) {
      $candidate = ConvertTo-ExitCode -Value $items[$i] -Default ([int]::MinValue)
      if ($candidate -ne [int]::MinValue) { return [int]$candidate }
    }
    return [int]$Default
  }
  if ($Value -is [bool]) {
    if ($Value) { return 0 }
    return 1
  }
  $parsed = 0
  if ([int]::TryParse(([string]$Value).Trim(), [ref]$parsed)) { return [int]$parsed }
  return [int]$Default
}

$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$Entry = Join-Path $ControlRoot "internal\py\prisma_control_center.py"

if (-not (Test-Path -LiteralPath $Entry)) {
  throw "No encontre prisma_control_center.py en $Entry"
}

$env:PYTHONDONTWRITEBYTECODE = "1"

if ($env:PYTHON_EXE) {
  & $env:PYTHON_EXE $Entry $Action @ForwardArgs
  exit (ConvertTo-ExitCode -Value $LASTEXITCODE -Default 1)
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  & py -3 $Entry $Action @ForwardArgs
  exit (ConvertTo-ExitCode -Value $LASTEXITCODE -Default 1)
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  & python $Entry $Action @ForwardArgs
  exit (ConvertTo-ExitCode -Value $LASTEXITCODE -Default 1)
}

$python3 = Get-Command python3 -ErrorAction SilentlyContinue
if ($python3) {
  & python3 $Entry $Action @ForwardArgs
  exit (ConvertTo-ExitCode -Value $LASTEXITCODE -Default 1)
}

throw "No encontre Python. Instala Python 3 o define PYTHON_EXE."
