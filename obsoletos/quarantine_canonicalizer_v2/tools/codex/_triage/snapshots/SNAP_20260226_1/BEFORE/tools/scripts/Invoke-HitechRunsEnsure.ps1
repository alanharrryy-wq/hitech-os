<#
.SYNOPSIS
Ensures the runs-root canonical shared-root+junction contract.
#>

[CmdletBinding()]
param(
  [string]$StartDir = '',
  [Alias('dry-run')][switch]$DryRun,
  [switch]$Write,
  [switch]$Force,
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

$writeMode = $false
if ($Write) {
  $writeMode = $true
}
elseif ($DryRun) {
  $writeMode = $false
}
else {
  $writeMode = $false
}

if ([string]::IsNullOrWhiteSpace($StartDir)) {
  $StartDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
}

$modulePath = Join-Path $PSScriptRoot '..\codex\tracking\Tracking.psm1'
$modulePath = (Resolve-Path -LiteralPath $modulePath).Path
Import-Module $modulePath -Force -DisableNameChecking

$result = Invoke-TrackingRunsEnsureCore -StartDir $StartDir -SharedRunsRoot $SharedRunsRoot -WorktreeRootOverride $WorktreeRootOverride -NoGit:$NoGit -Write:$writeMode -Force:$Force

if (-not $Quiet) {
  Write-Host ''
  Write-Host '=== HITECH RUNS ROOT ENSURE ===' -ForegroundColor Cyan
  Write-Host ('Mode: ' + $(if ($writeMode) { 'write' } else { 'dry-run' }))
  Write-Host ('SharedRunsRoot: ' + $result.drift_scan.shared_runs_root)
  Write-Host ('Compliant: ' + $result.drift_scan.compliant)
  Write-Host ('RC: ' + $result.rc)

  Write-Host ''
  Write-Host ('Migrated worktrees: ' + @($result.apply_summary.migrated_worktrees).Count)
  Write-Host ('Junctions created: ' + @($result.apply_summary.junctions_created).Count)
  Write-Host ('Files copied: ' + [int]$result.apply_summary.files_copied)
  Write-Host ('Files archived (force conflicts): ' + [int]$result.apply_summary.files_archived)

  Write-Host ''
  Write-Host ('DRIFT_SCAN.json: ' + $result.artifact_paths.drift_scan_json)
  Write-Host ('DRIFT_SCAN.md: ' + $result.artifact_paths.drift_scan_md)
  Write-Host ('REPAIR_REPORT.json: ' + $result.artifact_paths.repair_report_json)
  Write-Host ('REPAIR_REPORT.md: ' + $result.artifact_paths.repair_report_md)
}

exit ([int]$result.rc)
