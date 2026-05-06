@echo off
setlocal
set "PRISMA_CMD_SELF=%~f0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $path=$env:PRISMA_CMD_SELF; $content=Get-Content -LiteralPath $path -Raw; $start='::POWERSHELL_PAYLOAD_'+'START'; $end='::POWERSHELL_PAYLOAD_'+'END'; $parts=$content -split [regex]::Escape($start),2; if($parts.Count -lt 2){throw 'PowerShell payload start marker missing'}; $script=($parts[1] -split [regex]::Escape($end),2)[0]; Invoke-Expression $script"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" pause
exit /b %RC%

::POWERSHELL_PAYLOAD_START
$ErrorActionPreference = "Stop"
$SystemRoot = (Resolve-Path -LiteralPath (Join-Path (Split-Path -Parent $path) ".")).Path
$OutDir = "F:\descargasf"
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$Timestamp = Get-Date -Format "yyMMdd_HHmmss"
$AllLog = Join-Path $OutDir ("prisma_visual_os_{0}.log" -f $Timestamp)
$HealthUrl = "http://127.0.0.1:4177/health"
$RealtimeUrl = "http://127.0.0.1:3120/visual-os/realtime"
$ProUrl = "http://127.0.0.1:3120/visual-os/pro"

function Write-RunLog {
  param([string]$Message, [string]$Level = "INFO")
  $line = "[{0}] [{1}] {2}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), $Level, $Message
  Write-Host $line
  Add-Content -LiteralPath $AllLog -Value $line -Encoding UTF8
}

function ConvertTo-PsSingleQuoted {
  param([string]$Value)
  return "'" + ($Value -replace "'", "''") + "'"
}

function Test-HttpOk {
  param([string]$Url)
  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
    return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
  } catch {
    return $false
  }
}

function Get-PortOwners {
  param([int]$Port)
  $owners = @()
  $connections = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
  foreach ($connection in $connections) {
    $pid = [int]$connection.OwningProcess
    if ($owners.ProcessId -contains $pid) { continue }
    $commandLine = ""
    try {
      $process = Get-CimInstance Win32_Process -Filter ("ProcessId={0}" -f $pid) -ErrorAction Stop
      $commandLine = [string]$process.CommandLine
    } catch {
      $commandLine = ""
    }
    $owners += [pscustomobject]@{ ProcessId = $pid; CommandLine = $commandLine }
  }
  return $owners
}

function Write-PortOwners {
  param([int]$Port, [array]$Owners)
  foreach ($owner in $Owners) {
    Write-RunLog ("Port {0} owner PID={1} CommandLine={2}" -f $Port, $owner.ProcessId, $owner.CommandLine) "WARN"
  }
}

Write-RunLog ("SystemRoot={0}" -f $SystemRoot)
$ServerScript = Join-Path $SystemRoot "tools\prisma-visual-os\live-preview-server-00q.mjs"
if (-not (Test-Path -LiteralPath $ServerScript)) {
  throw "Visual OS realtime server not found: $ServerScript"
}

$nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
if ($null -eq $nodeCommand) { $nodeCommand = Get-Command node -ErrorAction SilentlyContinue }
if ($null -eq $nodeCommand) { throw "node is not available in PATH." }
$Node = $nodeCommand.Source

if (Test-HttpOk $HealthUrl) {
  Write-RunLog ("Visual OS realtime already running: {0}" -f $HealthUrl)
} else {
  $owners = @(Get-PortOwners -Port 4177)
  if ($owners.Count -gt 0) {
    Write-RunLog "Port 4177 is occupied but /health is not healthy. Not starting another Visual OS realtime server." "WARN"
    Write-PortOwners -Port 4177 -Owners $owners
  } else {
    $logPath = Join-Path $OutDir ("prisma_visual_os_realtime_{0}.log" -f $Timestamp)
    $command = @"
`$Host.UI.RawUI.WindowTitle = 'PRISMA Visual OS Realtime 4177'
Set-Location -LiteralPath $(ConvertTo-PsSingleQuoted $SystemRoot)
& $(ConvertTo-PsSingleQuoted $Node) $(ConvertTo-PsSingleQuoted $ServerScript) --port 4177 2>&1 | Tee-Object -FilePath $(ConvertTo-PsSingleQuoted $logPath) -Append
"@
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $command) -WindowStyle Normal
    Write-RunLog ("Started Visual OS realtime on {0}; log={1}" -f $HealthUrl, $logPath)
    Start-Sleep -Seconds 2
  }
}

if (-not (Test-HttpOk "http://127.0.0.1:3120/")) {
  Write-RunLog "[WARN] Tablet is not responding on http://127.0.0.1:3120/. Visual OS API may be up, but Tablet UI routes need Tablet running." "WARN"
}

Start-Process $HealthUrl
Start-Process $RealtimeUrl
Start-Process $ProUrl

Write-RunLog "Final URLs:"
Write-RunLog ("Visual OS health: {0}" -f $HealthUrl)
Write-RunLog ("Tablet realtime UI: {0}" -f $RealtimeUrl)
Write-RunLog ("Tablet pro UI: {0}" -f $ProUrl)
Write-RunLog ("Summary log: {0}" -f $AllLog)
::POWERSHELL_PAYLOAD_END
