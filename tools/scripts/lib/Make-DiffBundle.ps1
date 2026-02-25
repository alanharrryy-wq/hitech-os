<#
.SYNOPSIS
Create a deterministic disk-only run bundle with FINAL_REPORT.txt as the authoritative artifact.

.DESCRIPTION
Creates a run bundle under `tools/codex/Z_aggregator/RUN_<yyyyMMdd_HHmmss>/` (or a caller-provided run dir) with:
- CHANGED_FILES.txt
- logs/*.log
- FILES/ snapshot (optional)
- FINAL_REPORT.txt

Unified diff content is captured via `git diff --no-color --patch` and written only inside FINAL_REPORT.txt.
Diff bodies are never printed to console.
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

  [bool]$OpenArtifacts = $false,

  [string]$RunDir = "",

  [string]$DiffBaseRef = "HEAD",

  [string]$ReportStatus = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$invokeExternalPath = Join-Path $PSScriptRoot "Invoke-External.ps1"
$invokeExternalPath = (Resolve-Path -LiteralPath $invokeExternalPath).Path
. $invokeExternalPath

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

  return [pscustomobject]@{
    Code = $code
    Path = ($pathPart -replace "\\", "/")
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

function Write-TextFile {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [AllowNull()]
    [string]$Text
  )

  $safeText = if ($null -eq $Text) { "" } else { $Text }
  [System.IO.File]::WriteAllText($Path, $safeText, [System.Text.UTF8Encoding]::new($false))
}

function Resolve-RunDir {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$Timestamp,
    [string]$InputPath
  )

  if ([string]::IsNullOrWhiteSpace($InputPath)) {
    return (Join-Path $RepoRoot "tools/codex/Z_aggregator/RUN_$Timestamp")
  }

  if ([System.IO.Path]::IsPathRooted($InputPath)) {
    return $InputPath
  }

  return (Join-Path $RepoRoot $InputPath)
}

function Write-CommandFailureLog {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$LogsDir,
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [Parameter(Mandatory = $true)]
    [string]$CommandLine,
    [string]$Output
  )

  Ensure-Directory -Path $LogsDir
  $logPath = Join-Path $LogsDir "$Name.log"
  $safeOutput = if ([string]::IsNullOrWhiteSpace($Output)) { "<none>" } else { $Output.TrimEnd("`r", "`n") }
  $text = @(
    "COMMAND: $CommandLine"
    "OUTPUT:"
    $safeOutput
    ""
  ) -join "`n"
  Write-TextFile -Path $logPath -Text $text
  return $logPath
}

function Get-ReportStatus {
  [CmdletBinding()]
  param(
    [string[]]$ValidationEntries
  )

  $items = @($ValidationEntries)
  if ($items | Where-Object { $_ -match '^\[FAIL\]' }) {
    return "FAIL"
  }
  if ($items | Where-Object { $_ -match '^\[WARN\]' }) {
    return "WARN"
  }

  return "SUCCESS"
}

function Build-FinalReportText {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$RunId,
    [Parameter(Mandatory = $true)]
    [string]$Status,
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$RunDirPath,
    [Parameter(Mandatory = $true)]
    [string]$RunTimestamp,
    [Parameter(Mandatory = $true)]
    [string]$DiffBase,
    [string[]]$ChangedFiles,
    [string[]]$ValidationEntries,
    [string]$ExternalValidation,
    [string[]]$DebtEntries,
    [string]$InlineDebtNotes,
    [string]$FilesDumpDirectory,
    [string[]]$LogPaths,
    [string]$UnifiedDiffText
  )

  $normalizedChangedFiles = @($ChangedFiles | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
  $normalizedValidationEntries = @($ValidationEntries | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  $normalizedDebtEntries = @($DebtEntries | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  $normalizedLogPaths = @($LogPaths | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)

  $externalValidationLines = @()
  if (-not [string]::IsNullOrWhiteSpace($ExternalValidation)) {
    $externalValidationLines = @($ExternalValidation.TrimEnd("`r", "`n") -split "`r?`n")
  }

  $inlineDebtLines = @()
  if (-not [string]::IsNullOrWhiteSpace($InlineDebtNotes)) {
    $inlineDebtLines = @($InlineDebtNotes.TrimEnd("`r", "`n") -split "`r?`n")
  }

  $normalizedDiffText = if ($null -eq $UnifiedDiffText) { "" } else { [string]$UnifiedDiffText }
  $normalizedDiffText = $normalizedDiffText -replace "`r`n", "`n"
  $normalizedDiffText = $normalizedDiffText -replace "`r", "`n"
  $diffLines = @()
  if ([string]::IsNullOrWhiteSpace($normalizedDiffText)) {
    $diffLines = @("NO_CHANGES_DETECTED")
  }
  else {
    $diffLines = @($normalizedDiffText.TrimEnd("`n") -split "`n")
  }

  $lines = New-Object System.Collections.Generic.List[string]
  [void]$lines.Add("=== HITECH OS FINAL REPORT ===")
  [void]$lines.Add("")
  [void]$lines.Add("RUN_ID: $RunId")
  [void]$lines.Add("STATUS: $Status")
  [void]$lines.Add("")

  [void]$lines.Add("--- SUMMARY ---")
  [void]$lines.Add("TITLE: $Title")
  [void]$lines.Add("REPO_PATH: $RepoRoot")
  [void]$lines.Add("RUN_DIR: $RunDirPath")
  [void]$lines.Add("RUN_TIMESTAMP: $RunTimestamp")
  [void]$lines.Add("DIFF_BASE_REF: $DiffBase")
  [void]$lines.Add("CHANGED_FILES_COUNT: $($normalizedChangedFiles.Count)")
  [void]$lines.Add("LOG_ARTIFACT_COUNT: $($normalizedLogPaths.Count)")
  [void]$lines.Add("FILES_DUMP_DIR: $(if ([string]::IsNullOrWhiteSpace($FilesDumpDirectory)) { '<none>' } else { $FilesDumpDirectory })")
  [void]$lines.Add("")

  [void]$lines.Add("--- VALIDATIONS ---")
  if (
    ($normalizedValidationEntries.Count -eq 0) -and
    ($externalValidationLines.Count -eq 0) -and
    ($normalizedDebtEntries.Count -eq 0) -and
    ($inlineDebtLines.Count -eq 0)
  ) {
    [void]$lines.Add("(none)")
  }
  else {
    foreach ($entry in $normalizedValidationEntries) {
      [void]$lines.Add($entry)
    }

    if ($externalValidationLines.Count -gt 0) {
      if ($normalizedValidationEntries.Count -gt 0) {
        [void]$lines.Add("")
      }
      [void]$lines.Add("EXTERNAL_VALIDATION_LOG")
      foreach ($line in $externalValidationLines) {
        [void]$lines.Add($line)
      }
    }

    if (($normalizedDebtEntries.Count -gt 0) -or ($inlineDebtLines.Count -gt 0)) {
      if (($normalizedValidationEntries.Count -gt 0) -or ($externalValidationLines.Count -gt 0)) {
        [void]$lines.Add("")
      }
      [void]$lines.Add("DEBT_NOTES")
      foreach ($debt in $normalizedDebtEntries) {
        [void]$lines.Add($debt)
      }
      foreach ($debt in $inlineDebtLines) {
        [void]$lines.Add($debt)
      }
    }
  }
  [void]$lines.Add("")

  [void]$lines.Add("--- CHANGED FILES ---")
  if ($normalizedChangedFiles.Count -eq 0) {
    [void]$lines.Add("(none)")
  }
  else {
    foreach ($path in $normalizedChangedFiles) {
      [void]$lines.Add("- $path")
    }
  }
  [void]$lines.Add("")

  [void]$lines.Add("--- UNIFIED DIFF (PLAINTEXT) ---")
  foreach ($line in $diffLines) {
    [void]$lines.Add($line)
  }
  [void]$lines.Add("")
  [void]$lines.Add("=== END REPORT ===")
  [void]$lines.Add("")

  return [string]::Join("`n", $lines)
}

function Write-FinalReportArtifact {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$OutPath,
    [Parameter(Mandatory = $true)]
    [string]$RunId,
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$RunDirPath,
    [Parameter(Mandatory = $true)]
    [string]$RunTimestamp,
    [Parameter(Mandatory = $true)]
    [string]$DiffBase,
    [string[]]$ChangedFiles,
    [string[]]$ValidationEntries,
    [string]$ExternalValidation,
    [string[]]$DebtEntries,
    [string]$InlineDebtNotes,
    [string]$FilesDumpDirectory,
    [string[]]$LogPaths,
    [string]$UnifiedDiffText,
    [string]$ForcedStatus
  )

  $status = if ([string]::IsNullOrWhiteSpace($ForcedStatus)) {
    Get-ReportStatus -ValidationEntries @($ValidationEntries)
  }
  else {
    $ForcedStatus.Trim().ToUpperInvariant()
  }
  $reportText = Build-FinalReportText `
    -RunId $RunId `
    -Status $status `
    -Title $Title `
    -RepoRoot $RepoRoot `
    -RunDirPath $RunDirPath `
    -RunTimestamp $RunTimestamp `
    -DiffBase $DiffBase `
    -ChangedFiles @($ChangedFiles) `
    -ValidationEntries @($ValidationEntries) `
    -ExternalValidation $ExternalValidation `
    -DebtEntries @($DebtEntries) `
    -InlineDebtNotes $InlineDebtNotes `
    -FilesDumpDirectory $FilesDumpDirectory `
    -LogPaths @($LogPaths) `
    -UnifiedDiffText $UnifiedDiffText

  Write-TextFile -Path $OutPath -Text $reportText

  return [pscustomobject]@{
    Ok = $true
    OutPath = $OutPath
    Status = $status
    RunId = $RunId
  }
}

if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
  throw "Make-DiffBundle: RepoPath does not exist: $RepoPath"
}

$repoRoot = (Resolve-Path -LiteralPath $RepoPath).Path
$runTs = Get-Date -Format "yyyyMMdd_HHmmss"
$runId = "RUN_$runTs"
$runDir = Resolve-RunDir -RepoRoot $repoRoot -Timestamp $runTs -InputPath $RunDir
$filesDir = Join-Path $runDir "FILES"
$logsDir = Join-Path $runDir "logs"
$changedFilesTxtPath = Join-Path $runDir "CHANGED_FILES.txt"
$finalReportPath = Join-Path $runDir "FINAL_REPORT.txt"
$logArtifactPaths = New-Object System.Collections.Generic.List[string]

Ensure-Directory -Path $runDir
Ensure-Directory -Path $logsDir
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
  $gitVersionLog = Write-CommandFailureLog -LogsDir $logsDir -Name "GIT_VERSION" -CommandLine "git --version" -Output $gitVersion.Output
  [void]$logArtifactPaths.Add($gitVersionLog)
  Add-ValidationLine -Status "FAIL" -Message "git --version failed. See $gitVersionLog"
  throw "Make-DiffBundle: git unavailable. See $gitVersionLog"
}
Add-ValidationLine -Status "PASS" -Message "git --version :: $($gitVersion.Stdout.Trim())"

$statusResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("status", "--porcelain", "--untracked-files=all") -WorkDir $repoRoot -NoThrow
if (-not $statusResult.Ok) {
  $statusLog = Write-CommandFailureLog -LogsDir $logsDir -Name "GIT_STATUS" -CommandLine "git status --porcelain --untracked-files=all" -Output $statusResult.Output
  [void]$logArtifactPaths.Add($statusLog)
  Add-ValidationLine -Status "FAIL" -Message "git status failed. See $statusLog"
  throw "Make-DiffBundle: git status failed. See $statusLog"
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
Write-TextFile -Path $changedFilesTxtPath -Text ([string]::Join("`n", $statusOutputLines) + "`n")
Add-ValidationLine -Status "PASS" -Message "wrote CHANGED_FILES.txt"

$changedFilePaths = @($statusEntries | Select-Object -ExpandProperty Path -Unique | Sort-Object)

$diffVsBaseArgs = @("diff", "--no-color", "--patch", $DiffBaseRef, "--")
$diffVsBaseResult = Invoke-ExternalCommand -ExePath "git" -ArgList $diffVsBaseArgs -WorkDir $repoRoot -NoThrow
if (-not $diffVsBaseResult.Ok) {
  $cmd = "git diff --no-color --patch $DiffBaseRef --"
  $logPath = Write-CommandFailureLog -LogsDir $logsDir -Name "DIFF_VS_BASE" -CommandLine $cmd -Output $diffVsBaseResult.Output
  [void]$logArtifactPaths.Add($logPath)
  Add-ValidationLine -Status "FAIL" -Message "Make-DiffBundle: failed DIFF_VS_BASE. See $logPath"
  throw "Make-DiffBundle: failed DIFF_VS_BASE. See $logPath"
}
Add-ValidationLine -Status "PASS" -Message "captured unified diff via git diff --no-color --patch $DiffBaseRef --"

$diffUnstagedResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--no-color", "--patch", "--") -WorkDir $repoRoot -NoThrow
if (-not $diffUnstagedResult.Ok) {
  $logPath = Write-CommandFailureLog -LogsDir $logsDir -Name "DIFF_UNSTAGED" -CommandLine "git diff --no-color --patch --" -Output $diffUnstagedResult.Output
  [void]$logArtifactPaths.Add($logPath)
  Add-ValidationLine -Status "FAIL" -Message "Make-DiffBundle: failed DIFF_UNSTAGED. See $logPath"
  throw "Make-DiffBundle: failed DIFF_UNSTAGED. See $logPath"
}

$diffStagedResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--no-color", "--patch", "--cached", "--") -WorkDir $repoRoot -NoThrow
if (-not $diffStagedResult.Ok) {
  $logPath = Write-CommandFailureLog -LogsDir $logsDir -Name "DIFF_STAGED" -CommandLine "git diff --no-color --patch --cached --" -Output $diffStagedResult.Output
  [void]$logArtifactPaths.Add($logPath)
  Add-ValidationLine -Status "FAIL" -Message "Make-DiffBundle: failed DIFF_STAGED. See $logPath"
  throw "Make-DiffBundle: failed DIFF_STAGED. See $logPath"
}

if (Contains-AnsiSequence -Text $diffVsBaseResult.Stdout) {
  Add-ValidationLine -Status "FAIL" -Message "DIFF_VS_BASE output contains ANSI sequences"
  Add-DebtLine "DEBT_REQUIRED: remove ANSI sequences from DIFF_VS_BASE output generation."
}
else {
  Add-ValidationLine -Status "PASS" -Message "DIFF_VS_BASE output has no ANSI sequences"
}

if (Contains-AnsiSequence -Text $diffUnstagedResult.Stdout) {
  Add-ValidationLine -Status "FAIL" -Message "DIFF_UNSTAGED output contains ANSI sequences"
  Add-DebtLine "DEBT_REQUIRED: remove ANSI sequences from DIFF_UNSTAGED output generation."
}
else {
  Add-ValidationLine -Status "PASS" -Message "DIFF_UNSTAGED output has no ANSI sequences"
}

if (Contains-AnsiSequence -Text $diffStagedResult.Stdout) {
  Add-ValidationLine -Status "FAIL" -Message "DIFF_STAGED output contains ANSI sequences"
  Add-DebtLine "DEBT_REQUIRED: remove ANSI sequences from DIFF_STAGED output generation."
}
else {
  Add-ValidationLine -Status "PASS" -Message "DIFF_STAGED output has no ANSI sequences"
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
      Write-TextFile -Path $markerPath -Text "SKIPPED_DIRECTORY`t$relativePath`n"
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
      Write-TextFile -Path $deletedPath -Text "DELETED_OR_MISSING`t$relativePath`n"
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

$reportWrite = Write-FinalReportArtifact `
  -OutPath $finalReportPath `
  -RunId $runId `
  -Title $Title `
  -RepoRoot $repoRoot `
  -RunDirPath $runDir `
  -RunTimestamp $runTs `
  -DiffBase $DiffBaseRef `
  -ChangedFiles $changedFilePaths `
  -ValidationEntries @($validationLines) `
  -ExternalValidation $ValidationLog `
  -DebtEntries @($debtLines) `
  -InlineDebtNotes $DebtNotes `
  -FilesDumpDirectory $(if ($IncludeFilesDump) { $filesDir } else { "" }) `
  -LogPaths @($logArtifactPaths) `
  -UnifiedDiffText $diffVsBaseResult.Stdout `
  -ForcedStatus $ReportStatus

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

  $reportWrite = Write-FinalReportArtifact `
    -OutPath $finalReportPath `
    -RunId $runId `
    -Title $Title `
    -RepoRoot $repoRoot `
    -RunDirPath $runDir `
    -RunTimestamp $runTs `
    -DiffBase $DiffBaseRef `
    -ChangedFiles $changedFilePaths `
    -ValidationEntries @($validationLines) `
    -ExternalValidation $ValidationLog `
    -DebtEntries @($debtLines) `
    -InlineDebtNotes $DebtNotes `
    -FilesDumpDirectory $(if ($IncludeFilesDump) { $filesDir } else { "" }) `
    -LogPaths @($logArtifactPaths) `
    -UnifiedDiffText $diffVsBaseResult.Stdout `
    -ForcedStatus $ReportStatus
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
  RunId = $runId
  RunDir = $runDir
  FinalReportPath = $finalReportPath
  DiffArtifacts = @()
  LogArtifacts = @($logArtifactPaths)
  ChangedFiles = $changedFilePaths
  ChangedFilesCount = $changedFilePaths.Count
  ReportWrite = $reportWrite
}
