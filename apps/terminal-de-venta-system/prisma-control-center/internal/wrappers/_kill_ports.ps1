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

$remaining = @(Get-PortOwners -TargetPorts $Ports)
if ($remaining.Count -gt 0) {
  Write-Host "[PRISMA] ADVERTENCIA: quedan procesos usando puertos objetivo:" -ForegroundColor Yellow
  foreach ($owner in $remaining) {
    Write-Host "  PID=$($owner.Pid) PORTS=$(($owner.Ports | Sort-Object) -join ',')" -ForegroundColor Yellow
  }
} else {
  Write-Host "[PRISMA] Puertos liberados." -ForegroundColor Green
}
