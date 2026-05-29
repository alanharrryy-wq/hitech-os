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

  [object]$Code = $null,

  [Parameter(ValueFromRemainingArguments = $true)]
  [object[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $Utf8NoBom
$OutputEncoding = $Utf8NoBom
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8:replace"
$env:NO_COLOR = "1"

# PRISMO_LAUNCHER_GEMINI_ENV_GUARD_BEGIN
function Set-PrismoAiProcessEnv {
  $userGemini = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "User")
  if ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY) -and -not [string]::IsNullOrWhiteSpace($userGemini)) {
    $env:GEMINI_API_KEY = $userGemini
  }

  if (-not [string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
    $env:PRISMO_AI_ENABLED = "true"
    $env:PRISMO_AI_DEMO_MODE = "false"
  } else {
    if ([string]::IsNullOrWhiteSpace($env:PRISMO_AI_ENABLED)) { $env:PRISMO_AI_ENABLED = "false" }
    if ([string]::IsNullOrWhiteSpace($env:PRISMO_AI_DEMO_MODE)) { $env:PRISMO_AI_DEMO_MODE = "true" }
  }
}
Set-PrismoAiProcessEnv
# PRISMO_LAUNCHER_GEMINI_ENV_GUARD_END

function ConvertTo-ScalarExitCode {
  param(
    [object]$Code,
    [int]$Default = 1
  )

  $sentinel = [int]::MinValue
  if ($null -eq $Code) { return [int]$Default }

  if ($Code -is [System.Array]) {
    $items = @($Code)
    for ($i = $items.Count - 1; $i -ge 0; $i--) {
      $candidate = ConvertTo-ScalarExitCode -Code $items[$i] -Default $sentinel
      if ($candidate -ne $sentinel) { return [int]$candidate }
    }
    return [int]$Default
  }

  if ($Code -is [bool]) {
    if ($Code) { return 0 }
    return 1
  }

  $parsed = 0
  if ([int]::TryParse(([string]$Code).Trim(), [ref]$parsed)) {
    return [int]$parsed
  }

  return [int]$Default
}

function ConvertTo-ForwardArgs {
  param([object[]]$ArgsValue)
  $items = New-Object System.Collections.Generic.List[string]
  foreach ($arg in @($ArgsValue)) {
    if ($null -eq $arg) { continue }
    if ($arg -is [System.Array]) {
      foreach ($nested in @($arg)) {
        if ($null -ne $nested) { $items.Add([string]$nested) }
      }
      continue
    }
    $items.Add([string]$arg)
  }
  return [string[]]$items.ToArray()
}

function Get-NamedForwardArg {
  param([string[]]$ArgsValue, [string]$Name)
  for ($i = 0; $i -lt $ArgsValue.Count; $i++) {
    if ($ArgsValue[$i] -ieq $Name -and ($i + 1) -lt $ArgsValue.Count) {
      return [string]$ArgsValue[$i + 1]
    }
  }
  return ""
}

function Remove-NamedForwardArg {
  param([string[]]$ArgsValue, [string]$Name)
  $items = New-Object System.Collections.Generic.List[string]
  for ($i = 0; $i -lt $ArgsValue.Count; $i++) {
    if ($ArgsValue[$i] -ieq $Name) {
      $i++
      continue
    }
    $items.Add($ArgsValue[$i])
  }
  return [string[]]$items.ToArray()
}

function Test-IsAdministrator {
  try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  } catch {
    return $false
  }
}

function Get-PowerShellExecutable {
  try {
    $current = (Get-Process -Id $PID -ErrorAction Stop).Path
    if ($current -and (Test-Path -LiteralPath $current)) { return $current }
  } catch {
    # Fall through to PATH lookup.
  }
  foreach ($candidate in @("pwsh.exe", "powershell.exe", "pwsh", "powershell")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  return "powershell.exe"
}

$ForwardArgs = @(ConvertTo-ForwardArgs -ArgsValue $ForwardArgs)
$IgnoredLauncherCode = ConvertTo-ScalarExitCode -Code $Code -Default 0
$forwardServiceId = Get-NamedForwardArg -ArgsValue $ForwardArgs -Name "-ServiceId"
if ($forwardServiceId) {
  $ServiceId = $forwardServiceId
  $ForwardArgs = @(Remove-NamedForwardArg -ArgsValue $ForwardArgs -Name "-ServiceId")
}
if ($ServiceId -ieq "-ServiceId" -and $ForwardArgs.Count -gt 0) {
  $ServiceId = [string]$ForwardArgs[0]
  $ForwardArgs = @($ForwardArgs | Select-Object -Skip 1)
}
if ($ServiceId -and $ServiceId -notmatch '^[A-Za-z][A-Za-z0-9_-]*$') {
  Write-Host "[PRISMA] WARN ServiceId invalido recibido desde argumentos externos: $ServiceId. Se ignora para evitar crash de launcher." -ForegroundColor Yellow
  $ServiceId = ""
}

$Kill = Join-Path $PSScriptRoot "_kill_ports.ps1"
$Invoke = Join-Path $PSScriptRoot "_invoke_control_center.ps1"
$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $ControlRoot "..")).Path
$ServicesConfigPath = Join-Path $ControlRoot "internal\config\services.json"
$CloudflareConfigPath = Join-Path $ControlRoot "internal\config\cloudflare.json"

$LauncherName = $Profile.ToUpperInvariant().Replace("-", "_")
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BaseLogRoot = "<OUTPUT_DIR>"
$WorkRoot = Join-Path $env:TEMP "PRISMA_OPERATOR_RUNS"
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
  param([object]$Code, [string]$Status)
  $safeCode = ConvertTo-ScalarExitCode -Code $Code -Default 1
  $summary = [ordered]@{
    schemaVersion = "2.0"
    launcher = $Profile
    launcherName = $LauncherName
    selectedServiceId = $ServiceId
    startedAt = $script:StartedAt
    finishedAt = (Get-Date).ToString("s")
    exitCode = $safeCode
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
  param([object]$Code, [string]$Status)

  $safeCode = ConvertTo-ScalarExitCode -Code $Code -Default 1

  try {
    Write-Summary -Code $safeCode -Status $Status
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
  return (ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1)
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

function Test-HttpReady {
  param([Parameter(Mandatory = $true)][string]$Url, [int]$TimeoutSeconds = 8)
  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds
    return ([int]$response.StatusCode -ge 200 -and [int]$response.StatusCode -lt 500)
  } catch {
    return $false
  }
}

function Test-SelectedModulePublicReady {
  param([Parameter(Mandatory = $true)]$Service)
  if (-not $Service.PublicHost) { return $false }
  $publicUrl = "https://{0}/" -f $Service.PublicHost
  return (Test-HttpReady -Url $publicUrl -TimeoutSeconds 20)
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
  $psExe = Get-PowerShellExecutable
  $safeWorkingDirectory = $WorkingDirectory.Replace("'", "''")
  $safeLogPath = $logPath.Replace("'", "''")
  $wrapped = "`$utf8NoBom = New-Object System.Text.UTF8Encoding(`$false); [Console]::OutputEncoding = `$utf8NoBom; `$OutputEncoding = `$utf8NoBom; `$env:PYTHONUTF8 = '1'; `$env:PYTHONIOENCODING = 'utf-8:replace'; `$env:NO_COLOR = '1'; Set-Location -LiteralPath '$safeWorkingDirectory'; $Command 2>&1 | Tee-Object -FilePath '$safeLogPath'"
  Start-Process $psExe -WorkingDirectory $WorkingDirectory -ArgumentList @(
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
  if (Test-HttpReady -Url $Service.Url) {
    Write-Host "[PRISMA] $($Service.Name) ya responde en $($Service.Url); reutilizo el modulo local existente." -ForegroundColor Green
    Start-Process $Service.Url
    return 0
  }
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
    $allProcesses = @(Get-CimInstance Win32_Process -ErrorAction Stop)
    $processById = @{}
    foreach ($procInfo in $allProcesses) {
      $processById[[int]$procInfo.ProcessId] = $procInfo
    }

    function Test-IsCurrentProcessLineage {
      param([int]$CandidatePid)
      $cursor = $currentPid
      $guard = 0
      while ($processById.ContainsKey($cursor) -and $guard -lt 64) {
        if ($CandidatePid -eq $cursor) { return $true }
        $parent = [int]$processById[$cursor].ParentProcessId
        if ($CandidatePid -eq $parent) { return $true }
        if ($parent -le 0 -or $parent -eq $cursor) { break }
        $cursor = $parent
        $guard++
      }
      return $false
    }

    $procs = @($allProcesses | Where-Object {
      $cmdLine = [string]$_.CommandLine
      $_.ProcessId -ne $currentPid -and
      -not (Test-IsCurrentProcessLineage -CandidatePid ([int]$_.ProcessId)) -and
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
  $isAdmin = Test-IsAdministrator
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
      if (-not $isAdmin) {
        Write-Host "[PRISMA] WARN $serviceName corre como servicio protegido y esta Running; no lo detengo sin Administrador." -ForegroundColor Yellow
        Write-Host "[PRISMA] Continuo reutilizando el conector existente. Si el tunel queda stale, relanza como Administrador o ejecuta: Restart-Service -Name '$serviceName' -Force" -ForegroundColor DarkYellow
        return 0
      }
      Stop-Service -Name $serviceName -Force -ErrorAction Stop
      Start-Sleep -Seconds 2
      Write-Host "[PRISMA] Servicio $serviceName detenido." -ForegroundColor Green
    }
  } catch {
    Write-Host "[PRISMA] WARN no pude detener servicio ${serviceName}: $($_.Exception.Message)" -ForegroundColor Yellow
    if (-not $isAdmin) {
      Write-Host "[PRISMA] TIP: $serviceName requiere consola elevada para detener/reiniciar el servicio." -ForegroundColor DarkYellow
      return 0
    }
  }

  foreach ($proc in @(Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue)) {
    $cloudflaredPid = [int]$proc.Id
    if (-not $isAdmin) {
      Write-Host "[PRISMA] WARN cloudflared PID=$cloudflaredPid parece protegido; no intento Stop-Process sin Administrador." -ForegroundColor Yellow
      continue
    }
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
  $localUpExit = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
  if ($localUpExit -ne 0) { return $localUpExit }

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
  $localUpExit = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
  if ($localUpExit -ne 0) { return $localUpExit }

  $panelExit = Start-ControlCenterDetached -OpenBrowser
  if ($panelExit -ne 0) { return $panelExit }

  return 0
}

function Start-WebControlLocal {
  $resetExit = Reset-Ports -Ports @(3110,3150) -Reason "Web + Control reset 3110,3150"
  if ($resetExit -ne 0) { return $resetExit }

  & $Invoke -Action "local-up" @ForwardArgs
  $localUpExit = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
  if ($localUpExit -ne 0) { return $localUpExit }

  & $Invoke -Action "panel" "--open-browser"
  return (ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1)
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
  $localExit = ConvertTo-ScalarExitCode -Code (Start-OneServiceLocal -Service $selected) -Default 1
  if ($localExit -ne 0) { return $localExit }

  Stop-CloudflareLocal
  & $Invoke -Action "cloudflare-up" @ForwardArgs
  $cfExit = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
  if ($cfExit -ne 0) {
    $selectedLocalOk = Test-HttpReady -Url $selected.Url
    $selectedPublicOk = Test-SelectedModulePublicReady -Service $selected
    if ($selectedLocalOk -and $selectedPublicOk) {
      Write-Host "[PRISMA] WARN Cloudflare global esta degradado, pero el modulo seleccionado responde local y publico." -ForegroundColor Yellow
      Write-Host "[PRISMA] Continuo con exito para $($selected.Name); revisa el reporte global para otros modulos caidos." -ForegroundColor DarkYellow
      $cfExit = 0
    } else {
      return $cfExit
    }
  }

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
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-AllLocal) -Default 1
      break
    }

    "all-cloudflare" {
      Stop-CloudflareLocal
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
      break
    }

    "all-local-cloudflare" {
      Stop-CloudflareLocal
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-AllLocalDetachedForCloudflare) -Default 1
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
      if ($ExitCode -ne 0) { break }

      Write-Host ""
      Write-Host "PRISMA LOCAL + CLOUDFLARE: READY" -ForegroundColor Green
      Write-Host "Local : http://127.0.0.1:3150/" -ForegroundColor White
      Write-Host "Modo  : LOCAL_PUBLIC" -ForegroundColor White
      $ExitCode = 0
      break
    }

    "module-cloudflare" {
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-ModuleCloudflare) -Default 1
      break
    }

    "diagnose" {
      & $Invoke -Action "health" @ForwardArgs
      $HealthExit = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
      if ($HealthExit -ne 0) { Write-Host "[WARN] Diagnostico encontro fallas operativas; ZIP generado como evidencia." -ForegroundColor Yellow }
      $ExitCode = 0
      break
    }

    "web-control-local" {
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-WebControlLocal) -Default 1
      break
    }

    "web-control-local-cloudflare" {
      Stop-CloudflareLocal
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-WebControlLocal) -Default 1
      if ($ExitCode -ne 0) { break }
      & $Invoke -Action "cloudflare-up" @ForwardArgs
      $ExitCode = ConvertTo-ScalarExitCode -Code $LASTEXITCODE -Default 1
      break
    }

    "panel" {
      # PRISMO_PANEL_PROFILE_STARTS_SERVER_BEGIN
      # El perfil panel no debe solo abrir navegador: debe asegurar servidor 3150 vivo.
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-ControlCenterDetached -OpenBrowser) -Default 1
      # PRISMO_PANEL_PROFILE_STARTS_SERVER_END
      break
    }

    "chart-lab-local" {
      $ExitCode = ConvertTo-ScalarExitCode -Code (Start-ChartLab) -Default 1
      break
    }

    "kill-everything" {
      Stop-CloudflareLocal
      $ExitCode = ConvertTo-ScalarExitCode -Code (Reset-Ports -Ports @(3000,3100,3110,3120,3130,3140,3150,3200) -Reason "Kill all local PRISMA reset 3000,3100,3110,3120,3130,3140,3150,3200") -Default 1
      [void](Stop-PrismaRuntimeProcesses -Reason "Kill all local")
      break
    }
  }
} catch {
  $ExitCode = 1
  Write-Host "[PRISMA] ERROR: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
} finally {
  $ExitCode = ConvertTo-ScalarExitCode -Code $ExitCode -Default 1
  $Status = if ($ExitCode -eq 0) { "ok" } else { "failed" }
  Finalize-LauncherZip -Code $ExitCode -Status $Status
}

exit (ConvertTo-ScalarExitCode -Code $ExitCode -Default 1)
