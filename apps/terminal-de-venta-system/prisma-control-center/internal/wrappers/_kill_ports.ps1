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

function Get-PortOwners {
  param([int[]]$TargetPorts)

  $rows = @(netstat -ano -p tcp) + @(netstat -ano -p udp)
  $owners = @{}

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

    $portText = $null
    if ($local -match "\]:(\d+)$") {
      $portText = $Matches[1]
    } elseif ($local -match ":(\d+)$") {
      $portText = $Matches[1]
    }

    if (-not $portText) { continue }

    $port = [int]$portText
    if ($TargetPorts -notcontains $port) { continue }

    $targetPid = [int]$pidText

    if (-not $owners.ContainsKey($targetPid)) {
      $owners[$targetPid] = [ordered]@{
        Pid = $targetPid
        Ports = New-Object System.Collections.Generic.List[int]
        Lines = New-Object System.Collections.Generic.List[string]
      }
    }

    if (-not $owners[$targetPid].Ports.Contains($port)) {
      $owners[$targetPid].Ports.Add($port)
    }

    $owners[$targetPid].Lines.Add($trim)
  }

  return $owners.Values
}

Write-Host ""
Write-Host "[PRISMA] Revisando puertos: $($Ports -join ', ')" -ForegroundColor Cyan
Write-Host "[PRISMA] Motivo: $Reason" -ForegroundColor DarkCyan

$owners = @(Get-PortOwners -TargetPorts $Ports)

if ($owners.Count -eq 0) {
  Write-Host "[PRISMA] Puertos libres." -ForegroundColor Green
  return
}

foreach ($owner in $owners) {
  $targetPid = [int]$owner.Pid
  $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
  $name = if ($proc) { $proc.ProcessName + ".exe" } else { "UNKNOWN" }
  $portsText = ($owner.Ports | Sort-Object) -join ","

  if ($targetPid -eq 0 -or $targetPid -eq 4 -or $ProtectedNames -contains $name) {
    Write-Host "[PRISMA] SKIP protegido PID=$targetPid NAME=$name PORTS=$portsText" -ForegroundColor Yellow
    continue
  }

  if ($DryRun) {
    Write-Host "[PRISMA] DRY-RUN mataria PID=$targetPid NAME=$name PORTS=$portsText" -ForegroundColor Yellow
    continue
  }

  Write-Host "[PRISMA] Matando PID=$targetPid NAME=$name PORTS=$portsText" -ForegroundColor Yellow
  taskkill /PID $targetPid /T /F | Out-Host
}

Start-Sleep -Seconds 2

$remainingAll = @(Get-PortOwners -TargetPorts $Ports)
$remainingReal = @()
foreach ($owner in $remainingAll) {
  $ownerPid = [int]$owner.Pid
  $ownerProc = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
  $ownerName = if ($ownerProc) { $ownerProc.ProcessName + ".exe" } else { "UNKNOWN" }
  if ($ownerPid -eq 0 -or $ownerPid -eq 4 -or $ProtectedNames -contains $ownerName) {
    Write-Host "[PRISMA] SKIP restante protegido PID=$ownerPid NAME=$ownerName PORTS=$(($owner.Ports | Sort-Object) -join ',')" -ForegroundColor DarkYellow
    continue
  }
  $remainingReal += $owner
}

if ($remainingReal.Count -gt 0) {
  Write-Host "[PRISMA] ERROR: quedan procesos reales usando puertos objetivo:" -ForegroundColor Red
  foreach ($owner in $remainingReal) {
    Write-Host "  PID=$($owner.Pid) PORTS=$(($owner.Ports | Sort-Object) -join ',')" -ForegroundColor Red
  }
  throw "No se pudieron liberar todos los puertos PRISMA reales."
} else {
  Write-Host "[PRISMA] Puertos liberados o solo quedan puertos protegidos/sistema ignorables." -ForegroundColor Green
}
