param(
  [Parameter(Mandatory = $true)]
  [ValidateSet(
    "all-local",
    "all-cloudflare",
    "all-local-cloudflare",
    "diagnose",
    "web-control-local",
    "web-control-local-cloudflare",
    "panel",
    "chart-lab-local",
    "kill-everything"
  )]
  [string]$Profile,

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

$Kill = Join-Path $PSScriptRoot "_kill_ports.ps1"
$Invoke = Join-Path $PSScriptRoot "_invoke_control_center.ps1"
$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $ControlRoot "..")).Path

$LauncherName = $Profile.ToUpperInvariant().Replace("-", "_")
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BaseLogRoot = "F:\descargasf"
$WorkRoot = Join-Path $env:TEMP "PRISMA_LAUNCHER_RUNS"
$RunDir = Join-Path $WorkRoot ("{0}_{1}" -f $LauncherName, $Stamp)
$LatestZip = Join-Path $BaseLogRoot ("latest_{0}.zip" -f $LauncherName)
$TranscriptPath = Join-Path $RunDir "transcript.log"
$SummaryPath = Join-Path $RunDir "summary.json"
$ZipPath = Join-Path $BaseLogRoot ("{0}_{1}.zip" -f $LauncherName, $Stamp)

New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$ExitCode = 0
$TranscriptStarted = $false

function Get-LauncherPorts {
  switch ($Profile) {
    "all-local" { return @(3000,3110,3120,3130,3140,3150) }
    "all-local-cloudflare" { return @(3000,3110,3120,3130,3140,3150) }
    "web-control-local" { return @(3110,3150) }
    "web-control-local-cloudflare" { return @(3110,3150) }
    "chart-lab-local" { return @(3000) }
    "kill-everything" { return @(3000,3100,3110,3120,3130,3140,3150,3200) }
    default { return @() }
  }
}

function Write-Summary {
  param([int]$Code, [string]$Status)
  $summary = [ordered]@{
    schemaVersion = "1.0"
    launcher = $Profile
    launcherName = $LauncherName
    startedAt = $script:StartedAt
    finishedAt = (Get-Date).ToString("s")
    exitCode = $Code
    status = $Status
    repoRoot = $RepoRoot
    controlRoot = $ControlRoot
    tempRunDir = $RunDir
    zipPath = $ZipPath
    latestZip = $LatestZip
    args = $ForwardArgs
    ports = @(Get-LauncherPorts)
    chartLabLiveLog = $script:ChartLog
  }
  $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $SummaryPath -Encoding UTF8
}

function Finalize-LauncherZip {
  param([int]$Code, [string]$Status)

  try {
    Write-Summary -Code $Code -Status $Status
  } catch {
    Write-Host "[PRISMA] WARN no pude escribir summary: $($_.Exception.Message)" -ForegroundColor Yellow
  }

  try {
    if ($TranscriptStarted) {
      Stop-Transcript | Out-Null
      $script:TranscriptStarted = $false
    }
  } catch {
    Write-Host "[PRISMA] WARN Stop-Transcript fallo: $($_.Exception.Message)" -ForegroundColor Yellow
  }

  try {
    if (Test-Path -LiteralPath $ZipPath) {
      Remove-Item -LiteralPath $ZipPath -Force
    }
    Compress-Archive -Path (Join-Path $RunDir "*") -DestinationPath $ZipPath -Force
    Copy-Item -LiteralPath $ZipPath -Destination $LatestZip -Force
    Write-Host ""
    Write-Host "[PRISMA] ZIP de launcher:" -ForegroundColor Green
    Write-Host "  $ZipPath" -ForegroundColor White
    Write-Host "[PRISMA] Latest:" -ForegroundColor Cyan
    Write-Host "  $LatestZip" -ForegroundColor White
  } catch {
    Write-Host "[PRISMA] ERROR no pude crear ZIP: $($_.Exception.Message)" -ForegroundColor Red
    $script:ExitCode = 1
  }

  try {
    if (Test-Path -LiteralPath $RunDir) {
      Remove-Item -LiteralPath $RunDir -Recurse -Force -ErrorAction SilentlyContinue
    }
  } catch {
    Write-Host "[PRISMA] WARN no pude limpiar temp RunDir: $($_.Exception.Message)" -ForegroundColor Yellow
  }
}

function Reset-Ports {
  param([int[]]$Ports, [string]$Reason)
  & $Kill -Ports $Ports -Reason $Reason
  return $LASTEXITCODE
}

function Invoke-Control {
  param([string]$Action)
  & $Invoke -Action $Action @ForwardArgs
  return $LASTEXITCODE
}

function Start-ChartLab {
  $resetExit = Reset-Ports -Ports @(3000) -Reason "Chart Lab local reset 3000"
  if ($resetExit -ne 0) { return $resetExit }

  Write-Host ""
  Write-Host "[PRISMA] Levantando Chart Lab en http://127.0.0.1:3000" -ForegroundColor Cyan

  $script:ChartLog = Join-Path $env:TEMP ("PRISMA_CHART_LAB_{0}.log" -f $Stamp)
  $ChartCommand = "`$ErrorActionPreference='Stop'; Set-Location -LiteralPath '$RepoRoot'; pnpm chart-lab:dev 2>&1 | Tee-Object -FilePath '$script:ChartLog'"

  Start-Process powershell.exe -WorkingDirectory $RepoRoot -ArgumentList @(
    "-NoLogo",
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    $ChartCommand
  ) | Out-Null

  Start-Sleep -Seconds 8
  Start-Process "http://127.0.0.1:3000"
  return 0
}

function Start-AllLocal {
  $resetExit = Reset-Ports -Ports @(3000,3110,3120,3130,3140,3150) -Reason "Todo local reset 3000,3110-3150"
  if ($resetExit -ne 0) { return $resetExit }

  $chartExit = Start-ChartLab
  if ($chartExit -ne 0) { return $chartExit }

  & $Invoke -Action "local-up" @ForwardArgs
  if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }

  & $Invoke -Action "panel" "--open-browser"
  return $LASTEXITCODE
}

function Start-WebControlLocal {
  $resetExit = Reset-Ports -Ports @(3110,3150) -Reason "Web + Control reset 3110,3150"
  if ($resetExit -ne 0) { return $resetExit }

  & $Invoke -Action "local-up" @ForwardArgs
  if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }

  & $Invoke -Action "panel" "--open-browser"
  return $LASTEXITCODE
}

$script:StartedAt = (Get-Date).ToString("s")
$script:ChartLog = $null

try {
  Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null
  $script:TranscriptStarted = $true

  Write-Host "=== PRISMA Launcher OS ===" -ForegroundColor Cyan
  Write-Host "Profile: $Profile" -ForegroundColor Yellow
  Write-Host "Temp RunDir: $RunDir" -ForegroundColor Yellow
  Write-Host "ZipPath: $ZipPath" -ForegroundColor Yellow
  Write-Host "RepoRoot: $RepoRoot" -ForegroundColor DarkCyan
  Write-Host "ControlRoot: $ControlRoot" -ForegroundColor DarkCyan
  Write-Host ""

  switch ($Profile) {
    "all-local" {
      $ExitCode = Start-AllLocal
      break
    }

    "all-cloudflare" {
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = $LASTEXITCODE
      break
    }

    "all-local-cloudflare" {
      $ExitCode = Start-AllLocal
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "health" @ForwardArgs
      if ($LASTEXITCODE -ne 0) { Write-Host "[WARN] Health local reporto problemas; continuo a Cloudflare para dejar evidencia." -ForegroundColor Yellow }
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = $LASTEXITCODE
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "health" @ForwardArgs
      $ExitCode = 0
      break
    }

    "diagnose" {
      & $Invoke -Action "health" @ForwardArgs
      $HealthExit = $LASTEXITCODE
      if ($HealthExit -ne 0) { Write-Host "[WARN] Diagnostico encontro fallas operativas; ZIP generado como evidencia." -ForegroundColor Yellow }
      $ExitCode = 0
      break
    }

    "web-control-local" {
      $ExitCode = Start-WebControlLocal
      break
    }

    "web-control-local-cloudflare" {
      $ExitCode = Start-WebControlLocal
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "health" @ForwardArgs
      if ($LASTEXITCODE -ne 0) { Write-Host "[WARN] Health local reporto problemas; continuo a Cloudflare para dejar evidencia." -ForegroundColor Yellow }
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = $LASTEXITCODE
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "health" @ForwardArgs
      $ExitCode = 0
      break
    }

    "panel" {
      Start-Process "http://127.0.0.1:3150"
      $ExitCode = 0
      break
    }

    "chart-lab-local" {
      $ExitCode = Start-ChartLab
      break
    }

    "kill-everything" {
      $ExitCode = Reset-Ports -Ports @(3000,3100,3110,3120,3130,3140,3150,3200) -Reason "Kill everything PRISMA reset 3000,3100,3110,3120,3130,3140,3150,3200"
      break
    }
  }
} catch {
  $ExitCode = 1
  Write-Host "[PRISMA] ERROR: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
} finally {
  $Status = if ($ExitCode -eq 0) { "ok" } else { "failed" }
  Finalize-LauncherZip -Code $ExitCode -Status $Status
}

exit $ExitCode
