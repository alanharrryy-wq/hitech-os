$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$ToolRoot = Split-Path -Parent $PSScriptRoot
$EngineRoot = Join-Path $ToolRoot 'engine'
$selfTest = Join-Path $PSScriptRoot 'autogit-selftest.py'
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
  & py -3 $selfTest
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) { throw 'No encontre Python ni py launcher en PATH.' }
  & python $selfTest
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
$env:AUTOGIT_MODE = 'audit'
& (Join-Path $PSScriptRoot 'autogit.ps1')
