param(
  [string]$PreferredRepo = "F:\repos\hitech-os",
  [int]$PreferredPort = 3100,
  [string]$SceneIP = "127.0.0.2",
  [string]$WebIP = "127.0.0.3",
  [switch]$AdminOnly,
  [switch]$Background,
  [switch]$NoBrowser,
  [switch]$NoExplorer
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 3.0

function Test-IsAdmin {
  try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  } catch {
    return $false
  }
}

function Find-RepoRoot {
  param([string]$PreferredPath)

  if ($PreferredPath -and (Test-Path $PreferredPath)) {
    return (Resolve-Path -LiteralPath $PreferredPath).Path
  }

  if ($PSScriptRoot) {
    $fromScript = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
    if (
      (Test-Path (Join-Path $fromScript ".git")) -and
      (Test-Path (Join-Path $fromScript "apps\keystone\package.json"))
    ) {
      return $fromScript
    }
  }

  $cursor = (Get-Location).Path
  for ($i = 0; $i -lt 14; $i += 1) {
    if (
      (Test-Path (Join-Path $cursor ".git")) -and
      (Test-Path (Join-Path $cursor "apps\keystone\package.json"))
    ) {
      return $cursor
    }

    $parent = Split-Path $cursor -Parent
    if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $cursor) {
      break
    }

    $cursor = $parent
  }

  throw "No encontre el repo. Esperaba $PreferredPath o ejecutar dentro de hitech-os."
}

function Ensure-Dir {
  param([Parameter(Mandatory = $true)][string]$Path)

  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Get-LoopbackAlias {
  try {
    $alias =
      Get-NetIPInterface -AddressFamily IPv4 -ErrorAction SilentlyContinue |
      Where-Object { $_.InterfaceAlias -match "Loopback|Bucle" } |
      Select-Object -ExpandProperty InterfaceAlias -Unique |
      Select-Object -First 1

    if ($alias) {
      return $alias
    }
  } catch {
  }

  return "Loopback Pseudo-Interface 1"
}

function Set-HostsBlock {
  param([hashtable[]]$Entries)

  $hostsPath = Join-Path $env:WINDIR "System32\drivers\etc\hosts"
  $backupPath = "$hostsPath.hitech.bak"
  if (-not (Test-Path $backupPath)) {
    Copy-Item -LiteralPath $hostsPath -Destination $backupPath -Force
  }

  $begin = "# HITECH-LOOPBACK-BEGIN"
  $end = "# HITECH-LOOPBACK-END"
  $raw = Get-Content -Raw -LiteralPath $hostsPath

  $blockLines = [System.Collections.Generic.List[string]]::new()
  $null = $blockLines.Add($begin)
  $null = $blockLines.Add("# Managed by HITECH launcher - do not edit inside block")
  foreach ($entry in $Entries) {
    $null = $blockLines.Add(("{0}`t{1}" -f $entry.ip, $entry.host))
  }
  $null = $blockLines.Add($end)

  $block = ($blockLines -join "`r`n")
  $pattern = [regex]::Escape($begin) + ".*?" + [regex]::Escape($end)

  if ([regex]::IsMatch($raw, $pattern, [Text.RegularExpressions.RegexOptions]::Singleline)) {
    $newRaw = [regex]::Replace($raw, $pattern, $block, [Text.RegularExpressions.RegexOptions]::Singleline)
  } else {
    $newRaw = $raw.TrimEnd() + "`r`n`r`n" + $block + "`r`n"
  }

  Set-Content -LiteralPath $hostsPath -Value $newRaw -Encoding ASCII
}

function Ensure-LoopbackIPs_Admin {
  param(
    [string[]]$IPs,
    [hashtable[]]$HostsEntries
  )

  $alias = Get-LoopbackAlias
  foreach ($ip in $IPs) {
    $exists = $false
    try {
      $exists = @(
        Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -eq $ip }
      ).Count -gt 0
    } catch {
      $exists = $false
    }

    if (-not $exists) {
      & netsh interface ipv4 add address "$alias" $ip 255.0.0.0 | Out-Null
    }
  }

  Set-HostsBlock -Entries $HostsEntries
}

function Invoke-AdminHelper {
  param(
    [string[]]$IPs,
    [hashtable[]]$HostsEntries,
    [string]$RepoPath,
    [int]$Port,
    [string]$SceneAddress,
    [string]$WebAddress
  )

  if (Test-IsAdmin) {
    Ensure-LoopbackIPs_Admin -IPs $IPs -HostsEntries $HostsEntries
    return
  }

  $pwsh = Get-Command "pwsh" -ErrorAction SilentlyContinue
  if (-not $pwsh) {
    throw "pwsh no esta disponible para elevacion UAC."
  }

  if ([string]::IsNullOrWhiteSpace($PSCommandPath)) {
    throw "PSCommandPath no disponible; no puedo elevar el helper admin."
  }

  $argLine = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", ('"{0}"' -f $PSCommandPath),
    "-PreferredRepo", ('"{0}"' -f $RepoPath),
    "-PreferredPort", $Port,
    "-SceneIP", ('"{0}"' -f $SceneAddress),
    "-WebIP", ('"{0}"' -f $WebAddress),
    "-AdminOnly"
  ) -join " "

  Start-Process -FilePath $pwsh.Source -Verb RunAs -ArgumentList $argLine -Wait | Out-Null
}

function Get-ListenerPids {
  param([int]$Port)

  try {
    return @(
      Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty OwningProcess -Unique
    )
  } catch {
    return @()
  }
}

function Get-ProcCmdLine {
  param([int]$ProcessId)

  try {
    return (Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue).CommandLine
  } catch {
    return ""
  }
}

function Should-KillForPort {
  param(
    [int]$ProcessId,
    [string]$RepoRoot
  )

  $commandLine = Get-ProcCmdLine -ProcessId $ProcessId
  if ([string]::IsNullOrWhiteSpace($commandLine)) {
    return $false
  }

  $lc = $commandLine.ToLowerInvariant()
  if ($lc -match "node\.exe" -and ($lc -match "next" -or $lc -match "vite" -or $lc -match "pnpm")) {
    return $true
  }

  $escapedRepo = [regex]::Escape($RepoRoot.ToLowerInvariant())
  return ($lc -match $escapedRepo)
}

function Stop-PortConflicts {
  param(
    [int]$Port,
    [string]$RepoRoot
  )

  foreach ($processId in (Get-ListenerPids -Port $Port)) {
    if (Should-KillForPort -ProcessId $processId -RepoRoot $RepoRoot) {
      try {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
      } catch {
      }
    }
  }
}

function Is-BindPossible {
  param(
    [string]$IP,
    [int]$Port
  )

  $listeners = @()
  try {
    $listeners = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
  } catch {
    $listeners = @()
  }

  foreach ($listener in $listeners) {
    if ($listener.LocalAddress -eq $IP) {
      return $false
    }

    if ($listener.LocalAddress -eq "0.0.0.0" -or $listener.LocalAddress -eq "::") {
      return $false
    }
  }

  return $true
}

function Find-FreePort {
  param(
    [string[]]$IPs,
    [int]$Preferred,
    [int]$Start,
    [int]$End
  )

  $preferredConflicts = @($IPs | Where-Object { -not (Is-BindPossible -IP $_ -Port $Preferred) }).Count
  if ($preferredConflicts -eq 0) {
    return $Preferred
  }

  for ($port = $Start; $port -le $End; $port += 1) {
    $ok = $true
    foreach ($ip in $IPs) {
      if (-not (Is-BindPossible -IP $ip -Port $port)) {
        $ok = $false
        break
      }
    }

    if ($ok) {
      return $port
    }
  }

  throw "No encontre puerto libre en rango $Start-$End para IPs: $($IPs -join ', ')."
}

function Convert-ToEncodedCommand {
  param([string]$ScriptText)

  return [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($ScriptText))
}

function Start-WtTab {
  param(
    [string]$Title,
    [string]$Command
  )

  $encoded = Convert-ToEncodedCommand -ScriptText $Command
  $wt = Get-Command "wt.exe" -ErrorAction SilentlyContinue

  if ($wt) {
    Start-Process -FilePath $wt.Source -ArgumentList @(
      "new-tab", "--title", $Title,
      "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-EncodedCommand", $encoded
    ) | Out-Null
    return
  }

  $pwsh = Get-Command "pwsh" -ErrorAction SilentlyContinue
  if (-not $pwsh) {
    throw "No encontre wt.exe ni pwsh para abrir tabs de launcher."
  }

  Start-Process -FilePath $pwsh.Source -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-EncodedCommand", $encoded
  ) | Out-Null
}

function Start-BackgroundPowerShell {
  param([string]$Command)

  $pwsh = Get-Command "pwsh" -ErrorAction SilentlyContinue
  if (-not $pwsh) {
    throw "No encontre pwsh para ejecutar servicio en background."
  }

  $encoded = Convert-ToEncodedCommand -ScriptText $Command
  return Start-Process -FilePath $pwsh.Source -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded
  ) -WindowStyle Hidden -PassThru
}

$repo = Find-RepoRoot -PreferredPath $PreferredRepo
$ips = @($SceneIP, $WebIP)
$hostEntries = @(
  @{ ip = $SceneIP; host = "scene.local" },
  @{ ip = $WebIP; host = "web.local" }
)

if ($AdminOnly) {
  Ensure-LoopbackIPs_Admin -IPs $ips -HostsEntries $hostEntries
  return
}

Write-Progress -Activity "HITECH: Ports/Interfaces" -Status "Admin setup (loopback + hosts)" -PercentComplete 10
Invoke-AdminHelper -IPs $ips -HostsEntries $hostEntries -RepoPath $repo -Port $PreferredPort -SceneAddress $SceneIP -WebAddress $WebIP

Write-Progress -Activity "HITECH: Ports/Interfaces" -Status "Resolviendo conflictos de puerto" -PercentComplete 30
Stop-PortConflicts -Port $PreferredPort -RepoRoot $repo

Write-Progress -Activity "HITECH: Ports/Interfaces" -Status "Seleccionando puerto" -PercentComplete 45
$port = Find-FreePort -IPs $ips -Preferred $PreferredPort -Start 3110 -End 3199

Write-Progress -Activity "HITECH: Ports/Interfaces" -Status "Preparando logs" -PercentComplete 60
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $repo "tools\_local\ports\logs\$timestamp"
Ensure-Dir -Path $logDir

$sceneLog = Join-Path $logDir "scene-studio.log"
$webLog = Join-Path $logDir "web.log"

Write-Progress -Activity "HITECH: Ports/Interfaces" -Status "Lanzando servicios" -PercentComplete 80

$sceneCmd = @"
Set-Location -LiteralPath '$repo'
Write-Host 'Keystone Scene Studio => http://scene.local:$port/dev/scene-studio'
pnpm -C '$repo\apps\keystone' exec next dev -H $SceneIP -p $port 2>&1 | Tee-Object -FilePath '$sceneLog'
"@

$webCmd = @"
Set-Location -LiteralPath '$repo'
Write-Host 'Web (Vite) => http://web.local:$port'
pnpm -C '$repo\apps\web' dev -- --host $WebIP --port $port --strictPort 2>&1 | Tee-Object -FilePath '$webLog'
"@

if ($Background) {
  $sceneProc = Start-BackgroundPowerShell -Command $sceneCmd
  $webProc = Start-BackgroundPowerShell -Command $webCmd

  Start-Sleep -Seconds 2
  if ($sceneProc.HasExited) {
    throw "Scene Studio process exited immediately. Revisa: $sceneLog"
  }
  if ($webProc.HasExited) {
    throw "Web process exited immediately. Revisa: $webLog"
  }
} else {
  Start-WtTab -Title "HOS: Scene Studio (${SceneIP}:$port)" -Command $sceneCmd
  Start-WtTab -Title "HOS: Web (${WebIP}:$port)" -Command $webCmd
}

Write-Progress -Activity "HITECH: Ports/Interfaces" -Completed

Write-Host ""
Write-Host "LISTO:"
Write-Host "1) Scene Studio: http://scene.local:$port/dev/scene-studio"
Write-Host "2) Web:          http://web.local:$port"
Write-Host "Logs: $logDir"
Write-Host ""
if ($Background) {
  Write-Host "PIDs:"
  Write-Host ("- Scene Studio: {0}" -f $sceneProc.Id)
  Write-Host ("- Web:          {0}" -f $webProc.Id)
  Write-Host ""
}

if (-not $NoBrowser) {
  Start-Process "http://scene.local:$port/dev/scene-studio" | Out-Null
  Start-Process "http://web.local:$port" | Out-Null
}

if (-not $NoExplorer) {
  Start-Process "explorer.exe" $logDir | Out-Null
}
