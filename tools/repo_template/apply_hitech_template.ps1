[CmdletBinding()]
param(
    [string]$TemplateRoot,
    [string]$ReposRoot,
    [switch]$SkipCommit,
    [switch]$SkipPush
)

$ErrorActionPreference = "Stop"

$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:HostRepoRoot = (Resolve-Path (Join-Path $script:ScriptDir "..\\..")).Path
if (-not $ReposRoot) {
    $ReposRoot = (Resolve-Path (Join-Path $script:HostRepoRoot "..")).Path
}

$script:OverlayEngine = Join-Path $script:ScriptDir "overlay_engine.py"
$script:BlockedReportPath = Join-Path $script:ScriptDir "BLOCKED_REPORT.json"
$script:CommitMessage = "chore: apply Hitech enterprise repo template overlay"
$script:ProgressActivity = "Hitech Template Overlay"

function Write-BlockedReport {
    param(
        [string]$Reason,
        [string[]]$Details
    )

    $payload = [ordered]@{
        blocked   = $true
        reason    = $Reason
        details   = $Details
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -Path $script:BlockedReportPath -Encoding UTF8
    Write-Error "$Reason`n$($Details -join [Environment]::NewLine)"
}

function Write-StepProgress {
    param(
        [int]$Step,
        [int]$Total,
        [string]$Status
    )

    $percent = [int](($Step / $Total) * 100)
    Write-Progress -Activity $script:ProgressActivity -Status $Status -PercentComplete $percent
}

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @($python.Source)
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return @($pyLauncher.Source, "-3")
    }

    throw "Python runtime not found (`python` or `py -3`)."
}

function Invoke-Python {
    param(
        [string[]]$PythonCommand,
        [string]$ScriptPath,
        [string[]]$Arguments
    )

    $output = if ($PythonCommand.Count -eq 1) {
        & $PythonCommand[0] $ScriptPath @Arguments
    }
    else {
        & $PythonCommand[0] $PythonCommand[1] $ScriptPath @Arguments
    }
    $script:LastPythonExitCode = $LASTEXITCODE
    return @($output)
}

function Resolve-NestedTemplateFolder {
    param([string]$RootPath)

    $root = (Resolve-Path $RootPath).Path
    foreach ($candidateName in @("template", "repo-template", "repository-template")) {
        $candidate = Join-Path $root $candidateName
        if (Test-Path -Path $candidate -PathType Container) {
            return (Resolve-Path $candidate).Path
        }
    }

    $dirs = Get-ChildItem -Path $root -Directory -Force | Where-Object { $_.Name -ne ".git" }
    $files = Get-ChildItem -Path $root -File -Force | Where-Object { $_.Name -ne ".gitkeep" }
    if ($dirs.Count -eq 1 -and $files.Count -eq 0) {
        return $dirs[0].FullName
    }

    return $root
}

function Resolve-TemplateRoot {
    param([string]$UserTemplateRoot)

    $candidates = @()
    if ($UserTemplateRoot) {
        $candidates += $UserTemplateRoot
    }
    if ($env:HITECH_TEMPLATE_ROOT) {
        $candidates += $env:HITECH_TEMPLATE_ROOT
    }
    $candidates += (Join-Path $ReposRoot "hitech-enterprise-repo-template")

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not $candidate) {
            continue
        }
        if (Test-Path -Path $candidate -PathType Container) {
            return Resolve-NestedTemplateFolder -RootPath $candidate
        }
    }

    throw "Template root not found. Tried: $($candidates -join ', ')"
}

function Ensure-GitRepoOrBlock {
    param([string]$RepoPath)
    if (-not (Test-Path -Path $RepoPath -PathType Container)) {
        Write-BlockedReport -Reason "Repository path missing." -Details @($RepoPath)
    }
    if (-not (Test-Path -Path (Join-Path $RepoPath ".git"))) {
        Write-BlockedReport -Reason "Invalid git repository." -Details @($RepoPath)
    }
}

function Ensure-OverlayBranchIfDirty {
    param([string]$RepoPath)

    $status = (git -C $RepoPath status --porcelain)
    $currentBranchRaw = git -C $RepoPath rev-parse --abbrev-ref HEAD
    $currentBranch = if ($currentBranchRaw) { ($currentBranchRaw | Out-String).Trim() } else { "HEAD" }
    if ([string]::IsNullOrWhiteSpace(($status -join ""))) {
        return $currentBranch
    }

    $overlayBranch = "chore/template-overlay-{0}" -f (Get-Date -Format "yyyyMMdd")
    if ($currentBranch -eq $overlayBranch) {
        return $currentBranch
    }

    $branchExistsRaw = git -C $RepoPath branch --list $overlayBranch
    $branchExists = if ($branchExistsRaw) { ($branchExistsRaw | Out-String).Trim() } else { "" }
    if ($branchExists) {
        git -C $RepoPath checkout $overlayBranch | Out-Null
    }
    else {
        git -C $RepoPath checkout -b $overlayBranch | Out-Null
    }

    return $overlayBranch
}

function Commit-OverlayChanges {
    param(
        [string]$RepoPath,
        [string]$ReportPath
    )

    if ($SkipCommit) {
        return
    }

    $report = Get-Content -Path $ReportPath -Raw | ConvertFrom-Json
    $filesAdded = @($report.files_added)
    foreach ($relativePath in $filesAdded) {
        git -C $RepoPath add -- $relativePath
    }

    $staged = (git -C $RepoPath diff --cached --name-only)
    if ([string]::IsNullOrWhiteSpace(($staged -join ""))) {
        return
    }

    git -C $RepoPath commit -m $script:CommitMessage | Out-Null
}

function Push-IfOriginExists {
    param([string]$RepoPath)

    if ($SkipPush) {
        return
    }

    $originUrl = ""
    try {
        $originUrl = (git -C $RepoPath remote get-url origin 2>$null).Trim()
    }
    catch {
        $originUrl = ""
    }

    if ([string]::IsNullOrWhiteSpace($originUrl)) {
        return
    }

    $branch = (git -C $RepoPath rev-parse --abbrev-ref HEAD).Trim()
    try {
        git -C $RepoPath push --set-upstream origin $branch | Out-Null
    }
    catch {
        Write-Warning "Push failed for $RepoPath on branch ${branch}: $($_.Exception.Message)"
    }
}

function Resolve-LatestReportPath {
    param(
        [string]$RepoPath,
        [string]$ReportDir,
        [object[]]$CommandOutput
    )

    $line = (
        $CommandOutput |
        Where-Object { $_ -and $_.ToString().Trim() -ne "" } |
        Select-Object -Last 1
    )
    if ($line) {
        return $line.ToString().Trim()
    }

    $repoName = (Split-Path -Leaf $RepoPath).ToLower()
    $candidate = Get-ChildItem -Path $ReportDir -File -Filter "*_${repoName}.json" |
        Sort-Object LastWriteTimeUtc |
        Select-Object -Last 1
    if ($candidate) {
        return $candidate.FullName
    }

    return ""
}

try {
    Write-StepProgress -Step 1 -Total 7 -Status "Detecting template root"
    $resolvedTemplateRoot = Resolve-TemplateRoot -UserTemplateRoot $TemplateRoot
    if (-not (Test-Path -Path $script:OverlayEngine -PathType Leaf)) {
        Write-BlockedReport -Reason "Overlay engine not found." -Details @($script:OverlayEngine)
    }

    Write-StepProgress -Step 2 -Total 7 -Status "Scanning target repositories"
    $targetRepos = @(
        (Join-Path $ReposRoot "hitech-os"),
        (Join-Path $ReposRoot "hitech-forms")
    )

    foreach ($repo in $targetRepos) {
        Ensure-GitRepoOrBlock -RepoPath $repo
    }

    $pythonCommand = Get-PythonCommand

    Write-StepProgress -Step 3 -Total 7 -Status "Running dry-run overlay"
    $runLedger = @()
    foreach ($repo in $targetRepos) {
        $repoName = Split-Path -Leaf $repo
        Write-Progress -Activity $script:ProgressActivity -Status "Dry-run $repoName" -PercentComplete 42

        $reportDir = Join-Path $repo "tools\\repo_template\\reports"
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        $args = @(
            "--template", $resolvedTemplateRoot,
            "--repo", $repo,
            "--report-dir", $reportDir,
            "--dry-run"
        )
        $dryRunOutput = Invoke-Python -PythonCommand $pythonCommand -ScriptPath $script:OverlayEngine -Arguments $args
        if ($script:LastPythonExitCode -ne 0) {
            Write-BlockedReport -Reason "Dry-run overlay failed." -Details @($repo)
        }
        $dryRunReport = Resolve-LatestReportPath -RepoPath $repo -ReportDir $reportDir -CommandOutput $dryRunOutput
        if ([string]::IsNullOrWhiteSpace($dryRunReport)) {
            Write-BlockedReport -Reason "Dry-run report not found." -Details @($repo)
        }
        $runLedger += [pscustomobject]@{
            Repo         = $repo
            DryRunReport = $dryRunReport
            ApplyReport  = ""
        }
    }

    Write-StepProgress -Step 4 -Total 7 -Status "Applying overlay"
    foreach ($entry in $runLedger) {
        $repoName = Split-Path -Leaf $entry.Repo
        Write-Progress -Activity $script:ProgressActivity -Status "Apply overlay $repoName" -PercentComplete 57

        $args = @(
            "--template", $resolvedTemplateRoot,
            "--repo", $entry.Repo,
            "--report-dir", (Join-Path $entry.Repo "tools\\repo_template\\reports")
        )
        $applyOutput = Invoke-Python -PythonCommand $pythonCommand -ScriptPath $script:OverlayEngine -Arguments $args
        if ($script:LastPythonExitCode -ne 0) {
            Write-BlockedReport -Reason "Overlay apply failed." -Details @($entry.Repo)
        }
        $entry.ApplyReport = Resolve-LatestReportPath -RepoPath $entry.Repo -ReportDir (Join-Path $entry.Repo "tools\\repo_template\\reports") -CommandOutput $applyOutput
        if ([string]::IsNullOrWhiteSpace($entry.ApplyReport)) {
            Write-BlockedReport -Reason "Apply report not found." -Details @($entry.Repo)
        }
    }

    Write-StepProgress -Step 5 -Total 7 -Status "Reports created"
    Start-Sleep -Milliseconds 150

    Write-StepProgress -Step 6 -Total 7 -Status "Committing changes"
    foreach ($entry in $runLedger) {
        $repoName = Split-Path -Leaf $entry.Repo
        Write-Progress -Activity $script:ProgressActivity -Status "Commit $repoName" -PercentComplete 85

        $null = Ensure-OverlayBranchIfDirty -RepoPath $entry.Repo
        Commit-OverlayChanges -RepoPath $entry.Repo -ReportPath $entry.ApplyReport
    }

    Write-StepProgress -Step 7 -Total 7 -Status "Pushing branches (if origin exists)"
    foreach ($entry in $runLedger) {
        $repoName = Split-Path -Leaf $entry.Repo
        Write-Progress -Activity $script:ProgressActivity -Status "Push $repoName" -PercentComplete 95
        Push-IfOriginExists -RepoPath $entry.Repo
    }

    Write-Progress -Activity $script:ProgressActivity -Completed -Status "Completed"
    $runLedger | Format-Table -AutoSize
}
catch {
    $details = @(
        $_.Exception.Message,
        $_.InvocationInfo.PositionMessage,
        $_.ScriptStackTrace
    ) | Where-Object { $_ -and $_.ToString().Trim() -ne "" }
    Write-BlockedReport -Reason "Template overlay process aborted." -Details $details
    exit 1
}
