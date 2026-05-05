[CmdletBinding()]
param([string]$PublicUrl="https://prisma.hitechrts.com/prisma-app",[string]$InstallUrl="https://prisma.hitechrts.com/prisma-app/install",[string]$CheckUrl="https://prisma.hitechrts.com/.well-known/pwa-domain-check.json")
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Failed = $false
foreach ($Url in @($PublicUrl,$InstallUrl,$CheckUrl)) { try { $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15; Write-Host "OK $($r.StatusCode): $Url" -ForegroundColor Green } catch { Write-Host "FAIL $Url :: $($_.Exception.Message)" -ForegroundColor Red; $Failed = $true } }
if ($Failed) { exit 2 }
exit 0
