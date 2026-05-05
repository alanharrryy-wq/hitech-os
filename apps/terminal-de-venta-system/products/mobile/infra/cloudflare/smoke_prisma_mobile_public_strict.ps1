[CmdletBinding()]
param(
  [string]$RepoRoot = "F:\repos\hitech-os\apps\terminal-de-venta-system",
  [string]$Hostname = "prisma.hitechrts.com",
  [string]$OriginUrl = "http://127.0.0.1:3140"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $PSCommandPath
$Repair = Join-Path $ScriptDir "repair_prisma_mobile_cloudflare_live_route.ps1"
& $Repair -Smoke -RepoRoot $RepoRoot -Hostname $Hostname -OriginUrl $OriginUrl
exit $LASTEXITCODE
