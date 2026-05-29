$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'
$env:PYTHONIOENCODING = 'utf-8'
$ToolRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $ToolRoot
$EngineRoot = Join-Path $ToolRoot 'engine'
$OutDir = if ($env:AUTOGIT_OUT) { $env:AUTOGIT_OUT } else { 'F:\descargasf' }
$Mode = if ($env:AUTOGIT_MODE) { $env:AUTOGIT_MODE } else { 'full' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Transcript = Join-Path $OutDir ('autogit repo transcript ' + (Get-Date -Format 'ddMM HHmmss') + '.log')
Start-Transcript -Path $Transcript -Force | Out-Null
try {
  Set-Location $EngineRoot
  $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
  if ($pyLauncher) {
    & py -3 -m autogit_engine.cli --repo $RepoRoot --out $OutDir --mode $Mode @args
    $code = $LASTEXITCODE
  } else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { throw 'No encontre Python ni py launcher en PATH.' }
    & python -m autogit_engine.cli --repo $RepoRoot --out $OutDir --mode $Mode @args
    $code = $LASTEXITCODE
  }
  if ($code -ne 0) { throw "AutoGit termino con codigo $code. Revisa el ZIP fail en $OutDir." }
}
finally {
  Stop-Transcript | Out-Null
}
