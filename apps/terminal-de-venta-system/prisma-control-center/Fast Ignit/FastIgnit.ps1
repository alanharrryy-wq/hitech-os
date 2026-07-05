param(
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

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Engine = Join-Path $ScriptDir "internal\fast_ignit.py"
if (-not (Test-Path -LiteralPath $Engine)) {
  throw "No encontre motor Fast Ignit: $Engine"
}

function Invoke-PythonEngine {
  param([string]$PythonExe)
  & $PythonExe $Engine @ForwardArgs
  $code = if ($null -eq $LASTEXITCODE) { 1 } else { [int]$LASTEXITCODE }
  exit $code
}

if (-not [string]::IsNullOrWhiteSpace($env:PYTHON_EXE) -and (Test-Path -LiteralPath $env:PYTHON_EXE)) {
  Invoke-PythonEngine -PythonExe $env:PYTHON_EXE
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  & py -3 $Engine @ForwardArgs
  $code = if ($null -eq $LASTEXITCODE) { 1 } else { [int]$LASTEXITCODE }
  exit $code
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  Invoke-PythonEngine -PythonExe $python.Source
}

$python3 = Get-Command python3 -ErrorAction SilentlyContinue
if ($python3) {
  Invoke-PythonEngine -PythonExe $python3.Source
}

throw "No encontre Python 3. Define PYTHON_EXE o instala Python."
