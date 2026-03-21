[CmdletBinding()]
param(
  [string]$RepoRoot = "F:\repos\hitech-os",
  [string]$TunnelName = "engine",
  [string]$Hostname = "engine.hitechrts.com",
  [string]$OriginUrl = "http://127.0.0.1:3100",
  [string]$LogDir = "",
  [int]$FailureThreshold = 2,
  [string]$WebhookUrl = $(if ($env:HITECH_CLOUDFLARE_ALERT_WEBHOOK) { $env:HITECH_CLOUDFLARE_ALERT_WEBHOOK } else { "" }),
  [switch]$ForceAlert
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($LogDir)) {
  $LogDir = Join-Path $RepoRoot "logs\cloudflare"
}

$ValidatePy = Join-Path $RepoRoot "tools\infra\cloudflare\validate_tunnel.py"
$statePath = Join-Path $LogDir "public_health_alert_state.json"
$summaryPath = Join-Path $LogDir "public_health_probe_last.json"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$validateOutPath = Join-Path $LogDir ("public_health_validate_{0}.json" -f $timestamp)

function Ensure-Directory {
  param([string]$PathLiteral)
  if (-not (Test-Path -LiteralPath $PathLiteral)) {
    New-Item -ItemType Directory -Path $PathLiteral -Force | Out-Null
  }
}

function Read-JsonOrDefault {
  param(
    [string]$PathLiteral,
    [object]$Default
  )
  if (-not (Test-Path -LiteralPath $PathLiteral)) {
    return $Default
  }
  try {
    return Get-Content -LiteralPath $PathLiteral -Raw | ConvertFrom-Json -ErrorAction Stop
  } catch {
    return $Default
  }
}

function Write-Json {
  param(
    [string]$PathLiteral,
    [object]$Payload
  )
  ($Payload | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $PathLiteral -Encoding UTF8
}

function Send-Alert {
  param(
    [string]$Level,
    [int]$EventId,
    [string]$MessageText,
    [string]$Webhook,
    [hashtable]$Context
  )
  $eventType = if ($Level -eq "ERROR") { "ERROR" } else { "INFORMATION" }
  try {
    eventcreate /L APPLICATION /T $eventType /SO "HITECH-Cloudflare" /ID $EventId /D $MessageText | Out-Null
  } catch {
    # Best effort: do not crash probe because event log write failed.
  }

  if (-not [string]::IsNullOrWhiteSpace($Webhook)) {
    try {
      $body = @{
        source = "hitech-cloudflare-public-health"
        level = $Level
        event_id = $EventId
        message = $MessageText
        context = $Context
        ts_utc = (Get-Date).ToUniversalTime().ToString("o")
      }
      $jsonBody = $body | ConvertTo-Json -Depth 8 -Compress
      Invoke-RestMethod -Uri $Webhook -Method Post -ContentType "application/json" -Body $jsonBody | Out-Null
    } catch {
      # Best effort: do not crash probe because webhook failed.
    }
  }
}

Ensure-Directory -PathLiteral $LogDir

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $pythonCmd) {
  $errorPayload = @{
    ok = $false
    error = "python not found in PATH"
    ts_utc = (Get-Date).ToUniversalTime().ToString("o")
  }
  Write-Json -PathLiteral $summaryPath -Payload $errorPayload
  exit 2
}
$pythonExe = $pythonCmd.Source

if (-not (Test-Path -LiteralPath $ValidatePy)) {
  $errorPayload = @{
    ok = $false
    error = "validate_tunnel.py not found"
    path = $ValidatePy
    ts_utc = (Get-Date).ToUniversalTime().ToString("o")
  }
  Write-Json -PathLiteral $summaryPath -Payload $errorPayload
  exit 2
}

& $pythonExe $ValidatePy `
  --tunnel-name $TunnelName `
  --hostname $Hostname `
  --origin-url $OriginUrl `
  --log-dir $LogDir `
  --json-out $validateOutPath
$validateExit = $LASTEXITCODE

$validatePayload = Read-JsonOrDefault -PathLiteral $validateOutPath -Default @{}
$localHealthy = $false
$tunnelConnected = $false
$publicHealthy = $false
$publicStatusCode = $null
if ($validatePayload -and ($validatePayload.PSObject.Properties.Name -contains "local_origin_healthy")) {
  $localHealthy = [bool]$validatePayload.local_origin_healthy
}
if ($validatePayload -and ($validatePayload.PSObject.Properties.Name -contains "tunnel_connected")) {
  $tunnelConnected = [bool]$validatePayload.tunnel_connected
}
if ($validatePayload -and ($validatePayload.PSObject.Properties.Name -contains "public_hostname_healthy")) {
  $publicHealthy = [bool]$validatePayload.public_hostname_healthy
}
if ($validatePayload -and ($validatePayload.PSObject.Properties.Name -contains "public_status_code")) {
  $publicStatusCode = $validatePayload.public_status_code
}

$isHealthy = ($validateExit -eq 0) -and $publicHealthy
$statusText = if ($isHealthy) { "healthy" } else { "unhealthy" }
$nowUtc = (Get-Date).ToUniversalTime().ToString("o")
$stateDefault = @{
  consecutive_failures = 0
  last_status = "unknown"
  last_alert_utc = ""
  last_alert_reason = ""
}
$state = Read-JsonOrDefault -PathLiteral $statePath -Default $stateDefault

$prevFailures = 0
if ($state -and ($state.PSObject.Properties.Name -contains "consecutive_failures")) {
  $prevFailures = [int]$state.consecutive_failures
}

$alerted = $false
$alertReason = ""
$exitCode = 0

if ($isHealthy) {
  $recovered = $prevFailures -ge $FailureThreshold
  $state = @{
    consecutive_failures = 0
    last_status = "healthy"
    last_check_utc = $nowUtc
    last_alert_utc = if ($state.PSObject.Properties.Name -contains "last_alert_utc") { [string]$state.last_alert_utc } else { "" }
    last_alert_reason = if ($state.PSObject.Properties.Name -contains "last_alert_reason") { [string]$state.last_alert_reason } else { "" }
  }
  if ($recovered -or $ForceAlert) {
    $alertReason = "Cloudflare public endpoint recovered"
    $message = "RECOVERY: engine.hitechrts.com healthy again. status=$publicStatusCode local=$localHealthy tunnel=$tunnelConnected"
    Send-Alert -Level "INFO" -EventId 5301 -MessageText $message -Webhook $WebhookUrl -Context @{
      tunnel = $TunnelName
      hostname = $Hostname
      public_status = $publicStatusCode
      local_origin_healthy = $localHealthy
      tunnel_connected = $tunnelConnected
      validate_json = $validateOutPath
    }
    $alerted = $true
    $state.last_alert_utc = $nowUtc
    $state.last_alert_reason = $alertReason
  }
  $exitCode = 0
} else {
  $failures = $prevFailures + 1
  $shouldAlert = $ForceAlert -or ($failures -eq $FailureThreshold) -or ($failures % 12 -eq 0)
  $state = @{
    consecutive_failures = $failures
    last_status = "unhealthy"
    last_check_utc = $nowUtc
    last_alert_utc = if ($state.PSObject.Properties.Name -contains "last_alert_utc") { [string]$state.last_alert_utc } else { "" }
    last_alert_reason = if ($state.PSObject.Properties.Name -contains "last_alert_reason") { [string]$state.last_alert_reason } else { "" }
  }
  if ($shouldAlert) {
    $alertReason = "Public endpoint unhealthy"
    $message = "ALERT: engine.hitechrts.com unhealthy. public_status=$publicStatusCode local=$localHealthy tunnel=$tunnelConnected failures=$failures"
    Send-Alert -Level "ERROR" -EventId 5300 -MessageText $message -Webhook $WebhookUrl -Context @{
      tunnel = $TunnelName
      hostname = $Hostname
      public_status = $publicStatusCode
      local_origin_healthy = $localHealthy
      tunnel_connected = $tunnelConnected
      consecutive_failures = $failures
      validate_json = $validateOutPath
    }
    $alerted = $true
    $state.last_alert_utc = $nowUtc
    $state.last_alert_reason = $alertReason
  }
  $exitCode = 2
}

Write-Json -PathLiteral $statePath -Payload $state

$summaryPayload = @{
  ok = $isHealthy
  status = $statusText
  validate_exit_code = $validateExit
  alert_sent = $alerted
  alert_reason = $alertReason
  failure_threshold = $FailureThreshold
  consecutive_failures = [int]$state.consecutive_failures
  local_origin_healthy = $localHealthy
  tunnel_connected = $tunnelConnected
  public_hostname_healthy = $publicHealthy
  public_status_code = $publicStatusCode
  validate_json = $validateOutPath
  state_path = $statePath
  webhook_enabled = -not [string]::IsNullOrWhiteSpace($WebhookUrl)
  ts_utc = $nowUtc
}
Write-Json -PathLiteral $summaryPath -Payload $summaryPayload

Write-Output ($summaryPayload | ConvertTo-Json -Depth 8)
exit $exitCode
