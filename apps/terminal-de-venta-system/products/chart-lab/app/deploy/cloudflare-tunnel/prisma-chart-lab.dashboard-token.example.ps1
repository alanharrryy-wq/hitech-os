param(
  [string]$Token = $env:CLOUDFLARED_TOKEN
)

if (-not $Token) {
  Write-Error "CLOUDFLARED_TOKEN is required for dashboard-token mode."
  exit 1
}

cloudflared tunnel --no-autoupdate run --token $Token
