<#
.SYNOPSIS
Validates canonical shared runs-root governance across HITECH-OS worktrees and writes a deterministic evidence pack.

.DESCRIPTION
Runs:
- Ensure (write)
- Doctor
- Tracking (without bypass) from multiple worktrees
- Ensure idempotency stress
- Temporary worktree drift guard
- Intentional negative broken-junction test + recovery

Evidence is written to:
  <SharedRunsRoot>/<RUN_ID>/evidence/

Exit codes:
  0 = validations passed
  2 = governance blocked unexpectedly outside the intentional negative test
  1 = unexpected execution failure
#>

[CmdletBinding()]
param(
  [string]$StartDir = '',
  [string]$SharedRunsRoot = 'F:\repos\HITECHOS_SHARED\tools\codex\runs',
  [string]$TempWorktreePath = 'F:\repos\HITECHOS__E_temp'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Convert-ToCanonicalPath {
  [CmdletBinding()]
  param([string]$Path)

  if ([string]::IsNullOrWhiteSpace($Path)) {
    return ''
  }

  $expanded = [Environment]::ExpandEnvironmentVariables($Path.Trim())
  $full = [System.IO.Path]::GetFullPath($expanded)
  if ($full.StartsWith('\\?\')) {
    $full = $full.Substring(4)
  }

  return $full.TrimEnd('\', '/')
}

function Normalize-PathForReport {
  [CmdletBinding()]
  param([string]$Path)

  if ([string]::IsNullOrWhiteSpace($Path)) {
    return ''
  }

  return (Convert-ToCanonicalPath -Path $Path).Replace('\', '/')
}

function Write-DeterministicTextFile {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Content
  )

  $dir = Split-Path -Parent $Path
  if (-not [string]::IsNullOrWhiteSpace($dir) -and -not (Test-Path -LiteralPath $dir -PathType Container)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
  }

  $text = $Content
  if (-not $text.EndsWith("`n")) {
    $text += "`n"
  }

  [System.IO.File]::WriteAllText($Path, $text, [System.Text.UTF8Encoding]::new($false))
}

function Write-DeterministicJsonFile {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)]$Object
  )

  $json = ConvertTo-Json -InputObject $Object -Depth 100
  Write-DeterministicTextFile -Path $Path -Content $json
}

function Read-JsonFileSafe {
  [CmdletBinding()]
  param([string]$Path)

  if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    return $null
  }

  try {
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
  }
  catch {
    return $null
  }
}

function Test-PathUnderRoot {
  [CmdletBinding()]
  param(
    [string]$Candidate,
    [string]$Root
  )

  $candidateNorm = Normalize-PathForReport -Path $Candidate
  $rootNorm = Normalize-PathForReport -Path $Root
  if ([string]::IsNullOrWhiteSpace($candidateNorm) -or [string]::IsNullOrWhiteSpace($rootNorm)) {
    return $false
  }

  if ($candidateNorm.Equals($rootNorm, [System.StringComparison]::OrdinalIgnoreCase)) {
    return $true
  }

  return $candidateNorm.StartsWith(($rootNorm + '/'), [System.StringComparison]::OrdinalIgnoreCase)
}

function Invoke-PwshFile {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [Parameter(Mandatory = $true)][string]$WorkingDirectory,
    [string[]]$Arguments = @()
  )

  Push-Location $WorkingDirectory
  try {
    $output = & pwsh -NoProfile -ExecutionPolicy Bypass -File $FilePath @Arguments 2>&1
    $rc = $LASTEXITCODE
  }
  finally {
    Pop-Location
  }

  return [ordered]@{
    rc = [int]$rc
    output = @($output | ForEach-Object { [string]$_ })
    file = (Normalize-PathForReport -Path $FilePath)
    arguments = @($Arguments)
    working_directory = (Normalize-PathForReport -Path $WorkingDirectory)
  }
}

function Get-TrackingRunIdFromOutput {
  [CmdletBinding()]
  param([string[]]$Lines)

  foreach ($line in @($Lines)) {
    if ($line -match 'RUN_ID:\s*(.+)$') {
      return $matches[1].Trim()
    }
  }

  return ''
}

function Invoke-TrackingCapture {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)][string]$Label,
    [Parameter(Mandatory = $true)][string]$TrackingScript,
    [Parameter(Mandatory = $true)][string]$StartPath,
    [Parameter(Mandatory = $true)][string]$SharedRunsRoot
  )

  $result = Invoke-PwshFile -FilePath $TrackingScript -WorkingDirectory $StartPath -Arguments @('-Mode', 'CurrentRun', '-StartDir', $StartPath)
  $runId = Get-TrackingRunIdFromOutput -Lines $result.output
  $summaryPath = ''
  $summary = $null
  if (-not [string]::IsNullOrWhiteSpace($runId)) {
    $summaryPath = Join-Path (Join-Path $SharedRunsRoot $runId) 'RUN_SUMMARY.json'
    $summary = Read-JsonFileSafe -Path $summaryPath
  }
  else {
    $fallbackSummaryPath = Join-Path (Join-Path $SharedRunsRoot '__tracking_fallback__') 'RUN_SUMMARY.json'
    if (Test-Path -LiteralPath $fallbackSummaryPath -PathType Leaf) {
      $summaryPath = $fallbackSummaryPath
      $summary = Read-JsonFileSafe -Path $summaryPath
    }
  }

  $runDir = if ($null -ne $summary) { [string]$summary.run_dir } else { '' }

  return [ordered]@{
    label = $Label
    start_path = (Normalize-PathForReport -Path $StartPath)
    rc = [int]$result.rc
    run_id = $runId
    run_summary_path = (Normalize-PathForReport -Path $summaryPath)
    run_summary_repo_root = if ($null -ne $summary) { [string]$summary.repo_root } else { '' }
    run_summary_run_dir = $runDir
    run_summary_verdict = if ($null -ne $summary) { [string]$summary.verdict } else { '' }
    run_summary_issue_count = if ($null -ne $summary) { [int]$summary.issue_count } else { -1 }
    run_summary_issue_blocked_count = if ($null -ne $summary) { [int]$summary.issue_blocked_count } else { -1 }
    run_summary_issue_warn_count = if ($null -ne $summary) { [int]$summary.issue_warn_count } else { -1 }
    run_dir_is_canonical_shared = (Test-PathUnderRoot -Candidate $runDir -Root $SharedRunsRoot)
    command = $result
  }
}

function Parse-WorktreePathsFromPorcelain {
  [CmdletBinding()]
  param([string[]]$Lines)

  $paths = New-Object System.Collections.Generic.List[string]
  foreach ($line in @($Lines)) {
    if ($line.StartsWith('worktree ')) {
      $paths.Add((Convert-ToCanonicalPath -Path $line.Substring(9).Trim()))
    }
  }

  return @($paths.ToArray() | Sort-Object -Unique)
}

function Add-OutcomeAssessment {
  [CmdletBinding()]
  param(
    [string]$Phase,
    [int]$Rc,
    [switch]$AllowBlocked,
    [switch]$ExpectBlocked,
    [System.Collections.Generic.List[string]]$BlockedReasons,
    [System.Collections.Generic.List[string]]$UnexpectedFailures
  )

  if ($ExpectBlocked) {
    if ($Rc -ne 2) {
      $UnexpectedFailures.Add($Phase + ' expected rc=2 but got rc=' + $Rc)
    }
    return
  }

  if ($Rc -eq 0) {
    return
  }

  if ($Rc -eq 2) {
    if (-not $AllowBlocked) {
      $BlockedReasons.Add($Phase + ' returned rc=2 (unexpected governance block).')
    }
    return
  }

  $UnexpectedFailures.Add($Phase + ' returned rc=' + $Rc + ' (unexpected).')
}

if ([string]::IsNullOrWhiteSpace($StartDir)) {
  $StartDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
}

$repoRootOutput = & git -C $StartDir rev-parse --show-toplevel 2>&1
$repoRootLine = [string](@($repoRootOutput | ForEach-Object { [string]$_ }) | Select-Object -First 1)
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoRootLine)) {
  Write-Host ('FAIL: unable to resolve repository root from start dir: ' + $StartDir) -ForegroundColor Red
  exit 1
}

$repoRoot = Convert-ToCanonicalPath -Path $repoRootLine
$sharedRunsRootCanonical = Convert-ToCanonicalPath -Path $SharedRunsRoot
$trackingModulePath = Join-Path $repoRoot 'tools/codex/tracking/Tracking.psm1'
$ensureScript = Join-Path $repoRoot 'tools/scripts/Invoke-HitechRunsEnsure.ps1'
$doctorScript = Join-Path $repoRoot 'tools/scripts/Invoke-HitechRunsDoctor.ps1'
$trackingScript = Join-Path $repoRoot 'tools/codex/tracking/Invoke-HitechTracking.ps1'

foreach ($required in @($trackingModulePath, $ensureScript, $doctorScript, $trackingScript)) {
  if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
    Write-Host ('FAIL: missing required script/module: ' + $required) -ForegroundColor Red
    exit 1
  }
}

Import-Module $trackingModulePath -Force -DisableNameChecking

$blockedReasons = New-Object System.Collections.Generic.List[string]
$unexpectedFailures = New-Object System.Collections.Generic.List[string]
$notes = New-Object System.Collections.Generic.List[string]

$notes.Add('# Canonical Runs Validation Notes')
$notes.Add('')
$notes.Add('- repo_root: `' + (Normalize-PathForReport -Path $repoRoot) + '`')
$notes.Add('- shared_runs_root: `' + (Normalize-PathForReport -Path $sharedRunsRootCanonical) + '`')
$notes.Add('')

Write-Host 'Step 1/7: Discover worktrees and baseline pointers...' -ForegroundColor Cyan
$worktreePorcelain = & git -C $repoRoot worktree list --porcelain 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host 'FAIL: git worktree list --porcelain failed.' -ForegroundColor Red
  exit 1
}

$worktreePaths = Parse-WorktreePathsFromPorcelain -Lines @($worktreePorcelain | ForEach-Object { [string]$_ })
$normalizedWorktreePaths = @($worktreePaths | ForEach-Object { Normalize-PathForReport -Path $_ })
$repoRootNorm = Normalize-PathForReport -Path $repoRoot

if (-not ($normalizedWorktreePaths -contains $repoRootNorm)) {
  $normalizedWorktreePaths = @($repoRootNorm) + @($normalizedWorktreePaths)
}

$latestPointerPath = Join-Path $sharedRunsRootCanonical 'LATEST_RUN_ID.txt'
$latestPointerValue = ''
if (Test-Path -LiteralPath $latestPointerPath -PathType Leaf) {
  $latestPointerValue = [string](Get-Content -LiteralPath $latestPointerPath -TotalCount 1 -ErrorAction SilentlyContinue)
  if ($null -eq $latestPointerValue) { $latestPointerValue = '' }
  $latestPointerValue = $latestPointerValue.Trim()
}

Write-Host 'Step 2/7: Baseline Ensure + Doctor + Tracking from root/A/Z...' -ForegroundColor Cyan
$baselineEnsure = Invoke-PwshFile -FilePath $ensureScript -WorkingDirectory $repoRoot -Arguments @('--write', '-StartDir', $repoRoot)
$baselineDoctor = Invoke-PwshFile -FilePath $doctorScript -WorkingDirectory $repoRoot -Arguments @('-StartDir', $repoRoot)

Add-OutcomeAssessment -Phase 'baseline.ensure' -Rc $baselineEnsure.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
Add-OutcomeAssessment -Phase 'baseline.doctor' -Rc $baselineDoctor.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures

$driftScanPath = Join-Path $sharedRunsRootCanonical 'DRIFT_SCAN.json'
$repairReportPath = Join-Path $sharedRunsRootCanonical 'REPAIR_REPORT.json'
$baselineDriftScan = Read-JsonFileSafe -Path $driftScanPath
$baselineRepairReport = Read-JsonFileSafe -Path $repairReportPath

if ($null -eq $baselineDriftScan) {
  $unexpectedFailures.Add('baseline doctor did not produce readable DRIFT_SCAN.json at canonical shared root.')
}

$worktreeA = @($normalizedWorktreePaths | Where-Object { $_.EndsWith('/HITECHOS__A_core', [System.StringComparison]::OrdinalIgnoreCase) } | Select-Object -First 1)
$worktreeZ = @($normalizedWorktreePaths | Where-Object { $_.EndsWith('/HITECHOS__Z_aggregator', [System.StringComparison]::OrdinalIgnoreCase) } | Select-Object -First 1)

$trackingTargets = New-Object System.Collections.Generic.List[object]
$trackingTargets.Add([ordered]@{ label = 'root'; path = $repoRootNorm })
if (@($worktreeA).Count -gt 0) { $trackingTargets.Add([ordered]@{ label = 'A_core'; path = $worktreeA[0] }) }
if (@($worktreeZ).Count -gt 0) { $trackingTargets.Add([ordered]@{ label = 'Z_aggregator'; path = $worktreeZ[0] }) }

if (@($trackingTargets.ToArray()).Count -lt 3) {
  foreach ($p in @($normalizedWorktreePaths | Where-Object { $_ -ne $repoRootNorm })) {
    if (@($trackingTargets.ToArray() | Where-Object { $_.path -eq $p }).Count -eq 0) {
      $trackingTargets.Add([ordered]@{ label = ('worktree_' + @($trackingTargets.ToArray()).Count); path = $p })
    }
    if (@($trackingTargets.ToArray()).Count -ge 3) { break }
  }
}

$baselineTracking = New-Object System.Collections.Generic.List[object]
foreach ($target in @($trackingTargets.ToArray())) {
  $capture = Invoke-TrackingCapture -Label $target.label -TrackingScript $trackingScript -StartPath $target.path -SharedRunsRoot $sharedRunsRootCanonical
  $baselineTracking.Add($capture)
  Add-OutcomeAssessment -Phase ('baseline.tracking.' + $target.label) -Rc ([int]$capture.rc) -AllowBlocked -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
}

$canonicalRunDirFailures = @($baselineTracking.ToArray() | Where-Object { -not $_.run_dir_is_canonical_shared })
if (@($canonicalRunDirFailures).Count -gt 0) {
  $unexpectedFailures.Add('baseline tracking emitted non-canonical run_dir outside shared runs root.')
}

$evidenceRunId = ''
foreach ($item in @($baselineTracking.ToArray())) {
  if (-not [string]::IsNullOrWhiteSpace([string]$item.run_id)) {
    $evidenceRunId = [string]$item.run_id
    break
  }
}
if ([string]::IsNullOrWhiteSpace($evidenceRunId)) {
  if (-not [string]::IsNullOrWhiteSpace($latestPointerValue)) {
    $evidenceRunId = $latestPointerValue
  }
  else {
    $evidenceRunId = 'CANONICAL_VALIDATION'
  }
}

$evidenceDir = Join-Path (Join-Path $sharedRunsRootCanonical $evidenceRunId) 'evidence'
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null

$worktreePorcelainText = (@($worktreePorcelain | ForEach-Object { [string]$_ }) -join "`n")
Write-DeterministicTextFile -Path (Join-Path $evidenceDir 'worktree_list.porcelain.txt') -Content $worktreePorcelainText

if ($null -ne $baselineDriftScan) {
  $nonCanonicalStatuses = @($baselineDriftScan.runs_root_status | Where-Object { -not [bool]$_.is_canonical })
  $duplicateLatest = @($baselineDriftScan.latest_markers.duplicate_elsewhere | Where-Object { $null -ne $_ })
  if (@($nonCanonicalStatuses).Count -gt 0) {
    $blockedReasons.Add('STOP_CONDITION: multiple run universes/non-canonical runs roots detected by baseline doctor.')
  }
  if (@($duplicateLatest).Count -gt 0) {
    $blockedReasons.Add('STOP_CONDITION: duplicate LATEST_RUN_ID pointers detected outside canonical roots.')
  }
}

Write-Host 'Step 3/7: Ensure idempotency stress from three worktrees...' -ForegroundColor Cyan
$stressCandidates = New-Object System.Collections.Generic.List[string]
$stressCandidates.Add($repoRootNorm)
if (@($worktreeA).Count -gt 0) { $stressCandidates.Add($worktreeA[0]) }
if (@($worktreeZ).Count -gt 0) { $stressCandidates.Add($worktreeZ[0]) }
foreach ($p in @($normalizedWorktreePaths)) {
  if (@($stressCandidates.ToArray() | Where-Object { $_ -eq $p }).Count -eq 0) {
    $stressCandidates.Add($p)
  }
  if (@($stressCandidates.ToArray()).Count -ge 3) { break }
}

$stressWorktrees = @($stressCandidates.ToArray() | Select-Object -First 3)
if (@($stressWorktrees).Count -lt 3) {
  $unexpectedFailures.Add('idempotency stress requires three worktrees but fewer were available.')
}

$idempotencyRuns = New-Object System.Collections.Generic.List[object]
foreach ($path in $stressWorktrees) {
  $ensureRes = Invoke-PwshFile -FilePath $ensureScript -WorkingDirectory $path -Arguments @('--write', '-StartDir', $path)
  Add-OutcomeAssessment -Phase ('idempotency.ensure.' + (Normalize-PathForReport -Path $path)) -Rc $ensureRes.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures

  $repairHash = ''
  if (Test-Path -LiteralPath $repairReportPath -PathType Leaf) {
    $repairHash = (Get-FileHash -LiteralPath $repairReportPath -Algorithm SHA256).Hash
  }

  $driftHash = ''
  if (Test-Path -LiteralPath $driftScanPath -PathType Leaf) {
    $driftHash = (Get-FileHash -LiteralPath $driftScanPath -Algorithm SHA256).Hash
  }

  $idempotencyRuns.Add([ordered]@{
    start_path = (Normalize-PathForReport -Path $path)
    rc = [int]$ensureRes.rc
    repair_report_sha256 = $repairHash
    drift_scan_sha256 = $driftHash
    command = $ensureRes
  })
}

$idempotencyDoctor = Invoke-PwshFile -FilePath $doctorScript -WorkingDirectory $repoRoot -Arguments @('-StartDir', $repoRoot)
Add-OutcomeAssessment -Phase 'idempotency.doctor' -Rc $idempotencyDoctor.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
$idempotencyDrift = Read-JsonFileSafe -Path $driftScanPath

if (@($idempotencyRuns.ToArray()).Count -ge 3) {
  $hashes = @($idempotencyRuns.ToArray() | ForEach-Object { [string]$_.repair_report_sha256 } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  if (@($hashes).Count -ge 2) {
    $first = $hashes[0]
    $different = @($hashes | Where-Object { $_ -ne $first })
    if (@($different).Count -gt 0) {
      $unexpectedFailures.Add('idempotency stress detected REPAIR_REPORT hash drift across repeated ensure runs.')
    }
  }
}

if ($null -ne $idempotencyDrift) {
  $duplicates = @($idempotencyDrift.latest_markers.duplicate_elsewhere | Where-Object { $null -ne $_ })
  if (@($duplicates).Count -gt 0) {
    $blockedReasons.Add('STOP_CONDITION: duplicate LATEST_RUN_ID pointers detected after idempotency stress.')
  }
}

Write-Host 'Step 4/7: New worktree drift guard test...' -ForegroundColor Cyan
$newWorktree = [ordered]@{
  temp_worktree_path = (Normalize-PathForReport -Path $TempWorktreePath)
  add = $null
  ensure = $null
  doctor = $null
  tracking = $null
  remove = $null
  post_remove_ensure = $null
  post_remove_doctor = $null
}

if (Test-Path -LiteralPath $TempWorktreePath) {
  & git -C $repoRoot worktree remove --force $TempWorktreePath 2>$null | Out-Null
  if (Test-Path -LiteralPath $TempWorktreePath) {
    Remove-Item -LiteralPath $TempWorktreePath -Recurse -Force
  }
}

$addOutput = & git -C $repoRoot worktree add --detach $TempWorktreePath HEAD 2>&1
$addRc = $LASTEXITCODE
$newWorktree.add = [ordered]@{
  rc = [int]$addRc
  output = @($addOutput | ForEach-Object { [string]$_ })
}
if ($addRc -ne 0) {
  $unexpectedFailures.Add('new worktree add failed.')
}

if ($addRc -eq 0) {
  $newWorktree.ensure = Invoke-PwshFile -FilePath $ensureScript -WorkingDirectory $TempWorktreePath -Arguments @('--write', '-StartDir', $TempWorktreePath)
  $newWorktree.doctor = Invoke-PwshFile -FilePath $doctorScript -WorkingDirectory $TempWorktreePath -Arguments @('-StartDir', $TempWorktreePath)
  $newWorktree.tracking = Invoke-TrackingCapture -Label 'E_temp' -TrackingScript $trackingScript -StartPath $TempWorktreePath -SharedRunsRoot $sharedRunsRootCanonical

  Add-OutcomeAssessment -Phase 'new_worktree.ensure' -Rc $newWorktree.ensure.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
  Add-OutcomeAssessment -Phase 'new_worktree.doctor' -Rc $newWorktree.doctor.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
  Add-OutcomeAssessment -Phase 'new_worktree.tracking' -Rc $newWorktree.tracking.rc -AllowBlocked -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures

  if (-not [bool]$newWorktree.tracking.run_dir_is_canonical_shared) {
    $unexpectedFailures.Add('new worktree tracking emitted non-canonical run_dir.')
  }

  $removeOutput = & git -C $repoRoot worktree remove --force $TempWorktreePath 2>&1
  $removeRc = $LASTEXITCODE
  $newWorktree.remove = [ordered]@{
    rc = [int]$removeRc
    output = @($removeOutput | ForEach-Object { [string]$_ })
  }
  if ($removeRc -ne 0) {
    $unexpectedFailures.Add('new worktree remove failed.')
  }

  if (Test-Path -LiteralPath $TempWorktreePath) {
    Remove-Item -LiteralPath $TempWorktreePath -Recurse -Force
  }

  $newWorktree.post_remove_ensure = Invoke-PwshFile -FilePath $ensureScript -WorkingDirectory $repoRoot -Arguments @('--write', '-StartDir', $repoRoot)
  $newWorktree.post_remove_doctor = Invoke-PwshFile -FilePath $doctorScript -WorkingDirectory $repoRoot -Arguments @('-StartDir', $repoRoot)
  Add-OutcomeAssessment -Phase 'new_worktree.post_remove_ensure' -Rc $newWorktree.post_remove_ensure.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
  Add-OutcomeAssessment -Phase 'new_worktree.post_remove_doctor' -Rc $newWorktree.post_remove_doctor.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
}

Write-Host 'Step 5/7: Negative broken-junction governance block test...' -ForegroundColor Cyan
$negativeTest = [ordered]@{
  runs_path = (Normalize-PathForReport -Path (Join-Path $repoRoot 'tools/codex/runs'))
  original_target = ''
  broken_target = ''
  doctor = $null
  tracking = $null
  restored = $false
  recovery_ensure = $null
  recovery_doctor = $null
}

$runsPathNative = Join-Path $repoRoot 'tools/codex/runs'
$originalTarget = Get-TrackingJunctionTargetPath -Path $runsPathNative
if ([string]::IsNullOrWhiteSpace($originalTarget)) {
  $originalTarget = $sharedRunsRootCanonical
}
$negativeTest.original_target = Normalize-PathForReport -Path $originalTarget

$brokenTargetNative = Join-Path $repoRoot '.tmp\validate_canonical_runs\broken_runs_target'
$negativeTest.broken_target = Normalize-PathForReport -Path $brokenTargetNative

try {
  if (Test-Path -LiteralPath $brokenTargetNative) {
    Remove-Item -LiteralPath $brokenTargetNative -Recurse -Force
  }
  New-Item -ItemType Directory -Path $brokenTargetNative -Force | Out-Null

  if (Test-Path -LiteralPath $runsPathNative) {
    Remove-Item -LiteralPath $runsPathNative -Force
  }
  New-Item -ItemType Junction -Path $runsPathNative -Target $brokenTargetNative | Out-Null
  Remove-Item -LiteralPath $brokenTargetNative -Recurse -Force

  $negativeTest.doctor = Invoke-PwshFile -FilePath $doctorScript -WorkingDirectory $repoRoot -Arguments @('-StartDir', $repoRoot)
  $negativeTest.tracking = Invoke-PwshFile -FilePath $trackingScript -WorkingDirectory $repoRoot -Arguments @('-Mode', 'CurrentRun', '-StartDir', $repoRoot)

  Add-OutcomeAssessment -Phase 'negative_test.doctor' -Rc $negativeTest.doctor.rc -ExpectBlocked -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
  Add-OutcomeAssessment -Phase 'negative_test.tracking' -Rc $negativeTest.tracking.rc -ExpectBlocked -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
}
finally {
  try {
    if (Test-Path -LiteralPath $runsPathNative) {
      Remove-Item -LiteralPath $runsPathNative -Force
    }
    if (-not (Test-Path -LiteralPath $originalTarget -PathType Container)) {
      New-Item -ItemType Directory -Path $originalTarget -Force | Out-Null
    }
    New-Item -ItemType Junction -Path $runsPathNative -Target $originalTarget | Out-Null
    $negativeTest.restored = $true
  }
  catch {
    $unexpectedFailures.Add('negative test restoration failed: ' + $_.Exception.Message)
  }
}

$negativeTest.recovery_ensure = Invoke-PwshFile -FilePath $ensureScript -WorkingDirectory $repoRoot -Arguments @('--write', '-StartDir', $repoRoot)
$negativeTest.recovery_doctor = Invoke-PwshFile -FilePath $doctorScript -WorkingDirectory $repoRoot -Arguments @('-StartDir', $repoRoot)
Add-OutcomeAssessment -Phase 'negative_test.recovery_ensure' -Rc $negativeTest.recovery_ensure.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures
Add-OutcomeAssessment -Phase 'negative_test.recovery_doctor' -Rc $negativeTest.recovery_doctor.rc -BlockedReasons $blockedReasons -UnexpectedFailures $unexpectedFailures

Write-Host 'Step 6/7: Build evidence summaries...' -ForegroundColor Cyan
$finalDrift = Read-JsonFileSafe -Path $driftScanPath
$finalRepair = Read-JsonFileSafe -Path $repairReportPath

$ensureSummary = [ordered]@{
  schema = 'hitech.validation.ensure_runs_root.v1'
  repo_root = $repoRootNorm
  shared_runs_root = (Normalize-PathForReport -Path $sharedRunsRootCanonical)
  baseline = [ordered]@{
    rc = [int]$baselineEnsure.rc
    command = $baselineEnsure
  }
  idempotency = [ordered]@{
    worktrees = @($stressWorktrees | ForEach-Object { Normalize-PathForReport -Path $_ })
    runs = @($idempotencyRuns.ToArray())
  }
  new_worktree = [ordered]@{
    ensure_rc = if ($null -ne $newWorktree.ensure) { [int]$newWorktree.ensure.rc } else { -1 }
    post_remove_ensure_rc = if ($null -ne $newWorktree.post_remove_ensure) { [int]$newWorktree.post_remove_ensure.rc } else { -1 }
  }
  recovery = [ordered]@{
    ensure_rc = [int]$negativeTest.recovery_ensure.rc
  }
  final_repair_report = $finalRepair
}

$doctorSummary = [ordered]@{
  schema = 'hitech.validation.doctor_summary.v1'
  repo_root = $repoRootNorm
  shared_runs_root = (Normalize-PathForReport -Path $sharedRunsRootCanonical)
  baseline = [ordered]@{
    rc = [int]$baselineDoctor.rc
    drift_scan = $baselineDriftScan
    repair_report = $baselineRepairReport
    command = $baselineDoctor
  }
  idempotency = [ordered]@{
    rc = [int]$idempotencyDoctor.rc
    drift_scan = $idempotencyDrift
    command = $idempotencyDoctor
  }
  new_worktree = [ordered]@{
    rc = if ($null -ne $newWorktree.doctor) { [int]$newWorktree.doctor.rc } else { -1 }
    command = $newWorktree.doctor
  }
  recovery = [ordered]@{
    rc = [int]$negativeTest.recovery_doctor.rc
    command = $negativeTest.recovery_doctor
    drift_scan = $finalDrift
  }
}

$trackingSummary = [ordered]@{
  schema = 'hitech.validation.tracking_summary.v1'
  repo_root = $repoRootNorm
  shared_runs_root = (Normalize-PathForReport -Path $sharedRunsRootCanonical)
  baseline = @($baselineTracking.ToArray())
  new_worktree = if ($null -ne $newWorktree.tracking) { $newWorktree.tracking } else { $null }
  canonical_checks = [ordered]@{
    baseline_all_canonical = (@($baselineTracking.ToArray() | Where-Object { -not $_.run_dir_is_canonical_shared }).Count -eq 0)
    new_worktree_canonical = if ($null -ne $newWorktree.tracking) { [bool]$newWorktree.tracking.run_dir_is_canonical_shared } else { $false }
  }
}

$negativeSummary = [ordered]@{
  schema = 'hitech.validation.negative_test_broken_junction.v1'
  repo_root = $repoRootNorm
  shared_runs_root = (Normalize-PathForReport -Path $sharedRunsRootCanonical)
  runs_path = $negativeTest.runs_path
  original_target = $negativeTest.original_target
  broken_target = $negativeTest.broken_target
  doctor = $negativeTest.doctor
  tracking = $negativeTest.tracking
  expected = [ordered]@{
    doctor_rc = 2
    tracking_rc = 2
  }
  observed = [ordered]@{
    doctor_rc = if ($null -ne $negativeTest.doctor) { [int]$negativeTest.doctor.rc } else { -1 }
    tracking_rc = if ($null -ne $negativeTest.tracking) { [int]$negativeTest.tracking.rc } else { -1 }
  }
  restored = [bool]$negativeTest.restored
  recovery = [ordered]@{
    ensure_rc = [int]$negativeTest.recovery_ensure.rc
    doctor_rc = [int]$negativeTest.recovery_doctor.rc
  }
}

$notes.Add('## Commands')
$notes.Add('')
$notes.Add('- `pwsh -NoProfile -ExecutionPolicy Bypass -File "' + (Normalize-PathForReport -Path $ensureScript) + '" --write -StartDir "' + $repoRootNorm + '"`')
$notes.Add('- `pwsh -NoProfile -ExecutionPolicy Bypass -File "' + (Normalize-PathForReport -Path $doctorScript) + '" -StartDir "<worktree>"`')
$notes.Add('- `pwsh -NoProfile -ExecutionPolicy Bypass -File "' + (Normalize-PathForReport -Path $trackingScript) + '" -Mode CurrentRun -StartDir "<worktree>"`')
$notes.Add('- `git -C "' + $repoRootNorm + '" worktree add --detach "' + (Normalize-PathForReport -Path $TempWorktreePath) + '" HEAD`')
$notes.Add('- `git -C "' + $repoRootNorm + '" worktree remove --force "' + (Normalize-PathForReport -Path $TempWorktreePath) + '"`')
$notes.Add('')
$notes.Add('## Results')
$notes.Add('')
$notes.Add('- baseline_tracking_count: ' + @($baselineTracking.ToArray()).Count)
$notes.Add('- baseline_tracking_all_run_dir_canonical: ' + (@($baselineTracking.ToArray() | Where-Object { -not $_.run_dir_is_canonical_shared }).Count -eq 0))
$notes.Add('- idempotency_runs: ' + @($idempotencyRuns.ToArray()).Count)
$negativeDoctorRcText = '-1'
if ($null -ne $negativeTest.doctor) {
  $negativeDoctorRcText = [string]$negativeTest.doctor.rc
}
$negativeTrackingRcText = '-1'
if ($null -ne $negativeTest.tracking) {
  $negativeTrackingRcText = [string]$negativeTest.tracking.rc
}
$notes.Add('- negative_test_expected_blocked: doctor_rc=' + $negativeDoctorRcText + ', tracking_rc=' + $negativeTrackingRcText)
$notes.Add('- recovery_doctor_rc: ' + [string]$negativeTest.recovery_doctor.rc)
$notes.Add('')
$notes.Add('## Evidence')
$notes.Add('')
$notes.Add('- evidence_dir: `' + (Normalize-PathForReport -Path $evidenceDir) + '`')
$notes.Add('- ensure_runs_root.json: `' + (Normalize-PathForReport -Path (Join-Path $evidenceDir 'ensure_runs_root.json')) + '`')
$notes.Add('- doctor_summary.json: `' + (Normalize-PathForReport -Path (Join-Path $evidenceDir 'doctor_summary.json')) + '`')
$notes.Add('- tracking_summary.json: `' + (Normalize-PathForReport -Path (Join-Path $evidenceDir 'tracking_summary.json')) + '`')
$notes.Add('- negative_test_broken_junction.json: `' + (Normalize-PathForReport -Path (Join-Path $evidenceDir 'negative_test_broken_junction.json')) + '`')

Write-DeterministicJsonFile -Path (Join-Path $evidenceDir 'ensure_runs_root.json') -Object $ensureSummary
Write-DeterministicJsonFile -Path (Join-Path $evidenceDir 'doctor_summary.json') -Object $doctorSummary
Write-DeterministicJsonFile -Path (Join-Path $evidenceDir 'tracking_summary.json') -Object $trackingSummary
Write-DeterministicJsonFile -Path (Join-Path $evidenceDir 'negative_test_broken_junction.json') -Object $negativeSummary
Write-DeterministicTextFile -Path (Join-Path $evidenceDir 'worktree_list.porcelain.txt') -Content $worktreePorcelainText
Write-DeterministicTextFile -Path (Join-Path $evidenceDir 'notes.md') -Content ($notes -join "`n")

Write-Host 'Step 7/7: Final evaluation...' -ForegroundColor Cyan
$finalResult = [ordered]@{
  schema = 'hitech.validation.canonical_runs.result.v1'
  repo_root = $repoRootNorm
  shared_runs_root = (Normalize-PathForReport -Path $sharedRunsRootCanonical)
  evidence_dir = (Normalize-PathForReport -Path $evidenceDir)
  blocked_reasons = @($blockedReasons.ToArray())
  unexpected_failures = @($unexpectedFailures.ToArray())
}
Write-DeterministicJsonFile -Path (Join-Path $evidenceDir 'validation_result.json') -Object $finalResult

if (@($blockedReasons.ToArray()).Count -gt 0) {
  Write-Host 'VALIDATION RESULT: BLOCKED' -ForegroundColor Yellow
  Write-Host ('Evidence: ' + (Normalize-PathForReport -Path $evidenceDir))
  exit 2
}

if (@($unexpectedFailures.ToArray()).Count -gt 0) {
  Write-Host 'VALIDATION RESULT: FAIL' -ForegroundColor Red
  Write-Host ('Evidence: ' + (Normalize-PathForReport -Path $evidenceDir))
  exit 1
}

Write-Host 'VALIDATION RESULT: OK' -ForegroundColor Green
Write-Host ('Evidence: ' + (Normalize-PathForReport -Path $evidenceDir))
exit 0
