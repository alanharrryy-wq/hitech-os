[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$configPath = "F:\repos\hitech-os\tools\_local\cloudflare\public_health_probe_runner.config.json"
if (-not (Test-Path -LiteralPath $configPath)) {
  throw "Missing public health runner config at $configPath"
}

$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -ErrorAction Stop
$probeScript = [string]$config.probe_script
if ([string]::IsNullOrWhiteSpace($probeScript)) {
  throw "probe_script is missing in public health runner config."
}
if (-not (Test-Path -LiteralPath $probeScript)) {
  throw "Probe script not found: $probeScript"
}

& $probeScript `
  -RepoRoot ([string]$config.repo_root) `
  -TunnelName ([string]$config.tunnel_name) `
  -Hostname ([string]$config.hostname) `
  -OriginUrl ([string]$config.origin_url) `
  -FormsHostname ([string]$config.forms_hostname) `
  -FormsOriginUrl ([string]$config.forms_origin_url) `
  -TemplateHostname ([string]$config.template_hostname) `
  -TemplateOriginUrl ([string]$config.template_origin_url) `
  -LogDir ([string]$config.log_dir) `
  -FailureThreshold ([int]$config.failure_threshold)
exit $LASTEXITCODE
