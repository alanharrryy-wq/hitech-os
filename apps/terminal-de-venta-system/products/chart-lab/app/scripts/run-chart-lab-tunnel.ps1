param(
  [string]$ConfigPath = "",
  [string]$TunnelName = "prisma-chart-lab",
  [string]$Hostname = "prisma-chart-lab-preview.example.com",
  [int]$Port = 3000
)

$ErrorActionPreference = "Stop"
$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
  Write-Error "cloudflared is not installed. Install cloudflared or add it to PATH."
  exit 2
}

try {
  $probe = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -UseBasicParsing -TimeoutSec 5
  if (-not $probe.Content.Contains("PRISMA Chart Lab")) {
    Write-Error "Port $Port responded, but it does not look like PRISMA Chart Lab."
    exit 3
  }
} catch {
  Write-Error "PRISMA Chart Lab is not reachable on port $Port. Start it first."
  exit 3
}

if (-not [string]::IsNullOrWhiteSpace($env:CLOUDFLARED_TOKEN)) {
  Write-Host "Starting cloudflared dashboard-token tunnel for PRISMA Chart Lab."
  & cloudflared tunnel --no-autoupdate run --token $env:CLOUDFLARED_TOKEN
  exit $LASTEXITCODE
}

if ($ConfigPath) {
  if (-not (Test-Path -LiteralPath $ConfigPath)) {
    Write-Error "ConfigPath does not exist: $ConfigPath"
    exit 4
  }
  Write-Host "Starting cloudflared config-file tunnel for $Hostname -> local Chart Lab port $Port."
  & cloudflared tunnel --config $ConfigPath run $TunnelName
  exit $LASTEXITCODE
}

Write-Error "No CLOUDFLARED_TOKEN or ConfigPath was provided. Run tunnel:doctor for exact setup commands."
exit 5
