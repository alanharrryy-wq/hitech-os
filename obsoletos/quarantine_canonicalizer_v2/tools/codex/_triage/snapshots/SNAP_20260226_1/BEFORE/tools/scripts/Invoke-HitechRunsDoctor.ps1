<#
.SYNOPSIS
Runs runs-root doctor checks for canonical shared runs root enforcement.
#>

[CmdletBinding()]
param(
  [string]$StartDir = '',
  [Alias('dry-run')][switch]$DryRun,
  [switch]$Write,
  [string]$SharedRunsRoot = '',
  [Alias('worktree-roots')][string[]]$WorktreeRootOverride,
  [Alias('no-git')][switch]$NoGit,
  [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($DryRun -and $Write) {
  throw 'Invalid options: use either --dry-run or --write, not both.'
}

if ([string]::IsNullOrWhiteSpace($StartDir)) {
  $StartDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
}

$modulePath = Join-Path $PSScriptRoot '..\codex\tracking\Tracking.psm1'
$modulePath = (Resolve-Path -LiteralPath $modulePath).Path
Import-Module $modulePath -Force -DisableNameChecking

$result = Invoke-TrackingRunsDoctorCore -StartDir $StartDir -SharedRunsRoot $SharedRunsRoot -WorktreeRootOverride $WorktreeRootOverride -NoGit:$NoGit

if (-not $Quiet) {
  Write-Host ''
  Write-Host '=== HITECH RUNS ROOT DOCTOR ===' -ForegroundColor Cyan
  Write-Host ('SharedRunsRoot: ' + $result.drift_scan.shared_runs_root)
  Write-Host ('Compliant: ' + $result.drift_scan.compliant)
  Write-Host ('RC: ' + $result.rc)
  Write-Host ''
  Write-Host 'Worktree Matrix:'
  foreach ($status in @($result.drift_scan.runs_root_status | Sort-Object -Property worktree)) {
    Write-Host ('- worktree={0}; type={1}; canonical={2}; runs={3}; target={4}' -f $status.worktree, $status.type, $status.is_canonical, $status.runs_path, $status.junction_target)
  }
  if (@($result.drift_scan.runs_root_status).Count -eq 0) {
    Write-Host '- none'
  }

  Write-Host ''
  Write-Host ('Canonical latest pointer: ' + $result.drift_scan.canonical_latest_path)
  Write-Host ('Observed latest markers: ' + @($result.drift_scan.latest_markers.observed_paths).Count)
  Write-Host ('Duplicate latest markers elsewhere: ' + @($result.drift_scan.latest_markers.duplicate_elsewhere).Count)

  Write-Host ''
  Write-Host ('DRIFT_SCAN.json: ' + $result.artifact_paths.drift_scan_json)
  Write-Host ('DRIFT_SCAN.md: ' + $result.artifact_paths.drift_scan_md)
  Write-Host ('REPAIR_REPORT.json: ' + $result.artifact_paths.repair_report_json)
  Write-Host ('REPAIR_REPORT.md: ' + $result.artifact_paths.repair_report_md)
}

exit ([int]$result.rc)
