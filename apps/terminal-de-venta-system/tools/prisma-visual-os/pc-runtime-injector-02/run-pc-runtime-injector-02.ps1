param(
  [Parameter(Mandatory=$true)][string]$Root,
  [Parameter(Mandatory=$true)][string]$OutRoot
)

$ErrorActionPreference = "Stop"
$Py = Join-Path $Root "tools\prisma-visual-os\pc-runtime-injector-02\pc_runtime_injector_02.py"
$Ts = Get-Date -Format "yyyyMMdd_HHmmss"
$WorkRoot = Join-Path $OutRoot "PRISMA_PC_RUNTIME_INJECTOR_02_RERUN_$Ts"
New-Item -ItemType Directory -Force -Path (Join-Path $WorkRoot "reports") | Out-Null
python $Py --root $Root --out-root $OutRoot --work-root $WorkRoot --patch-json (Join-Path $WorkRoot "reports\patched-routes.json") --report (Join-Path $WorkRoot "reports\pc-runtime-injector-02-report.md")
$Compiler = Join-Path $Root "tools\prisma-visual-os\pc-interface-compiler\pc_interface_compiler_v3.py"
$Generated = Join-Path $Root "docs\design\pc-runtime-injector-02\generated"
New-Item -ItemType Directory -Force -Path $Generated | Out-Null
python $Compiler --root $Root --out-dir $Generated --strict-pilot-debt
Write-Host "Injector 02 rerun complete:" -ForegroundColor Green
Write-Host $Generated -ForegroundColor Yellow
