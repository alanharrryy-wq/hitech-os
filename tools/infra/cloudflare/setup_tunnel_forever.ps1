[CmdletBinding()]
param(
  [switch]$GuardOnly,
  [string]$OriginUrl = $(if ($env:HITECH_CLOUDFLARE_ORIGIN_URL) { $env:HITECH_CLOUDFLARE_ORIGIN_URL } else { "http://127.0.0.1:3100" }),
  [string]$FormsHostname = $(if ($env:HITECH_CLOUDFLARE_FORMS_HOSTNAME) { $env:HITECH_CLOUDFLARE_FORMS_HOSTNAME } else { "forms.hitechrts.com" }),
  [string]$FormsOriginUrl = $(if ($env:HITECH_CLOUDFLARE_FORMS_ORIGIN_URL) { $env:HITECH_CLOUDFLARE_FORMS_ORIGIN_URL } else { "http://127.0.0.1:3200" }),
  [string]$TemplateHostname = $(if ($env:HITECH_CLOUDFLARE_TEMPLATE_HOSTNAME) { $env:HITECH_CLOUDFLARE_TEMPLATE_HOSTNAME } else { "eit.hitechrts.com" }),
  [string]$TemplateOriginUrl = $(if ($env:HITECH_CLOUDFLARE_TEMPLATE_ORIGIN_URL) { $env:HITECH_CLOUDFLARE_TEMPLATE_ORIGIN_URL } else { "http://127.0.0.1:3110" })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "F:\repos\hitech-os"
$TunnelName = "engine"
$Hostname = "engine.hitechrts.com"
$LogDir = Join-Path $RepoRoot "logs\cloudflare"
$InfraDir = Join-Path $RepoRoot "tools\infra\cloudflare"
$TunnelForeverPy = Join-Path $InfraDir "tunnel_forever.py"
$ValidatePy = Join-Path $InfraDir "validate_tunnel.py"
$FinalReportPath = Join-Path $InfraDir "FINAL_REPORT.txt"

function Write-MagentaProgress {
  param(
    [int]$Id,
    [string]$Activity,
    [string]$Status,
    [int]$Percent
  )
  Write-Progress -Id $Id -Activity $Activity -Status $Status -PercentComplete $Percent
  Write-Host ("[{0,3}%] {1} :: {2}" -f $Percent, $Activity, $Status) -ForegroundColor Magenta
}

function Fail-AndExit {
  param(
    [string]$Message,
    [int]$Code = 2
  )
  Write-Error $Message
  exit $Code
}

function Invoke-NativeCapture {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FilePath,
    [string[]]$ArgumentList = @()
  )

  $nativePrefVar = Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue
  $hadNativePreference = $null -ne $nativePrefVar
  $previousNativePreference = $false
  if ($hadNativePreference) {
    $previousNativePreference = [bool]$nativePrefVar.Value
    Set-Variable -Scope Script -Name PSNativeCommandUseErrorActionPreference -Value $false
  }
  $previousErrorPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"

  try {
    $output = (& $FilePath @ArgumentList 2>&1 | Out-String).Trim()
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorPreference
    if ($hadNativePreference) {
      Set-Variable -Scope Script -Name PSNativeCommandUseErrorActionPreference -Value $previousNativePreference
    }
  }

  [pscustomobject]@{
    Output = $output
    ExitCode = $exitCode
  }
}

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Bootstrapping paths and runtime checks" -Percent 5
if (-not (Test-Path -LiteralPath $RepoRoot)) {
  Fail-AndExit "Repo root not found at '$RepoRoot'."
}
if (-not (Test-Path -LiteralPath $InfraDir)) {
  Fail-AndExit "Infra directory not found at '$InfraDir'."
}
if (-not (Test-Path -LiteralPath $TunnelForeverPy)) {
  Fail-AndExit "Entry script not found: $TunnelForeverPy"
}
if (-not (Test-Path -LiteralPath $ValidatePy)) {
  Fail-AndExit "Validation script not found: $ValidatePy"
}
if ([string]::IsNullOrWhiteSpace($OriginUrl)) {
  Fail-AndExit "OriginUrl cannot be empty. Use -OriginUrl or env HITECH_CLOUDFLARE_ORIGIN_URL."
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $pythonCmd) {
  Fail-AndExit "python not found in PATH. Install Python and retry."
}
$PythonExe = $pythonCmd.Source

$cloudflaredCmd = Get-Command cloudflared -ErrorAction SilentlyContinue
if ($null -eq $cloudflaredCmd) {
  Fail-AndExit "cloudflared not found in PATH. Install cloudflared and retry."
}

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$validateJsonPath = Join-Path $LogDir ("validate_{0}.json" -f $timestamp)

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Executing core Python orchestration" -Percent 35
$coreArgs = @(
  $TunnelForeverPy,
  "--repo-root", $RepoRoot,
  "--tunnel-name", $TunnelName,
  "--hostname", $Hostname,
  "--forms-hostname", $FormsHostname,
  "--template-hostname", $TemplateHostname,
  "--origin-url", $OriginUrl,
  "--forms-origin-url", $FormsOriginUrl,
  "--template-origin-url", $TemplateOriginUrl,
  "--log-dir", $LogDir,
  "--validate-json-out", $validateJsonPath,
  "--final-report", $FinalReportPath
)
if ($GuardOnly) {
  $coreArgs += "--guard-only"
}

& $PythonExe @coreArgs
$coreExit = $LASTEXITCODE
if ($GuardOnly) {
  Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Guard-only execution complete" -Percent 100
  Write-Progress -Id 1 -Activity "Cloudflare Industrial Setup" -Completed
  exit $coreExit
}

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Running explicit final validation JSON" -Percent 60
& $PythonExe $ValidatePy `
  --tunnel-name $TunnelName `
  --hostname $Hostname `
  --origin-url $OriginUrl `
  --extra-route "$FormsHostname=$FormsOriginUrl" `
  --extra-route "$TemplateHostname=$TemplateOriginUrl" `
  --extra-public-url "$FormsHostname=https://$FormsHostname" `
  --extra-public-url "$TemplateHostname=https://$TemplateHostname" `
  --log-dir $LogDir `
  --json-out $validateJsonPath
$validateExit = $LASTEXITCODE

$validateJson = @{}
if (Test-Path -LiteralPath $validateJsonPath) {
  try {
    $validateJson = Get-Content -LiteralPath $validateJsonPath -Raw | ConvertFrom-Json -ErrorAction Stop
  } catch {
    $validateJson = @{}
  }
}

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Checking DNS route list" -Percent 75
$dnsListResult = Invoke-NativeCapture -FilePath "cloudflared" -ArgumentList @("tunnel", "route", "dns", "list", "--tunnel", $TunnelName)
$dnsOutput = $dnsListResult.Output
$dnsExit = $dnsListResult.ExitCode
if ($dnsExit -ne 0 -and $dnsOutput -match "expects the format") {
  $dnsFallbackResultPrimary = Invoke-NativeCapture -FilePath "cloudflared" -ArgumentList @("tunnel", "route", "dns", $TunnelName, $Hostname)
  $dnsFallbackResultForms = Invoke-NativeCapture -FilePath "cloudflared" -ArgumentList @("tunnel", "route", "dns", $TunnelName, $FormsHostname)
  $dnsFallbackResultTemplate = Invoke-NativeCapture -FilePath "cloudflared" -ArgumentList @("tunnel", "route", "dns", $TunnelName, $TemplateHostname)
  $dnsFallbackOutput = $dnsFallbackResultPrimary.Output + "`n" + $dnsFallbackResultForms.Output + "`n" + $dnsFallbackResultTemplate.Output
  if ($dnsFallbackResultPrimary.ExitCode -eq 0 -and $dnsFallbackResultForms.ExitCode -eq 0 -and $dnsFallbackResultTemplate.ExitCode -eq 0) {
    $dnsOutput = $dnsOutput + "`n[FALLBACK]" + "`n" + $dnsFallbackOutput
    $dnsExit = 0
  }
}

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Checking service state" -Percent 85
$serviceObj = Get-Service cloudflared -ErrorAction SilentlyContinue
$serviceStatus = if ($null -eq $serviceObj) { "NotInstalled" } else { $serviceObj.Status.ToString() }
$serviceInstalled = ($null -ne $serviceObj)
$serviceOutput = if ($null -eq $serviceObj) { "cloudflared service not found" } else { $serviceObj | Format-List Name, Status, DisplayName | Out-String }

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Checking watchdog task state" -Percent 92
$taskResult = Invoke-NativeCapture -FilePath "schtasks" -ArgumentList @("/Query", "/TN", "HITECH-Cloudflared-TunnelGuard", "/V", "/FO", "LIST")
$taskOutput = $taskResult.Output
$taskExit = $taskResult.ExitCode
$taskOutputLower = $taskOutput.ToLowerInvariant()
$taskAccessDenied = ($taskOutputLower -match "acceso denegado") -or ($taskOutputLower -match "access is denied")
$taskInstalled = ($taskExit -eq 0) -or $taskAccessDenied

$publicTaskResult = Invoke-NativeCapture -FilePath "schtasks" -ArgumentList @("/Query", "/TN", "HITECH-Cloudflared-PublicHealth", "/V", "/FO", "LIST")
$publicTaskOutput = $publicTaskResult.Output
$publicTaskExit = $publicTaskResult.ExitCode
$publicTaskOutputLower = $publicTaskOutput.ToLowerInvariant()
$publicTaskAccessDenied = ($publicTaskOutputLower -match "acceso denegado") -or ($publicTaskOutputLower -match "access is denied")
$publicTaskInstalled = ($publicTaskExit -eq 0) -or $publicTaskAccessDenied

$publicUrl = "https://$Hostname"
$formsPublicUrl = "https://$FormsHostname"
$templatePublicUrl = "https://$TemplateHostname"
$localOriginHealthy = $false
$tunnelConnected = $false
$publicHostnameHealthy = $false
$publicStatusCode = "unknown"
$formsPublicHealthy = $false
$formsPublicStatusCode = "unknown"
$templatePublicHealthy = $false
$templatePublicStatusCode = "unknown"
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "public_url")) {
  $publicUrl = [string]$validateJson.public_url
}
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "local_origin_healthy")) {
  $localOriginHealthy = [bool]$validateJson.local_origin_healthy
}
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "tunnel_connected")) {
  $tunnelConnected = [bool]$validateJson.tunnel_connected
}
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "public_hostname_healthy")) {
  $publicHostnameHealthy = [bool]$validateJson.public_hostname_healthy
}
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "public_status_code")) {
  $publicStatusCode = [string]$validateJson.public_status_code
}
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "public_hosts")) {
  $publicHostProps = $validateJson.public_hosts.PSObject.Properties
  $formsEntry = $publicHostProps | Where-Object { $_.Name -eq $FormsHostname }
  if ($formsEntry) {
    $formsPublicUrl = [string]$formsEntry.Value.public_url
    $formsPublicHealthy = [bool]$formsEntry.Value.healthy
    $formsPublicStatusCode = [string]$formsEntry.Value.status_code
  }
  $templateEntry = $publicHostProps | Where-Object { $_.Name -eq $TemplateHostname }
  if ($templateEntry) {
    $templatePublicUrl = [string]$templateEntry.Value.public_url
    $templatePublicHealthy = [bool]$templateEntry.Value.healthy
    $templatePublicStatusCode = [string]$templateEntry.Value.status_code
  }
}

$status = "PASS"
if (
  $coreExit -ne 0 `
  -or $validateExit -ne 0 `
  -or $dnsExit -ne 0 `
  -or -not $serviceInstalled `
  -or $serviceStatus -ne "Running" `
  -or -not $taskInstalled `
  -or -not $publicTaskInstalled `
  -or -not $localOriginHealthy `
  -or -not $tunnelConnected `
  -or -not $publicHostnameHealthy
) {
  $status = "FAIL"
}

$hostnameRouteStatus = if ($dnsOutput -match [regex]::Escape($Hostname) -or $dnsOutput -match "already configured") { "BOUND" } else { "MISSING" }
$formsHostnameRouteStatus = if ($dnsOutput -match [regex]::Escape($FormsHostname) -or $dnsOutput -match "already configured") { "BOUND" } else { "MISSING" }
$templateHostnameRouteStatus = if ($dnsOutput -match [regex]::Escape($TemplateHostname) -or $dnsOutput -match "already configured") { "BOUND" } else { "MISSING" }
$watchdogStatus = if ($taskInstalled) {
  if ($taskAccessDenied -and $taskExit -ne 0) { "INSTALLED (QUERY RESTRICTED)" } else { "INSTALLED" }
} else {
  "MISSING"
}
$publicWatchdogStatus = if ($publicTaskInstalled) {
  if ($publicTaskAccessDenied -and $publicTaskExit -ne 0) { "INSTALLED (QUERY RESTRICTED)" } else { "INSTALLED" }
} else {
  "MISSING"
}

$report = @"
HITECH Cloudflare Tunnel Forever Report
======================================
Generated At: $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
Status: $status
GuardOnly: $GuardOnly

Tunnel Name: $TunnelName
Hostname: $Hostname
Public URL: $publicUrl
Forms Hostname: $FormsHostname
Forms Public URL: $formsPublicUrl
Template Hostname: $TemplateHostname
Template Public URL: $templatePublicUrl
Origin URL: $OriginUrl
Forms Origin URL: $FormsOriginUrl
Template Origin URL: $TemplateOriginUrl

Core Exit Code: $coreExit
Validation Exit Code: $validateExit
DNS List Exit Code: $dnsExit

Tunnel UUID: (see $validateJsonPath)
Hostname Route Status: $hostnameRouteStatus
Forms Hostname Route Status: $formsHostnameRouteStatus
Template Hostname Route Status: $templateHostnameRouteStatus
Service Status: $serviceStatus
Watchdog Task Status: $watchdogStatus
Public Health Task Status: $publicWatchdogStatus
Local Origin Healthy: $localOriginHealthy
Tunnel Connected: $tunnelConnected
Public Hostname Healthy (2xx/3xx): $publicHostnameHealthy
Public Status Code: $publicStatusCode
Forms Hostname Healthy (2xx/3xx): $formsPublicHealthy
Forms Status Code: $formsPublicStatusCode
Template Hostname Healthy (2xx/3xx): $templatePublicHealthy
Template Status Code: $templatePublicStatusCode

Log Directory: $LogDir
Validation JSON: $validateJsonPath
Final Report: $FinalReportPath

--- DNS LIST ---
$dnsOutput

--- SERVICE ---
$serviceOutput

--- WATCHDOG TASK ---
$taskOutput

--- PUBLIC HEALTH TASK ---
$publicTaskOutput
"@
$report | Set-Content -Path $FinalReportPath -Encoding UTF8

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Completed" -Percent 100
Write-Progress -Id 1 -Activity "Cloudflare Industrial Setup" -Completed

if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "hostname_bound")) {
  if ([bool]$validateJson.hostname_bound) {
    $hostnameRouteStatus = "BOUND"
  } elseif ($hostnameRouteStatus -ne "BOUND") {
    $hostnameRouteStatus = "MISSING"
  }
}

if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "hostnames_bound")) {
  $boundProps = $validateJson.hostnames_bound.PSObject.Properties
  $formsBoundEntry = $boundProps | Where-Object { $_.Name -eq $FormsHostname }
  if ($formsBoundEntry) {
    if ([bool]$formsBoundEntry.Value) {
      $formsHostnameRouteStatus = "BOUND"
    } elseif ($formsHostnameRouteStatus -ne "BOUND") {
      $formsHostnameRouteStatus = "MISSING"
    }
  }
  $templateBoundEntry = $boundProps | Where-Object { $_.Name -eq $TemplateHostname }
  if ($templateBoundEntry) {
    if ([bool]$templateBoundEntry.Value) {
      $templateHostnameRouteStatus = "BOUND"
    } elseif ($templateHostnameRouteStatus -ne "BOUND") {
      $templateHostnameRouteStatus = "MISSING"
    }
  }
}

$tunnelUuidOut = "UNKNOWN"
if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "tunnel_uuid")) {
  $rawUuid = [string]$validateJson.tunnel_uuid
  if ($rawUuid -match "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}") {
    $tunnelUuidOut = $Matches[0]
  }
}

Write-Host "CLOUDFLARE INDUSTRIAL MODE: ACTIVE" -ForegroundColor Green
Write-Host ("Tunnel UUID: {0}" -f $tunnelUuidOut)
Write-Host ("Hostname route status: {0}" -f $hostnameRouteStatus)
Write-Host ("Forms hostname route status: {0}" -f $formsHostnameRouteStatus)
Write-Host ("Template hostname route status: {0}" -f $templateHostnameRouteStatus)
Write-Host ("Service status: {0}" -f $serviceStatus)
Write-Host ("Watchdog task status: {0}" -f $watchdogStatus)
Write-Host ("Public health task status: {0}" -f $publicWatchdogStatus)
Write-Host ("Origin healthy: {0}" -f $localOriginHealthy)
Write-Host ("Tunnel connected: {0}" -f $tunnelConnected)
Write-Host ("Public hostname healthy: {0} (status={1})" -f $publicHostnameHealthy, $publicStatusCode)
Write-Host ("Forms hostname healthy: {0} (status={1})" -f $formsPublicHealthy, $formsPublicStatusCode)
Write-Host ("Template hostname healthy: {0} (status={1})" -f $templatePublicHealthy, $templatePublicStatusCode)
Write-Host ("Logs stored at: {0}" -f $LogDir)

if ($status -ne "PASS") {
  exit 2
}
exit 0
