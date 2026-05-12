param(
  [string]$ConfigPath = "",
  [string]$TunnelName = "prisma-chart-lab",
  [string]$Hostname = "prisma-chart-lab-preview.example.com",
  [int]$Port = 3000
)

$ErrorActionPreference = "Continue"
$AppRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$TerminalRoot = (Resolve-Path (Join-Path $AppRoot "..\..\..")).Path
$EvidenceRoot = Join-Path $TerminalRoot "tools\_local\evidence\chart-lab"
New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
$ReportPath = Join-Path $EvidenceRoot "tunnel-doctor.json"

function Test-Command($Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

$cloudflared = Test-Command "cloudflared"
$tcp = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
$http = $null
try {
  $http = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -UseBasicParsing -TimeoutSec 5
} catch {
  $http = $null
}

$configExists = $false
$configHasIngress = $false
if ($ConfigPath) {
  $configExists = Test-Path -LiteralPath $ConfigPath
  if ($configExists) {
    $configText = Get-Content -LiteralPath $ConfigPath -Raw
    $configHasIngress = ($configText -match "ingress:") -and ($configText -match "http_status:404")
  }
}

$tokenAvailable = -not [string]::IsNullOrWhiteSpace($env:CLOUDFLARED_TOKEN)
$localCredentialsPath = Join-Path $env:USERPROFILE ".cloudflared"
$localCredentialsAvailable = Test-Path -LiteralPath $localCredentialsPath

$runCommand = if ($tokenAvailable) {
  "pnpm -C `"$AppRoot`" tunnel:run"
} elseif ($ConfigPath -and $configExists) {
  "pnpm -C `"$AppRoot`" tunnel:run -- -ConfigPath `"$ConfigPath`" -TunnelName `"$TunnelName`" -Hostname `"$Hostname`""
} else {
  "cloudflared tunnel login; cloudflared tunnel create $TunnelName; cloudflared tunnel route dns $TunnelName $Hostname; pnpm -C `"$AppRoot`" tunnel:run -- -ConfigPath <config.yml> -TunnelName $TunnelName"
}

$canRunTunnel = $tokenAvailable -or $configHasIngress
$report = [ordered]@{
  status = if ($cloudflared -and $tcp -and $http -and $canRunTunnel) { "READY" } else { "BLOCKED_OR_INCOMPLETE" }
  cloudflared = [ordered]@{ found = [bool]$cloudflared; path = $cloudflared }
  port = [ordered]@{ port = $Port; listening = [bool]$tcp; processId = if ($tcp) { $tcp.OwningProcess } else { $null } }
  localHttp = [ordered]@{ ok = [bool]$http; statusCode = if ($http) { $http.StatusCode } else { $null }; containsChartLab = if ($http) { $http.Content.Contains("PRISMA Chart Lab") } else { $false } }
  auth = [ordered]@{ tokenAvailable = $tokenAvailable; localCredentialsAvailable = $localCredentialsAvailable }
  config = [ordered]@{ path = $ConfigPath; exists = $configExists; hasIngressAnd404Fallback = $configHasIngress; hostname = $Hostname; service = "http://localhost:$Port" }
  exactRunCommand = $runCommand
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$report | ConvertTo-Json -Depth 8

if (-not $cloudflared) { exit 2 }
if (-not $tcp -or -not $http) { exit 3 }
if (-not $canRunTunnel) { exit 4 }
exit 0
