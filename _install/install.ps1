param(
  [string]$RepoDir = "F:\repos\hitech-os",
  [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Step($i,$total,$msg){
  $pct=[int](($i/[double]$total)*100)
  Write-Progress -Activity "HITECH Guardrails LAW Installer" -Status $msg -PercentComplete $pct
}

function Ensure-Dir([string]$p){ if(-not (Test-Path $p)){ New-Item -ItemType Directory -Force -Path $p | Out-Null } }

$total=10; $i=0

$i++; Write-Step $i $total "Validando repo…"
if(-not (Test-Path $RepoDir)){ throw "RepoDir no existe: $RepoDir" }
$ws = Join-Path $RepoDir "pnpm-workspace.yaml"
if(-not (Test-Path $ws)){ throw "No parece repo root (falta pnpm-workspace.yaml): $RepoDir" }

$i++; Write-Step $i $total "Resolviendo origen del pack…"
$PackRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
# pack layout: this script lives in _install/
$PackRoot = Split-Path -Parent $PackRoot

$i++; Write-Step $i $total "Creando carpetas destino…"
Ensure-Dir (Join-Path $RepoDir "tools\hos\guardrails")
Ensure-Dir (Join-Path $RepoDir "tools\codex\dispatch")
Ensure-Dir (Join-Path $RepoDir "docs\guardrails")

$i++; Write-Step $i $total "Copiando archivos guardrails…"
Copy-Item -Recurse -Force (Join-Path $PackRoot "tools\hos\guardrails\*") (Join-Path $RepoDir "tools\hos\guardrails\") 

$i++; Write-Step $i $total "Copiando docs…"
Copy-Item -Recurse -Force (Join-Path $PackRoot "docs\guardrails\*") (Join-Path $RepoDir "docs\guardrails\") 

$i++; Write-Step $i $total "Copiando validator wrapper…"
Copy-Item -Force (Join-Path $PackRoot "tools\codex\dispatch\validator_ext.py") (Join-Path $RepoDir "tools\codex\dispatch\validator_ext.py")

$i++; Write-Step $i $total "Intentando parchear run_iter.ps1 para enforcement default…"
$runIter = Join-Path $RepoDir "tools\codex\dispatch\run_iter.ps1"
if(Test-Path $runIter){
  $txt = Get-Content $runIter -Raw
  $marker = "# HITECH_GUARDRAILS_LAW_V1"
  if($txt -notmatch [regex]::Escape($marker)){
    $append = @"

$marker
# Auto-enforce anti-padding/blinded-code guardrails after each run (default)
try {
  python `"$RepoDir\tools\codex\dispatch\validator_ext.py`" validate-guardrails --run-id `$RunId
} catch {
  Write-Host "GUARDRAILS LAW: BLOCKED — see tools/codex/runs/`$RunId/GUARDRAILS_REPORT.json" -ForegroundColor Red
  throw
}

"@
    Add-Content -Path $runIter -Value $append
  }
}

$i++; Write-Step $i $total "Escribiendo wrapper de comandos…"
$cmdDir = Join-Path $RepoDir "tools\hos\guardrails"
$shim = Join-Path $cmdDir "RUN_GUARDRAILS.ps1"
@"
param([Parameter(Mandatory=`$true)][string]`$RunId)
python `"$RepoDir\tools\codex\dispatch\validator_ext.py`" validate-guardrails --run-id `$RunId
"@ | Set-Content -Encoding utf8 $shim

$i++; Write-Step $i $total "Verificando instalación…"
$chk1 = Join-Path $RepoDir "tools\hos\guardrails\validate_run.py"
$chk2 = Join-Path $RepoDir "tools\codex\dispatch\validator_ext.py"
if(-not (Test-Path $chk1) -or -not (Test-Path $chk2)){ throw "Instalación incompleta. Revisa permisos." }

$i++; Write-Step $i $total "Listo. Abriendo carpeta…"
Write-Progress -Activity "HITECH Guardrails LAW Installer" -Completed
Start-Process (Join-Path $RepoDir "tools\hos\guardrails")
Write-Host "✅ Installed HITECH Guardrails LAW v1 into $RepoDir" -ForegroundColor Green
Write-Host "Use: python tools\codex\dispatch\validator_ext.py validate-guardrails --run-id <RUN_ID>" -ForegroundColor Yellow
"