param(
  [Parameter(Mandatory = $true)]
  [int[]]$Ports,

  [string]$Reason = "PRISMA launcher reset",

  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProtectedNames = @(
  "System",
  "System Idle Process",
  "Idle",
  "Registry",
  "smss.exe",
  "csrss.exe",
  "wininit.exe",
  "winlogon.exe",
  "services.exe",
  "lsass.exe",
  "fontdrvhost.exe",
  "dwm.exe"
)

$TcpBlockingStates = @(
  "LISTEN",
  "LISTENING",
  "BOUND"
)

function Add-PortOwner {
  param(
    [hashtable]$Owners,
    [int]$Pid,
    [int]$Port,
    [string]$Protocol,
    [string]$State,
    [string]$Line
  )

  if ($Pid -lt 0) { return }

  if (-not $Owners.ContainsKey($Pid)) {
    $Owners[$Pid] = [ordered]@{
      Pid = $Pid
      Ports = New-Object System.Collections.Generic.List[int]
      Lines = New-Object System.Collections.Generic.List[string]
      States = New-Object System.Collections.Generic.List[string]
    }
  }

  if (-not $Owners[$Pid].Ports.Contains($Port)) {
    $Owners[$Pid].Ports.Add($Port)
  }

  if ($Line) {
    $Owners[$Pid].Lines.Add($Line)
  }

  $stateText = if ($State) { "$Protocol/$State" } else { "$Protocol" }
  if (-not $Owners[$Pid].States.Contains($stateText)) {
    $Owners[$Pid].States.Add($stateText)
  }
}

function Get-PortFromLocalEndpoint {
  param([string]$LocalEndpoint)

  if (-not $LocalEndpoint) { return $null }

  if ($LocalEndpoint -match "\]:(\d+)$") {
    return [int]$Matches[1]
  }

  if ($LocalEndpoint -match ":(\d+)$") {
    return [int]$Matches[1]
  }

  return $null
}

function Get-PortOwnersFromNetTcp {
  param([int[]]$TargetPorts)

  $owners = @{}
  $canUseTcp = [bool](Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue)
  $canUseUdp = [bool](Get-Command Get-NetUDPEndpoint -ErrorAction SilentlyContinue)

  if (-not $canUseTcp -and -not $canUseUdp) {
    throw "Get-NetTCPConnection/Get-NetUDPEndpoint no disponibles."
  }

  if ($canUseTcp) {
    foreach ($conn in @(Get-NetTCPConnection -ErrorAction Stop)) {
      $localPort = [int]$conn.LocalPort
      if ($TargetPorts -notcontains $localPort) { continue }

      $state = ([string]$conn.State).ToUpperInvariant()

      # El puerto que bloquea un dev server es LISTENING/BOUND.
      # TIME_WAIT, CLOSE_WAIT, FIN_WAIT y residuos similares no deben romper el launcher.
      if ($TcpBlockingStates -notcontains $state) { continue }

      Add-PortOwner `
        -Owners $owners `
        -Pid ([int]$conn.OwningProcess) `
        -Port $localPort `
        -Protocol "TCP" `
        -State $state `
        -Line ("TCP {0}:{1} {2} PID={3}" -f $conn.LocalAddress, $conn.LocalPort, $state, $conn.OwningProcess)
    }
  }

  if ($canUseUdp) {
    foreach ($udp in @(Get-NetUDPEndpoint -ErrorAction Stop)) {
      $localPort = [int]$udp.LocalPort
      if ($TargetPorts -notcontains $localPort) { continue }

      Add-PortOwner `
        -Owners $owners `
        -Pid ([int]$udp.OwningProcess) `
        -Port $localPort `
        -Protocol "UDP" `
        -State "BOUND" `
        -Line ("UDP {0}:{1} PID={2}" -f $udp.LocalAddress, $udp.LocalPort, $udp.OwningProcess)
    }
  }

  return $owners.Values
}

function Get-PortOwnersFromNetstat {
  param([int[]]$TargetPorts)

  $owners = @{}
  $rows = @(netstat -ano -p tcp) + @(netstat -ano -p udp)

  foreach ($line in $rows) {
    $trim = $line.Trim()
    if (-not $trim) { continue }

    $parts = $trim -split "\s+"
    if ($parts.Count -lt 4) { continue }

    $proto = $parts[0].ToUpperInvariant()
    if ($proto -ne "TCP" -and $proto -ne "UDP") { continue }

    $local = $parts[1]
    $pidText = $parts[$parts.Count - 1]
    if ($pidText -notmatch "^\d+$") { continue }

    $port = Get-PortFromLocalEndpoint -LocalEndpoint $local
    if ($null -eq $port) { continue }
    if ($TargetPorts -notcontains [int]$port) { continue }

    $state = "BOUND"

    if ($proto -eq "TCP") {
      if ($parts.Count -lt 5) { continue }
      $state = $parts[$parts.Count - 2].ToUpperInvariant()

      # netstat reporta residuos TCP como TIME_WAIT/CLOSE_WAIT después de taskkill.
      # Esos no son listeners y no deben causar falso FAIL.
      if ($TcpBlockingStates -notcontains $state) { continue }
    }

    Add-PortOwner `
      -Owners $owners `
      -Pid ([int]$pidText) `
      -Port ([int]$port) `
      -Protocol $proto `
      -State $state `
      -Line $trim
  }

  return $owners.Values
}

function Get-PortOwners {
  param([int[]]$TargetPorts)

  try {
    return @(Get-PortOwnersFromNetTcp -TargetPorts $TargetPorts)
  } catch {
    Write-Host "[PRISMA] WARN Get-NetTCPConnection/Get-NetUDPEndpoint no basto; uso netstat filtrado. $($_.Exception.Message)" -ForegroundColor DarkYellow
    return @(Get-PortOwnersFromNetstat -TargetPorts $TargetPorts)
  }
}

function Get-OwnerRuntimeInfo {
  param([Parameter(Mandatory = $true)]$Owner)

  $targetPid = [int]$Owner.Pid
  $portsText = ($Owner.Ports | Sort-Object) -join ","
  $statesText = ($Owner.States | Sort-Object) -join ","

  if ($targetPid -le 4) {
    return [pscustomobject]@{
      Ignore = $true
      Reason = "PID protegido/sistema"
      Pid = $targetPid
      Name = "SYSTEM"
      Process = $null
      PortsText = $portsText
      StatesText = $statesText
    }
  }

  $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
  if (-not $proc) {
    return [pscustomobject]@{
      Ignore = $true
      Reason = "PID stale, el proceso ya no existe"
      Pid = $targetPid
      Name = "UNKNOWN"
      Process = $null
      PortsText = $portsText
      StatesText = $statesText
    }
  }

  $namePlain = [string]$proc.ProcessName
  $nameExe = "$namePlain.exe"

  if ($ProtectedNames -contains $namePlain -or $ProtectedNames -contains $nameExe) {
    return [pscustomobject]@{
      Ignore = $true
      Reason = "proceso protegido"
      Pid = $targetPid
      Name = $nameExe
      Process = $proc
      PortsText = $portsText
      StatesText = $statesText
    }
  }

  return [pscustomobject]@{
    Ignore = $false
    Reason = ""
    Pid = $targetPid
    Name = $nameExe
    Process = $proc
    PortsText = $portsText
    StatesText = $statesText
  }
}

function Get-RealBlockingOwners {
  param([int[]]$TargetPorts)

  $owners = @(Get-PortOwners -TargetPorts $TargetPorts)
  $real = @()

  foreach ($owner in $owners) {
    $info = Get-OwnerRuntimeInfo -Owner $owner

    if ($info.Ignore) {
      Write-Host "[PRISMA] SKIP $($info.Reason) PID=$($info.Pid) NAME=$($info.Name) PORTS=$($info.PortsText) STATES=$($info.StatesText)" -ForegroundColor DarkYellow
      continue
    }

    $real += [pscustomobject]@{
      Owner = $owner
      Pid = [int]$info.Pid
      Name = [string]$info.Name
      PortsText = [string]$info.PortsText
      StatesText = [string]$info.StatesText
      Process = $info.Process
    }
  }

  return @($real)
}

Write-Host ""
Write-Host "[PRISMA] Revisando puertos: $($Ports -join ', ')" -ForegroundColor Cyan
Write-Host "[PRISMA] Motivo: $Reason" -ForegroundColor DarkCyan

$maxRounds = if ($DryRun) { 1 } else { 6 }

for ($round = 1; $round -le $maxRounds; $round++) {
  $blockingOwners = @(Get-RealBlockingOwners -TargetPorts $Ports)

  if ($blockingOwners.Count -eq 0) {
    Write-Host "[PRISMA] Puertos libres o solo quedan residuos/protegidos ignorables." -ForegroundColor Green
    return
  }

  if ($DryRun) {
    foreach ($owner in $blockingOwners) {
      Write-Host "[PRISMA] DRY-RUN mataria PID=$($owner.Pid) NAME=$($owner.Name) PORTS=$($owner.PortsText) STATES=$($owner.StatesText)" -ForegroundColor Yellow
    }
    return
  }

  Write-Host "[PRISMA] Ronda ${round}: liberando procesos reales que escuchan puertos objetivo." -ForegroundColor Yellow

  foreach ($pidValue in @($blockingOwners.Pid | Sort-Object -Unique)) {
    $ownedByPid = @($blockingOwners | Where-Object { $_.Pid -eq $pidValue })
    $portsText = (($ownedByPid | ForEach-Object { $_.Owner.Ports } | ForEach-Object { $_ }) | Sort-Object -Unique) -join ","
    $statesText = (($ownedByPid | ForEach-Object { $_.Owner.States } | ForEach-Object { $_ }) | Sort-Object -Unique) -join ","
    $proc = Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue
    $name = if ($proc) { "$($proc.ProcessName).exe" } else { "UNKNOWN" }

    if (-not $proc) {
      Write-Host "[PRISMA] SKIP PID=$pidValue ya desaparecio antes de taskkill. PORTS=$portsText" -ForegroundColor DarkYellow
      continue
    }

    Write-Host "[PRISMA] Matando PID=$pidValue NAME=$name PORTS=$portsText STATES=$statesText" -ForegroundColor Yellow

    $taskkillOk = $false
    try {
      taskkill.exe /PID ([string]$pidValue) /T /F | Out-Host
      if ($LASTEXITCODE -eq 0) { $taskkillOk = $true }
    } catch {
      $taskkillOk = $false
    }

    if (-not $taskkillOk) {
      try {
        Stop-Process -Id ([int]$pidValue) -Force -ErrorAction Stop
        Write-Host "[PRISMA] Stop-Process OK PID=$pidValue" -ForegroundColor Green
      } catch {
        Write-Host "[PRISMA] WARN no pude matar PID=${pidValue}: $($_.Exception.Message)" -ForegroundColor Yellow
      }
    }
  }

  Start-Sleep -Milliseconds (450 * $round)
}

$remainingReal = @(Get-RealBlockingOwners -TargetPorts $Ports)

if ($remainingReal.Count -gt 0) {
  Write-Host "[PRISMA] ERROR: quedan listeners reales usando puertos objetivo:" -ForegroundColor Red
  foreach ($owner in $remainingReal) {
    Write-Host "  PID=$($owner.Pid) NAME=$($owner.Name) PORTS=$($owner.PortsText) STATES=$($owner.StatesText)" -ForegroundColor Red
  }
  throw "No se pudieron liberar todos los puertos PRISMA reales."
}

Write-Host "[PRISMA] Puertos liberados o solo quedan residuos/protegidos ignorables." -ForegroundColor Green
