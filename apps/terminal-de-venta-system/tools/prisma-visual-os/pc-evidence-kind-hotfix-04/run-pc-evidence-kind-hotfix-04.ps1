param(
  [string]$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system",
  [string]$OutRoot = "F:\descargasf"
)
$ErrorActionPreference = "Stop"
$Ts = Get-Date -Format "yyyyMMdd_HHmmss"
$WorkRoot = Join-Path $OutRoot "PRISMA_PC_EVIDENCE_KIND_HOTFIX_04_RERUN_$Ts"
New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
$Engine = Join-Path $Root "tools\prisma-visual-os\pc-evidence-kind-hotfix-04\pc_evidence_kind_hotfix_04.py"
if (-not (Test-Path -LiteralPath $Engine)) { throw "No existe engine: $Engine" }
py -3 $Engine --root $Root --workroot $WorkRoot
pnpm -C (Join-Path $Root "products\pc\app") run check:all
Compress-Archive -Path (Join-Path $WorkRoot "*") -DestinationPath "$WorkRoot.zip" -Force
Write-Host "Hotfix rerun evidence: $WorkRoot.zip" -ForegroundColor Green
