<#
.SYNOPSIS
Write a deterministic single-file plaintext run report.

.DESCRIPTION
Generates a UTF-8 report with fixed section headers and content ordering:
1) TITLE + TIMESTAMP + REPO PATH
2) SUMMARY
3) CHANGED FILES
4) PATCH ARTIFACTS
5) LOG ARTIFACTS
6) VALIDATION OUTPUTS
7) WARN / DEBT

Raw unified diff content must not be embedded in this report.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$RepoPath,

  [Parameter(Mandatory = $true)]
  [string]$OutPath,

  [string]$Title = "RUN REPORT",

  [string[]]$ChangedFiles = @(),

  [string[]]$DiffPaths = @(),

  [string[]]$LogPaths = @(),

  [string]$FilesDumpDir = "",

  [string]$ValidationLog = "",

  [string]$DebtNotes = "",

  [string]$RunTimestamp = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ReportOutputPath {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$BasePath,
    [Parameter(Mandatory = $true)]
    [string]$RawOutPath
  )

  if ([System.IO.Path]::IsPathRooted($RawOutPath)) {
    return $RawOutPath
  }

  return (Join-Path $BasePath $RawOutPath)
}

function Normalize-PathList {
  [CmdletBinding()]
  param(
    [string]$RepoRoot,
    [string[]]$Paths
  )

  $normalized = New-Object System.Collections.Generic.List[string]
  foreach ($path in @($Paths)) {
    if ([string]::IsNullOrWhiteSpace($path)) {
      continue
    }
    $candidate = $path.Trim()
    if (-not [System.IO.Path]::IsPathRooted($candidate)) {
      $candidate = Join-Path $RepoRoot $candidate
    }
    $normalized.Add($candidate)
  }
  return @($normalized | Sort-Object -Unique)
}

if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
  throw "Write-RunReport: RepoPath does not exist: $RepoPath"
}

$resolvedRepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
$resolvedOutPath = Resolve-ReportOutputPath -BasePath $resolvedRepoPath -RawOutPath $OutPath
$resolvedOutDir = Split-Path -Parent $resolvedOutPath
if (-not [string]::IsNullOrWhiteSpace($resolvedOutDir)) {
  New-Item -ItemType Directory -Path $resolvedOutDir -Force -WhatIf:$false -Confirm:$false | Out-Null
}

$timestamp = if ([string]::IsNullOrWhiteSpace($RunTimestamp)) { Get-Date -Format "yyyyMMdd_HHmmss" } else { $RunTimestamp }
$normalizedChangedFiles = @($ChangedFiles | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
$normalizedDiffPaths = @(Normalize-PathList -RepoRoot $resolvedRepoPath -Paths $DiffPaths)
$normalizedLogPaths = @(Normalize-PathList -RepoRoot $resolvedRepoPath -Paths $LogPaths)
$safeValidationLog = if ($null -eq $ValidationLog) { "" } else { [string]$ValidationLog }
$safeDebtNotes = if ($null -eq $DebtNotes) { "" } else { [string]$DebtNotes }

$lines = New-Object System.Collections.Generic.List[string]
$nl = "`n"

[void]$lines.Add("1) TITLE + TIMESTAMP + REPO PATH")
[void]$lines.Add("TITLE: $Title")
[void]$lines.Add("TIMESTAMP: $timestamp")
[void]$lines.Add("REPO PATH: $resolvedRepoPath")
[void]$lines.Add("")

[void]$lines.Add("2) SUMMARY")
[void]$lines.Add("CHANGED_FILES_COUNT: $($normalizedChangedFiles.Count)")
[void]$lines.Add("PATCH_ARTIFACT_COUNT: $($normalizedDiffPaths.Count)")
[void]$lines.Add("LOG_ARTIFACT_COUNT: $($normalizedLogPaths.Count)")
[void]$lines.Add("FILES_DUMP_DIR: $(if ([string]::IsNullOrWhiteSpace($FilesDumpDir)) { '<none>' } else { $FilesDumpDir })")
[void]$lines.Add("")

[void]$lines.Add("3) CHANGED FILES")
if ($normalizedChangedFiles.Count -eq 0) {
  [void]$lines.Add("(none)")
}
else {
  foreach ($path in $normalizedChangedFiles) {
    [void]$lines.Add("- $path")
  }
}
[void]$lines.Add("")

[void]$lines.Add("4) PATCH ARTIFACTS")
if ($normalizedDiffPaths.Count -eq 0) {
  [void]$lines.Add("(none)")
}
else {
  foreach ($diffPath in $normalizedDiffPaths) {
    if (Test-Path -LiteralPath $diffPath -PathType Leaf) {
      $len = (Get-Item -LiteralPath $diffPath -Force).Length
      [void]$lines.Add("- $diffPath (bytes=$len)")
    }
    else {
      [void]$lines.Add("- $diffPath (missing)")
    }
  }
}
[void]$lines.Add("")

[void]$lines.Add("5) LOG ARTIFACTS")
if ($normalizedLogPaths.Count -eq 0) {
  [void]$lines.Add("(none)")
}
else {
  foreach ($logPath in $normalizedLogPaths) {
    if (Test-Path -LiteralPath $logPath -PathType Leaf) {
      $len = (Get-Item -LiteralPath $logPath -Force).Length
      [void]$lines.Add("- $logPath (bytes=$len)")
    }
    else {
      [void]$lines.Add("- $logPath (missing)")
    }
  }
}
[void]$lines.Add("")

[void]$lines.Add("6) VALIDATION OUTPUTS")
if ([string]::IsNullOrWhiteSpace($safeValidationLog)) {
  [void]$lines.Add("(none)")
}
else {
  [void]$lines.Add($safeValidationLog.TrimEnd("`r", "`n"))
}
[void]$lines.Add("")

[void]$lines.Add("7) WARN / DEBT")
if ([string]::IsNullOrWhiteSpace($safeDebtNotes)) {
  [void]$lines.Add("(none)")
}
else {
  [void]$lines.Add($safeDebtNotes.TrimEnd("`r", "`n"))
}
[void]$lines.Add("")

$reportText = [string]::Join($nl, $lines.ToArray()) + $nl
[System.IO.File]::WriteAllText($resolvedOutPath, $reportText, [System.Text.UTF8Encoding]::new($false))

return [pscustomobject]@{
  Ok = $true
  OutPath = $resolvedOutPath
  Timestamp = $timestamp
  ChangedFilesCount = $normalizedChangedFiles.Count
  PatchArtifactCount = $normalizedDiffPaths.Count
  LogArtifactCount = $normalizedLogPaths.Count
}
