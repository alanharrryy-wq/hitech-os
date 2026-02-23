<#
.SYNOPSIS
Safely swap docs/CONTRACT_STAGE.md into docs/CONTRACT.md with rollback and optional gates.

.DESCRIPTION
Performs a deterministic SAFE SWAP flow:
preflight -> git checks -> content integrity check -> backup -> swap -> gates ->
commit -> optional push -> open docs folder -> print last commit summary.

Always generates a single FINAL_REPORT.txt bundle artifact (success and failure paths).
#>

param(
  [string]$RepoPath = "F:\repos\hitech-os",
  [bool]$AttemptPush = $true,
  [string]$CommitMessage = "docs(contract): safe swap CONTRACT_STAGE into CONTRACT",
  [switch]$NoGates
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$progressId = 7100
$totalStages = 11
$stageCounter = 0

$helperPath = Join-Path $PSScriptRoot "..\lib\Invoke-External.ps1"
$helperPath = (Resolve-Path -LiteralPath $helperPath).Path
. $helperPath

$bundleScriptPath = Join-Path $PSScriptRoot "..\lib\Make-DiffBundle.ps1"
$bundleScriptPath = (Resolve-Path -LiteralPath $bundleScriptPath).Path

$stageLogs = New-Object System.Collections.Generic.List[string]
$debtNotes = New-Object System.Collections.Generic.List[string]

function Write-SwapLog {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message
  )
  Write-Host $Message
  [void]$script:stageLogs.Add($Message)
}

function Add-Debt {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message
  )
  [void]$script:debtNotes.Add($Message)
  Write-SwapLog $Message
}

function Update-SwapProgress {
  param(
    [string]$Status
  )
  $script:stageCounter += 1
  $percent = [Math]::Min([int](($script:stageCounter / $script:totalStages) * 100), 100)
  Write-Progress -Id $progressId -Activity "SAFE SWAP CONTRACT" -Status $Status -PercentComplete $percent
  Write-SwapLog "STAGE: $Status"
}

function Normalize-Whitespace {
  param(
    [string]$Text
  )

  $normalized = $Text -replace "`r`n", "`n"
  $normalized = $normalized -replace "`r", "`n"
  $normalized = [regex]::Replace($normalized, "\s+", " ")
  return $normalized.Trim()
}

function Get-NormalizedParagraphs {
  param(
    [string]$Text
  )

  $lineNormalized = $Text -replace "`r`n", "`n"
  $lineNormalized = $lineNormalized -replace "`r", "`n"
  $chunks = [regex]::Split($lineNormalized, "\n\s*\n")

  $paragraphs = New-Object System.Collections.Generic.List[string]
  foreach ($chunk in $chunks) {
    $trimmed = $chunk.Trim()
    if ($trimmed.Length -eq 0) {
      continue
    }
    $paragraphs.Add((Normalize-Whitespace -Text $trimmed))
  }
  return $paragraphs
}

function Resolve-GitExecutable {
  $gitCandidates = @(Get-Command git -All -ErrorAction Stop)
  $gitApplication = $gitCandidates |
    Where-Object { $_.CommandType -eq "Application" } |
    Select-Object -First 1

  if (-not $gitApplication) {
    throw "git executable could not be resolved from PATH."
  }

  if ($gitApplication.Source) {
    return $gitApplication.Source
  }
  if ($gitApplication.Path) {
    return $gitApplication.Path
  }

  throw "git command was found, but executable path could not be resolved."
}

function Parse-GitStatusPath {
  param(
    [string]$StatusLine
  )

  if ([string]::IsNullOrWhiteSpace($StatusLine) -or $StatusLine.Length -lt 4) {
    return ""
  }

  $pathPart = $StatusLine.Substring(3).Trim()
  if ($pathPart.Contains(" -> ")) {
    $pathPart = ($pathPart -split " -> ")[-1].Trim()
  }

  return ($pathPart -replace "\\", "/")
}

$repoRoot = ""
$docsDir = ""
$contractPath = ""
$stagePath = ""
$backupPath = ""
$stageSnapshot = ""
$swapApplied = $false
$externalDebug = $true
$swapOutcome = "FAIL"
$exitCode = 1
$finalReportPath = ""

try {
  Update-SwapProgress -Status "Preflight checks"
  if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
    throw "RepoPath does not exist: $RepoPath"
  }

  $repoRoot = (Resolve-Path -LiteralPath $RepoPath).Path
  $docsDir = Join-Path $repoRoot "docs"
  $contractPath = Join-Path $docsDir "CONTRACT.md"
  $stagePath = Join-Path $docsDir "CONTRACT_STAGE.md"

  if (-not (Test-Path -LiteralPath $contractPath -PathType Leaf)) {
    throw "Required file missing: $contractPath"
  }
  if (-not (Test-Path -LiteralPath $stagePath -PathType Leaf)) {
    throw "Required file missing: $stagePath"
  }

  Update-SwapProgress -Status "Resolve git executable"
  $gitExe = Resolve-GitExecutable
  Write-SwapLog "Resolved git executable: $gitExe"

  Update-SwapProgress -Status "Verify git --version"
  $gitVersion = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("--version") -WorkDir $repoRoot -Debug:$externalDebug
  if ($gitVersion.Output) {
    Write-SwapLog $gitVersion.Output.Trim()
  }
  if (($gitVersion.ExitCode -ne 0) -or ($gitVersion.Output -notmatch "git version")) {
    throw "git --version did not return a valid version string."
  }

  Update-SwapProgress -Status "Verify git repo state"
  $insideRepo = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("rev-parse", "--is-inside-work-tree") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
  if ($insideRepo.ExitCode -ne 0) {
    throw "git rev-parse failed: $($insideRepo.Output)"
  }
  if ($insideRepo.Output.Trim().ToLowerInvariant() -ne "true") {
    throw "Path is not inside a git work tree: $repoRoot"
  }

  Update-SwapProgress -Status "Check working tree scope"
  $statusResult = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("status", "--porcelain", "--untracked-files=all") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
  if ($statusResult.ExitCode -ne 0) {
    throw "git status failed: $($statusResult.Output)"
  }

  $allowedPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
  [void]$allowedPaths.Add("docs/CONTRACT.md")
  [void]$allowedPaths.Add("docs/CONTRACT_STAGE.md")

  $disallowed = New-Object System.Collections.Generic.List[string]
  if ($statusResult.Output) {
    $statusLines = $statusResult.Output -split "`r?`n"
    foreach ($line in $statusLines) {
      if ([string]::IsNullOrWhiteSpace($line)) {
        continue
      }
      $parsedPath = Parse-GitStatusPath -StatusLine $line
      if ([string]::IsNullOrWhiteSpace($parsedPath)) {
        continue
      }
      if (-not $allowedPaths.Contains($parsedPath)) {
        $disallowed.Add($line)
      }
    }
  }

  if ($disallowed.Count -gt 0) {
    $preview = ($disallowed | Select-Object -First 20) -join "`n"
    throw "Working tree must be clean except docs/CONTRACT.md and docs/CONTRACT_STAGE.md.`nDisallowed entries:`n$preview"
  }

  Update-SwapProgress -Status "Run content-only integrity check"
  $sourceText = Get-Content -Raw -Encoding UTF8 -LiteralPath $contractPath
  $stageText = Get-Content -Raw -Encoding UTF8 -LiteralPath $stagePath

  $sourceParagraphs = Get-NormalizedParagraphs -Text $sourceText
  $normalizedStage = Normalize-Whitespace -Text $stageText

  $missingParagraphs = New-Object System.Collections.Generic.List[string]
  foreach ($paragraph in $sourceParagraphs) {
    if ($normalizedStage.IndexOf($paragraph, [System.StringComparison]::Ordinal) -lt 0) {
      $preview = if ($paragraph.Length -gt 220) { $paragraph.Substring(0, 220) + "..." } else { $paragraph }
      $missingParagraphs.Add($preview)
      if ($missingParagraphs.Count -ge 3) {
        break
      }
    }
  }

  if ($missingParagraphs.Count -gt 0) {
    $missingPreview = ($missingParagraphs | ForEach-Object { "- $_" }) -join "`n"
    throw "Integrity check failed: source paragraph(s) missing from CONTRACT_STAGE.md.`nFirst missing/changed paragraphs:`n$missingPreview"
  }
  Write-SwapLog "Integrity check passed: all source paragraphs were found in CONTRACT_STAGE.md."

  Update-SwapProgress -Status "Create pre-swap backup"
  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $backupDir = Join-Path $repoRoot ".tmp/safe-swap"
  New-Item -ItemType Directory -Force -Path $backupDir -WhatIf:$false -Confirm:$false | Out-Null
  $backupPath = Join-Path $backupDir "CONTRACT.pre-swap.$timestamp.md"
  Copy-Item -LiteralPath $contractPath -Destination $backupPath -Force
  $stageSnapshot = Get-Content -Raw -Encoding UTF8 -LiteralPath $stagePath
  Write-SwapLog "Backup created: $backupPath"

  Update-SwapProgress -Status "Swap CONTRACT_STAGE.md into CONTRACT.md"
  Copy-Item -LiteralPath $stagePath -Destination $contractPath -Force
  Remove-Item -LiteralPath $stagePath -Force
  $swapApplied = $true
  Write-SwapLog "Swap applied: CONTRACT_STAGE.md -> CONTRACT.md and CONTRACT_STAGE.md removed."

  Update-SwapProgress -Status "Run gates"
  if (-not $NoGates) {
    $healthResult = Invoke-ExternalCommand -ExePath "pnpm" -ArgList @("run", "health") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
    if ($healthResult.Output) {
      Write-SwapLog $healthResult.Output.Trim()
    }
    if ($healthResult.ExitCode -ne 0) {
      throw "Gate failed: pnpm run health (exit $($healthResult.ExitCode))."
    }

    $smokeResult = Invoke-ExternalCommand -ExePath "pnpm" -ArgList @("run", "factory:smoke") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
    if ($smokeResult.Output) {
      Write-SwapLog $smokeResult.Output.Trim()
    }
    if ($smokeResult.ExitCode -ne 0) {
      throw "Gate failed: pnpm run factory:smoke (exit $($smokeResult.ExitCode))."
    }
  }
  else {
    Write-SwapLog "Gates skipped due to -NoGates."
  }

  Update-SwapProgress -Status "Commit and optional push"
  Invoke-ExternalCommand -ExePath $gitExe -ArgList @("add", "--all", "--", "docs") -WorkDir $repoRoot -Debug:$externalDebug | Out-Null

  $stagedDiff = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("diff", "--cached", "--quiet") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
  $commitCreated = $false

  if ($stagedDiff.ExitCode -eq 0) {
    Write-SwapLog "No staged changes found after swap; commit skipped."
  }
  elseif ($stagedDiff.ExitCode -eq 1) {
    $commitResult = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("commit", "-m", $CommitMessage) -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
    if ($commitResult.Output) {
      Write-SwapLog $commitResult.Output.Trim()
    }
    if ($commitResult.ExitCode -ne 0) {
      throw "git commit failed (exit $($commitResult.ExitCode))."
    }
    $commitCreated = $true
  }
  else {
    throw "Unexpected exit code from git diff --cached --quiet: $($stagedDiff.ExitCode)"
  }

  if ($AttemptPush -and $commitCreated) {
    $pushResult = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("push") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
    if ($pushResult.Output) {
      Write-SwapLog $pushResult.Output.Trim()
    }
    if ($pushResult.ExitCode -ne 0) {
      Add-Debt "WARN_DEBT: git push failed (non-fatal, likely offline)."
      Add-Debt "DEBT_REQUIRED: record push retry owner/date in docs/NOTEBOOK.md before closing this run."
    }
  }
  elseif (-not $AttemptPush) {
    Write-SwapLog "Push skipped because -AttemptPush is false."
  }
  else {
    Write-SwapLog "Push skipped because no new commit was created."
  }

  Update-SwapProgress -Status "Open docs and print commit summary"
  try {
    Start-Process -FilePath "explorer.exe" -ArgumentList $docsDir -WhatIf:$false -Confirm:$false | Out-Null
    Write-SwapLog "Opened docs folder: $docsDir"
  }
  catch {
    Add-Debt "WARN_DEBT: could not open docs folder automatically: $docsDir"
  }

  $lastCommit = Invoke-ExternalCommand -ExePath $gitExe -ArgList @("log", "-1", "--oneline") -WorkDir $repoRoot -NoThrow -Debug:$externalDebug
  if ($lastCommit.Output) {
    Write-SwapLog "Last commit: $($lastCommit.Output.Trim())"
  }

  $swapOutcome = "PASS"
  $exitCode = 0
}
catch {
  Write-SwapLog "SAFE_SWAP_CONTRACT failed: $($_.Exception.Message)"
  if ($swapApplied -and -not [string]::IsNullOrWhiteSpace($backupPath) -and (Test-Path -LiteralPath $backupPath -PathType Leaf)) {
    Write-SwapLog "Rollback started: restoring CONTRACT.md from backup."
    Copy-Item -LiteralPath $backupPath -Destination $contractPath -Force
    if (-not [string]::IsNullOrWhiteSpace($stageSnapshot)) {
      Set-Content -LiteralPath $stagePath -Value $stageSnapshot -Encoding UTF8
      Write-SwapLog "Rollback restored CONTRACT_STAGE.md from in-memory snapshot."
    }
    Write-SwapLog "Rollback complete."
  }
  else {
    Add-Debt "WARN_DEBT: rollback not applied because backup/snapshot was unavailable."
  }
  $swapOutcome = "FAIL"
  $exitCode = 1
}
finally {
  Write-Progress -Id $progressId -Activity "SAFE SWAP CONTRACT" -Completed

  $bundleRepoPath = ""
  if (-not [string]::IsNullOrWhiteSpace($repoRoot) -and (Test-Path -LiteralPath $repoRoot -PathType Container)) {
    $bundleRepoPath = $repoRoot
  }
  elseif (-not [string]::IsNullOrWhiteSpace($RepoPath) -and (Test-Path -LiteralPath $RepoPath -PathType Container)) {
    $bundleRepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
  }

  if (-not [string]::IsNullOrWhiteSpace($bundleRepoPath)) {
    try {
      $validationPayload = if ($stageLogs.Count -eq 0) { "" } else { [string]::Join("`n", @($stageLogs)) }
      $debtPayload = if ($debtNotes.Count -eq 0) { "" } else { [string]::Join("`n", @($debtNotes)) }

      $bundleResult = & $bundleScriptPath `
        -RepoPath $bundleRepoPath `
        -Title "SAFE SWAP CONTRACT ($swapOutcome)" `
        -IncludeFilesDump:$true `
        -AlsoPrintShortSummary:$true `
        -ValidationLog $validationPayload `
        -DebtNotes $debtPayload

      if ($bundleResult -and $bundleResult.FinalReportPath) {
        $finalReportPath = $bundleResult.FinalReportPath
        Write-Host "FINAL_REPORT artifact: $finalReportPath"
      }
    }
    catch {
      Write-Host "WARN_DEBT: failed to generate FINAL_REPORT artifact: $($_.Exception.Message)"
      Write-Host "DEBT_REQUIRED: run tools/scripts/lib/Make-DiffBundle.ps1 manually."
      $exitCode = 1
    }
  }
  else {
    Write-Host "WARN_DEBT: bundle generation skipped because repo path could not be resolved."
    Write-Host "DEBT_REQUIRED: run tools/scripts/lib/Make-DiffBundle.ps1 manually."
    $exitCode = 1
  }
}

exit $exitCode
