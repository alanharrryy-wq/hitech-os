<#
.SYNOPSIS
Create a single deterministic plaintext diff/report bundle for a run.

.DESCRIPTION
Creates a run bundle under .tmp/run-reports/<yyyyMMdd_HHmmss>/ with:
- CHANGED_FILES.txt
- DIFF_VS_HEAD.patch
- DIFF_UNSTAGED.patch
- DIFF_STAGED.patch
- FILES/ snapshot (optional)
- FINAL_REPORT.txt

The report is generated through Write-RunReport.ps1.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$RepoPath,

  [string]$Title = "FINAL RUN REPORT",

  [bool]$IncludeFilesDump = $true,

  [bool]$AlsoPrintShortSummary = $true,

  [string]$ValidationLog = "",

  [string]$DebtNotes = "",

  [bool]$OpenArtifacts = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$invokeExternalPath = Join-Path $PSScriptRoot "Invoke-External.ps1"
$invokeExternalPath = (Resolve-Path -LiteralPath $invokeExternalPath).Path
. $invokeExternalPath

$writeRunReportPath = Join-Path $PSScriptRoot "Write-RunReport.ps1"
$writeRunReportPath = (Resolve-Path -LiteralPath $writeRunReportPath).Path

function Parse-GitStatusPath {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$StatusLine
  )

  if ([string]::IsNullOrWhiteSpace($StatusLine) -or $StatusLine.Length -lt 4) {
    return $null
  }

  $code = $StatusLine.Substring(0, 2)
  $pathPart = $StatusLine.Substring(3).Trim()
  if ([string]::IsNullOrWhiteSpace($pathPart)) {
    return $null
  }

  if ($pathPart.Contains(" -> ")) {
    $pathPart = ($pathPart -split " -> ")[-1].Trim()
  }

  $normalized = $pathPart -replace "\\", "/"
  return [pscustomobject]@{
    Code = $code
    Path = $normalized
    Raw = $StatusLine
  }
}

function Contains-AnsiSequence {
  [CmdletBinding()]
  param(
    [string]$Text
  )

  if ([string]::IsNullOrEmpty($Text)) {
    return $false
  }

  $esc = [char]27
  $pattern = [regex]::Escape("$esc") + "\[[0-9;]*[A-Za-z]"
  return [regex]::IsMatch($Text, $pattern)
}

function Ensure-Directory {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  New-Item -ItemType Directory -Path $Path -Force -WhatIf:$false -Confirm:$false | Out-Null
}

if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
  throw "Make-DiffBundle: RepoPath does not exist: $RepoPath"
}

$repoRoot = (Resolve-Path -LiteralPath $RepoPath).Path
$runTs = Get-Date -Format "yyyyMMdd_HHmmss"
$runDir = Join-Path $repoRoot ".tmp/run-reports/$runTs"
$filesDir = Join-Path $runDir "FILES"
$changedFilesTxtPath = Join-Path $runDir "CHANGED_FILES.txt"
$diffVsHeadPath = Join-Path $runDir "DIFF_VS_HEAD.patch"
$diffUnstagedPath = Join-Path $runDir "DIFF_UNSTAGED.patch"
$diffStagedPath = Join-Path $runDir "DIFF_STAGED.patch"
$finalReportPath = Join-Path $runDir "FINAL_REPORT.txt"

Ensure-Directory -Path $runDir
if ($IncludeFilesDump) {
  Ensure-Directory -Path $filesDir
}

$validationLines = New-Object System.Collections.Generic.List[string]
$debtLines = New-Object System.Collections.Generic.List[string]

function Add-ValidationLine {
  param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("PASS", "WARN", "FAIL")]
    [string]$Status,
    [Parameter(Mandatory = $true)]
    [string]$Message
  )
  [void]$validationLines.Add("[$Status] $Message")
}

function Add-DebtLine {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message
  )
  [void]$debtLines.Add($Message)
}

$gitVersion = Invoke-ExternalCommand -ExePath "git" -ArgList @("--version") -WorkDir $repoRoot -NoThrow
if (-not $gitVersion.Ok) {
  Add-ValidationLine -Status "FAIL" -Message "git --version :: $($gitVersion.Output)"
  throw "Make-DiffBundle: git unavailable. $($gitVersion.Output)"
}
Add-ValidationLine -Status "PASS" -Message "git --version :: $($gitVersion.Stdout.Trim())"

$statusResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("status", "--porcelain", "--untracked-files=all") -WorkDir $repoRoot -NoThrow
if (-not $statusResult.Ok) {
  Add-ValidationLine -Status "FAIL" -Message "git status --porcelain --untracked-files=all :: $($statusResult.Output)"
  throw "Make-DiffBundle: git status failed. $($statusResult.Output)"
}
Add-ValidationLine -Status "PASS" -Message "git status --porcelain --untracked-files=all"

$statusEntries = New-Object System.Collections.Generic.List[object]
if (-not [string]::IsNullOrWhiteSpace($statusResult.Stdout)) {
  $statusLines = $statusResult.Stdout -split "`r?`n"
  foreach ($line in $statusLines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
      continue
    }

    $entry = Parse-GitStatusPath -StatusLine $line
    if ($null -eq $entry) {
      continue
    }

    $tokens = @($entry.Code.ToCharArray())
    $allowed = @('?', 'M', 'A', 'D', 'R')
    if (($allowed -contains $tokens[0]) -or ($allowed -contains $tokens[1])) {
      [void]$statusEntries.Add($entry)
    }
  }
}

$statusOutputLines = if ($statusEntries.Count -eq 0) {
  @("(none)")
}
else {
  @($statusEntries | Sort-Object Path, Code | ForEach-Object { "$($_.Code)`t$($_.Path)" })
}
[System.IO.File]::WriteAllText($changedFilesTxtPath, ([string]::Join("`n", $statusOutputLines) + "`n"), [System.Text.UTF8Encoding]::new($false))
Add-ValidationLine -Status "PASS" -Message "wrote CHANGED_FILES.txt"

$changedFilePaths = @($statusEntries | Select-Object -ExpandProperty Path -Unique | Sort-Object)

$diffVsHeadResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--no-color", "--patch", "HEAD", "--") -WorkDir $repoRoot -NoThrow
if (-not $diffVsHeadResult.Ok) {
  Add-ValidationLine -Status "FAIL" -Message "git diff --no-color --patch HEAD -- :: $($diffVsHeadResult.Output)"
  throw "Make-DiffBundle: failed DIFF_VS_HEAD. $($diffVsHeadResult.Output)"
}
[System.IO.File]::WriteAllText($diffVsHeadPath, $diffVsHeadResult.Stdout, [System.Text.UTF8Encoding]::new($false))
Add-ValidationLine -Status "PASS" -Message "wrote DIFF_VS_HEAD.patch"

$diffUnstagedResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--no-color", "--patch", "--") -WorkDir $repoRoot -NoThrow
if (-not $diffUnstagedResult.Ok) {
  Add-ValidationLine -Status "FAIL" -Message "git diff --no-color --patch -- :: $($diffUnstagedResult.Output)"
  throw "Make-DiffBundle: failed DIFF_UNSTAGED. $($diffUnstagedResult.Output)"
}
[System.IO.File]::WriteAllText($diffUnstagedPath, $diffUnstagedResult.Stdout, [System.Text.UTF8Encoding]::new($false))
Add-ValidationLine -Status "PASS" -Message "wrote DIFF_UNSTAGED.patch"

$diffStagedResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--no-color", "--patch", "--cached", "--") -WorkDir $repoRoot -NoThrow
if (-not $diffStagedResult.Ok) {
  Add-ValidationLine -Status "FAIL" -Message "git diff --no-color --patch --cached -- :: $($diffStagedResult.Output)"
  throw "Make-DiffBundle: failed DIFF_STAGED. $($diffStagedResult.Output)"
}
[System.IO.File]::WriteAllText($diffStagedPath, $diffStagedResult.Stdout, [System.Text.UTF8Encoding]::new($false))
Add-ValidationLine -Status "PASS" -Message "wrote DIFF_STAGED.patch"

if (Contains-AnsiSequence -Text $diffVsHeadResult.Stdout) {
  Add-ValidationLine -Status "FAIL" -Message "DIFF_VS_HEAD.patch contains ANSI sequences"
  Add-DebtLine "DEBT_REQUIRED: remove ANSI sequences from DIFF_VS_HEAD.patch generation."
}
else {
  Add-ValidationLine -Status "PASS" -Message "DIFF_VS_HEAD.patch has no ANSI sequences"
}

if (Contains-AnsiSequence -Text $diffUnstagedResult.Stdout) {
  Add-ValidationLine -Status "FAIL" -Message "DIFF_UNSTAGED.patch contains ANSI sequences"
  Add-DebtLine "DEBT_REQUIRED: remove ANSI sequences from DIFF_UNSTAGED.patch generation."
}
else {
  Add-ValidationLine -Status "PASS" -Message "DIFF_UNSTAGED.patch has no ANSI sequences"
}

if (Contains-AnsiSequence -Text $diffStagedResult.Stdout) {
  Add-ValidationLine -Status "FAIL" -Message "DIFF_STAGED.patch contains ANSI sequences"
  Add-DebtLine "DEBT_REQUIRED: remove ANSI sequences from DIFF_STAGED.patch generation."
}
else {
  Add-ValidationLine -Status "PASS" -Message "DIFF_STAGED.patch has no ANSI sequences"
}

if ($IncludeFilesDump) {
  foreach ($relativePath in $changedFilePaths) {
    $sourcePath = Join-Path $repoRoot ($relativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)
    $destPath = Join-Path $filesDir ($relativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)
    $destDir = Split-Path -Parent $destPath
    if (-not [string]::IsNullOrWhiteSpace($destDir)) {
      Ensure-Directory -Path $destDir
    }

    if (Test-Path -LiteralPath $sourcePath -PathType Container) {
      $markerPath = "$destPath.skipped_dir.txt"
      [System.IO.File]::WriteAllText($markerPath, "SKIPPED_DIRECTORY`t$relativePath`n", [System.Text.UTF8Encoding]::new($false))
      Add-ValidationLine -Status "WARN" -Message "skipped directory in snapshot: $relativePath"
      Add-DebtLine "DEBT_REQUIRED: inspect skipped directory path in FILES snapshot: $relativePath"
      continue
    }

    if (Test-Path -LiteralPath $sourcePath -PathType Leaf) {
      Copy-Item -LiteralPath $sourcePath -Destination $destPath -Force
      Add-ValidationLine -Status "PASS" -Message "snapshotted file: $relativePath"
    }
    else {
      $deletedPath = "$destPath.deleted.txt"
      [System.IO.File]::WriteAllText($deletedPath, "DELETED_OR_MISSING`t$relativePath`n", [System.Text.UTF8Encoding]::new($false))
      Add-ValidationLine -Status "PASS" -Message "recorded deleted/missing path: $relativePath"
    }
  }
}
else {
  Add-ValidationLine -Status "WARN" -Message "FILES dump disabled by IncludeFilesDump=false"
  Add-DebtLine "DEBT_REQUIRED: FILES dump was disabled for this run."
}

if (-not [string]::IsNullOrWhiteSpace($ValidationLog)) {
  Add-ValidationLine -Status "PASS" -Message "ingested external validation log"
}

if (-not [string]::IsNullOrWhiteSpace($DebtNotes)) {
  Add-DebtLine $DebtNotes.Trim()
}

$combinedValidation = [string]::Join("`n", @($validationLines))
if (-not [string]::IsNullOrWhiteSpace($ValidationLog)) {
  $combinedValidation = $combinedValidation + "`n`nEXTERNAL_VALIDATION_LOG`n" + $ValidationLog.Trim()
}

$combinedDebt = if ($debtLines.Count -eq 0) { "" } else { [string]::Join("`n", @($debtLines)) }

$reportWrite = & $writeRunReportPath `
  -RepoPath $repoRoot `
  -OutPath $finalReportPath `
  -Title $Title `
  -ChangedFiles $changedFilePaths `
  -DiffText $diffVsHeadResult.Stdout `
  -FilesDumpDir $(if ($IncludeFilesDump) { $filesDir } else { "" }) `
  -ValidationLog $combinedValidation `
  -DebtNotes $combinedDebt `
  -RunTimestamp $runTs

if ($OpenArtifacts) {
  try {
    Start-Process -FilePath "explorer.exe" -ArgumentList $runDir -WhatIf:$false -Confirm:$false | Out-Null
    Add-ValidationLine -Status "PASS" -Message "auto-opened run folder in explorer.exe"
  }
  catch {
    Add-ValidationLine -Status "WARN" -Message "could not auto-open run folder: $runDir"
    Add-DebtLine "DEBT_REQUIRED: manually open run folder $runDir"
  }

  try {
    Invoke-Item -LiteralPath $finalReportPath -ErrorAction Stop
    Add-ValidationLine -Status "PASS" -Message "auto-opened FINAL_REPORT.txt"
  }
  catch {
    Add-ValidationLine -Status "WARN" -Message "could not auto-open FINAL_REPORT.txt: $finalReportPath"
    Add-DebtLine "DEBT_REQUIRED: manually open FINAL_REPORT.txt at $finalReportPath"
  }

  $combinedValidation = [string]::Join("`n", @($validationLines))
  if (-not [string]::IsNullOrWhiteSpace($ValidationLog)) {
    $combinedValidation = $combinedValidation + "`n`nEXTERNAL_VALIDATION_LOG`n" + $ValidationLog.Trim()
  }
  $combinedDebt = if ($debtLines.Count -eq 0) { "" } else { [string]::Join("`n", @($debtLines)) }

  [void](& $writeRunReportPath `
      -RepoPath $repoRoot `
      -OutPath $finalReportPath `
      -Title $Title `
      -ChangedFiles $changedFilePaths `
      -DiffText $diffVsHeadResult.Stdout `
      -FilesDumpDir $(if ($IncludeFilesDump) { $filesDir } else { "" }) `
      -ValidationLog $combinedValidation `
      -DebtNotes $combinedDebt `
      -RunTimestamp $runTs)
}

if ($AlsoPrintShortSummary) {
  Write-Host "FINAL_REPORT: $finalReportPath"
  Write-Host "RUN_DIR: $runDir"
  Write-Host "CHANGED_FILES: $($changedFilePaths.Count)"
}

return [pscustomobject]@{
  Ok = $true
  RepoPath = $repoRoot
  RunTimestamp = $runTs
  RunDir = $runDir
  FinalReportPath = $finalReportPath
  ChangedFiles = $changedFilePaths
  ChangedFilesCount = $changedFilePaths.Count
  ReportWrite = $reportWrite
}
