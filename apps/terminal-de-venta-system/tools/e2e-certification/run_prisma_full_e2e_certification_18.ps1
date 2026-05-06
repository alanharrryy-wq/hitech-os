param(
  [string]$RepoRoot = "F:\repos\hitech-os",
  [string]$Out = "F:\descargasf",
  [switch]$Full,
  [switch]$HttpOnly,
  [switch]$NoHttp,
  [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$SystemRoot = Join-Path $RepoRoot "apps\terminal-de-venta-system"
$Script = Join-Path $SystemRoot "tools\e2e-certification\prisma_full_e2e_certification_18.mjs"
if (-not (Test-Path -LiteralPath $Script)) {
  throw "No existe certificador: $Script"
}

$argsList = @($Script, "--repo-root", $RepoRoot, "--system-root", $SystemRoot, "--out", $Out)
if ($Full) { $argsList += "--full" }
if ($HttpOnly) { $argsList += "--http-only" }
if ($NoHttp) { $argsList += "--no-http" }

node @argsList
$exit = $LASTEXITCODE

$latest = Get-ChildItem -LiteralPath $Out -Directory -Filter "prisma_full_e2e_certification_18_*" -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if ($latest) {
  $report = Join-Path $latest.FullName "prisma_full_e2e_certification_18_report.md"
  Write-Host "Reporte: $report" -ForegroundColor Cyan
  if ($OpenReport -and (Test-Path -LiteralPath $report)) {
    Invoke-Item $report
  }
}

exit $exit
