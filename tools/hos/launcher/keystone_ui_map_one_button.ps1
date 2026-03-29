param(
  [Parameter(Mandatory = $false)]
  [string]$RepoPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
  param([string]$OverridePath)

  if ($OverridePath) {
    $resolved = (Resolve-Path -LiteralPath $OverridePath).Path
    $hasPackage = Test-Path -LiteralPath (Join-Path $resolved "package.json")
    $hasWorkspace = Test-Path -LiteralPath (Join-Path $resolved "pnpm-workspace.yaml")
    if (-not ($hasPackage -or $hasWorkspace)) {
      throw "-RepoPath '$resolved' is not a repo root. Expected package.json or pnpm-workspace.yaml."
    }
    return $resolved
  }

  $cursor = (Get-Location).Path
  while ($true) {
    $hasPackage = Test-Path -LiteralPath (Join-Path $cursor "package.json")
    $hasWorkspace = Test-Path -LiteralPath (Join-Path $cursor "pnpm-workspace.yaml")
    if ($hasPackage -or $hasWorkspace) {
      return $cursor
    }

    $parent = Split-Path -Parent $cursor
    if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $cursor) {
      throw "Unable to auto-detect repo root. Run from inside the repo or pass -RepoPath <absolute_path>."
    }
    $cursor = $parent
  }
}

function Resolve-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    return @("python")
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return @("py", "-3")
  }

  throw "Python not found. Install Python 3.11+ and ensure 'python' or 'py' is on PATH. Example fix: winget install Python.Python.3.12"
}

$repoRoot = Resolve-RepoRoot -OverridePath $RepoPath
$pythonCommand = @(Resolve-PythonCommand)

$runTag = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $repoRoot ("tools/ui_map/_logs/" + $runTag)
$docsDir = Join-Path $repoRoot "docs/ui-map"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$steps = @(
  @{ Name = "doctor"; Percent = 25 },
  @{ Name = "generate"; Percent = 50 },
  @{ Name = "validate"; Percent = 75 },
  @{ Name = "queries"; Percent = 100 }
)

$activity = "Keystone UI Map One-Button Runner"
$summaryLog = Join-Path $logDir "runner-summary.log"
"RUN_TAG=$runTag" | Set-Content -Encoding UTF8 $summaryLog
"REPO=$repoRoot" | Add-Content -Encoding UTF8 $summaryLog

for ($i = 0; $i -lt $steps.Count; $i++) {
  $step = $steps[$i]
  $name = $step.Name
  $percent = [int]$step.Percent

  Write-Progress -Activity $activity -Status ("Running " + $name) -PercentComplete $percent

  $stepLog = Join-Path $logDir ("{0:D2}_{1}.log" -f ($i + 1), $name)
  $cliArgs = @("-m", "tools.ui_map.cli", $name, "--repo", $repoRoot, "--out", "docs/ui-map", "--run-tag", $runTag)
  $allArgs = @()
  if ($pythonCommand.Count -gt 1) {
    $allArgs += $pythonCommand[1..($pythonCommand.Count - 1)]
  }
  $allArgs += $cliArgs

  "STEP=$name" | Add-Content -Encoding UTF8 $summaryLog
  "CMD=$($pythonCommand[0]) $($allArgs -join ' ')" | Add-Content -Encoding UTF8 $summaryLog

  & $pythonCommand[0] @allArgs 2>&1 | Tee-Object -FilePath $stepLog
  $exitCode = $LASTEXITCODE
  "EXIT_CODE=$exitCode" | Add-Content -Encoding UTF8 $stepLog
  "EXIT_CODE=$exitCode" | Add-Content -Encoding UTF8 $summaryLog

  if ($exitCode -ne 0) {
    Write-Progress -Activity $activity -Completed
    Write-Error ("Step '" + $name + "' failed with exit code " + $exitCode + ". Review log: " + $stepLog)
    exit $exitCode
  }
}

Write-Progress -Activity $activity -Completed
Start-Process explorer.exe $docsDir
Write-Host ("Completed successfully. Docs: " + $docsDir)
exit 0
