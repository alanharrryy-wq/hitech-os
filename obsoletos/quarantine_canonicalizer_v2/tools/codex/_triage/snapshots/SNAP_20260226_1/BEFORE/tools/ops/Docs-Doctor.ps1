[CmdletBinding()]
param(
  [switch]$Check,
  [switch]$Write,
  [string]$RepoRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Check -and -not $Write) {
  $Check = $true
}

if ($Check -and $Write) {
  Write-Host 'RESULT: FAIL - choose one mode: --check or --write.' -ForegroundColor Red
  exit 1
}

$scriptRepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$repoRootResolved = if ([string]::IsNullOrWhiteSpace($RepoRoot)) { $scriptRepoRoot } else { (Resolve-Path -LiteralPath $RepoRoot).Path }
$pythonEntry = Join-Path $scriptRepoRoot 'tools/ops/docs_doctor.py'

if (-not (Test-Path -LiteralPath $pythonEntry -PathType Leaf)) {
  Write-Host ('RESULT: FAIL - missing python entrypoint: ' + $pythonEntry) -ForegroundColor Red
  exit 1
}

$python = (Get-Command python -ErrorAction SilentlyContinue)
if ($null -eq $python) {
  Write-Host 'RESULT: FAIL - python executable not found in PATH.' -ForegroundColor Red
  exit 1
}

$args = @($pythonEntry)
if ($Check) { $args += '--check' }
if ($Write) { $args += '--write' }
$args += @('--repo-root', $repoRootResolved)

Write-Progress -Activity 'Docs Doctor' -Status 'Step 1/2 - Running deterministic doctor core' -PercentComplete 35
$output = & $python.Source @args 2>&1
$rc = $LASTEXITCODE
Write-Progress -Activity 'Docs Doctor' -Status 'Step 2/2 - Finalizing' -PercentComplete 100 -Completed

foreach ($line in @($output)) {
  Write-Host ([string]$line)
}

if ($rc -eq 0) { exit 0 }
if ($rc -eq 2) { exit 2 }
exit 1
