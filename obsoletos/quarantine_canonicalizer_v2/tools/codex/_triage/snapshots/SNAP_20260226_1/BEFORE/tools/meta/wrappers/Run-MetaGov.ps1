[CmdletBinding()]
param(
  [string]$Registry = '',
  [string]$RepoRoot = '',
  [string]$RunId = '',
  [switch]$Open,
  [switch]$Strict,
  [switch]$NoRunDocsDoctor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
  param([string]$InputRoot)

  if (-not [string]::IsNullOrWhiteSpace($InputRoot)) {
    return (Resolve-Path -LiteralPath $InputRoot).Path
  }

  $out = & git rev-parse --show-toplevel 2>&1
  if ($LASTEXITCODE -eq 0) {
    $line = [string](@($out | ForEach-Object { [string]$_ }) | Select-Object -First 1)
    if (-not [string]::IsNullOrWhiteSpace($line)) {
      return (Resolve-Path -LiteralPath $line).Path
    }
  }

  return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
}

function Resolve-Python {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($null -eq $python) {
    throw 'python executable not found in PATH.'
  }
  return $python.Source
}

$root = Resolve-RepoRoot -InputRoot $RepoRoot
$pythonExe = Resolve-Python

$registryPath = if ([string]::IsNullOrWhiteSpace($Registry)) {
  Join-Path $root 'docs/meta-gov/REPO_REGISTRY.yaml'
} elseif ([System.IO.Path]::IsPathRooted($Registry)) {
  $Registry
} else {
  Join-Path $root $Registry
}

$scriptPath = Join-Path $root 'tools/meta/meta_orchestrator.py'
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
  throw ('Missing orchestrator script: ' + $scriptPath)
}

$moduleArgs = @(
  $scriptPath,
  '--registry', $registryPath,
  '--repo-root', $root,
  '--write'
)
if (-not [string]::IsNullOrWhiteSpace($RunId)) {
  $moduleArgs += @('--run-id', $RunId)
}
if ($Open) {
  $moduleArgs += '--open'
}
if ($Strict) {
  $moduleArgs += '--strict'
}
if ($NoRunDocsDoctor) {
  $moduleArgs += '--no-run-docs-doctor'
}

Write-Progress -Activity 'Meta-Gov Wrapper' -Status 'Launching orchestrator' -PercentComplete 25
Push-Location $root
try {
  Write-Progress -Activity 'Meta-Gov Wrapper' -Status 'Running python orchestrator' -PercentComplete 70
  $output = & $pythonExe @moduleArgs 2>&1
  $rc = $LASTEXITCODE
}
finally {
  Pop-Location
}
Write-Progress -Activity 'Meta-Gov Wrapper' -Status 'Completed' -PercentComplete 100 -Completed

foreach ($line in @($output)) {
  Write-Host ([string]$line)
}

if ($rc -eq 0) { exit 0 }
if ($rc -eq 2) { exit 2 }
exit 1
