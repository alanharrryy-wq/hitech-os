param(
  [Parameter(Mandatory=$true)][string]$Root,
  [string]$OutDir
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($OutDir)) {
  $OutDir = Join-Path $Root "docs\design\pc-runtime-injector-02\generated"
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Py = Join-Path $Root "tools\prisma-visual-os\pc-interface-compiler\pc_interface_compiler_v3.py"
python $Py --root $Root --out-dir $OutDir
Write-Host "Compiler v3 report:" -ForegroundColor Green
Write-Host (Join-Path $OutDir "pc-interface-compiler-report-v3.md") -ForegroundColor Yellow
