[CmdletBinding()]
param(
  [switch]$DryRun,
  [switch]$OuterRetry
)

$ErrorActionPreference = "Stop"
if ($PSVersionTable.PSVersion.Major -ge 7) {
  $PSNativeCommandUseErrorActionPreference = $false
}

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
      Exe = $python.Source
      Args = @()
    }
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return @{
      Exe = $py.Source
      Args = @("-3")
    }
  }

  throw "python is not available (neither 'python' nor 'py')."
}

$repoRoot = Resolve-HosRepoRoot
if (-not (Test-Path $repoRoot)) {
  throw "Resolved repo root does not exist: $repoRoot"
}

$executorPath = Join-Path $repoRoot "tools/hos/launcher/one_button_executor.py"
if (-not (Test-Path $executorPath)) {
  throw "Executor script is missing: $executorPath"
}

$pythonInvocation = Resolve-PythonInvocation
$executorArgs = @($executorPath)
if ($DryRun) {
  $executorArgs += "--dry-run"
}
if ($OuterRetry) {
  $executorArgs += "--outer-retry"
}

$rc = 1
Push-Location $repoRoot
try {
  $previousNativePreference = $null
  $previousErrorPreference = $ErrorActionPreference
  try {
    if ($PSVersionTable.PSVersion.Major -ge 7) {
      $previousNativePreference = $PSNativeCommandUseErrorActionPreference
      $PSNativeCommandUseErrorActionPreference = $false
    }
    $ErrorActionPreference = "Continue"
    & $pythonInvocation.Exe @($pythonInvocation.Args + $executorArgs)
    $rc = $LASTEXITCODE
  }
  finally {
    $ErrorActionPreference = $previousErrorPreference
    if ($PSVersionTable.PSVersion.Major -ge 7 -and $null -ne $previousNativePreference) {
      $PSNativeCommandUseErrorActionPreference = $previousNativePreference
    }
  }
}
finally {
  Pop-Location
}

exit $rc
