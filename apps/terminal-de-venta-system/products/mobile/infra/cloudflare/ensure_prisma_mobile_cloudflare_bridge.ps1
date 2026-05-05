[CmdletBinding()]
param([switch]$DryRun,[switch]$Apply,[switch]$VerifyOnly,[string]$RepoRoot="F:\repos\hitech-os\apps\terminal-de-venta-system",[string]$Hostname="prisma.hitechrts.com",[string]$OriginUrl="http://127.0.0.1:3140",[string]$TunnelName="engine",[string]$ConfigPath="C:\Users\alanh\.cloudflared\config.yml")
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $PSCommandPath
$Py = Join-Path $ScriptDir "ensure_prisma_mobile_cloudflare_bridge.py"
if (-not (Test-Path -LiteralPath $Py)) { throw "Missing bridge python script: $Py" }
$Mode = "--dry-run"
if ($Apply) { $Mode = "--apply" }
if ($VerifyOnly) { $Mode = "--verify" }
python $Py $Mode --repo-root $RepoRoot --hostname $Hostname --origin-url $OriginUrl --tunnel-name $TunnelName --config-path $ConfigPath
exit $LASTEXITCODE
