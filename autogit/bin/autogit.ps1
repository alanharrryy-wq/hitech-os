$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$ToolRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $ToolRoot
$EngineRoot = Join-Path $ToolRoot 'engine'
$DefaultOut = 'F:\descargasf'
$Cfg = Join-Path $ToolRoot 'config\repo_layout.json'
if ($env:AUTOGIT_OUT) { $OutDir = $env:AUTOGIT_OUT }
elseif (Test-Path -LiteralPath $Cfg) { try { $OutDir = (Get-Content -LiteralPath $Cfg -Raw | ConvertFrom-Json).outputs.primary } catch { $OutDir = $DefaultOut } }
else { $OutDir = $DefaultOut }
if ([string]::IsNullOrWhiteSpace($OutDir) -or $OutDir -match '[<>]') { $OutDir = $DefaultOut }
$Mode = if ($env:AUTOGIT_MODE) { $env:AUTOGIT_MODE } else { 'full' }
if (-not (Test-Path -LiteralPath $EngineRoot)) { throw "No encontre EngineRoot: $EngineRoot" }
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) { throw "RepoRoot no parece repo Git: $RepoRoot. AutoGit debe vivir dentro del repo hitech-os." }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Transcript = Join-Path $OutDir ('autogit repo transcript ' + (Get-Date -Format 'ddMM HHmmss') + '.log')
try { Start-Transcript -Path $Transcript -Force | Out-Null } catch { Write-Host "[AutoGit] WARN: transcript no inicio: $($_.Exception.Message)" -ForegroundColor Yellow }
try {
  Set-Location $EngineRoot
  $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
  $python = Get-Command python -ErrorAction SilentlyContinue
  $UsePy = $false
  if ($pyLauncher) { $UsePy = $true }
  elseif (-not $python) { throw 'No encontre Python ni py launcher en PATH.' }

  $FlightCommands = @('plan','apply-plan','merge')
  $FirstArg = if ($args.Count -gt 0) { [string]$args[0] } else { '' }

  if ($FlightCommands -contains $FirstArg) {
    if ($UsePy) { & py -3 -m autogit_engine.flight_cli --repo $RepoRoot --out $OutDir @args; $code = $LASTEXITCODE }
    else { & python -m autogit_engine.flight_cli --repo $RepoRoot --out $OutDir @args; $code = $LASTEXITCODE }
  } else {
    if ($UsePy) { & py -3 -m autogit_engine.cli --repo $RepoRoot --out $OutDir --mode $Mode @args; $code = $LASTEXITCODE }
    else { & python -m autogit_engine.cli --repo $RepoRoot --out $OutDir --mode $Mode @args; $code = $LASTEXITCODE }
  }
  if ($code -eq 2 -and $FirstArg -eq 'plan') {
    Write-Host "[AutoGit] PLAN BLOQUEADO con codigo 2. Revisa el PLAN_ZIP y corrige blockers antes de apply-plan." -ForegroundColor Yellow
    exit 2
  }
  if ($code -ne 0) { throw "AutoGit termino con codigo $code. Revisa el ZIP fail en $OutDir." }
}
finally { try { Stop-Transcript | Out-Null } catch {} }
