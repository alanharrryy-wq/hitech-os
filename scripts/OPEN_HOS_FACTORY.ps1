[CmdletBinding()]
param(
  [string]$RunId,
  [switch]$Update,
  [string]$BaseBranch = "main",
  [string]$CodeCmd
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

function Resolve-HosRepoRoot {
  $fallback = "F:\repos\hitech-os"
  $scriptHint = Split-Path -Parent $PSScriptRoot

  if (Get-Command git -ErrorAction SilentlyContinue) {
    try {
      $viaScript = (& git -C $scriptHint rev-parse --show-toplevel 2>$null | Select-Object -First 1).Trim()
      if ($viaScript) {
        return $viaScript
      }
    } catch {
    }

    try {
      $viaCwd = (& git rev-parse --show-toplevel 2>$null | Select-Object -First 1).Trim()
      if ($viaCwd) {
        return $viaCwd
      }
    } catch {
    }
  }

  return $fallback
}

function Resolve-PythonInvocation {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    return @{
      Exe  = $python.Source
      Args = @("-m", "tools.hos.launcher.hos_factory_launcher")
    }
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return @{
      Exe  = $py.Source
      Args = @("-3", "-m", "tools.hos.launcher.hos_factory_launcher")
    }
  }

  throw "python is not available (neither 'python' nor 'py')."
}

$repoRoot = Resolve-HosRepoRoot
Write-Progress -Activity "HITECH-OS Factory Launcher" -Status "Resolving repository root" -PercentComplete 10

if (-not (Test-Path $repoRoot)) {
  throw "Resolved repo root does not exist: $repoRoot"
}

$pythonInvocation = Resolve-PythonInvocation
Write-Progress -Activity "HITECH-OS Factory Launcher" -Status "Configuring environment" -PercentComplete 25

if ($RunId) {
  $env:RUN_ID = $RunId
} else {
  Remove-Item Env:RUN_ID -ErrorAction SilentlyContinue
}

$env:HOS_LAUNCHER_BASE_BRANCH = $BaseBranch

if ($Update) {
  $env:HOS_LAUNCHER_UPDATE = "1"
} else {
  Remove-Item Env:HOS_LAUNCHER_UPDATE -ErrorAction SilentlyContinue
}

if ($CodeCmd) {
  $env:HOS_LAUNCHER_CODE_CMD = $CodeCmd
} else {
  Remove-Item Env:HOS_LAUNCHER_CODE_CMD -ErrorAction SilentlyContinue
}

$stdoutLines = @()
$launcherExitCode = 1

Push-Location $repoRoot
try {
  Write-Progress -Activity "HITECH-OS Factory Launcher" -Status "Running Python launcher" -PercentComplete 55

  & $pythonInvocation.Exe @($pythonInvocation.Args) 2>&1 | ForEach-Object {
    $line = $_.ToString()
    $stdoutLines += $line
    Write-Host $line
  }
  $launcherExitCode = $LASTEXITCODE
}
finally {
  Pop-Location
}

Write-Progress -Activity "HITECH-OS Factory Launcher" -Status "Parsing launcher summary" -PercentComplete 80

$summary = $null
for ($idx = $stdoutLines.Count - 1; $idx -ge 0; $idx--) {
  $candidate = $stdoutLines[$idx].Trim()
  if ($candidate.StartsWith("{") -and $candidate.EndsWith("}")) {
    try {
      $summary = $candidate | ConvertFrom-Json -ErrorAction Stop
      break
    } catch {
    }
  }
}

$resolvedRunId = $null
if ($summary -and $summary.run_id) {
  $resolvedRunId = [string]$summary.run_id
} elseif ($RunId) {
  $resolvedRunId = $RunId
}

if ($resolvedRunId) {
  $debugDir = Join-Path $repoRoot "tools/codex/runs/$resolvedRunId/_debug"
  if (Test-Path $debugDir) {
    Write-Progress -Activity "HITECH-OS Factory Launcher" -Status "Opening debug folder" -PercentComplete 95
    try {
      Start-Process explorer.exe $debugDir | Out-Null
    } catch {
      Write-Warning "Unable to open debug folder automatically: $debugDir"
    }
  }
}

Write-Progress -Activity "HITECH-OS Factory Launcher" -Completed
exit $launcherExitCode
