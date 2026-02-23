<#
.SYNOPSIS
Canonical SAFE SWAP for docs/CONTRACT_STAGE.md -> docs/CONTRACT.md.

.DESCRIPTION
Performs deterministic safe swap with integrity checks, backup/rollback, quality gates,
commit + optional push, and mandatory plaintext unified diff artifact output.

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

$writeDiffPath = Join-Path $PSScriptRoot "lib\Write-UnifiedDiff.ps1"
$writeDiffPath = (Resolve-Path -LiteralPath $writeDiffPath).Path
. $writeDiffPath

$progressId = 9701
$totalStages = 10
$stageCounter = 0

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

function Emit-PlaintextDiffArtifact {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$BackupDir,
    [bool]$CommitCreated,
    [int]$MaxPrintedPatchChars = 0
  )

  if (-not (Test-Path -LiteralPath $BackupDir -PathType Container)) {
    New-Item -ItemType Directory -Path $BackupDir -Force -WhatIf:$false -Confirm:$false | Out-Null
  }

  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $diffPath = Join-Path $BackupDir "DIFF_$timestamp.patch"
  $baseRef = if ($CommitCreated) { "HEAD~1" } else { "HEAD" }

  try {
    $summary = Write-UnifiedDiffArtifact -RepoPath $RepoRoot -OutPath $diffPath -BaseRef $baseRef
  }
  catch {
    if ($CommitCreated) {
      $baseRef = "HEAD"
      $summary = Write-UnifiedDiffArtifact -RepoPath $RepoRoot -OutPath $diffPath -BaseRef $baseRef
    }
    else {
      throw
    }
  }

  Write-Host "Diff artifact: $diffPath"
  Write-Host "Diff summary: files=$($summary.FilesChanged) insertions=$($summary.Insertions) deletions=$($summary.Deletions) base=$baseRef"
  [Console]::Out.WriteLine("----- BEGIN UNIFIED DIFF PATCH -----")

  $patchText = ""
  if (Test-Path -LiteralPath $diffPath -PathType Leaf) {
    $patchText = Get-Content -Raw -LiteralPath $diffPath
  }

  if ([string]::IsNullOrEmpty($patchText)) {
    [Console]::Out.WriteLine("(no diff)")
  }
  else {
    if (($MaxPrintedPatchChars -gt 0) -and ($patchText.Length -gt $MaxPrintedPatchChars)) {
      $headChars = [Math]::Max([int]($MaxPrintedPatchChars / 2), 1)
      $tailChars = [Math]::Max($MaxPrintedPatchChars - $headChars, 1)
      [Console]::Out.WriteLine($patchText.Substring(0, $headChars))
      [Console]::Out.WriteLine(("[PATCH_TRIMMED totalChars={0} printedChars={1}]" -f $patchText.Length, $MaxPrintedPatchChars))
      [Console]::Out.WriteLine($patchText.Substring($patchText.Length - $tailChars))
    }
    else {
      [Console]::Out.WriteLine($patchText)
    }
  }

  [Console]::Out.WriteLine("----- END UNIFIED DIFF PATCH -----")

  return [pscustomobject]@{
    DiffPath = $diffPath
    Summary = $summary
  }
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
    Write-Host "DRY_RUN: would create backup at $backupPath"
  }
  elseif ($PSCmdlet.ShouldProcess($contractPath, "Create backup at $backupPath")) {
    Copy-Item -LiteralPath $contractPath -Destination $backupPath -Force
    Write-Host "Backup created: $backupPath"
  }

  Update-SwapProgress -Status "Swap CONTRACT_STAGE.md into CONTRACT.md"
  if ($isSimulation) {
    Write-Host "DRY_RUN: would replace $contractPath with $stagePath and remove $stagePath"
  }
  elseif ($PSCmdlet.ShouldProcess($contractPath, "Replace CONTRACT.md with CONTRACT_STAGE.md and remove CONTRACT_STAGE.md")) {
    Copy-Item -LiteralPath $stagePath -Destination $contractPath -Force
    Remove-Item -LiteralPath $stagePath -Force
    $swapApplied = $true
    Write-Host "Swap applied."
  }

  Update-SwapProgress -Status "Run gates"
  if ($isSimulation) {
    Write-Host "DRY_RUN: gates skipped."
  }
  elseif ($NoGates) {
    Write-Host "Gates skipped due to -NoGates."
  }
  else {
    $healthResult = Invoke-ExternalCommand -ExePath "pnpm" -ArgList @("run", "health") -WorkDir $repoRoot -NoThrow
    if ($healthResult.Stdout) {
      Write-Host $healthResult.Stdout
    }
    if ($healthResult.Stderr) {
      Write-Host $healthResult.Stderr
    }
    if (-not $healthResult.Ok) {
      throw "Gate failed: pnpm run health (exit $($healthResult.ExitCode))."
    }

    $smokeResult = Invoke-ExternalCommand -ExePath "pnpm" -ArgList @("run", "factory:smoke") -WorkDir $repoRoot -NoThrow
    if ($smokeResult.Stdout) {
      Write-Host $smokeResult.Stdout
    }
    if ($smokeResult.Stderr) {
      Write-Host $smokeResult.Stderr
    }
    if (-not $smokeResult.Ok) {
      throw "Gate failed: pnpm run factory:smoke (exit $($smokeResult.ExitCode))."
    }
  }

  Update-SwapProgress -Status "Stage and commit"
  if ($isSimulation) {
    Write-Host "DRY_RUN: would stage docs/CONTRACT.md and docs/CONTRACT_STAGE.md, then commit."
  }
  else {
    Invoke-ExternalCommand -ExePath "git" -ArgList @("add", "--", "docs/CONTRACT.md", "docs/CONTRACT_STAGE.md") -WorkDir $repoRoot | Out-Null
    $stagedDiff = Invoke-ExternalCommand -ExePath "git" -ArgList @("diff", "--cached", "--quiet", "--", "docs/CONTRACT.md", "docs/CONTRACT_STAGE.md") -WorkDir $repoRoot -NoThrow

    if ($stagedDiff.ExitCode -eq 0) {
      Write-Host "No staged swap changes found; commit skipped."
    }
    elseif ($stagedDiff.ExitCode -eq 1) {
      $commitResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("commit", "-m", $CommitMessage) -WorkDir $repoRoot -NoThrow
      if ($commitResult.Stdout) {
        Write-Host $commitResult.Stdout
      }
      if ($commitResult.Stderr) {
        Write-Host $commitResult.Stderr
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
    Write-Host "DRY_RUN: would run git push when commit exists."
  }
  elseif ($AttemptPush -and $commitCreated) {
    $pushResult = Invoke-ExternalCommand -ExePath "git" -ArgList @("push") -WorkDir $repoRoot -NoThrow
    if ($pushResult.Stdout) {
      Write-Host $pushResult.Stdout
    }
    if ($pushResult.Stderr) {
      Write-Host $pushResult.Stderr
    }
    if (-not $pushResult.Ok) {
      Write-Host "WARN_DEBT: git push failed (non-fatal, likely offline)."
      Write-Host "DEBT_REQUIRED: retry push and record owner/date before closing run."
    }
  }
  elseif (-not $AttemptPush) {
    Write-Host "Push skipped because AttemptPush is false."
  }
  else {
    Write-Host "Push skipped because no commit was created."
  }

  Update-SwapProgress -Status "Generate plaintext unified diff"
  $diffInfo = Emit-PlaintextDiffArtifact -RepoRoot $repoRoot -BackupDir $backupDir -CommitCreated:$commitCreated -MaxPrintedPatchChars $MaxPrintedPatchChars
  Write-Host "Diff artifact written: $($diffInfo.DiffPath)"

  Write-Progress -Id $progressId -Activity "SAFE SWAP CONTRACT" -Completed
  exit 0
}
catch {
  Write-Host "SAFE_SWAP_CONTRACT failed: $($_.Exception.Message)"

  if (-not $isSimulation) {
    $rollbackBackup = Get-NewestBackupPath -BackupDir $backupDir
    if (-not [string]::IsNullOrWhiteSpace($rollbackBackup) -and (Test-Path -LiteralPath $rollbackBackup -PathType Leaf)) {
      Copy-Item -LiteralPath $rollbackBackup -Destination $contractPath -Force
      Write-Host "Rollback complete: CONTRACT.md restored from $rollbackBackup"
      if (-not [string]::IsNullOrWhiteSpace($stageSnapshot) -and -not (Test-Path -LiteralPath $stagePath -PathType Leaf)) {
        Set-Content -LiteralPath $stagePath -Value $stageSnapshot -Encoding UTF8
        Write-Host "Rollback note: CONTRACT_STAGE.md restored from in-memory snapshot."
      }
    }
    else {
      Write-Host "WARN_DEBT: rollback backup not found in $backupDir"
      Write-Host "DEBT_REQUIRED: manually verify docs/CONTRACT.md integrity before closing run."
    }
  }

  try {
    if (-not [string]::IsNullOrWhiteSpace($repoRoot) -and (Test-Path -LiteralPath $repoRoot -PathType Container)) {
      [void](Emit-PlaintextDiffArtifact -RepoRoot $repoRoot -BackupDir $backupDir -CommitCreated:$commitCreated -MaxPrintedPatchChars $MaxPrintedPatchChars)
    }
  }
  catch {
    Write-Host "WARN_DEBT: failed to generate plaintext diff artifact during failure handling."
    Write-Host "DEBT_REQUIRED: run tools/scripts/lib/Write-UnifiedDiff.ps1 manually and attach patch."
  }

  Write-Progress -Id $progressId -Activity "SAFE SWAP CONTRACT" -Completed
  exit 1
}
