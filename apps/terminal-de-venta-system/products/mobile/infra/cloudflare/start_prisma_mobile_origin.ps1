[CmdletBinding()]
param([string]$RepoRoot="F:\repos\hitech-os\apps\terminal-de-venta-system",[int]$Port=3140,[switch]$BuildFirst)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$AppRoot = Join-Path $RepoRoot "products\mobile\app"
$Logs = Join-Path $RepoRoot "logs\prisma-mobile"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
if (-not (Test-Path -LiteralPath $AppRoot)) { throw "Mobile app root not found: $AppRoot" }
$Pnpm = (Get-Command pnpm.cmd -ErrorAction SilentlyContinue).Source
if (-not $Pnpm) { $Pnpm = (Get-Command pnpm -ErrorAction Stop).Source }
$conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) { Write-Host "PRISMA Mobile origin already listening on port $Port. PID: $($conn.OwningProcess)" -ForegroundColor Cyan; exit 0 }
if ($BuildFirst) { & $Pnpm -C $AppRoot build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
$OutLog = Join-Path $Logs "prisma-mobile-origin.out.log"
$ErrLog = Join-Path $Logs "prisma-mobile-origin.err.log"
$p = Start-Process -FilePath $Pnpm -ArgumentList @("-C", $AppRoot, "start") -WorkingDirectory $RepoRoot -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog -WindowStyle Hidden -PassThru
Write-Host "PRISMA Mobile origin launcher PID: $($p.Id)" -ForegroundColor Green
Write-Host "stdout: $OutLog"
Write-Host "stderr: $ErrLog"
for ($i=1; $i -le 30; $i++) { Start-Sleep -Seconds 2; try { $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/prisma-app" -UseBasicParsing -TimeoutSec 8; Write-Host "OK PRISMA Mobile origin responds $($r.StatusCode)" -ForegroundColor Green; exit 0 } catch {} }
Write-Host "WARN origin did not confirm HTTP. Check logs." -ForegroundColor Yellow
exit 2
