<#
.SYNOPSIS
Canonical SAFE SWAP for docs/CONTRACT_STAGE.md -> docs/CONTRACT.md.

.DESCRIPTION
Performs deterministic safe swap with integrity checks, backup/rollback, quality gates,
commit + optional push, and mandatory FINAL_REPORT.txt artifact output.

.EXAMPLE
pwsh tools/scripts/safe_swap_contract.ps1 -DryRun
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
  [string]$RepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path,
  [string]$CommitMessage = "docs(contract): safe swap CONTRACT_STAGE into CONTRACT",
  [bool]$AttemptPush = $true,
  [switch]$NoGates,
  [switch]$DryRun,
  [int]$MaxPrintedPatchChars = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$invokeExternalPath = Join-Path $PSScriptRoot "lib\Invoke-External.ps1"
$invokeExternalPath = (Resolve-Path -LiteralPath $invokeExternalPath).Path
. $invokeExternalPath

$bundleScriptPath = Join-Path $PSScriptRoot "lib\Make-DiffBundle.ps1"
$bundleScriptPath = (Resolve-Path -LiteralPath $bundleScriptPath).Path

$progressId = 9701
$totalStages = 10
$stageCounter = 0

$stageLogs = New-Object System.Collections.Generic.List[string]
$debtNotes = New-Object System.Collections.Generic.List[string]

function Write-SwapLog {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message
  )

  Write-Host $Message
  [void]$script:stageLogs.Add($Message)
}

function Add-Debt {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message
  )

  [void]$script:debtNotes.Add($Message)
  Write-SwapLog $Message
}

function Update-SwapProgress {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Status
  )

  $script:stageCounter += 1
  $percent = [Math]::Min([int](($script:stageCounter / $script:totalStages) * 100), 100)
  Write-Progress -Id $progressId -Activity "SAFE SWAP CONTRACT" -Status $Status -PercentComplete $percent
}

function Normalize-Whitespace {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Text
  )

  $normalized = $Text -replace "`r`n", "`n"
  $normalized = $normalized -replace "`r", "`n"
  $normalized = [regex]::Replace($normalized, "\s+", " ")
  return $normalized.Trim()
}

function Get-NormalizedParagraphs {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
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

function Get-NewestBackupPath {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$BackupDir
  )

  if (-not (Test-Path -LiteralPath $BackupDir -PathType Container)) {
    return ""
  }

  $latest = Get-ChildItem -LiteralPath $BackupDir -Filter "CONTRACT.pre-swap.*.md" -File |
    Sort-Object LastWriteTimeUtc -Descending |
    Select-Object -First 1

  if ($null -eq $latest) {
    return ""
  }

  return $latest.FullName
}

$repoRoot = ""
$docsDir = ""
$contractPath = ""
$stagePath = ""
$backupDir = ""
$backupPath = ""
$stageSnapshot = ""
$swapApplied = $false
$commitCreated = $false
$isSimulation = ($DryRun -or [bool]$WhatIfPreference)
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
  $backupDir = Join-Path $repoRoot ".tmp/safe-swap"
  New-Item -ItemType Directory -Path $backupDir -Force -WhatIf:$false -Confirm:$false | Out-Null

  if (-not (Test-Path -LiteralPath $contractPath -PathType Leaf)) {
    throw "Required file missing: $contractPath"
  }
  if (-not (Test-Path -LiteralPath $stagePath -PathType Leaf)) {
    throw "Required file missing: $stagePath"
  }

  Update-SwapProgress -Status "Git checks"
  $gitVersion = Invoke-ExternalCommand -ExePath "git" -ArgList @("--version") -WorkDir $repoRoot -NoThrow
  if (-not $gitVersion.Ok -or ($gitVersion.Stdout -notmatch "git version")) {
    throw "git is unavailable or returned unexpected output: $($gitVersion.Output)"
  }

  $insideRepo = Invoke-ExternalCommand -ExePath "git" -ArgList @("rev-parse", "--is-inside-work-tree") -WorkDir $repoRoot -NoThrow
  if (-not $insideRepo.Ok) {
    throw "git rev-parse failed: $($insideRepo.Output)"
  }
  if ($insideRepo.Stdout.Trim().ToLowerInvariant() -ne "true") {
    throw "Path is not a git work tree: $repoRoot"
  }

  Update-SwapProgress -Status "Content integrity check"
  $sourceText = Get-Content -Raw -Encoding UTF8 -LiteralPath $contractPath
  $stageText = Get-Content -Raw -Encoding UTF8 -LiteralPath $stagePath
  $stageSnapshot = $stageText

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
    throw "Integrity check failed: source paragraph(s) missing from CONTRACT_STAGE.md.`n$missingPreview"
  }

  Update-SwapProgress -Status "Backup current CONTRACT.md"
  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $backupPath = Join-Path $backupDir "CONTRACT.pre-swap.$timestamp.md"

  if ($isSimulation) {
    Write-SwapLog "DRY_RUN: would create backup at $backupPath"
  }
  elseif ($PSCmdlet.ShouldProcess($contractPath, "Create backup at $backupPath")) {
    Copy-Item -LiteralPath $contractPath -Destination $backupPath -Force
    Write-SwapLog "Backup created: $backupPath"
  }

  Update-SwapProgress -Status "Swap CONTRACT_STAGE.md into CONTRACT.md"
  if ($isSimulation) {
    Write-SwapLog "DRY_RUN: would replace $contractPath with $stagePath and remove $stagePath"
  }
  elseif ($PSCmdlet.ShouldProcess($contractPath, "Replace CONTRACT.md with CONTRACT_STAGE.md and remove CONTRACT_STAGE.md")) {
    Copy-Item -LiteralPath $stagePath -Destination $contractPath -Force
    Remove-Item -LiteralPath $stagePath -Force
    $swapApplied = $true
    Write-SwapLog "Swap applied."
  }

  Update-SwapProgress -Status "Run gates"
  if ($isSimulation) {
    Write-SwapLog "DRY_RUN: gates skipped."
  }
  elseif ($NoGates) {
    Write-SwapLog "Gates skipped due to -NoGates."
  }
  else {
    $healthResult = Invoke-ExternalCommand -ExePath "pnpm" -ArgList @("run", "health") -WorkDir $repoRoot -NoThrow
    if ($healthResult.Stdout) {
      Write-SwapLog $healthResult.Stdout
    }
    if ($healthResult.Stderr) {
      Write-SwapLog $healthResult.Stderr
    }
    if (-not $healthResult.Ok) {
      throw "Gate failed: pnpm run health (exit $($healthResult.ExitCode))."
    }

    $smokeResult = Invoke-ExternalCommand -ExePath "pnpm" -ArgList @("run", "factory:smoke") -WorkDir $repoRoot -NoThrow
    if ($smokeResult.Stdout) {
      Write-SwapLog $smokeResult.Stdout
    }
    if ($smokeResult.Stderr) {
      Write-SwapLog $smokeResult.Stderr
    }
    if (-not $smokeResult.Ok) {
      throw "Gate failed: pnpm run factory:smoke (exit $($smokeResult.ExitCode))."
    }
  }

  Update-SwapProgress -Status "Stage and commit"
  if ($isSimulation) {
    Write-SwapLog "DRY_RUN: would stage docs/CONTRACT.md and docs/CONTRACT_STAGE.md, then commit."
  }
  else {
    Invoke-ExternalCommand -ExePath "git" -ArgList @("add", "--", "docs/CONTRACT.md", "docs/CONTRACT_STAGE.md") -WorkDir $repoRoot | Out-Null
    $stagedDiff = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--cached", "--quiet", "--", "docs/CONTRACT.md", "docs/CONTRACT_STAGE.md") -WorkDir $repoRoot -NoThrow

    if ($stagedDiff.ExitCode -eq 0) {
      Write-SwapLog "No staged swap changes found; commit skipped."
    }
    elseif ($stagedDiff.ExitCode -eq 1) {
      $commitResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("commit", "-m", $CommitMessage) -WorkDir $repoRoot -NoThrow
      if ($commitResult.Stdout) {
        Write-SwapLog $commitResult.Stdout
      }
      if ($commitResult.Stderr) {
        Write-SwapLog $commitResult.Stderr
      }
      if (-not $commitResult.Ok) {
        throw "git commit failed (exit $($commitResult.ExitCode))."
      }
      $commitCreated = $true
    }
    else {
      throw "Unexpected exit code from git diff --cached --quiet: $($stagedDiff.ExitCode)"
    }
  }

  Update-SwapProgress -Status "Attempt push"
  if ($isSimulation) {
    Write-SwapLog "DRY_RUN: would run git push when commit exists."
  }
  elseif ($AttemptPush -and $commitCreated) {
    $pushResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("push") -WorkDir $repoRoot -NoThrow
    if ($pushResult.Stdout) {
      Write-SwapLog $pushResult.Stdout
    }
    if ($pushResult.Stderr) {
      Write-SwapLog $pushResult.Stderr
    }
    if (-not $pushResult.Ok) {
      Add-Debt "WARN_DEBT: git push failed (non-fatal, likely offline)."
      Add-Debt "DEBT_REQUIRED: retry push and record owner/date before closing run."
    }
  }
  elseif (-not $AttemptPush) {
    Write-SwapLog "Push skipped because AttemptPush is false."
  }
  else {
    Write-SwapLog "Push skipped because no commit was created."
  }

  $swapOutcome = "PASS"
  $exitCode = 0
}
catch {
  Write-SwapLog "SAFE_SWAP_CONTRACT failed: $($_.Exception.Message)"

  if (-not $isSimulation) {
    $rollbackBackup = Get-NewestBackupPath -BackupDir $backupDir
    if (-not [string]::IsNullOrWhiteSpace($rollbackBackup) -and (Test-Path -LiteralPath $rollbackBackup -PathType Leaf)) {
      Copy-Item -LiteralPath $rollbackBackup -Destination $contractPath -Force
      Write-SwapLog "Rollback complete: CONTRACT.md restored from $rollbackBackup"
      if (-not [string]::IsNullOrWhiteSpace($stageSnapshot) -and -not (Test-Path -LiteralPath $stagePath -PathType Leaf)) {
        Set-Content -LiteralPath $stagePath -Value $stageSnapshot -Encoding UTF8
        Write-SwapLog "Rollback note: CONTRACT_STAGE.md restored from in-memory snapshot."
      }
    }
    else {
      Add-Debt "WARN_DEBT: rollback backup not found in $backupDir"
      Add-Debt "DEBT_REQUIRED: manually verify docs/CONTRACT.md integrity before closing run."
    }
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
    $validationPayload = if ($stageLogs.Count -eq 0) { "" } else { [string]::Join("`n", @($stageLogs)) }
    $debtPayload = if ($debtNotes.Count -eq 0) { "" } else { [string]::Join("`n", @($debtNotes)) }

    $diffBaseRef = if ($commitCreated) { "HEAD~1" } else { "HEAD" }
    $reportStatus = if ($swapOutcome -eq "PASS") { "SUCCESS" } else { "FAIL" }

    try {
      $bundleResult = $null
      try {
        $bundleResult = & $bundleScriptPath `
          -RepoPath $bundleRepoPath `
          -Title "SAFE SWAP CONTRACT ($swapOutcome)" `
          -IncludeFilesDump:$true `
          -AlsoPrintShortSummary:$true `
          -ValidationLog $validationPayload `
          -DebtNotes $debtPayload `
          -DiffBaseRef $diffBaseRef `
          -ReportStatus $reportStatus
      }
      catch {
        if ($commitCreated -and ($diffBaseRef -eq "HEAD~1")) {
          $bundleResult = & $bundleScriptPath `
            -RepoPath $bundleRepoPath `
            -Title "SAFE SWAP CONTRACT ($swapOutcome)" `
            -IncludeFilesDump:$true `
            -AlsoPrintShortSummary:$true `
            -ValidationLog $validationPayload `
            -DebtNotes $debtPayload `
            -DiffBaseRef "HEAD" `
            -ReportStatus $reportStatus
        }
        else {
          throw
        }
      }

      if ($bundleResult -and $bundleResult.FinalReportPath) {
        $finalReportPath = $bundleResult.FinalReportPath
        Write-SwapLog "FINAL_REPORT artifact: $finalReportPath"
      }
      else {
        Add-Debt "WARN_DEBT: FINAL_REPORT path was not returned by Make-DiffBundle."
        Add-Debt "DEBT_REQUIRED: run tools/scripts/lib/Make-DiffBundle.ps1 manually."
        $exitCode = 1
      }
    }
    catch {
      Add-Debt "WARN_DEBT: failed to generate FINAL_REPORT artifact: $($_.Exception.Message)"
      Add-Debt "DEBT_REQUIRED: run tools/scripts/lib/Make-DiffBundle.ps1 manually."
      $exitCode = 1
    }
  }
  else {
    Add-Debt "WARN_DEBT: bundle generation skipped because repo path could not be resolved."
    Add-Debt "DEBT_REQUIRED: run tools/scripts/lib/Make-DiffBundle.ps1 manually."
    $exitCode = 1
  }
}

exit $exitCode
