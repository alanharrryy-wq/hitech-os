[CmdletBinding()]
param(
  [string]$RepoRoot = "F:\repos\hitech-os",
  [string]$TunnelName = "engine",
  [string]$Hostname = "engine.hitechrts.com",
  [string]$OriginUrl = "http://127.0.0.1:3100",
  [string]$FormsHostname = "forms.hitechrts.com",
  [string]$FormsOriginUrl = "http://127.0.0.1:3200",
  [string]$TemplateHostname = "eit.hitechrts.com",
  [string]$TemplateOriginUrl = "http://127.0.0.1:3110",
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
$GuardSetupPs1 = Join-Path $RepoRoot "tools\infra\cloudflare\setup_tunnel_forever.ps1"
$statePath = Join-Path $LogDir "public_health_alert_state.json"
$summaryPath = Join-Path $LogDir "public_health_probe_last.json"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$validateOutPath = Join-Path $LogDir ("public_health_validate_{0}.json" -f $timestamp)

$autoRecoveryAttempted = $false
$autoRecoveryExitCode = $null
$autoRecoveryOutputTail = ""

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
  --extra-route "$FormsHostname=$FormsOriginUrl" `
  --extra-route "$TemplateHostname=$TemplateOriginUrl" `
  --extra-public-url "$FormsHostname=https://$FormsHostname" `
  --extra-public-url "$TemplateHostname=https://$TemplateHostname" `
  --log-dir $LogDir `
  --json-out $validateOutPath
$validateExit = $LASTEXITCODE

$validatePayload = Read-JsonOrDefault -PathLiteral $validateOutPath -Default @{}
$localHealthy = $false
$tunnelConnected = $false
$publicHealthy = $false
$publicStatusCode = $null
$formsPublicHealthy = $false
$formsPublicStatusCode = $null
$templatePublicHealthy = $false
$templatePublicStatusCode = $null
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
if ($validatePayload -and ($validatePayload.PSObject.Properties.Name -contains "public_hosts")) {
  $publicHostProps = $validatePayload.public_hosts.PSObject.Properties
  $formsEntry = $publicHostProps | Where-Object { $_.Name -eq $FormsHostname }
  if ($formsEntry) {
    $formsPublicHealthy = [bool]$formsEntry.Value.healthy
    $formsPublicStatusCode = $formsEntry.Value.status_code
  }
  $templateEntry = $publicHostProps | Where-Object { $_.Name -eq $TemplateHostname }
  if ($templateEntry) {
    $templatePublicHealthy = [bool]$templateEntry.Value.healthy
    $templatePublicStatusCode = $templateEntry.Value.status_code
  }
}

$isHealthy = ($validateExit -eq 0) -and $publicHealthy
$statusText = if ($isHealthy) { "healthy" } else { "unhealthy" }

if (-not $isHealthy -and (Test-Path -LiteralPath $GuardSetupPs1)) {
  $autoRecoveryAttempted = $true
  try {
    $guardOutput = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $GuardSetupPs1 -GuardOnly 2>&1 | Out-String)
    $autoRecoveryExitCode = $LASTEXITCODE
    $autoRecoveryOutputTail = $guardOutput
  } catch {
    $autoRecoveryExitCode = 9010
    $autoRecoveryOutputTail = ($_ | Out-String)
  }
  if ($autoRecoveryOutputTail.Length -gt 4000) {
    $autoRecoveryOutputTail = $autoRecoveryOutputTail.Substring($autoRecoveryOutputTail.Length - 4000)
  }

  if ($autoRecoveryExitCode -eq 0) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $validateOutPath = Join-Path $LogDir ("public_health_validate_{0}.json" -f $timestamp)
    & $pythonExe $ValidatePy `
      --tunnel-name $TunnelName `
      --hostname $Hostname `
      --origin-url $OriginUrl `
      --extra-route "$FormsHostname=$FormsOriginUrl" `
      --extra-route "$TemplateHostname=$TemplateOriginUrl" `
      --extra-public-url "$FormsHostname=https://$FormsHostname" `
      --extra-public-url "$TemplateHostname=https://$TemplateHostname" `
      --log-dir $LogDir `
      --json-out $validateOutPath
    $validateExit = $LASTEXITCODE

    $validatePayload = Read-JsonOrDefault -PathLiteral $validateOutPath -Default @{}
    $localHealthy = $false
    $tunnelConnected = $false
    $publicHealthy = $false
    $publicStatusCode = $null
    $formsPublicHealthy = $false
    $formsPublicStatusCode = $null
    $templatePublicHealthy = $false
    $templatePublicStatusCode = $null
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
    if ($validatePayload -and ($validatePayload.PSObject.Properties.Name -contains "public_hosts")) {
      $publicHostProps = $validatePayload.public_hosts.PSObject.Properties
      $formsEntry = $publicHostProps | Where-Object { $_.Name -eq $FormsHostname }
      if ($formsEntry) {
        $formsPublicHealthy = [bool]$formsEntry.Value.healthy
        $formsPublicStatusCode = $formsEntry.Value.status_code
      }
      $templateEntry = $publicHostProps | Where-Object { $_.Name -eq $TemplateHostname }
      if ($templateEntry) {
        $templatePublicHealthy = [bool]$templateEntry.Value.healthy
        $templatePublicStatusCode = $templateEntry.Value.status_code
      }
    }
    $isHealthy = ($validateExit -eq 0) -and $publicHealthy
    $statusText = if ($isHealthy) { "healthy" } else { "unhealthy" }
  }
}

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
      forms_hostname = $FormsHostname
      forms_public_status = $formsPublicStatusCode
      template_hostname = $TemplateHostname
      template_public_status = $templatePublicStatusCode
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
      forms_hostname = $FormsHostname
      forms_public_status = $formsPublicStatusCode
      template_hostname = $TemplateHostname
      template_public_status = $templatePublicStatusCode
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
  forms_hostname = $FormsHostname
  forms_origin_url = $FormsOriginUrl
  forms_public_healthy = $formsPublicHealthy
  forms_public_status_code = $formsPublicStatusCode
  template_hostname = $TemplateHostname
  template_origin_url = $TemplateOriginUrl
  template_public_healthy = $templatePublicHealthy
  template_public_status_code = $templatePublicStatusCode
  auto_recovery_attempted = $autoRecoveryAttempted
  auto_recovery_exit_code = $autoRecoveryExitCode
  auto_recovery_output_tail = $autoRecoveryOutputTail
  validate_json = $validateOutPath
  state_path = $statePath
  webhook_enabled = -not [string]::IsNullOrWhiteSpace($WebhookUrl)
  ts_utc = $nowUtc
}
Write-Json -PathLiteral $summaryPath -Payload $summaryPayload

Write-Output ($summaryPayload | ConvertTo-Json -Depth 8)
exit $exitCode
