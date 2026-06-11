param(
  [int]$WaitSeconds = 180,
  [int]$TimeoutSeconds = 25,
  [int]$MaxWorkers = 14,
  [switch]$NoPause
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$PyFile = Join-Path $Root "internal\py\dev_route_warmer.py"

if (-not (Test-Path -LiteralPath $PyFile)) {
  throw "No encontre dev_route_warmer.py en $PyFile"
}

$python = $null
foreach ($candidate in @("py.exe", "python.exe", "python3.exe")) {
  $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
  if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) { throw "No encontre Python disponible como py.exe, python.exe o python3.exe" }

Write-Host "PRISMA dev route warmer" -ForegroundColor Cyan
Write-Host "Root: $Root"
Write-Host "No mata procesos, no abre navegador, no levanta servidores, no toca Prisma." -ForegroundColor Yellow

& $python $PyFile --root $Root --wait-seconds $WaitSeconds --timeout-seconds $TimeoutSeconds --max-workers $MaxWorkers
$code = $LASTEXITCODE

if (-not $NoPause -and $Host.Name -notlike "*ISE*") {
  Write-Host ""
  Write-Host "Listo. Enter para cerrar." -ForegroundColor DarkGray
  try { [void][Console]::ReadLine() } catch {}
}

exit $code
