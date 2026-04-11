<#
.SYNOPSIS
Installs an optional local git hook that runs runs-root doctor before commit/push.
#>

[CmdletBinding()]
param(
  [string]$StartDir = '',
  [string]$HookName = 'pre-commit',
  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($StartDir)) {
  $StartDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
}

$modulePath = Join-Path $PSScriptRoot '..\codex\tracking\Tracking.psm1'
$modulePath = (Resolve-Path -LiteralPath $modulePath).Path
Import-Module $modulePath -Force -DisableNameChecking

$repoRoot = Resolve-TrackingRepoRootForRunsRoot -StartDir $StartDir
$gitMarker = Join-Path $repoRoot '.git'

if (-not (Test-Path -LiteralPath $gitMarker)) {
  throw ('.git marker not found at: ' + $repoRoot)
}

$hooksDir = ''
if (Test-Path -LiteralPath $gitMarker -PathType Container) {
  $hooksDir = Join-Path $gitMarker 'hooks'
}
else {
  $line = Get-Content -LiteralPath $gitMarker -TotalCount 1 -ErrorAction Stop
  if ([string]::IsNullOrWhiteSpace($line) -or -not $line.StartsWith('gitdir:')) {
    throw ('Unsupported .git file format at: ' + $gitMarker)
  }

  $gitDirPath = $line.Substring(7).Trim()
  if (-not [System.IO.Path]::IsPathRooted($gitDirPath)) {
    $gitDirPath = Join-Path $repoRoot $gitDirPath
  }

  $hooksDir = Join-Path (Convert-TrackingCanonicalFsPath -Path $gitDirPath) 'hooks'
}

if (-not (Test-Path -LiteralPath $hooksDir -PathType Container)) {
  New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
}

$hookPath = Join-Path $hooksDir $HookName
if ((Test-Path -LiteralPath $hookPath) -and (-not $Force)) {
  throw ('Hook already exists. Re-run with -Force to overwrite: ' + $hookPath)
}

$doctorScript = Convert-TrackingCanonicalFsPath -Path (Join-Path $repoRoot 'tools/scripts/Invoke-HitechRunsDoctor.ps1')
$doctorScriptSh = $doctorScript.Replace('\\', '/')

$hookBody = @(
  '#!/bin/sh',
  ('pwsh -NoProfile -ExecutionPolicy Bypass -File "{0}" --dry-run --quiet' -f $doctorScriptSh),
  'rc=$?',
  'if [ "$rc" -ne 0 ]; then',
  '  echo "Runs-root doctor BLOCKED. See DRIFT_SCAN and REPAIR_REPORT for evidence."',
  'fi',
  'exit $rc'
) -join "`n"

[System.IO.File]::WriteAllText($hookPath, $hookBody + "`n", [System.Text.UTF8Encoding]::new($false))

Write-Host ('Hook installed: ' + $hookPath)
Write-Host ('Doctor script: ' + $doctorScript)
