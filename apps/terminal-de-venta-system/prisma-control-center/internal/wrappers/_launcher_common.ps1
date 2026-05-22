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
    "kill-everything",
    "module-cloudflare"
  )]
  [string]$Profile,

  [string]$ServiceId = "",

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

$Kill = Join-Path $PSScriptRoot "_kill_ports.ps1"
$Invoke = Join-Path $PSScriptRoot "_invoke_control_center.ps1"
$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $ControlRoot "..")).Path
$ServicesConfigPath = Join-Path $ControlRoot "internal\config\services.json"
$CloudflareConfigPath = Join-Path $ControlRoot "internal\config\cloudflare.json"

$LauncherName = $Profile.ToUpperInvariant().Replace("-", "_")
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BaseLogRoot = "F:\descargasf"
$WorkRoot = Join-Path $env:TEMP "PRISMA_LAUNCHER_RUNS"
$RunDir = Join-Path $WorkRoot ("{0}_{1}" -f $LauncherName, $Stamp)
$LatestZip = Join-Path $BaseLogRoot ("latest_{0}.zip" -f $LauncherName)
$TranscriptPath = Join-Path $RunDir "transcript.log"
$SummaryPath = Join-Path $RunDir "summary.json"
$ZipPath = Join-Path $BaseLogRoot ("{0}_{1}.zip" -f $LauncherName, $Stamp)

New-Item -ItemType Directory -Force -Path $BaseLogRoot, $RunDir | Out-Null

$ExitCode = 0
$TranscriptStarted = $false

function Write-Banner {
  param([string]$Text)
  Write-Host ""
  Write-Host "============================================================" -ForegroundColor DarkCyan
  Write-Host $Text -ForegroundColor Cyan
  Write-Host "============================================================" -ForegroundColor DarkCyan
}

function Get-JsonObject {
  param([Parameter(Mandatory = $true)][string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "No existe config requerido: $Path"
  }
  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-ServiceDefinitions {
  $cfg = Get-JsonObject -Path $ServicesConfigPath
  $items = @()
  foreach ($svc in @($cfg.services)) {
    $items += [pscustomobject]@{
      Id = [string]$svc.id
      Name = [string]$svc.name
      Port = [int]$svc.port
      Url = [string]$svc.localUrl
      StartCommand = [string]$svc.startCommand
      Cwd = [string]$svc.cwd
      PublicHost = [string]$svc.publicHost
      Kind = "node"
      BrowserPath = "/"
    }
  }
  $items += [pscustomobject]@{
    Id = "control-center-3150"
    Name = "PRISMA Control Center"
    Port = 3150
    Url = "http://127.0.0.1:3150/"
    StartCommand = ""
    Cwd = $ControlRoot
    PublicHost = "control.hitechrts.com"
    Kind = "control-center"
    BrowserPath = "/"
  }
  $items += [pscustomobject]@{
    Id = "chart-lab-3000"
    Name = "PRISMA Chart Lab"
    Port = 3000
    Url = "http://127.0.0.1:3000/"
    StartCommand = "pnpm chart-lab:dev"
    Cwd = $RepoRoot
    PublicHost = ""
    Kind = "chart-lab"
    BrowserPath = "/"
  }
  return @($items | Sort-Object Port)
}

function Get-ServiceById {
  param([Parameter(Mandatory = $true)][string]$Id)
  $match = @(Get-ServiceDefinitions | Where-Object { $_.Id -ieq $Id })
  if ($match.Count -ne 1) {
    throw "Servicio no reconocido: $Id"
  }
  return $match[0]
}

function Get-LauncherPorts {
  switch ($Profile) {
    "all-local" { return @(3000,3110,3120,3130,3140,3150) }
    "all-local-cloudflare" { return @(3000,3110,3120,3130,3140,3150) }
    "web-control-local" { return @(3110,3150) }
    "web-control-local-cloudflare" { return @(3110,3150) }
    "chart-lab-local" { return @(3000) }
    "kill-everything" { return @(3000,3100,3110,3120,3130,3140,3150,3200) }
    "module-cloudflare" {
      if ($ServiceId) { return @((Get-ServiceById -Id $ServiceId).Port) }
      return @()
    }
    default { return @() }
  }
}

function Write-Summary {
  param([int]$Code, [string]$Status)
  $summary = [ordered]@{
    schemaVersion = "2.0"
    launcher = $Profile
    launcherName = $LauncherName
    selectedServiceId = $ServiceId
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
    mode = "minimal-launcher-v2"
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
  if (-not $Ports -or $Ports.Count -eq 0) { return 0 }

  # Do not trust a stale $LASTEXITCODE from a previous native command.
  # _kill_ports.ps1 is a PowerShell script, so success is represented by $? unless it throws.
  $global:LASTEXITCODE = 0
  try {
    & $Kill -Ports $Ports -Reason $Reason
    if (-not $?) { return 1 }
    return 0
  } catch {
    Write-Host "[PRISMA] ERROR liberando puertos: $($_.Exception.Message)" -ForegroundColor Red
    return 1
  }
}

function Invoke-Control {
  param([string]$Action, [string[]]$ExtraArgs = @())
  & $Invoke -Action $Action @ExtraArgs @ForwardArgs
  return $LASTEXITCODE
}

function Test-TcpPort {
  param([string]$HostName = "127.0.0.1", [int]$Port, [int]$TimeoutMs = 900)
  $client = New-Object System.Net.Sockets.TcpClient
  try {
    $iar = $client.BeginConnect($HostName, $Port, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
    if (-not $ok) { return $false }
    $client.EndConnect($iar)
    return $true
  } catch {
    return $false
  } finally {
    $client.Close()
  }
}

function Wait-Port {
  param([int]$Port, [int]$TimeoutSeconds = 60, [string]$Name = "service")
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if (Test-TcpPort -Port $Port) {
      Write-Host "[PRISMA] READY $Name en puerto $Port" -ForegroundColor Green
      return $true
    }
    Start-Sleep -Milliseconds 750
  }
  Write-Host "[PRISMA] TIMEOUT $Name no respondio en puerto $Port" -ForegroundColor Red
  return $false
}

function Start-DetachedPowerShell {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string]$WorkingDirectory
  )
  if (-not (Test-Path -LiteralPath $WorkingDirectory)) {
    throw "No existe working directory para ${Name}: $WorkingDirectory"
  }
  $logPath = Join-Path $BaseLogRoot ("PRISMA_{0}_{1}.log" -f (($Name -replace '[^A-Za-z0-9_-]', '_')), $Stamp)
  $wrapped = "Set-Location -LiteralPath '$WorkingDirectory'; $Command 2>&1 | Tee-Object -FilePath '$logPath'"
  Start-Process powershell.exe -WorkingDirectory $WorkingDirectory -ArgumentList @(
    "-NoLogo",
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    $wrapped
  ) | Out-Null
  Write-Host "[PRISMA] Lanzado $Name. Log vivo: $logPath" -ForegroundColor Cyan
  return $logPath
}

function Start-ChartLab {
  $resetExit = Reset-Ports -Ports @(3000) -Reason "Chart Lab reset 3000"
  if ($resetExit -ne 0) { return $resetExit }

  Write-Host ""
  Write-Host "[PRISMA] Levantando Chart Lab en http://127.0.0.1:3000" -ForegroundColor Cyan

  $script:ChartLog = Start-DetachedPowerShell -Name "chart-lab-3000" -WorkingDirectory $RepoRoot -Command "pnpm chart-lab:dev"
  if (-not (Wait-Port -Port 3000 -TimeoutSeconds 80 -Name "Chart Lab")) { return 2 }
  Start-Process "http://127.0.0.1:3000"
  return 0
}

function Start-ControlCenterDetached {
  param([switch]$OpenBrowser)
  $cmd = "& '$Invoke' -Action panel"
  if ($OpenBrowser) { $cmd = "$cmd --open-browser" }
  Start-DetachedPowerShell -Name "control-center-3150" -WorkingDirectory $ControlRoot -Command $cmd | Out-Null
  if (-not (Wait-Port -Port 3150 -TimeoutSeconds 40 -Name "Control Center")) { return 2 }
  return 0
}

function Start-NodeLikeService {
  param([Parameter(Mandatory = $true)]$Service)
  $resetExit = Reset-Ports -Ports @([int]$Service.Port) -Reason "Modulo reset $($Service.Name) puerto $($Service.Port)"
  if ($resetExit -ne 0) { return $resetExit }
  [void](Start-DetachedPowerShell -Name $Service.Id -WorkingDirectory $Service.Cwd -Command $Service.StartCommand)
  if (-not (Wait-Port -Port ([int]$Service.Port) -TimeoutSeconds 90 -Name $Service.Name)) { return 2 }
  Start-Process $Service.Url
  return 0
}

function Start-OneServiceLocal {
  param([Parameter(Mandatory = $true)]$Service)
  if ($Service.Kind -eq "control-center") {
    $resetExit = Reset-Ports -Ports @([int]$Service.Port) -Reason "Modulo reset $($Service.Name) puerto $($Service.Port)"
    if ($resetExit -ne 0) { return $resetExit }
    return Start-ControlCenterDetached -OpenBrowser
  }
  return Start-NodeLikeService -Service $Service
}


function Stop-PrismaRuntimeProcesses {
  param([string]$Reason = "PRISMA runtime cleanup")

  Write-Host "[PRISMA] Buscando procesos runtime PRISMA fuera de puertos: $Reason" -ForegroundColor Cyan
  $currentPid = [int]$PID
  $targetNames = @(
    "node.exe", "node",
    "npm.exe", "npm",
    "npx.exe", "npx",
    "pnpm.exe", "pnpm",
    "python.exe", "python",
    "python3.exe", "python3",
    "powershell.exe", "powershell",
    "pwsh.exe", "pwsh"
  )
  $needles = @(
    "terminal-de-venta-system",
    "external_interaction_template",
    "prisma-control-center",
    "PRISMA_CONTROL_CENTER_SERVICE_ID"
  )

  try {
    $procs = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
      $cmdLine = [string]$_.CommandLine
      $_.ProcessId -ne $currentPid -and
      $targetNames -contains $_.Name -and
      $cmdLine -and
      @(($needles | Where-Object { $cmdLine -like "*$_*" })).Count -gt 0
    })
  } catch {
    Write-Host "[PRISMA] WARN no pude consultar procesos por ruta: $($_.Exception.Message)" -ForegroundColor Yellow
    return 0
  }

  if ($procs.Count -eq 0) {
    Write-Host "[PRISMA] No encontre procesos runtime PRISMA extra." -ForegroundColor Green
    return 0
  }

  foreach ($proc in $procs) {
    try {
      $pidText = [string]$proc.ProcessId
      Write-Host ("[PRISMA] Matando runtime PID={0} NAME={1}" -f $proc.ProcessId, $proc.Name) -ForegroundColor Yellow
      taskkill.exe /PID $pidText /T /F | Out-Host
    } catch {
      Write-Host "[PRISMA] WARN no pude matar PID=$($proc.ProcessId): $($_.Exception.Message)" -ForegroundColor Yellow
    }
  }
  Start-Sleep -Seconds 1
  return 0
}

function Stop-CloudflareLocal {
  $serviceName = "cloudflared"
  try {
    if (Test-Path -LiteralPath $CloudflareConfigPath) {
      $cfg = Get-JsonObject -Path $CloudflareConfigPath
      if ($cfg.serviceName) { $serviceName = [string]$cfg.serviceName }
    }
  } catch {
    Write-Host "[PRISMA] WARN no pude leer cloudflare.json: $($_.Exception.Message)" -ForegroundColor Yellow
  }

  Write-Host "[PRISMA] Deteniendo Cloudflare local si existe: $serviceName" -ForegroundColor Cyan
  try {
    $svc = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -ne 'Stopped') {
      Stop-Service -Name $serviceName -Force -ErrorAction Stop
      Start-Sleep -Seconds 2
      Write-Host "[PRISMA] Servicio $serviceName detenido." -ForegroundColor Green
    }
  } catch {
    Write-Host "[PRISMA] WARN no pude detener servicio ${serviceName}: $($_.Exception.Message)" -ForegroundColor Yellow
  }

  foreach ($proc in @(Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue)) {
    $cloudflaredPid = [int]$proc.Id
    try {
      Write-Host "[PRISMA] Matando cloudflared PID=$cloudflaredPid" -ForegroundColor Yellow
      Stop-Process -Id $cloudflaredPid -Force -ErrorAction Stop
    } catch {
      Write-Host "[PRISMA] WARN no pude matar cloudflared PID=${cloudflaredPid}: $($_.Exception.Message)" -ForegroundColor Yellow
      Write-Host "[PRISMA] TIP: si cloudflared corre como servicio protegido, ejecuta el launcher como Administrador." -ForegroundColor DarkYellow
    }
  }
}

function Start-AllLocal {
  $resetExit = Reset-Ports -Ports @(3000,3110,3120,3130,3140,3150) -Reason "Todo local reset 3000,3110-3150"
  if ($resetExit -ne 0) { return $resetExit }
  [void](Stop-PrismaRuntimeProcesses -Reason "Todo local cleanup")

  $chartExit = Start-ChartLab
  if ($chartExit -ne 0) { return $chartExit }

  & $Invoke -Action "local-up" @ForwardArgs
  if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }

  $panelExit = Start-ControlCenterDetached -OpenBrowser
  if ($panelExit -ne 0) { return $panelExit }

  Write-Host ""
  Write-Host "PRISMA LOCAL: READY" -ForegroundColor Green
  Write-Host "Local : http://127.0.0.1:3150/" -ForegroundColor White
  Write-Host "Modo  : LOCAL" -ForegroundColor White
  return 0
}

function Start-AllLocalDetachedForCloudflare {
  $resetExit = Reset-Ports -Ports @(3000,3110,3120,3130,3140,3150) -Reason "Todo local + Cloudflare reset 3000,3110-3150"
  if ($resetExit -ne 0) { return $resetExit }
  [void](Stop-PrismaRuntimeProcesses -Reason "Todo local + Cloudflare cleanup")

  $chartExit = Start-ChartLab
  if ($chartExit -ne 0) { return $chartExit }

  & $Invoke -Action "local-up" @ForwardArgs
  if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }

  $panelExit = Start-ControlCenterDetached -OpenBrowser
  if ($panelExit -ne 0) { return $panelExit }

  return 0
}

function Start-WebControlLocal {
  $resetExit = Reset-Ports -Ports @(3110,3150) -Reason "Web + Control reset 3110,3150"
  if ($resetExit -ne 0) { return $resetExit }

  & $Invoke -Action "local-up" @ForwardArgs
  if ($LASTEXITCODE -ne 0) { return $LASTEXITCODE }

  & $Invoke -Action "panel" "--open-browser"
  return $LASTEXITCODE
}

function Show-ModuleMenu {
  $services = @(Get-ServiceDefinitions)
  Write-Host ""
  Write-Host "PRISMA - elegir modulo local + Cloudflare" -ForegroundColor Cyan
  Write-Host ""
  for ($i = 0; $i -lt $services.Count; $i++) {
    $svc = $services[$i]
    $hostText = if ($svc.PublicHost) { "https://$($svc.PublicHost)/" } else { "sin hostname publico configurado" }
    Write-Host (" {0}) {1} | puerto {2} | {3}" -f ($i + 1), $svc.Name, $svc.Port, $hostText) -ForegroundColor White
  }
  Write-Host " 0) Cancelar" -ForegroundColor DarkGray
  Write-Host ""
  $choice = Read-Host "Elige modulo"
  if ($choice -eq "0") { return $null }
  if ($choice -notmatch '^\d+$') { throw "Opcion invalida: $choice" }
  $index = [int]$choice - 1
  if ($index -lt 0 -or $index -ge $services.Count) { throw "Opcion fuera de rango: $choice" }
  return $services[$index]
}

function Start-ModuleCloudflare {
  if (-not $ServiceId) {
    $selected = Show-ModuleMenu
    if ($null -eq $selected) {
      Write-Host "[PRISMA] Cancelado." -ForegroundColor Yellow
      return 0
    }
    $script:ServiceId = [string]$selected.Id
  } else {
    $selected = Get-ServiceById -Id $ServiceId
  }

  Write-Banner "PRISMA MODULO + CLOUDFLARE: $($selected.Name)"
  $localExit = Start-OneServiceLocal -Service $selected
  if ($localExit -ne 0) { return $localExit }

  Stop-CloudflareLocal
  & $Invoke -Action "cloudflare-up" @ForwardArgs
  $cfExit = $LASTEXITCODE
  if ($cfExit -ne 0) { return $cfExit }

  if ($selected.PublicHost) {
    Start-Process ("https://{0}/" -f $selected.PublicHost)
  }

  Write-Host ""
  Write-Host "PRISMA MODULO + CLOUDFLARE: READY" -ForegroundColor Green
  Write-Host ("Local : {0}" -f $selected.Url) -ForegroundColor White
  if ($selected.PublicHost) {
    Write-Host ("Public: https://{0}/" -f $selected.PublicHost) -ForegroundColor White
  } else {
    Write-Host "Public: no configurado para este modulo" -ForegroundColor Yellow
  }
  return 0
}

$script:StartedAt = (Get-Date).ToString("s")
$script:ChartLog = $null

try {
  Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null
  $script:TranscriptStarted = $true

  Write-Host "=== PRISMA Minimal Launcher OS v2 ===" -ForegroundColor Cyan
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
      Stop-CloudflareLocal
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = $LASTEXITCODE
      break
    }

    "all-local-cloudflare" {
      Stop-CloudflareLocal
      $ExitCode = Start-AllLocalDetachedForCloudflare
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = $LASTEXITCODE
      if ($ExitCode -ne 0) { break }

      Write-Host ""
      Write-Host "PRISMA LOCAL + CLOUDFLARE: READY" -ForegroundColor Green
      Write-Host "Local : http://127.0.0.1:3150/" -ForegroundColor White
      Write-Host "Modo  : LOCAL_PUBLIC" -ForegroundColor White
      $ExitCode = 0
      break
    }

    "module-cloudflare" {
      $ExitCode = Start-ModuleCloudflare
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
      Stop-CloudflareLocal
      $ExitCode = Start-WebControlLocal
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = $LASTEXITCODE
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
      Stop-CloudflareLocal
      $ExitCode = Reset-Ports -Ports @(3000,3100,3110,3120,3130,3140,3150,3200) -Reason "Kill all local PRISMA reset 3000,3100,3110,3120,3130,3140,3150,3200"
      [void](Stop-PrismaRuntimeProcesses -Reason "Kill all local")
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
