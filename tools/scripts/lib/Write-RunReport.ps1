<#
.SYNOPSIS
Write a deterministic single-file plaintext run report.

.DESCRIPTION
Generates a UTF-8 report with fixed section headers and content ordering:
1) TITLE + TIMESTAMP + REPO PATH
2) SUMMARY
3) CHANGED FILES
4) UNIFIED DIFF (NO COLOR)
5) FILE CONTENTS SNAPSHOT
6) VALIDATION OUTPUTS
7) WARN / DEBT
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$RepoPath,

  [Parameter(Mandatory = $true)]
  [string]$OutPath,

  [string]$Title = "RUN REPORT",

  [string[]]$ChangedFiles = @(),

  [string]$DiffText = "",

  [string]$FilesDumpDir = "",

  [string]$ValidationLog = "",

  [string]$DebtNotes = "",

  [string]$RunTimestamp = "",

  [int]$InlineLimitBytes = 12288
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

function Get-SnapshotPaths {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$FilesDumpDir,
    [Parameter(Mandatory = $true)]
    [string]$RelativePath
  )

  $normalizedRelative = $RelativePath -replace '/', [System.IO.Path]::DirectorySeparatorChar
  $snapshotPath = Join-Path $FilesDumpDir $normalizedRelative
  $deletedPath = "$snapshotPath.deleted.txt"

  return [pscustomobject]@{
    SnapshotPath = $snapshotPath
    DeletedPath = $deletedPath
  }
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
$safeDiffText = if ($null -eq $DiffText) { "" } else { [string]$DiffText }
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
[void]$lines.Add("DIFF_CHAR_COUNT: $($safeDiffText.Length)")
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

[void]$lines.Add("4) UNIFIED DIFF (NO COLOR)")
if ([string]::IsNullOrWhiteSpace($safeDiffText)) {
  [void]$lines.Add("(no diff)")
}
else {
  [void]$lines.Add($safeDiffText.TrimEnd("`r", "`n"))
}
[void]$lines.Add("")

[void]$lines.Add("5) FILE CONTENTS SNAPSHOT")
if ($normalizedChangedFiles.Count -eq 0) {
  [void]$lines.Add("(none)")
}
else {
  foreach ($relativePath in $normalizedChangedFiles) {
    [void]$lines.Add("FILE: $relativePath")

    $usedSnapshot = $false
    if (-not [string]::IsNullOrWhiteSpace($FilesDumpDir) -and (Test-Path -LiteralPath $FilesDumpDir -PathType Container)) {
      $paths = Get-SnapshotPaths -FilesDumpDir $FilesDumpDir -RelativePath $relativePath
      if (Test-Path -LiteralPath $paths.SnapshotPath -PathType Leaf) {
        $usedSnapshot = $true
        $fileInfo = Get-Item -LiteralPath $paths.SnapshotPath -Force
        if ($fileInfo.Length -le $InlineLimitBytes) {
          [void]$lines.Add("MODE: INLINE")
          [void]$lines.Add("SOURCE: $($paths.SnapshotPath)")
          [void]$lines.Add("----- BEGIN FILE $relativePath -----")
          $snapshotText = Get-Content -Raw -LiteralPath $paths.SnapshotPath
          if ([string]::IsNullOrEmpty($snapshotText)) {
            [void]$lines.Add("(empty file)")
          }
          else {
            [void]$lines.Add($snapshotText.TrimEnd("`r", "`n"))
          }
          [void]$lines.Add("----- END FILE $relativePath -----")
        }
        else {
          [void]$lines.Add("MODE: DUMP_REFERENCE")
          [void]$lines.Add("SNAPSHOT: $($paths.SnapshotPath)")
          [void]$lines.Add("NOTE: omitted inline content due to size > $InlineLimitBytes bytes.")
        }
      }
      elseif (Test-Path -LiteralPath $paths.DeletedPath -PathType Leaf) {
        $usedSnapshot = $true
        [void]$lines.Add("MODE: DUMP_REFERENCE")
        [void]$lines.Add("SNAPSHOT: $($paths.DeletedPath)")
        [void]$lines.Add("NOTE: file deleted or unavailable in working tree.")
      }
    }

    if (-not $usedSnapshot) {
      [void]$lines.Add("MODE: MISSING_SNAPSHOT")
      [void]$lines.Add("NOTE: no snapshot available for this path.")
    }

    [void]$lines.Add("")
  }
}

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
}
