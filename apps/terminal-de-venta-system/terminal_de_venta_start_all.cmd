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
$AllLog = Join-Path $OutDir ("prisma_start_all_{0}.log" -f $Timestamp)

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

function Start-PrismaApp {
  param(
    [string]$Name,
    [string]$Root,
    [int]$Port,
    [string]$Url,
    [string]$Pnpm
  )

  if (-not (Test-Path -LiteralPath (Join-Path $Root "package.json"))) {
    throw "Missing package.json for $Name at $Root"
  }

  if (Test-HttpOk $Url) {
    Write-RunLog ("{0} already running: {1}" -f $Name, $Url)
    return
  }

  $owners = @(Get-PortOwners -Port $Port)
  if ($owners.Count -gt 0) {
    Write-RunLog ("{0} port {1} is occupied but {2} is not healthy. Not starting duplicate service." -f $Name, $Port, $Url) "WARN"
    Write-PortOwners -Port $Port -Owners $owners
    return
  }

  $logPath = Join-Path $OutDir ("prisma_start_all_{0}_{1}.log" -f $Name.ToLowerInvariant(), $Timestamp)
  $title = "PRISMA {0} ({1})" -f $Name, $Port
  $command = @"
`$Host.UI.RawUI.WindowTitle = $(ConvertTo-PsSingleQuoted $title)
Set-Location -LiteralPath $(ConvertTo-PsSingleQuoted $Root)
& $(ConvertTo-PsSingleQuoted $Pnpm) -C $(ConvertTo-PsSingleQuoted $Root) dev 2>&1 | Tee-Object -FilePath $(ConvertTo-PsSingleQuoted $logPath) -Append
"@
  Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $command) -WindowStyle Normal
  Write-RunLog ("Started {0} on {1}; log={2}" -f $Name, $Url, $logPath)
}

Write-RunLog ("SystemRoot={0}" -f $SystemRoot)
$TabletRoot = Join-Path $SystemRoot "products\tablet\app"
$PcRoot = Join-Path $SystemRoot "products\pc\app"
$MobileRoot = Join-Path $SystemRoot "products\mobile\app"
$pnpmCommand = Get-Command pnpm.cmd -ErrorAction SilentlyContinue
if ($null -eq $pnpmCommand) { $pnpmCommand = Get-Command pnpm -ErrorAction SilentlyContinue }
if ($null -eq $pnpmCommand) { throw "pnpm is not available in PATH." }
$Pnpm = $pnpmCommand.Source

Start-PrismaApp -Name "Tablet" -Root $TabletRoot -Port 3120 -Url "http://127.0.0.1:3120/" -Pnpm $Pnpm
Start-PrismaApp -Name "PC" -Root $PcRoot -Port 3130 -Url "http://127.0.0.1:3130/" -Pnpm $Pnpm
Start-PrismaApp -Name "Mobile" -Root $MobileRoot -Port 3140 -Url "http://127.0.0.1:3140/" -Pnpm $Pnpm

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:3120/"
Start-Process "http://127.0.0.1:3130/"
Start-Process "http://127.0.0.1:3140/"

Write-RunLog "Final URLs:"
Write-RunLog "Tablet: http://127.0.0.1:3120/"
Write-RunLog "PC:     http://127.0.0.1:3130/"
Write-RunLog "Mobile: http://127.0.0.1:3140/"
Write-RunLog ("Summary log: {0}" -f $AllLog)
::POWERSHELL_PAYLOAD_END
