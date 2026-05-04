[CmdletBinding()]
param(
  [switch]$Apply,
  [switch]$Verify,
  [switch]$Smoke,
  [switch]$Diagnose,
  [switch]$RequireDnsBind,
  [string]$RepoRoot = "F:\repos\hitech-os\apps\terminal-de-venta-system",
  [string]$Hostname = "prisma.hitechrts.com",
  [string]$OriginUrl = "http://127.0.0.1:3140",
  [string]$TunnelName = "engine",
  [string]$ConfigPath = "C:\Users\alanh\.cloudflared\config.yml"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $PSCommandPath
$Py = Join-Path $ScriptDir "repair_prisma_mobile_cloudflare_live_route.py"
if (-not (Test-Path -LiteralPath $Py)) { throw "Missing repair script: $Py" }
$Mode = "--verify"
if ($Apply) { $Mode = "--apply" }
elseif ($Smoke) { $Mode = "--smoke" }
elseif ($Diagnose) { $Mode = "--diagnose" }
elseif ($Verify) { $Mode = "--verify" }
$argsList = @($Py, $Mode, "--repo-root", $RepoRoot, "--hostname", $Hostname, "--origin-url", $OriginUrl, "--tunnel-name", $TunnelName, "--config-path", $ConfigPath)
if ($RequireDnsBind) { $argsList += "--require-dns-bind" }
python @argsList
exit $LASTEXITCODE
