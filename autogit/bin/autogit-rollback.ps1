$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$ToolRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $ToolRoot
$EngineRoot = Join-Path $ToolRoot 'engine'
$OutDir = if ($env:AUTOGIT_OUT) { $env:AUTOGIT_OUT } else { 'F:\descargasf' }
Set-Location $EngineRoot
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
  & py -3 -m autogit_engine.rollback_cli --repo $RepoRoot --out $OutDir
  exit $LASTEXITCODE
}
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw 'No encontre Python ni py launcher en PATH.' }
& python -m autogit_engine.rollback_cli --repo $RepoRoot --out $OutDir
exit $LASTEXITCODE
