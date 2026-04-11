<#
.SYNOPSIS
Backward-compatible wrapper for ALL-IN-ONE current run report.

.DESCRIPTION
Delegates to the official tracking entrypoint in CurrentRun mode.
Maintains previous script path and behavior contract.
#>

[CmdletBinding()]
param(
  [string]$StartDir = '',
  [switch]$OpenRunFolder,
  [switch]$Strict,
  [switch]$JsonOnly,
  [switch]$MdOnly,
  [switch]$NoSidecarScan,
  [string[]]$RunsRootOverride,
  [switch]$DiscoverSiblingRoots,
  [switch]$DryRun,
  [switch]$VerboseMode,
  [switch]$Quiet,
  [switch]$HydrateMissingBundles,
  [string]$SharedRunsRoot,
  [string[]]$WorktreeRootOverride,
  [switch]$NoGitWorktreeDiscovery,
  [switch]$BypassRunsRootDoctor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($StartDir)) {
  $StartDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
}

$trackingEntrypoint = Join-Path $PSScriptRoot '..\codex\tracking\Invoke-HitechTracking.ps1'
$trackingEntrypoint = (Resolve-Path -LiteralPath $trackingEntrypoint).Path

$forward = [ordered]@{
  StartDir = $StartDir
  Mode = 'CurrentRun'
}

if ($OpenRunFolder) { $forward.OpenFolder = $true }
if ($Strict) { $forward.Strict = $true }
if ($JsonOnly) { $forward.JsonOnly = $true }
if ($MdOnly) { $forward.MdOnly = $true }
if ($NoSidecarScan) { $forward.NoSidecarScan = $true }
if ($DiscoverSiblingRoots) { $forward.DiscoverSiblingRoots = $true }
if ($DryRun) { $forward.DryRun = $true }
if ($VerboseMode) { $forward.VerboseMode = $true }
if ($Quiet) { $forward.Quiet = $true }
if ($HydrateMissingBundles) { $forward.HydrateMissingBundles = $true }
if (-not [string]::IsNullOrWhiteSpace($SharedRunsRoot)) { $forward.SharedRunsRoot = $SharedRunsRoot }
if (@($WorktreeRootOverride).Count -gt 0) { $forward.WorktreeRootOverride = @($WorktreeRootOverride) }
if ($NoGitWorktreeDiscovery) { $forward.NoGitWorktreeDiscovery = $true }
if ($BypassRunsRootDoctor) { $forward.BypassRunsRootDoctor = $true }
if (@($RunsRootOverride).Count -gt 0) { $forward.RunsRootOverride = @($RunsRootOverride) }

& $trackingEntrypoint @forward
$rc = $LASTEXITCODE
exit $rc
