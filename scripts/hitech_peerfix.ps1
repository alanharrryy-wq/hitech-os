#requires -Version 7.0
param(
  [Parameter(Mandatory=$false)]
  [string]$ProjectDir = (Get-Location).Path,

  [Parameter(Mandatory=$false)]
  [string]$FallbackRepo = "F:\repos\hitech-os",

  [Parameter(Mandatory=$false)]
  [string]$LogRoot = "F:\OneDrive\Hitech\3.Proyectos\CHAT GPT AI Estudio\HITECH_AISTUDIO_SYSTEM\00.Resplogs\LOGS",

  [Parameter(Mandatory=$false)]
  [switch]$NoBuild,

  [Parameter(Mandatory=$false)]
  [switch]$OpenLogs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

function Write-Stage {
  param([string]$Msg)
  Write-Host ("`n[HITECH] " + $Msg) -ForegroundColor Magenta
}

function Fail {
  param([string]$Msg)
  Write-Host ("`n[HITECH][FAIL] " + $Msg) -ForegroundColor Red
  throw $Msg
}

function Test-Command {
  param([string]$Name)
  try {
    Get-Command $Name -ErrorAction Stop | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Resolve-ExecutablePath {
  param([Parameter(Mandatory=$true)][string]$Name)

  $cmd = Get-Command $Name -ErrorAction Stop | Select-Object -First 1

  if ($cmd.CommandType -eq "Application") {
    return $cmd.Source
  }

  if ($cmd.CommandType -eq "ExternalScript" -and $cmd.Path -match "\.ps1$") {
    $cmdPath = [System.IO.Path]::ChangeExtension($cmd.Path, ".cmd")
    if (Test-Path $cmdPath) { return $cmdPath }

    $exePath = [System.IO.Path]::ChangeExtension($cmd.Path, ".exe")
    if (Test-Path $exePath) { return $exePath }
  }

  if ($cmd.Path) { return $cmd.Path }
  return $Name
}

function Invoke-Exe {
  param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [Parameter(Mandatory=$false)][string[]]$Arguments = @(),
    [Parameter(Mandatory=$false)][string]$WorkingDirectory = (Get-Location).Path
  )

  $resolvedFile = Resolve-ExecutablePath -Name $FilePath

  $psi = [System.Diagnostics.ProcessStartInfo]::new()
  $psi.FileName = $resolvedFile
  $psi.WorkingDirectory = $WorkingDirectory
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  foreach ($a in $Arguments) { [void]$psi.ArgumentList.Add($a) }

  Write-Host ("`n> " + $resolvedFile + " " + ($Arguments -join " ")) -ForegroundColor DarkGray
  $p = [System.Diagnostics.Process]::new()
  $p.StartInfo = $psi
  [void]$p.Start()
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()

  if ($stdout) { Write-Host $stdout }
  if ($stderr) { Write-Host $stderr -ForegroundColor DarkYellow }

  if ($p.ExitCode -ne 0) {
    Fail "Command failed (exit $($p.ExitCode)): $resolvedFile $($Arguments -join " ")"
  }
}

function Resolve-RepoRoot {
  param(
    [string]$StartDir,
    [string]$FallbackDir
  )

  $d = (Resolve-Path $StartDir).Path
  for ($i = 0; $i -lt 25; $i++) {
    $pkg = Join-Path $d "package.json"
    $ws = Join-Path $d "pnpm-workspace.yaml"
    $tj = Join-Path $d "turbo.json"
    if ((Test-Path $pkg) -and ((Test-Path $ws) -or (Test-Path $tj))) { return $d }
    $parent = Split-Path $d -Parent
    if (-not $parent -or $parent -eq $d) { break }
    $d = $parent
  }

  if ($FallbackDir -and (Test-Path (Join-Path $FallbackDir "package.json"))) {
    return $FallbackDir
  }

  return $null
}

function Backup-File {
  param([string]$Path, [string]$Suffix)
  if (-not (Test-Path $Path)) { return }

  $dir = Split-Path $Path -Parent
  $name = Split-Path $Path -Leaf
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $bakName = "$name.bak_$($Suffix)_$stamp"
  $bak = Join-Path $dir $bakName
  Copy-Item $Path $bak -Force
  Write-Stage "Backup: $bak"
}

function Ensure-Pnpm {
  Write-Progress -Activity "HITECH OS" -Status "Ensuring pnpm..." -PercentComplete 5
  if (Test-Command "pnpm") {
    Write-Stage "pnpm ok: $((pnpm -v) -join '')"
    return
  }

  Write-Stage "pnpm not found. Trying corepack..."
  if (Test-Command "corepack") {
    try {
      Invoke-Exe -FilePath "corepack" -Arguments @("enable")
      Invoke-Exe -FilePath "corepack" -Arguments @("prepare", "pnpm@latest", "--activate")
    } catch {}
  }

  if (-not (Test-Command "pnpm")) {
    if (-not (Test-Command "npm")) { Fail "No pnpm/npm found. Install Node.js, then rerun." }
    Write-Stage "Installing pnpm globally via npm..."
    Invoke-Exe -FilePath "npm" -Arguments @("i", "-g", "pnpm")
  }

  if (-not (Test-Command "pnpm")) { Fail "pnpm still not available." }
  Write-Stage "pnpm ready: $((pnpm -v) -join '')"
}

function Ensure-Turbo {
  param([string]$RepoRoot)

  Write-Progress -Activity "HITECH OS" -Status "Ensuring turbo devDependency..." -PercentComplete 25
  try {
    $out = & pnpm -C $RepoRoot ls turbo --depth 0 2>$null | Out-String
    if ($out -match "turbo\s+[0-9]+\.[0-9]+\.[0-9]+") {
      Write-Stage "turbo already installed"
      return
    }
  } catch {}

  Backup-File -Path (Join-Path $RepoRoot "package.json") -Suffix "turbo"
  Write-Stage "Adding turbo (devDependency) via pnpm..."
  Invoke-Exe -FilePath "pnpm" -Arguments @("add", "-D", "turbo") -WorkingDirectory $RepoRoot
}

function Patch-PeerWarningsByPolicy {
  param([string]$RepoRoot)

  Write-Progress -Activity "HITECH OS" -Status "Patching peerDependencyRules.allowedVersions..." -PercentComplete 40
  Backup-File -Path (Join-Path $RepoRoot "package.json") -Suffix "peers"

  $tsTarget = "5.8.2"
  $reactMajor = "19"
  $typesReactMajor = "19"

  try {
    $tsLine = & pnpm -C $RepoRoot ls typescript --depth 0 2>$null | Out-String
    if ($tsLine -match "typescript\s+([0-9]+\.[0-9]+\.[0-9]+)") { $tsTarget = $Matches[1] }
  } catch {}

  try {
    $rLine = & pnpm -C $RepoRoot ls react --depth 0 2>$null | Out-String
    if ($rLine -match "react\s+([0-9]+)\.([0-9]+)\.([0-9]+)") { $reactMajor = "$($Matches[1])" }
  } catch {}

  Invoke-Exe -FilePath "pnpm" -Arguments @("pkg", "set", ("pnpm.peerDependencyRules.allowedVersions.typescript=^$tsTarget")) -WorkingDirectory $RepoRoot
  Invoke-Exe -FilePath "pnpm" -Arguments @("pkg", "set", ("pnpm.peerDependencyRules.allowedVersions.react=^$reactMajor")) -WorkingDirectory $RepoRoot
  Invoke-Exe -FilePath "pnpm" -Arguments @("pkg", "set", ("pnpm.peerDependencyRules.allowedVersions.@types/react=^$typesReactMajor")) -WorkingDirectory $RepoRoot

  Write-Stage "allowedVersions set (typescript/react/@types-react)"
}

function Install-RootDeps {
  param([string]$RepoRoot)

  Write-Progress -Activity "HITECH OS" -Status "pnpm install (root)..." -PercentComplete 60
  $lock = Join-Path $RepoRoot "pnpm-lock.yaml"
  if (Test-Path $lock) {
    try {
      Invoke-Exe -FilePath "pnpm" -Arguments @("install", "--prefer-frozen-lockfile") -WorkingDirectory $RepoRoot
      return
    } catch {
      Write-Host "[HITECH] frozen-lockfile failed; fallback to pnpm install..." -ForegroundColor DarkYellow
    }
  }

  Invoke-Exe -FilePath "pnpm" -Arguments @("install") -WorkingDirectory $RepoRoot
}

function Run-TurboBuild {
  param([string]$RepoRoot)

  Write-Progress -Activity "HITECH OS" -Status "turbo build (Keystone if present)..." -PercentComplete 85
  $keystoneDir = Join-Path $RepoRoot "apps\keystone"
  $args = @("turbo", "run", "build")
  if (Test-Path $keystoneDir) {
    $keystonePkg = Join-Path $keystoneDir "package.json"
    $keystoneFilter = $null

    if (Test-Path $keystonePkg) {
      try {
        $pkgJson = Get-Content -Raw -Path $keystonePkg | ConvertFrom-Json
        if ($pkgJson.name) { $keystoneFilter = "$($pkgJson.name)" }
      } catch {}
    }

    if (-not $keystoneFilter) {
      $keystoneFilter = "./apps/keystone"
    }

    $args += @("--filter=$keystoneFilter")
    Write-Stage "Building Keystone only: $keystoneFilter"
  } else {
    Write-Stage "Keystone not found; running full build."
  }

  Invoke-Exe -FilePath "pnpm" -Arguments $args -WorkingDirectory $RepoRoot
}

# ---------------- MAIN ----------------
Write-Stage "HITECH OS peer warnings cleanup + turbo build"

$repoRoot = Resolve-RepoRoot -StartDir $ProjectDir -FallbackDir $FallbackRepo
if (-not $repoRoot) {
  Fail "Repo root not found. Expected a parent with package.json + pnpm-workspace.yaml/turbo.json."
}

if (-not (Test-Path $LogRoot)) { New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $LogRoot ("HITECH_OS_peerfix4_" + $ts)
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$transcript = Join-Path $logDir "TRANSCRIPT.txt"

Start-Transcript -Path $transcript -Force | Out-Null
try {
  Write-Stage "Repo root: $repoRoot"
  Set-Location $repoRoot

  Ensure-Pnpm
  Ensure-Turbo -RepoRoot $repoRoot
  Patch-PeerWarningsByPolicy -RepoRoot $repoRoot
  Install-RootDeps -RepoRoot $repoRoot
  if (-not $NoBuild) {
    Run-TurboBuild -RepoRoot $repoRoot
  } else {
    Write-Stage "NoBuild active: skipping turbo build."
  }

  Write-Progress -Activity "HITECH OS" -Status "Done." -PercentComplete 100
  Write-Stage "OK. Logs: $logDir"
} catch {
  Write-Progress -Activity "HITECH OS" -Status "Failed." -PercentComplete 100
  Write-Host "`n[HITECH][EXCEPTION] $($_.Exception.Message)" -ForegroundColor Red
  Write-Host "[HITECH] Logs: $logDir" -ForegroundColor Yellow
  throw
} finally {
  try { Stop-Transcript | Out-Null } catch {}
  if ($OpenLogs) {
    try { Start-Process -FilePath "explorer.exe" -ArgumentList $logDir | Out-Null } catch {}
  }
}
