param(
  [switch]$StartWeb,
  [switch]$PanelOnly,
  [switch]$NoBrowser,
  [int]$PanelPort = 3150,
  [int]$WebPort = 3110
)

$ErrorActionPreference = "Stop"

$WrapperRoot = $PSScriptRoot
$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $WrapperRoot "..\..")).Path
$Invoke = Join-Path $WrapperRoot "_invoke_control_center.ps1"
$Kill = Join-Path $WrapperRoot "_kill_ports.ps1"
$ServicesPath = Join-Path $ControlRoot "internal\config\services.json"

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutDir = "F:\descargasf"
$RunRoot = Join-Path $env:TEMP "PRISMA_CONTROL_SAFE_RUNS"
$RunDir = Join-Path $RunRoot ("CONTROL_SAFE_{0}" -f $Stamp)
$StageDir = Join-Path $RunDir "_zip_stage"
$SummaryPath = Join-Path $RunDir "summary.json"
$TranscriptPath = Join-Path $RunDir "transcript.log"
$ZipPath = Join-Path $OutDir ("CONTROL_SAFE_{0}.zip" -f $Stamp)
$LatestZip = Join-Path $OutDir "latest_CONTROL_SAFE.zip"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$Events = @()
$Probes = @()
$Warnings = @()
$TranscriptOn = $false

function Add-Event($Action, $Detail) {
  $script:Events += [pscustomobject]@{ time = (Get-Date).ToString("s"); action = $Action; detail = $Detail }
}

function Add-Warn($Text) {
  $script:Warnings += $Text
  Write-Host "[PRISMA] WARN: $Text" -ForegroundColor Yellow
}

function Probe($Url, [switch]$Json) {
  try {
    $R = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 8 -ErrorAction Stop
    $JsonOk = $false
    if ($Json) {
      try { $null = $R.Content | ConvertFrom-Json -ErrorAction Stop; $JsonOk = $true } catch { $JsonOk = $false }
    }
    $Obj = [pscustomobject]@{ url = $Url; ok = $true; status = [int]$R.StatusCode; json = $JsonOk; error = "" }
  } catch {
    $Code = $null
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) { $Code = [int]$_.Exception.Response.StatusCode }
    $Obj = [pscustomobject]@{ url = $Url; ok = $false; status = $Code; json = $false; error = $_.Exception.Message }
  }
  $script:Probes += $Obj
  return $Obj
}

function Kill-Ports([int[]]$Ports) {
  Add-Event "kill-ports" ($Ports -join ",")
  & $Kill -Ports $Ports -Reason "PRISMA Control Center safe launcher"
  if ($LASTEXITCODE -ne 0) { Add-Warn "_kill_ports retorno $LASTEXITCODE para $($Ports -join ',')" }
}

function Invoke-ControlQuiet($Action, [string[]]$ArgsList = @()) {
  $Log = Join-Path $RunDir ("control_{0}_{1}.log" -f $Action, (Get-Date -Format "HHmmss"))
  Add-Event "control-$Action" @{ args = ($ArgsList -join " "); log = $Log }
  & $Invoke -Action $Action @ArgsList *> $Log
  $Code = if ($null -eq $LASTEXITCODE) { 0 } else { [int]$LASTEXITCODE }
  return $Code
}

function Start-Web3110() {
  if (-not (Test-Path -LiteralPath $ServicesPath)) {
    Add-Warn "No existe services.json; salto Web/EIT 3110."
    return $false
  }
  $Services = Get-Content -LiteralPath $ServicesPath -Raw -Encoding UTF8 | ConvertFrom-Json
  $Svc = $Services.services | Where-Object { [int]$_.port -eq $WebPort } | Select-Object -First 1
  if (-not $Svc) {
    Add-Warn "No encontre servicio puerto ${WebPort} en services.json."
    return $false
  }
  if (-not (Test-Path -LiteralPath $Svc.cwd)) {
    Add-Warn "No existe cwd de Web/EIT: $($Svc.cwd)"
    return $false
  }

  Kill-Ports @($WebPort)
  $WebLog = Join-Path $RunDir "web_3110.log"
  $Command = "`$ErrorActionPreference='Continue'; $($Svc.startCommand) *> '$WebLog'"
  Add-Event "start-web-3110" @{ cwd = $Svc.cwd; command = $Svc.startCommand; log = $WebLog }
  Start-Process powershell.exe -WorkingDirectory $Svc.cwd -ArgumentList @("-NoLogo", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $Command) | Out-Null

  for ($i = 1; $i -le 35; $i++) {
    Start-Sleep -Seconds 2
    $WebProbe = Probe "http://127.0.0.1:${WebPort}/"
    if ($WebProbe.ok) { return $true }
  }
  Add-Warn "Web/EIT 3110 no confirmo HTTP; continuo con panel."
  return $false
}

function Start-Panel3150() {
  Kill-Ports @($PanelPort)
  $Args = @("-NoLogo", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $Invoke, "-Action", "panel")
  if (-not $NoBrowser) { $Args += "--open-browser" }
  Add-Event "start-panel-3150" "http://127.0.0.1:${PanelPort}/"
  Start-Process powershell.exe -WorkingDirectory $ControlRoot -ArgumentList $Args | Out-Null

  for ($i = 1; $i -le 35; $i++) {
    Start-Sleep -Seconds 1
    $PanelHomeProbe = Probe "http://127.0.0.1:${PanelPort}/"
    $PanelHealthProbe = Probe "http://127.0.0.1:${PanelPort}/api/health" -Json
    if ($PanelHomeProbe.ok -and $PanelHealthProbe.json) { return $true }
  }
  Add-Warn "Panel 3150 no confirmo /api/health JSON a tiempo."
  return $false
}

function Copy-IfReadable($Source, $Destination) {
  try {
    if (-not (Test-Path -LiteralPath $Source)) { return $false }
    New-Item -ItemType Directory -Force -Path (Split-Path $Destination -Parent) | Out-Null
    $In = [System.IO.File]::Open($Source, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
      $Out = [System.IO.File]::Open($Destination, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
      try { $In.CopyTo($Out) } finally { $Out.Close() }
    } finally { $In.Close() }
    return $true
  } catch {
    Add-Warn "No pude copiar para ZIP: $Source :: $($_.Exception.Message)"
    return $false
  }
}

function Finish($ExitCode, $Status) {
  $Summary = [pscustomobject]@{
    schemaVersion = "3.0"
    launcher = "control-center-safe"
    status = $Status
    exitCode = $ExitCode
    generatedAt = (Get-Date).ToString("s")
    controlRoot = $ControlRoot
    runDir = $RunDir
    zipPath = $ZipPath
    latestZip = $LatestZip
    startWeb = [bool]$StartWeb
    panelOnly = [bool]$PanelOnly
    warnings = $Warnings
    events = $Events
    probes = $Probes
  }
  $Summary | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $SummaryPath -Encoding UTF8

  if ($script:TranscriptOn) {
    try { Stop-Transcript | Out-Null } catch {}
    $script:TranscriptOn = $false
  }

  if (Test-Path -LiteralPath $StageDir) { Remove-Item -LiteralPath $StageDir -Recurse -Force -ErrorAction SilentlyContinue }
  New-Item -ItemType Directory -Force -Path $StageDir | Out-Null

  Get-ChildItem -LiteralPath $RunDir -File -ErrorAction SilentlyContinue | ForEach-Object {
    $Dest = Join-Path $StageDir $_.Name
    [void](Copy-IfReadable $_.FullName $Dest)
  }

  if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction SilentlyContinue }
  Compress-Archive -Path (Join-Path $StageDir "*") -DestinationPath $ZipPath -Force
  Copy-Item -LiteralPath $ZipPath -Destination $LatestZip -Force

  Write-Host ""
  Write-Host "[PRISMA] Estado: $Status" -ForegroundColor Green
  Write-Host "[PRISMA] Panel: http://127.0.0.1:${PanelPort}/" -ForegroundColor Cyan
  Write-Host "[PRISMA] Evidencia: $ZipPath" -ForegroundColor Cyan
  Write-Host "[PRISMA] Latest: $LatestZip" -ForegroundColor Cyan
}

$ExitCode = 0
$Status = "panel-ready"

try {
  Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null
  $TranscriptOn = $true

  Write-Host "=== PRISMA Control Center Safe Launcher v3 ===" -ForegroundColor Cyan
  Write-Host "ControlRoot: $ControlRoot" -ForegroundColor DarkCyan

  if ($PanelOnly) {
    $PanelOk = Start-Panel3150
  } else {
    if ($StartWeb) { $null = Start-Web3110 }

    $HealthBeforeCode = Invoke-ControlQuiet "health"
    if ($HealthBeforeCode -ne 0) { Add-Warn "health previo regreso $HealthBeforeCode; continuo para abrir panel con evidencia." }

    $PanelOk = Start-Panel3150

    $HealthAfterCode = Invoke-ControlQuiet "health"
    if ($HealthAfterCode -ne 0) { Add-Warn "health posterior regreso $HealthAfterCode; panel queda abierto con estado degradado." }
  }

  $FinalHomeProbe = Probe "http://127.0.0.1:${PanelPort}/"
  $FinalHealthProbe = Probe "http://127.0.0.1:${PanelPort}/api/health" -Json
  if (-not ($FinalHomeProbe.ok -and $FinalHealthProbe.json)) {
    $ExitCode = 2
    $Status = "panel-not-confirmed"
  } elseif ($Warnings.Count -gt 0) {
    $ExitCode = 0
    $Status = "degraded-but-panel-ready"
  } else {
    $ExitCode = 0
    $Status = "panel-ready"
  }
} catch {
  $ExitCode = 1
  $Status = "launcher-error"
  Add-Warn $_.Exception.Message
} finally {
  Finish $ExitCode $Status
}

exit $ExitCode
