[CmdletBinding()]
param(
  [switch]$GuardOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "F:\repos\hitech-os"
$TunnelName = "engine"
$Hostname = "engine.hitechrts.com"
$OriginUrl = "http://localhost:3000"
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
  "--origin-url", $OriginUrl,
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
  --log-dir $LogDir `
  --json-out $validateJsonPath
$validateExit = $LASTEXITCODE

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Checking DNS route list" -Percent 75
$dnsOutput = (& cloudflared tunnel route dns list --tunnel $TunnelName 2>&1 | Out-String).Trim()
$dnsExit = $LASTEXITCODE
if ($dnsExit -ne 0 -and $dnsOutput -match "expects the format") {
  $dnsFallbackOutput = (& cloudflared tunnel route dns $TunnelName $Hostname 2>&1 | Out-String).Trim()
  if ($LASTEXITCODE -eq 0) {
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
$taskOutput = (& schtasks /Query /TN "HITECH-Cloudflared-TunnelGuard" /V /FO LIST 2>&1 | Out-String).Trim()
$taskExit = $LASTEXITCODE
$taskOutputLower = $taskOutput.ToLowerInvariant()
$taskAccessDenied = ($taskOutputLower -match "acceso denegado") -or ($taskOutputLower -match "access is denied")
$taskInstalled = ($taskExit -eq 0) -or $taskAccessDenied

$status = "PASS"
if ($coreExit -ne 0 -or $validateExit -ne 0 -or $dnsExit -ne 0 -or -not $serviceInstalled -or $serviceStatus -ne "Running" -or -not $taskInstalled) {
  $status = "FAIL"
}

$hostnameRouteStatus = if ($dnsOutput -match [regex]::Escape($Hostname) -or $dnsOutput -match "already configured") { "BOUND" } else { "MISSING" }
$watchdogStatus = if ($taskInstalled) {
  if ($taskAccessDenied -and $taskExit -ne 0) { "INSTALLED (QUERY RESTRICTED)" } else { "INSTALLED" }
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
Origin URL: $OriginUrl

Core Exit Code: $coreExit
Validation Exit Code: $validateExit
DNS List Exit Code: $dnsExit

Tunnel UUID: (see $validateJsonPath)
Hostname Route Status: $hostnameRouteStatus
Service Status: $serviceStatus
Watchdog Task Status: $watchdogStatus

Log Directory: $LogDir
Validation JSON: $validateJsonPath
Final Report: $FinalReportPath

--- DNS LIST ---
$dnsOutput

--- SERVICE ---
$serviceOutput

--- WATCHDOG TASK ---
$taskOutput
"@
$report | Set-Content -Path $FinalReportPath -Encoding UTF8

Write-MagentaProgress -Id 1 -Activity "Cloudflare Industrial Setup" -Status "Completed" -Percent 100
Write-Progress -Id 1 -Activity "Cloudflare Industrial Setup" -Completed

$validateJson = @{}
if (Test-Path -LiteralPath $validateJsonPath) {
  try {
    $validateJson = Get-Content -LiteralPath $validateJsonPath -Raw | ConvertFrom-Json -ErrorAction Stop
  } catch {
    $validateJson = @{}
  }
}

if ($validateJson -and ($validateJson.PSObject.Properties.Name -contains "hostname_bound")) {
  if ([bool]$validateJson.hostname_bound) {
    $hostnameRouteStatus = "BOUND"
  } elseif ($hostnameRouteStatus -ne "BOUND") {
    $hostnameRouteStatus = "MISSING"
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
Write-Host ("Service status: {0}" -f $serviceStatus)
Write-Host ("Watchdog task status: {0}" -f $watchdogStatus)
Write-Host ("Logs stored at: {0}" -f $LogDir)

if ($status -ne "PASS") {
  exit 2
}
exit 0

