[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RunId,

    [string]$PromptsPackPath,

    [switch]$SkipInitialDispatch,

    [Nullable[int]]$WindowReadyTimeout,
    [Nullable[int]]$ReadinessTimeout,
    [Nullable[int]]$WorkerDoneTimeout,
    [Nullable[int]]$BetweenWorkersDelayMs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:StageResults = New-Object System.Collections.Generic.List[object]
$script:BufferedLogs = New-Object System.Collections.Generic.List[string]
$script:RunLogPath = $null

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$CodexDir = Join-Path $RepoRoot "tools/codex"
$PromptsRoot = Join-Path $CodexDir "prompts"
$DocWorkers = @("A_core", "B_tooling", "C_features", "D_validation")
$AggregatorWorkers = @("Z_aggregator")
$Workers = @($DocWorkers + $AggregatorWorkers)
$WorkersCsv = [string]::Join(",", $Workers)
$DocWorkersCsv = [string]::Join(",", $DocWorkers)
$AggregatorWorkersCsv = [string]::Join(",", $AggregatorWorkers)

$PromptsDir = $null
$LogsDir = $null
$ReportPath = $null

$finalVerdict = "PASS"
$fatalMessage = ""
$RunDir = $null
$DebugDir = $null
$RunManifestPath = $null
$DispatchHeartbeatStaleSeconds = 15
$DispatchHeartbeatPath = $null
$DispatchTimeoutReportPath = $null
$SubprocessHelperPath = Join-Path $CodexDir "shared\subprocessx.py"
$RunsRootDoctorScriptPath = Join-Path $RepoRoot "tools\scripts\Invoke-HitechRunsDoctor.ps1"
$RunsRootEnsureScriptPath = Join-Path $RepoRoot "tools\scripts\Invoke-HitechRunsEnsure.ps1"
$RunsRootAutoEnsureRaw = [string]([Environment]::GetEnvironmentVariable("FACTORY_RUNS_ROOT_AUTO_ENSURE", "Process"))
if ([string]::IsNullOrWhiteSpace($RunsRootAutoEnsureRaw)) {
    $RunsRootAutoEnsureRaw = [string]([Environment]::GetEnvironmentVariable("FACTORY_RUNS_ROOT_AUTO_ENSURE", "User"))
}
if ([string]::IsNullOrWhiteSpace($RunsRootAutoEnsureRaw)) {
    $RunsRootAutoEnsureRaw = [string]([Environment]::GetEnvironmentVariable("FACTORY_RUNS_ROOT_AUTO_ENSURE", "Machine"))
}
$RunsRootAutoEnsure = @("1", "true", "yes", "on") -contains $RunsRootAutoEnsureRaw.Trim().ToLowerInvariant()
$RunsRootEnsureForceRaw = [string]([Environment]::GetEnvironmentVariable("FACTORY_RUNS_ROOT_ENSURE_FORCE", "Process"))
if ([string]::IsNullOrWhiteSpace($RunsRootEnsureForceRaw)) {
    $RunsRootEnsureForceRaw = [string]([Environment]::GetEnvironmentVariable("FACTORY_RUNS_ROOT_ENSURE_FORCE", "User"))
}
if ([string]::IsNullOrWhiteSpace($RunsRootEnsureForceRaw)) {
    $RunsRootEnsureForceRaw = [string]([Environment]::GetEnvironmentVariable("FACTORY_RUNS_ROOT_ENSURE_FORCE", "Machine"))
}
$RunsRootEnsureForce = @("1", "true", "yes", "on") -contains $RunsRootEnsureForceRaw.Trim().ToLowerInvariant()
$DebugFlagRaw = [string]([Environment]::GetEnvironmentVariable("HITECH_FACTORY_DEBUG_STACK", "Process"))
if ([string]::IsNullOrWhiteSpace($DebugFlagRaw)) {
    $DebugFlagRaw = [string]([Environment]::GetEnvironmentVariable("HITECH_FACTORY_DEBUG_STACK", "User"))
}
if ([string]::IsNullOrWhiteSpace($DebugFlagRaw)) {
    $DebugFlagRaw = [string]([Environment]::GetEnvironmentVariable("HITECH_FACTORY_DEBUG_STACK", "Machine"))
}
$DebugStackEnabled = @("1", "true", "yes", "on") -contains $DebugFlagRaw.Trim().ToLowerInvariant()

function Get-EnvValue {
    param(
        [string[]]$Names
    )

    foreach ($name in $Names) {
        $item = Get-Item -Path ("Env:" + $name) -ErrorAction SilentlyContinue
        if ($null -ne $item -and -not [string]::IsNullOrWhiteSpace($item.Value)) {
            return $item.Value.Trim()
        }
    }

    return $null
}

function Resolve-StringSetting {
    param(
        [string]$Explicit,
        [string[]]$EnvKeys,
        [string]$Default
    )

    if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
        return $Explicit.Trim()
    }

    $envValue = Get-EnvValue -Names $EnvKeys
    if (-not [string]::IsNullOrWhiteSpace($envValue)) {
        return $envValue
    }

    return $Default
}

function Resolve-IntSetting {
    param(
        [Nullable[int]]$Explicit,
        [string[]]$EnvKeys,
        [int]$Default
    )

    if ($null -ne $Explicit) {
        return [int]$Explicit
    }

    $envValue = Get-EnvValue -Names $EnvKeys
    if ([string]::IsNullOrWhiteSpace($envValue)) {
        return [int]$Default
    }

    $parsed = 0
    if ([int]::TryParse($envValue, [ref]$parsed)) {
        return [int]$parsed
    }

    return [int]$Default
}

function Get-AutoRunId {
    param(
        [datetime]$NowUtc
    )

    $day = $NowUtc.ToString("yyyyMMdd")
    $roots = @(
        (Join-Path $CodexDir "runs"),
        (Join-Path $CodexDir "prompts"),
        (Join-Path $CodexDir "prompt_zips")
    )

    $pattern = "^{0}_(\d+)$" -f [regex]::Escape($day)
    $maxSeq = 0

    foreach ($root in $roots) {
        if (-not (Test-Path $root)) {
            continue
        }

        if ($root -like "*prompt_zips") {
            $items = Get-ChildItem -Path $root -File -Filter "*.zip" -ErrorAction SilentlyContinue
            foreach ($item in $items) {
                $name = [System.IO.Path]::GetFileNameWithoutExtension($item.Name)
                $match = [regex]::Match($name, $pattern)
                if ($match.Success) {
                    $seq = 0
                    if ([int]::TryParse($match.Groups[1].Value, [ref]$seq)) {
                        $maxSeq = [Math]::Max($maxSeq, $seq)
                    }
                }
            }
            continue
        }

        $entries = Get-ChildItem -Path $root -ErrorAction SilentlyContinue
        foreach ($entry in $entries) {
            $name = $entry.Name
            $match = [regex]::Match($name, $pattern)
            if ($match.Success) {
                $seq = 0
                if ([int]::TryParse($match.Groups[1].Value, [ref]$seq)) {
                    $maxSeq = [Math]::Max($maxSeq, $seq)
                }
            }
        }
    }

    return "$day" + "_" + ([string]($maxSeq + 1))
}

function Resolve-PromptsPackPath {
    param(
        [string]$ExplicitPath
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        $resolved = Resolve-Path -Path $ExplicitPath -ErrorAction SilentlyContinue
        if ($null -ne $resolved) {
            return $resolved.Path
        }
        throw "Prompts pack file was not found: $ExplicitPath"
    }

    $defaultPath = Join-Path $RepoRoot "PROMPTS_PACK_TEST.txt"
    if (Test-Path $defaultPath) {
        return (Resolve-Path $defaultPath).Path
    }

    throw "Prompts pack path is required. Pass -PromptsPackPath <path>."
}

function Resolve-FactoryWorktreeMode {
    $contractPath = Join-Path $RepoRoot "tools\hos\factory\config.json"
    if (-not (Test-Path $contractPath)) {
        throw "Unified factory contract missing: $contractPath"
    }

    $contractRaw = Get-Content -Path $contractPath -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($contractRaw)) {
        throw "Unified factory contract is empty: $contractPath"
    }

    $contract = ConvertFrom-JsonSafe -Text $contractRaw
    if ($null -eq $contract -or $null -eq $contract.PSObject.Properties["worktree_mode"]) {
        throw "Unified factory contract missing required key worktree_mode: $contractPath"
    }

    $contractMode = [string]$contract.worktree_mode
    if ([string]::IsNullOrWhiteSpace($contractMode) -or $contractMode.Trim().ToLowerInvariant() -ne "fixed") {
        throw "Unified factory contract requires worktree_mode=fixed: $contractPath"
    }

    $envMode = Get-EnvValue -Names @("FACTORY_WORKTREE_MODE")
    if (-not [string]::IsNullOrWhiteSpace($envMode) -and $envMode.Trim().ToLowerInvariant() -ne "fixed") {
        throw "FACTORY_WORKTREE_MODE must be fixed when set. got: $envMode"
    }

    return "fixed"
}

function Initialize-RunPaths {
    param(
        [string]$ResolvedRunId
    )

    $script:RunId = $ResolvedRunId
    $script:PromptsDir = Join-Path $PromptsRoot $ResolvedRunId
    $script:LogsDir = Join-Path $script:PromptsDir "logs"
    $script:ReportPath = Join-Path $script:LogsDir "DISPATCH_REPORT.md"
    $script:RunDir = Join-Path (Join-Path $CodexDir "runs") $ResolvedRunId
    $script:DebugDir = Join-Path $script:RunDir "_debug"
    $script:RunManifestPath = Join-Path $script:RunDir "RUN_MANIFEST.json"
    $script:DispatchHeartbeatPath = Join-Path $script:DebugDir "DISPATCH_HEARTBEAT.json"
    $script:DispatchTimeoutReportPath = Join-Path $script:DebugDir "TIMEOUT_REPORT.json"
}

function Update-DispatchRunManifest {
    param(
        [int]$ReadinessTimeoutSeconds,
        [object[]]$DispatchPhases
    )

    if ([string]::IsNullOrWhiteSpace($RunManifestPath)) {
        return
    }

    $manifest = [ordered]@{}
    if (Test-Path $RunManifestPath) {
        try {
            $raw = Get-Content -Path $RunManifestPath -Raw -Encoding UTF8
            if (-not [string]::IsNullOrWhiteSpace($raw)) {
                $parsed = ConvertFrom-JsonSafe -Text $raw
                if ($null -ne $parsed) {
                    $manifest = [ordered]@{}
                    foreach ($property in $parsed.PSObject.Properties) {
                        $manifest[$property.Name] = $property.Value
                    }
                }
            }
        } catch {
            $manifest = [ordered]@{}
        }
    }

    $artifactPaths = [ordered]@{
        prompts_dir = $PromptsDir
        logs_dir = $LogsDir
        report = $ReportPath
        debug_dir = $DebugDir
        context_dir = (Join-Path $RunDir "_context")
        apply_dir = (Join-Path $RunDir "_apply")
        queue_root = (Join-Path $RunDir "_queue")
        rework_queue_inbox = (Join-Path $RunDir "_queue\rework\inbox")
        rework_queue_outbox = (Join-Path $RunDir "_queue\rework\outbox")
        ahk_log = (Join-Path $DebugDir "AHK_DISPATCH.log")
        ahk_worker_results = (Join-Path $DebugDir "AHK_WORKER_RESULTS.log")
        heartbeat = $DispatchHeartbeatPath
        timeout_report = $DispatchTimeoutReportPath
    }

    $computedHardTimeout = 0
    foreach ($phase in $DispatchPhases) {
        if ($null -eq $phase) {
            continue
        }
        $phaseTimeout = 0
        if ($null -ne $phase.config -and $null -ne $phase.config.computed_hard_timeout_seconds) {
            try {
                $phaseTimeout = [int]$phase.config.computed_hard_timeout_seconds
            } catch {
                $phaseTimeout = 0
            }
        }
        $computedHardTimeout = [Math]::Max($computedHardTimeout, $phaseTimeout)
    }

    $manifest["run_id"] = $RunId
    $manifest["ordered_workers"] = $Workers
    $manifest["dispatch_runtime"] = [ordered]@{
        computed_hard_timeout_seconds = $computedHardTimeout
        readiness_timeout_seconds = [int]$ReadinessTimeoutSeconds
        artifact_paths = $artifactPaths
        phases = @($DispatchPhases)
    }

    New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
    $manifestJson = $manifest | ConvertTo-Json -Depth 32
    Set-Content -Path $RunManifestPath -Value $manifestJson -Encoding UTF8
}

function Write-Log {
    param(
        [string]$Message
    )

    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $line = "${stamp} | $Message"
    Write-Host $line

    if ($script:RunLogPath) {
        Add-Content -Path $script:RunLogPath -Value $line -Encoding UTF8
    } else {
        $script:BufferedLogs.Add($line) | Out-Null
    }
}

function Initialize-Logs {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    $script:RunLogPath = Join-Path $LogsDir "RUN_ITER.log"

    if ($script:BufferedLogs.Count -gt 0) {
        Add-Content -Path $script:RunLogPath -Value $script:BufferedLogs -Encoding UTF8
        $script:BufferedLogs.Clear()
    }
}

function Add-StageResult {
    param(
        [string]$Stage,
        [string]$Status,
        [int]$Rc,
        [datetime]$Started,
        [datetime]$Ended,
        [string]$Command,
        [string]$Output,
        [object]$Payload
    )

    $script:StageResults.Add(
        [pscustomobject]@{
            Stage = $Stage
            Status = $Status
            Rc = [int]$Rc
            StartedAtUtc = $Started.ToUniversalTime().ToString("o")
            EndedAtUtc = $Ended.ToUniversalTime().ToString("o")
            Command = $Command
            Output = $Output
            Payload = $Payload
        }
    ) | Out-Null
}

function Get-StageDebugPrefix {
    param([string]$Stage)
    $normalized = ($Stage.ToUpperInvariant() -replace "[^A-Z0-9]+", "_").Trim("_")
    return "STAGE_${normalized}"
}

function Write-DebugArtifact {
    param(
        [string]$FileName,
        [string]$Content
    )

    if (-not $DebugStackEnabled) {
        return
    }
    if ([string]::IsNullOrWhiteSpace($FileName)) {
        return
    }

    New-Item -ItemType Directory -Path $DebugDir -Force | Out-Null
    $target = Join-Path $DebugDir $FileName
    Set-Content -Path $target -Value $Content -Encoding UTF8
}

function Write-EnvDiagnostics {
    if (-not $DebugStackEnabled) {
        return
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    $codeCmd = Get-Command code.cmd -ErrorAction SilentlyContinue
    $pathEntries = @(
        $env:Path -split ";" |
            ForEach-Object { $_.Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
    $diag = [ordered]@{
        run_id = $RunId
        repo_root = $RepoRoot
        cwd = (Get-Location).Path
        helper = $SubprocessHelperPath
        debug_flag = $DebugStackEnabled
        python = if ($null -ne $pythonCmd) { $pythonCmd.Source } else { "" }
        git = if ($null -ne $gitCmd) { $gitCmd.Source } else { "" }
        code_cmd = if ($null -ne $codeCmd) { $codeCmd.Source } else { "" }
        path_entries = $pathEntries
    }
    $json = $diag | ConvertTo-Json -Depth 8
    Write-DebugArtifact -FileName "ENV_DIAGNOSTICS.json" -Content $json
}

function ConvertFrom-JsonSafe {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        throw "ConvertFrom-JsonSafe requires non-empty text."
    }

    $command = Get-Command ConvertFrom-Json -ErrorAction Stop
    if ($command.Parameters.ContainsKey("Depth")) {
        return $Text | ConvertFrom-Json -Depth 100 -ErrorAction Stop
    }
    return $Text | ConvertFrom-Json -ErrorAction Stop
}

function Invoke-ExternalStep {
    param(
        [string]$Stage,
        [string]$Executable,
        [string[]]$Arguments
    )

    $started = Get-Date
    $commandText = ($Executable + " " + ($Arguments -join " ")).Trim()
    Write-Log "[$Stage] START: $commandText"

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCmd) {
        $ended = Get-Date
        $message = "python executable not found in PATH"
        Add-StageResult -Stage $Stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $message -Payload $null
        Write-DebugArtifact -FileName ((Get-StageDebugPrefix $Stage) + "_TRACEBACK.txt") -Content $message
        throw $message
    }

    if (-not (Test-Path $SubprocessHelperPath)) {
        $ended = Get-Date
        $message = "subprocess helper missing: $SubprocessHelperPath"
        Add-StageResult -Stage $Stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $message -Payload $null
        Write-DebugArtifact -FileName ((Get-StageDebugPrefix $Stage) + "_TRACEBACK.txt") -Content $message
        throw $message
    }

    $helperArgs = @($SubprocessHelperPath, "--cwd", $RepoRoot, "--", $Executable) + $Arguments
    $helperRaw = & $pythonCmd.Source @helperArgs 2>&1
    $helperRc = $LASTEXITCODE
    $ended = Get-Date
    $helperText = (($helperRaw | ForEach-Object { "$_" }) -join [Environment]::NewLine).TrimEnd()
    $debugPrefix = Get-StageDebugPrefix $Stage

    if ($helperRc -ne 0) {
        $errorOutput = if ([string]::IsNullOrWhiteSpace($helperText)) { "subprocess helper failed with rc=$helperRc" } else { $helperText }
        Add-StageResult -Stage $Stage -Status "BLOCKED" -Rc $helperRc -Started $started -Ended $ended -Command $commandText -Output $errorOutput -Payload $null
        Write-DebugArtifact -FileName ($debugPrefix + "_STDOUT.txt") -Content ""
        Write-DebugArtifact -FileName ($debugPrefix + "_STDERR.txt") -Content $errorOutput
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content $errorOutput
        throw "Stage '$Stage' helper invocation failed with rc=$helperRc"
    }

    $runner = $null
    try {
        $runner = ConvertFrom-JsonSafe -Text $helperText
    } catch {
        $parseError = "Failed to parse helper JSON for stage '$Stage'. raw=$helperText"
        Add-StageResult -Stage $Stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $parseError -Payload $null
        Write-DebugArtifact -FileName ($debugPrefix + "_STDOUT.txt") -Content ""
        Write-DebugArtifact -FileName ($debugPrefix + "_STDERR.txt") -Content $parseError
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content ($_ | Out-String)
        throw $parseError
    }

    $stdout = [string]$runner.stdout
    $stderr = [string]$runner.stderr
    $rc = [int]$runner.rc
    $runnerCwd = [string]$runner.cwd
    $durationMs = [int]$runner.duration_ms
    $runnerCmd = ""
    if ($null -ne $runner.cmd) {
        $runnerCmd = [string]::Join(" ", @($runner.cmd | ForEach-Object { "$_" }))
    }

    Write-Log "[$Stage] EXEC: python=$($pythonCmd.Source) cwd=$runnerCwd duration_ms=$durationMs"
    Write-Log "[$Stage] CMD: $runnerCmd"

    $outputParts = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($stdout)) {
        $outputParts.Add("[stdout]") | Out-Null
        $outputParts.Add($stdout.TrimEnd()) | Out-Null
    }
    if (-not [string]::IsNullOrWhiteSpace($stderr)) {
        $outputParts.Add("[stderr]") | Out-Null
        $outputParts.Add($stderr.TrimEnd()) | Out-Null
    }
    $outputText = ""
    if ($outputParts.Count -gt 0) {
        $outputText = ($outputParts -join [Environment]::NewLine)
        Write-Log "[$Stage] OUTPUT:`n$outputText"
    }

    if ($DebugStackEnabled) {
        Write-DebugArtifact -FileName ($debugPrefix + "_STDOUT.txt") -Content $stdout
        Write-DebugArtifact -FileName ($debugPrefix + "_STDERR.txt") -Content $stderr
        $resultPayload = [ordered]@{
            stage = $Stage
            cmd = $runner.cmd
            cwd = $runnerCwd
            rc = $rc
            duration_ms = $durationMs
            python = $pythonCmd.Source
        }
        Write-DebugArtifact -FileName ($debugPrefix + "_RESULT.json") -Content ($resultPayload | ConvertTo-Json -Depth 6)
    }

    $payload = $null
    if (-not [string]::IsNullOrWhiteSpace($stdout)) {
        try {
            $payload = ConvertFrom-JsonSafe -Text $stdout
        } catch {
            $payload = $null
        }
    }

    $status = if ($rc -eq 0) { "PASS" } else { "BLOCKED" }
    Add-StageResult -Stage $Stage -Status $status -Rc $rc -Started $started -Ended $ended -Command $commandText -Output $outputText -Payload $payload

    if ($rc -ne 0) {
        $traceText = if (-not [string]::IsNullOrWhiteSpace($stderr)) { $stderr } else { $outputText }
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content $traceText
        throw "Stage '$Stage' failed with rc=$rc"
    }

    Write-Log "[$Stage] PASS"
    return $payload
}

function Invoke-DispatchStep {
    param(
        [string]$StageName,
        [string]$WorkersCsv,
        [string]$AhkExe,
        [int]$EffectiveWindowReadyTimeout,
        [int]$EffectiveReadinessTimeout,
        [int]$EffectiveBetweenWorkersDelayMs
    )

    $stage = $StageName
    $started = Get-Date
    $commandText = (
        "python tools/codex/dispatch/dispatch_prompts.py --run-id $RunId --workers $WorkersCsv " +
        "--window-ready-timeout $EffectiveWindowReadyTimeout --readiness-timeout $EffectiveReadinessTimeout " +
        "--between-workers-delay-ms $EffectiveBetweenWorkersDelayMs --ahk-exe `"$AhkExe`""
    ).Trim()
    Write-Log "[$stage] START: $commandText"

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCmd) {
        $ended = Get-Date
        $message = "python executable not found in PATH"
        Add-StageResult -Stage $stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $message -Payload $null
        Write-DebugArtifact -FileName ((Get-StageDebugPrefix $stage) + "_TRACEBACK.txt") -Content $message
        throw $message
    }

    if (-not (Test-Path $SubprocessHelperPath)) {
        $ended = Get-Date
        $message = "subprocess helper missing: $SubprocessHelperPath"
        Add-StageResult -Stage $stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $message -Payload $null
        Write-DebugArtifact -FileName ((Get-StageDebugPrefix $stage) + "_TRACEBACK.txt") -Content $message
        throw $message
    }

    New-Item -ItemType Directory -Path $DebugDir -Force | Out-Null
    if (Test-Path $DispatchHeartbeatPath) {
        Remove-Item -Path $DispatchHeartbeatPath -Force -ErrorAction SilentlyContinue
    }

    $helperArgs = @(
        $SubprocessHelperPath,
        "--cwd",
        $RepoRoot,
        "--",
        "python",
        "tools/codex/dispatch/dispatch_prompts.py",
        "--run-id",
        $RunId,
        "--workers",
        $WorkersCsv,
        "--window-ready-timeout",
        [string]$EffectiveWindowReadyTimeout,
        "--readiness-timeout",
        [string]$EffectiveReadinessTimeout,
        "--between-workers-delay-ms",
        [string]$EffectiveBetweenWorkersDelayMs,
        "--ahk-exe",
        $AhkExe
    )

    $debugPrefix = Get-StageDebugPrefix $stage
    $stdoutCapturePath = Join-Path $DebugDir ($debugPrefix + "_HELPER_STDOUT.txt")
    $stderrCapturePath = Join-Path $DebugDir ($debugPrefix + "_HELPER_STDERR.txt")
    Remove-Item -Path $stdoutCapturePath -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $stderrCapturePath -Force -ErrorAction SilentlyContinue

    $process = Start-Process -FilePath $pythonCmd.Source -ArgumentList $helperArgs -WorkingDirectory $RepoRoot -NoNewWindow -RedirectStandardOutput $stdoutCapturePath -RedirectStandardError $stderrCapturePath -PassThru

    $lastHeartbeatSeq = -1
    $lastHeartbeatAt = (Get-Date).ToUniversalTime()
    $lastHeartbeatStep = "<none>"
    $staleDetected = $false
    $staleReason = ""

    while (-not $process.HasExited) {
        Start-Sleep -Milliseconds 500
        $nowUtc = (Get-Date).ToUniversalTime()

        if (Test-Path $DispatchHeartbeatPath) {
            try {
                $rawHeartbeat = Get-Content -Path $DispatchHeartbeatPath -Raw -Encoding UTF8
                $heartbeat = ConvertFrom-JsonSafe -Text $rawHeartbeat
                $seq = -1
                if ($null -ne $heartbeat.seq) {
                    $seq = [int]$heartbeat.seq
                }
                if ($seq -gt $lastHeartbeatSeq) {
                    $lastHeartbeatSeq = $seq
                    $lastHeartbeatAt = $nowUtc
                    $lastHeartbeatStep = [string]$heartbeat.last_step
                }
            } catch {
                # Keep monitoring; malformed heartbeat should not break dispatch watchdog.
            }
        }

        if ((New-TimeSpan -Start $lastHeartbeatAt -End $nowUtc).TotalSeconds -gt $DispatchHeartbeatStaleSeconds) {
            $staleDetected = $true
            $staleReason = "HEARTBEAT_STALE: no heartbeat advance for > $DispatchHeartbeatStaleSeconds seconds (last_seq=$lastHeartbeatSeq last_step=$lastHeartbeatStep)"
            break
        }
    }

    if ($staleDetected -and -not $process.HasExited) {
        try {
            $process.Kill($true)
        } catch {
            # Ignore kill errors; stage will fail deterministically.
        }
        try {
            [void]$process.WaitForExit(5000)
        } catch {
            # Ignore wait errors.
        }
    }

    $stdout = if (Test-Path $stdoutCapturePath) { Get-Content -Path $stdoutCapturePath -Raw -Encoding UTF8 } else { "" }
    $stderr = if (Test-Path $stderrCapturePath) { Get-Content -Path $stderrCapturePath -Raw -Encoding UTF8 } else { "" }

    if (-not $process.HasExited) {
        try {
            [void]$process.WaitForExit(2000)
        } catch {
            # Ignore wait errors.
        }
    }

    $helperRc = if ($process.HasExited) { [int]$process.ExitCode } else { 124 }
    $ended = Get-Date
    if ($staleDetected) {
        $timeoutReport = ""
        if (Test-Path $DispatchTimeoutReportPath) {
            try {
                $timeoutReport = Get-Content -Path $DispatchTimeoutReportPath -Raw -Encoding UTF8
            } catch {
                $timeoutReport = ""
            }
        }
        $diagnosticLines = @(
            $staleReason,
            "run_id=$RunId",
            "heartbeat_path=$DispatchHeartbeatPath",
            "timeout_report_path=$DispatchTimeoutReportPath",
            "timeout_report_present=$([bool](Test-Path $DispatchTimeoutReportPath))",
            "helper_rc=$helperRc"
        )
        if (-not [string]::IsNullOrWhiteSpace($stderr)) {
            $diagnosticLines += "helper_stderr_tail:"
            $diagnosticLines += (Get-TextTail -Text $stderr -MaxLines 20)
        }
        if (-not [string]::IsNullOrWhiteSpace($timeoutReport)) {
            $diagnosticLines += "timeout_report:"
            $diagnosticLines += $timeoutReport.TrimEnd()
        }
        $diagnostic = ($diagnosticLines -join [Environment]::NewLine).TrimEnd()
        Add-StageResult -Stage $stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $diagnostic -Payload ([ordered]@{
                cause = "HEARTBEAT_STALE"
                run_id = $RunId
                stage = $stage
                heartbeat_path = $DispatchHeartbeatPath
                timeout_report_path = $DispatchTimeoutReportPath
            })
        Write-DebugArtifact -FileName ($debugPrefix + "_STDOUT.txt") -Content $stdout
        Write-DebugArtifact -FileName ($debugPrefix + "_STDERR.txt") -Content $stderr
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content $diagnostic
        throw "Stage '$stage' failed with cause HEARTBEAT_STALE"
    }

    if ($DebugStackEnabled) {
        Write-DebugArtifact -FileName ($debugPrefix + "_STDOUT.txt") -Content $stdout
        Write-DebugArtifact -FileName ($debugPrefix + "_STDERR.txt") -Content $stderr
    }

    if ($helperRc -ne 0) {
        $errorOutput = if ([string]::IsNullOrWhiteSpace($stderr)) { "subprocess helper failed with rc=$helperRc" } else { $stderr.TrimEnd() }
        Add-StageResult -Stage $stage -Status "BLOCKED" -Rc $helperRc -Started $started -Ended $ended -Command $commandText -Output $errorOutput -Payload $null
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content $errorOutput
        throw "Stage '$stage' helper invocation failed with rc=$helperRc"
    }

    $helperText = $stdout.Trim()
    $runner = $null
    try {
        $runner = ConvertFrom-JsonSafe -Text $helperText
    } catch {
        $parseError = "Failed to parse helper JSON for stage '$stage'. raw=$helperText"
        Add-StageResult -Stage $stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command $commandText -Output $parseError -Payload $null
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content $parseError
        throw $parseError
    }

    $runnerStdout = [string]$runner.stdout
    $runnerStderr = [string]$runner.stderr
    $rc = [int]$runner.rc
    $durationMs = [int]$runner.duration_ms
    $runnerCmd = ""
    if ($null -ne $runner.cmd) {
        $runnerCmd = [string]::Join(" ", @($runner.cmd | ForEach-Object { "$_" }))
    }

    Write-Log "[$stage] EXEC: python=$($pythonCmd.Source) cwd=$($runner.cwd) duration_ms=$durationMs"
    Write-Log "[$stage] CMD: $runnerCmd"

    $outputParts = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($runnerStdout)) {
        $outputParts.Add("[stdout]") | Out-Null
        $outputParts.Add($runnerStdout.TrimEnd()) | Out-Null
    }
    if (-not [string]::IsNullOrWhiteSpace($runnerStderr)) {
        $outputParts.Add("[stderr]") | Out-Null
        $outputParts.Add($runnerStderr.TrimEnd()) | Out-Null
    }
    $outputText = ""
    if ($outputParts.Count -gt 0) {
        $outputText = ($outputParts -join [Environment]::NewLine)
        Write-Log "[$stage] OUTPUT:`n$outputText"
    }

    $payload = $null
    if (-not [string]::IsNullOrWhiteSpace($runnerStdout)) {
        try {
            $payload = ConvertFrom-JsonSafe -Text $runnerStdout
        } catch {
            $payload = $null
        }
    }

    $status = if ($rc -eq 0) { "PASS" } else { "BLOCKED" }
    Add-StageResult -Stage $stage -Status $status -Rc $rc -Started $started -Ended $ended -Command $commandText -Output $outputText -Payload $payload

    if ($rc -ne 0) {
        $traceText = if (-not [string]::IsNullOrWhiteSpace($runnerStderr)) { $runnerStderr } else { $outputText }
        Write-DebugArtifact -FileName ($debugPrefix + "_TRACEBACK.txt") -Content $traceText
        if ($null -ne $payload -and [string]$payload.cause -eq "TIMEOUT_HARD") {
            throw "Stage '$stage' failed with cause TIMEOUT_HARD"
        }
        throw "Stage '$stage' failed with rc=$rc"
    }

    Write-Log "[$stage] PASS"
    return $payload
}

function ConvertTo-PathCompareKey {
    param([string]$PathValue)

    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ""
    }
    $candidate = $PathValue.Trim().Trim('"')
    if ($candidate.EndsWith("\")) {
        $candidate = $candidate.TrimEnd("\")
    }
    return $candidate.ToLowerInvariant()
}

function Split-PathEntries {
    param([string]$PathValue)

    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return @()
    }

    return @(
        $PathValue -split ";" |
            ForEach-Object { $_.Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
}

function Add-ProcessPathEntry {
    param([string]$EntryPath)

    if ([string]::IsNullOrWhiteSpace($EntryPath)) {
        return
    }
    $resolvedEntry = (Resolve-Path $EntryPath -ErrorAction SilentlyContinue)
    $target = if ($null -ne $resolvedEntry) { $resolvedEntry.Path } else { $EntryPath.Trim() }
    $targetNorm = ConvertTo-PathCompareKey -PathValue $target
    if ([string]::IsNullOrWhiteSpace($targetNorm)) {
        return
    }

    $entries = New-Object System.Collections.Generic.List[string]
    $seen = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in (Split-PathEntries -PathValue $env:Path)) {
        $norm = ConvertTo-PathCompareKey -PathValue $entry
        if ([string]::IsNullOrWhiteSpace($norm)) {
            continue
        }
        if ($seen.Add($norm)) {
            $entries.Add($entry) | Out-Null
        }
    }
    if ($seen.Add($targetNorm)) {
        $entries.Add($target) | Out-Null
    }
    $env:Path = [string]::Join(";", $entries)
}

function Update-ProcessPathFromScopes {
    $combined = New-Object System.Collections.Generic.List[string]
    $seen = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)

    foreach ($raw in @(
        [Environment]::GetEnvironmentVariable("Path", "Process"),
        [Environment]::GetEnvironmentVariable("Path", "Machine"),
        [Environment]::GetEnvironmentVariable("Path", "User")
    )) {
        foreach ($entry in (Split-PathEntries -PathValue $raw)) {
            $norm = ConvertTo-PathCompareKey -PathValue $entry
            if ([string]::IsNullOrWhiteSpace($norm)) {
                continue
            }
            if ($seen.Add($norm)) {
                $combined.Add($entry) | Out-Null
            }
        }
    }

    $env:Path = [string]::Join(";", $combined)
}

function Invoke-NativeCapture {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    foreach ($arg in $Arguments) {
        [void]$psi.ArgumentList.Add($arg)
    }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.WorkingDirectory = $RepoRoot
    $psi.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $stdoutText = if ($null -eq $stdout) { "" } else { [string]$stdout }
    $stderrText = if ($null -eq $stderr) { "" } else { [string]$stderr }
    return [ordered]@{
        rc = [int]$process.ExitCode
        stdout = $stdoutText.TrimEnd()
        stderr = $stderrText.TrimEnd()
        command = ($FilePath + " " + ($Arguments -join " ")).Trim()
    }
}

function Get-ProbedAutoHotkeyPaths {
    $candidates = @(
        (Join-Path $env:ProgramFiles "AutoHotkey\v2\AutoHotkey64.exe"),
        (Join-Path $env:ProgramFiles "AutoHotkey\v2\AutoHotkey32.exe"),
        (Join-Path $env:ProgramFiles "AutoHotkey\AutoHotkey.exe"),
        (Join-Path $env:LocalAppData "Programs\AutoHotkey\v2\AutoHotkey64.exe"),
        (Join-Path $env:LocalAppData "Programs\AutoHotkey\AutoHotkey.exe")
    )

    $ordered = New-Object System.Collections.Generic.List[string]
    $seen = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($candidate in $candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }
        $norm = ConvertTo-PathCompareKey -PathValue $candidate
        if ([string]::IsNullOrWhiteSpace($norm)) {
            continue
        }
        if ($seen.Add($norm)) {
            $ordered.Add($candidate) | Out-Null
        }
    }
    return @($ordered)
}

function Get-TextTail {
    param(
        [string]$Text,
        [int]$MaxLines = 20
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return ""
    }
    $normalized = @($Text -split "`r`n|`n|`r")
    if ($normalized.Count -le $MaxLines) {
        return ([string]::Join([Environment]::NewLine, $normalized)).TrimEnd()
    }
    return ([string]::Join([Environment]::NewLine, $normalized[($normalized.Count - $MaxLines)..($normalized.Count - 1)])).TrimEnd()
}

function Convert-WorkerListToCsv {
    param(
        [object]$Value
    )

    $workers = New-Object System.Collections.Generic.List[string]
    if ($null -eq $Value) {
        return ""
    }

    foreach ($item in @($Value)) {
        $text = [string]$item
        if ([string]::IsNullOrWhiteSpace($text)) {
            continue
        }
        $workers.Add($text.Trim()) | Out-Null
    }

    if ($workers.Count -eq 0) {
        return ""
    }
    return [string]::Join(",", $workers)
}

function Resolve-AutoHotkeyPath {
    $envPath = Get-EnvValue -Names @("FACTORY_AHK_EXE", "FACTORY_DISPATCH__AHK_EXE")
    $probedPaths = Get-ProbedAutoHotkeyPaths

    $result = [ordered]@{
        path = $null
        source = ""
        command_candidates = @("AutoHotkey64.exe", "AutoHotkey.exe")
        command_hits = @()
        probed_paths = @($probedPaths)
    }

    if (-not [string]::IsNullOrWhiteSpace($envPath)) {
        if (Test-Path $envPath) {
            $result.path = (Resolve-Path $envPath).Path
            $result.source = "env_override"
            return $result
        }
    }

    foreach ($candidate in $result.command_candidates) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -ne $cmd -and -not [string]::IsNullOrWhiteSpace($cmd.Source) -and (Test-Path $cmd.Source)) {
            $result.command_hits += $cmd.Source
            $result.path = $cmd.Source
            $result.source = "get_command:$candidate"
            return $result
        }
    }

    foreach ($probe in $probedPaths) {
        if (Test-Path $probe) {
            $result.path = (Resolve-Path $probe).Path
            $result.source = "known_path"
            return $result
        }
    }

    return $result
}

function Resolve-AutoHotkeyExecutable {
    $started = Get-Date
    $stage = "ensure_autohotkey"
    $wingetStdout = ""
    $wingetStderr = ""
    $wingetRc = -1
    $resolution = Resolve-AutoHotkeyPath
    $script:AutoHotkeyExe = $null

    if (-not [string]::IsNullOrWhiteSpace([string]$resolution.path) -and (Test-Path $resolution.path)) {
        $resolvedPath = (Resolve-Path $resolution.path).Path
        $script:AutoHotkeyExe = $resolvedPath
        Add-ProcessPathEntry -EntryPath (Split-Path -Path $resolvedPath -Parent)
        $ended = Get-Date
        Add-StageResult -Stage $stage -Status "PASS" -Rc 0 -Started $started -Ended $ended -Command "resolve-ahk" -Output ("AutoHotkey found: " + $resolvedPath) -Payload $resolution
        Write-Log "[$stage] PASS: AutoHotkey found at $resolvedPath"
        return $resolvedPath
    }

    Write-Log "[$stage] AutoHotkey not found. Attempting installation via winget."
    $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($null -eq $wingetCmd) {
        $ended = Get-Date
        $details = "winget not available`nprobed_paths:`n" + (($resolution.probed_paths | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
        Add-StageResult -Stage $stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command "winget install AutoHotkey.AutoHotkey" -Output $details -Payload $resolution
        throw "BLOCKED: AutoHotkey is not installed and winget is unavailable. Install AutoHotkey manually."
    }

    $wingetResult = Invoke-NativeCapture -FilePath $wingetCmd.Source -Arguments @("install", "--id", "AutoHotkey.AutoHotkey", "-e", "--accept-package-agreements", "--accept-source-agreements")
    $wingetRc = [int]$wingetResult.rc
    $wingetStdout = [string]$wingetResult.stdout
    $wingetStderr = [string]$wingetResult.stderr

    if (-not [string]::IsNullOrWhiteSpace($wingetStdout)) {
        Write-Log "[$stage] winget stdout:`n$wingetStdout"
    }
    if (-not [string]::IsNullOrWhiteSpace($wingetStderr)) {
        Write-Log "[$stage] winget stderr:`n$wingetStderr"
    }
    Write-DebugArtifact -FileName "WINGET_AHK_STDOUT.txt" -Content $wingetStdout
    Write-DebugArtifact -FileName "WINGET_AHK_STDERR.txt" -Content $wingetStderr

    Update-ProcessPathFromScopes
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        $resolution = Resolve-AutoHotkeyPath
        if (-not [string]::IsNullOrWhiteSpace([string]$resolution.path) -and (Test-Path $resolution.path)) {
            break
        }
        if ($attempt -lt 3) {
            Start-Sleep -Seconds 1
        }
    }

    $ended = Get-Date

    if (-not [string]::IsNullOrWhiteSpace([string]$resolution.path) -and (Test-Path $resolution.path)) {
        $resolvedPath = (Resolve-Path $resolution.path).Path
        $script:AutoHotkeyExe = $resolvedPath
        Add-ProcessPathEntry -EntryPath (Split-Path -Path $resolvedPath -Parent)
        Add-StageResult -Stage $stage -Status "PASS" -Rc 0 -Started $started -Ended $ended -Command "winget install AutoHotkey.AutoHotkey" -Output ("Installed and resolved: " + $resolvedPath) -Payload $resolution
        Write-Log "[$stage] PASS: AutoHotkey available at $resolvedPath"
        return $resolvedPath
    }

    $stdoutTail = Get-TextTail -Text $wingetStdout -MaxLines 20
    $stderrTail = Get-TextTail -Text $wingetStderr -MaxLines 20
    $probeLines = @($resolution.probed_paths | ForEach-Object { "- $_" })
    $resolutionLines = @(
        "winget_rc=$wingetRc",
        "winget_stdout_tail:",
        $stdoutTail,
        "winget_stderr_tail:",
        $stderrTail,
        "probed_paths:",
        ($probeLines -join [Environment]::NewLine),
        "expected_path_hint: $env:ProgramFiles\AutoHotkey\v2\AutoHotkey64.exe"
    )
    $resolutionReport = ($resolutionLines -join [Environment]::NewLine).TrimEnd()
    Write-DebugArtifact -FileName "AHK_RESOLUTION_REPORT.txt" -Content $resolutionReport

    $blockedMessage = (
        "BLOCKED: AutoHotkey installation failed or executable still not found." + [Environment]::NewLine +
        $resolutionReport
    )
    Add-StageResult -Stage $stage -Status "BLOCKED" -Rc 2 -Started $started -Ended $ended -Command "winget install AutoHotkey.AutoHotkey" -Output $blockedMessage -Payload $resolution
    throw $blockedMessage
}

function Build-DispatchReport {
    param(
        [string]$Verdict,
        [string]$ErrorMessage,
        [int]$EffectiveWindowReadyTimeout,
        [int]$EffectiveReadinessTimeout,
        [int]$EffectiveWorkerDoneTimeout,
        [int]$EffectiveBetweenWorkersDelayMs
    )

    $reportLines = New-Object System.Collections.Generic.List[string]

    $reportLines.Add("# DISPATCH_REPORT") | Out-Null
    $reportLines.Add("") | Out-Null
    $reportLines.Add("- run_id: $RunId") | Out-Null
    $reportLines.Add("- generated_at_utc: $((Get-Date).ToUniversalTime().ToString('o'))") | Out-Null
    $reportLines.Add("- final_verdict: $Verdict") | Out-Null
    $reportLines.Add("- prompt_input_mode: pack_only") | Out-Null
    $reportLines.Add("- initial_dispatch_mode: $(if ($SkipInitialDispatch) { 'manual' } else { 'automatic' })") | Out-Null
    $reportLines.Add("- window_ready_timeout: $EffectiveWindowReadyTimeout") | Out-Null
    $reportLines.Add("- readiness_timeout: $EffectiveReadinessTimeout") | Out-Null
    $reportLines.Add("- worker_done_timeout: $EffectiveWorkerDoneTimeout") | Out-Null
    $reportLines.Add("- between_workers_delay_ms: $EffectiveBetweenWorkersDelayMs") | Out-Null
    $reportLines.Add("- workers: $WorkersCsv") | Out-Null

    if (-not [string]::IsNullOrWhiteSpace($ErrorMessage)) {
        $reportLines.Add("- error: $ErrorMessage") | Out-Null
    }

    $reportLines.Add("") | Out-Null
    $reportLines.Add("## Stage Timeline") | Out-Null
    $reportLines.Add("") | Out-Null
    $reportLines.Add("| Stage | Status | RC | Started (UTC) | Ended (UTC) |") | Out-Null
    $reportLines.Add("|---|---|---:|---|---|") | Out-Null

    foreach ($stage in $script:StageResults) {
        $reportLines.Add("| $($stage.Stage) | $($stage.Status) | $($stage.Rc) | $($stage.StartedAtUtc) | $($stage.EndedAtUtc) |") | Out-Null
    }

    $dispatchStages = $script:StageResults | Where-Object {
        $_.Stage -eq "dispatch_prompts_docs" -or $_.Stage -eq "dispatch_prompts_z"
    }
    if (@($dispatchStages).Count -gt 0) {
        $reportLines.Add("") | Out-Null
        $reportLines.Add("## Dispatch Worker Status") | Out-Null
        $reportLines.Add("") | Out-Null
        $reportLines.Add("| Stage | Worker | Status | Detail |") | Out-Null
        $reportLines.Add("|---|---|---|---|") | Out-Null

        foreach ($dispatchStage in $dispatchStages) {
            if ($null -eq $dispatchStage.Payload -or $null -eq $dispatchStage.Payload.workers_results) {
                continue
            }
            foreach ($worker in $dispatchStage.Payload.workers_results) {
                $detail = [string]$worker.detail
                if ([string]::IsNullOrWhiteSpace($detail)) {
                    $detail = "<none>"
                }
                $reportLines.Add("| $($dispatchStage.Stage) | $($worker.worker) | $($worker.status) | $detail |") | Out-Null
            }
        }
    }

    $doneStages = $script:StageResults | Where-Object {
        $_.Stage -eq "wait_done_markers_docs" -or $_.Stage -eq "wait_done_markers_z"
    }
    if (@($doneStages).Count -gt 0) {
        $reportLines.Add("") | Out-Null
        $reportLines.Add("## DONE Marker Status") | Out-Null
        $reportLines.Add("") | Out-Null
        $reportLines.Add("| Stage | Worker | Status | Marker | Error |") | Out-Null
        $reportLines.Add("|---|---|---|---|---|") | Out-Null

        foreach ($doneStage in $doneStages) {
            if ($null -eq $doneStage.Payload -or $null -eq $doneStage.Payload.workers) {
                continue
            }
            foreach ($worker in $doneStage.Payload.workers) {
                $workerError = [string]$worker.error
                if ([string]::IsNullOrWhiteSpace($workerError)) {
                    $workerError = "<none>"
                }
                $reportLines.Add("| $($doneStage.Stage) | $($worker.worker) | $($worker.status) | $($worker.marker) | $workerError |") | Out-Null
            }
        }
    }

    $integrateStage = $script:StageResults | Where-Object { $_.Stage -eq "factory_integrate" } | Select-Object -Last 1
    if ($null -ne $integrateStage -and $null -ne $integrateStage.Payload) {
        $gateVerdict = "MISSING"
        if ($null -ne $integrateStage.Payload.meaningful_gate) {
            $gateValue = [string]$integrateStage.Payload.meaningful_gate.verdict
            if (-not [string]::IsNullOrWhiteSpace($gateValue)) {
                $gateVerdict = $gateValue
            }
        }

        $reportLines.Add("") | Out-Null
        $reportLines.Add("## Integration Summary") | Out-Null
        $reportLines.Add("") | Out-Null
        $reportLines.Add("- integrate_status: $($integrateStage.Payload.status)") | Out-Null
        $reportLines.Add("- meaningful_gate_verdict: $gateVerdict") | Out-Null
        $reportLines.Add("- report_path: $($integrateStage.Payload.report)") | Out-Null
    }

    $reportLines.Add("") | Out-Null
    $reportLines.Add("## Artifacts") | Out-Null
    $reportLines.Add("") | Out-Null
    $reportLines.Add("- run_log: tools/codex/prompts/$RunId/logs/RUN_ITER.log") | Out-Null
    $reportLines.Add("- dispatch_json: tools/codex/prompts/$RunId/logs/DISPATCH_PROMPTS.json") | Out-Null
    $reportLines.Add("- context_dir: tools/codex/runs/$RunId/_context") | Out-Null
    $reportLines.Add("- apply_dir: tools/codex/runs/$RunId/_apply") | Out-Null
    $reportLines.Add("- rework_queue_inbox: tools/codex/runs/$RunId/_queue/rework/inbox") | Out-Null
    $reportLines.Add("- rework_queue_outbox: tools/codex/runs/$RunId/_queue/rework/outbox") | Out-Null
    $reportLines.Add("- rework_transport: file_queue") | Out-Null
    $reportLines.Add("- task_bank_health_report: tools/codex/dispatch/reports/task_bank_health.json") | Out-Null
    $reportLines.Add("- execution_rules_summary: tools/codex/runs/$RunId/_debug/EXECUTION_RULES_SUMMARY.json") | Out-Null
    $reportLines.Add("- memory_dir: tools/codex/memory") | Out-Null
    $reportLines.Add("- ahk_runtime: tools/codex/prompts/$RunId/logs/DISPATCH_RUNTIME.ahk") | Out-Null
    $reportLines.Add("- ahk_log: tools/codex/runs/$RunId/_debug/AHK_DISPATCH.log") | Out-Null
    $reportLines.Add("- ahk_worker_results: tools/codex/runs/$RunId/_debug/AHK_WORKER_RESULTS.log") | Out-Null
    $reportLines.Add("- report: tools/codex/prompts/$RunId/logs/DISPATCH_REPORT.md") | Out-Null
    if ($DebugStackEnabled) {
        $reportLines.Add("- debug_dir: tools/codex/runs/$RunId/_debug") | Out-Null
    }

    Set-Content -Path $ReportPath -Value $reportLines -Encoding UTF8
}

$resolvedPromptsPackPath = Resolve-PromptsPackPath -ExplicitPath $PromptsPackPath
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = Get-AutoRunId -NowUtc ((Get-Date).ToUniversalTime())
}
Initialize-RunPaths -ResolvedRunId $RunId

$effectiveWindowReadyTimeout = Resolve-IntSetting -Explicit $WindowReadyTimeout -EnvKeys @("FACTORY_WINDOW_READY_TIMEOUT", "FACTORY_DISPATCH__WINDOW_READY_TIMEOUT") -Default 120
$effectiveReadinessTimeout = Resolve-IntSetting -Explicit $ReadinessTimeout -EnvKeys @("FACTORY_READINESS_TIMEOUT", "FACTORY_DISPATCH__READINESS_TIMEOUT") -Default 25
$effectiveWorkerDoneTimeout = Resolve-IntSetting -Explicit $WorkerDoneTimeout -EnvKeys @("FACTORY_WORKER_DONE_TIMEOUT", "FACTORY_DISPATCH__WORKER_DONE_TIMEOUT") -Default 3600
$effectiveBetweenWorkersDelayMs = Resolve-IntSetting -Explicit $BetweenWorkersDelayMs -EnvKeys @("FACTORY_BETWEEN_WORKERS_DELAY_MS", "FACTORY_DISPATCH__BETWEEN_WORKERS_DELAY_MS") -Default 700
$effectiveReworkMaxCycles = Resolve-IntSetting -Explicit $null -EnvKeys @("FACTORY_REWORK_MAX_CYCLES", "FACTORY_DISPATCH__REWORK_MAX_CYCLES") -Default 3
$effectiveBaseLocTarget = Resolve-IntSetting -Explicit $null -EnvKeys @("FACTORY_REWORK_BASE_LOC_TARGET", "FACTORY_DISPATCH__REWORK_BASE_LOC_TARGET") -Default 10000
$effectiveReworkLocIncrement = Resolve-IntSetting -Explicit $null -EnvKeys @("FACTORY_REWORK_LOC_INCREMENT", "FACTORY_DISPATCH__REWORK_LOC_INCREMENT") -Default 5000

if ($effectiveWindowReadyTimeout -le 0) {
    throw "window_ready_timeout must be > 0"
}
if ($effectiveReadinessTimeout -le 0) {
    throw "readiness_timeout must be > 0"
}
if ($effectiveWorkerDoneTimeout -le 0) {
    throw "worker_done_timeout must be > 0"
}
if ($effectiveBetweenWorkersDelayMs -lt 0) {
    throw "between_workers_delay_ms must be >= 0"
}
if ($effectiveReworkMaxCycles -lt 0) {
    throw "rework_max_cycles must be >= 0"
}
if ($effectiveBaseLocTarget -lt 0) {
    throw "rework_base_loc_target must be >= 0"
}
if ($effectiveReworkLocIncrement -lt 0) {
    throw "rework_loc_increment must be >= 0"
}

Write-Log "RUN_ID dispatcher started for $RunId"
Write-Log "Prompts pack: $resolvedPromptsPackPath"
Write-Log "Config: window_ready_timeout=$effectiveWindowReadyTimeout readiness_timeout=$effectiveReadinessTimeout worker_done_timeout=$effectiveWorkerDoneTimeout between_workers_delay_ms=$effectiveBetweenWorkersDelayMs rework_max_cycles=$effectiveReworkMaxCycles base_loc_target=$effectiveBaseLocTarget rework_loc_increment=$effectiveReworkLocIncrement"
Write-Log "Debug stack diagnostics enabled: $DebugStackEnabled"

$dispatchDocsPayload = $null
$dispatchZPayload = $null

Push-Location $RepoRoot
try {
    Write-EnvDiagnostics

    if (-not (Test-Path $RunsRootDoctorScriptPath)) {
        throw "runs-root doctor script missing: $RunsRootDoctorScriptPath"
    }
    if ($RunsRootAutoEnsure -and -not (Test-Path $RunsRootEnsureScriptPath)) {
        throw "runs-root ensure script missing: $RunsRootEnsureScriptPath"
    }

    $runsRootDoctorArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $RunsRootDoctorScriptPath, "-Quiet")
    try {
        Invoke-ExternalStep -Stage "runs_root_doctor" -Executable "pwsh" -Arguments $runsRootDoctorArgs | Out-Null
    } catch {
        if (-not $RunsRootAutoEnsure) {
            throw "RUNS_ROOT_DRIFT_BLOCKED: non-canonical runs root detected. Run tools/scripts/Invoke-HitechRunsEnsure.ps1 --write --force and retry."
        }

        $runsRootEnsureArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $RunsRootEnsureScriptPath, "--write", "-Quiet")
        if ($RunsRootEnsureForce) {
            $runsRootEnsureArgs += "--force"
        }
        Invoke-ExternalStep -Stage "runs_root_ensure" -Executable "pwsh" -Arguments $runsRootEnsureArgs | Out-Null
        Invoke-ExternalStep -Stage "runs_root_doctor_after_ensure" -Executable "pwsh" -Arguments $runsRootDoctorArgs | Out-Null
    }

    Invoke-ExternalStep -Stage "validate_run_id" -Executable "python" -Arguments @("tools/codex/dispatch/validator.py", "validate-run-id", "--run-id", $RunId) | Out-Null

    Invoke-ExternalStep -Stage "materialize_prompt_pack" -Executable "python" -Arguments @(
        "tools/codex/dispatch/validator.py",
        "materialize-pack",
        "--run-id",
        $RunId,
        "--pack-path",
        $resolvedPromptsPackPath
    ) | Out-Null

    Initialize-Logs

    Invoke-ExternalStep -Stage "validate_prompts" -Executable "python" -Arguments @("tools/codex/dispatch/validator.py", "validate-prompts", "--run-id", $RunId) | Out-Null

    Resolve-FactoryWorktreeMode | Out-Null
    Invoke-ExternalStep -Stage "factory_launch" -Executable "python" -Arguments @(
        "tools/codex/factory/launch_with_sanitized_env.py",
        "--run-id",
        $RunId,
        "--workers",
        $WorkersCsv,
        "--base-ref",
        "HEAD"
    ) | Out-Null

    Invoke-ExternalStep -Stage "factory_context_layer" -Executable "python" -Arguments @(
        "tools/codex/factory/context_layer.py",
        "--run-id",
        $RunId,
        "--workers",
        $WorkersCsv
    ) | Out-Null

    Invoke-ExternalStep -Stage "task_bank_refresh" -Executable "python" -Arguments @(
        "tools/codex/dispatch/task_bank_refresh.py",
        "--repo",
        ".",
        "--task-bank",
        "tools/codex/dispatch/rework_task_bank.json",
        "--sources",
        "tools/codex/dispatch/task_bank_sources.json",
        "--state",
        "tools/codex/dispatch/task_bank_state.json",
        "--report",
        "tools/codex/dispatch/reports/task_bank_health.json",
        "--apply",
        "--run-id",
        $RunId
    ) | Out-Null

    $ahkExe = ""
    if ($SkipInitialDispatch) {
        $manualStarted = Get-Date
        $manualEnded = Get-Date
        $manualOutput = "Initial dispatch skipped by operator. Distribute prompts manually from $PromptsDir."
        Add-StageResult -Stage "dispatch_prompts_initial_manual" -Status "PASS" -Rc 0 -Started $manualStarted -Ended $manualEnded -Command "manual" -Output $manualOutput -Payload ([ordered]@{
                mode = "manual"
                prompt_dir = $PromptsDir
                workers = $Workers
            })
        Write-Log "[dispatch_prompts_initial_manual] PASS: $manualOutput"
    } else {
        $ahkExe = Resolve-AutoHotkeyExecutable
        $dispatchZPayload = Invoke-DispatchStep -StageName "dispatch_prompts_z" -WorkersCsv $AggregatorWorkersCsv -AhkExe $ahkExe -EffectiveWindowReadyTimeout $effectiveWindowReadyTimeout -EffectiveReadinessTimeout $effectiveReadinessTimeout -EffectiveBetweenWorkersDelayMs $effectiveBetweenWorkersDelayMs
        $dispatchDocsPayload = Invoke-DispatchStep -StageName "dispatch_prompts_docs" -WorkersCsv $DocWorkersCsv -AhkExe $ahkExe -EffectiveWindowReadyTimeout $effectiveWindowReadyTimeout -EffectiveReadinessTimeout $effectiveReadinessTimeout -EffectiveBetweenWorkersDelayMs $effectiveBetweenWorkersDelayMs
    }

    Invoke-ExternalStep -Stage "wait_done_markers_docs" -Executable "python" -Arguments @(
        "tools/codex/dispatch/validator.py",
        "wait-done",
        "--run-id", $RunId,
        "--workers", $DocWorkersCsv,
        "--timeout-seconds", $effectiveWorkerDoneTimeout,
        "--poll-seconds", "2"
    ) | Out-Null

    if ($effectiveReworkMaxCycles -gt 0) {
        for ($reworkCycle = 1; $reworkCycle -le $effectiveReworkMaxCycles; $reworkCycle++) {
            $docsReworkPayload = Invoke-ExternalStep -Stage ("factory_rework_docs_cycle_{0}" -f $reworkCycle) -Executable "python" -Arguments @(
                "tools/codex/dispatch/validator.py",
                "rework-cycle",
                "--run-id", $RunId,
                "--workers", $DocWorkersCsv,
                "--cycle", ([string]$reworkCycle),
                "--max-reworks", ([string]$effectiveReworkMaxCycles),
                "--base-loc-target", ([string]$effectiveBaseLocTarget),
                "--loc-increment", ([string]$effectiveReworkLocIncrement)
            )

            $docsNeedsRedispatch = $false
            if ($null -ne $docsReworkPayload -and $null -ne $docsReworkPayload.needs_redispatch) {
                $docsNeedsRedispatch = [bool]$docsReworkPayload.needs_redispatch
            }
            if (-not $docsNeedsRedispatch) {
                break
            }

            $reworkWorkersCsv = ""
            if ($null -ne $docsReworkPayload -and -not [string]::IsNullOrWhiteSpace([string]$docsReworkPayload.rework_workers_csv)) {
                $reworkWorkersCsv = [string]$docsReworkPayload.rework_workers_csv
            } elseif ($null -ne $docsReworkPayload -and $null -ne $docsReworkPayload.rework_workers) {
                $reworkWorkersCsv = Convert-WorkerListToCsv -Value $docsReworkPayload.rework_workers
            }
            if ([string]::IsNullOrWhiteSpace($reworkWorkersCsv)) {
                throw "factory_rework_docs_cycle_$reworkCycle requested redispatch but returned no rework workers."
            }

            Invoke-ExternalStep -Stage ("queue_wait_outbox_docs_rework_{0}" -f $reworkCycle) -Executable "python" -Arguments @(
                "tools/codex/dispatch/validator.py",
                "queue-wait-outbox",
                "--run-id", $RunId,
                "--workers", $reworkWorkersCsv,
                "--cycle", ([string]$reworkCycle),
                "--timeout-seconds", $effectiveWorkerDoneTimeout,
                "--poll-seconds", "2"
            ) | Out-Null

            Invoke-ExternalStep -Stage ("wait_done_markers_docs_rework_{0}" -f $reworkCycle) -Executable "python" -Arguments @(
                "tools/codex/dispatch/validator.py",
                "wait-done",
                "--run-id", $RunId,
                "--workers", $reworkWorkersCsv,
                "--timeout-seconds", $effectiveWorkerDoneTimeout,
                "--poll-seconds", "2"
            ) | Out-Null
        }
    }

    Invoke-ExternalStep -Stage "factory_watch_z_pre_integrate" -Executable "python" -Arguments @("-m", "tools.codex.factory", "watch", "--run-id", $RunId) | Out-Null

    Invoke-ExternalStep -Stage "wait_done_markers_z" -Executable "python" -Arguments @(
        "tools/codex/dispatch/validator.py",
        "wait-done",
        "--run-id", $RunId,
        "--workers", $AggregatorWorkersCsv,
        "--timeout-seconds", $effectiveWorkerDoneTimeout,
        "--poll-seconds", "2"
    ) | Out-Null

    if ($effectiveReworkMaxCycles -gt 0) {
        for ($reworkCycle = 1; $reworkCycle -le $effectiveReworkMaxCycles; $reworkCycle++) {
            $zReworkPayload = Invoke-ExternalStep -Stage ("factory_rework_z_cycle_{0}" -f $reworkCycle) -Executable "python" -Arguments @(
                "tools/codex/dispatch/validator.py",
                "rework-cycle",
                "--run-id", $RunId,
                "--workers", $AggregatorWorkersCsv,
                "--cycle", ([string]$reworkCycle),
                "--max-reworks", ([string]$effectiveReworkMaxCycles),
                "--base-loc-target", ([string]$effectiveBaseLocTarget),
                "--loc-increment", ([string]$effectiveReworkLocIncrement)
            )

            $zNeedsRedispatch = $false
            if ($null -ne $zReworkPayload -and $null -ne $zReworkPayload.needs_redispatch) {
                $zNeedsRedispatch = [bool]$zReworkPayload.needs_redispatch
            }
            if (-not $zNeedsRedispatch) {
                break
            }

            $zReworkWorkersCsv = ""
            if ($null -ne $zReworkPayload -and -not [string]::IsNullOrWhiteSpace([string]$zReworkPayload.rework_workers_csv)) {
                $zReworkWorkersCsv = [string]$zReworkPayload.rework_workers_csv
            } elseif ($null -ne $zReworkPayload -and $null -ne $zReworkPayload.rework_workers) {
                $zReworkWorkersCsv = Convert-WorkerListToCsv -Value $zReworkPayload.rework_workers
            }
            if ([string]::IsNullOrWhiteSpace($zReworkWorkersCsv)) {
                throw "factory_rework_z_cycle_$reworkCycle requested redispatch but returned no rework workers."
            }

            Invoke-ExternalStep -Stage ("queue_wait_outbox_z_rework_{0}" -f $reworkCycle) -Executable "python" -Arguments @(
                "tools/codex/dispatch/validator.py",
                "queue-wait-outbox",
                "--run-id", $RunId,
                "--workers", $zReworkWorkersCsv,
                "--cycle", ([string]$reworkCycle),
                "--timeout-seconds", $effectiveWorkerDoneTimeout,
                "--poll-seconds", "2"
            ) | Out-Null

            Invoke-ExternalStep -Stage ("wait_done_markers_z_rework_{0}" -f $reworkCycle) -Executable "python" -Arguments @(
                "tools/codex/dispatch/validator.py",
                "wait-done",
                "--run-id", $RunId,
                "--workers", $zReworkWorkersCsv,
                "--timeout-seconds", $effectiveWorkerDoneTimeout,
                "--poll-seconds", "2"
            ) | Out-Null
        }
    }

    Invoke-ExternalStep -Stage "factory_execution_audit" -Executable "python" -Arguments @(
        "tools/codex/dispatch/validator.py",
        "execution-audit",
        "--run-id",
        $RunId,
        "--workers",
        $WorkersCsv
    ) | Out-Null

    Invoke-ExternalStep -Stage "factory_auto_closeout" -Executable "python" -Arguments @("-m", "tools.codex.factory", "auto-closeout", "--run-id", $RunId, "--workers", $WorkersCsv) | Out-Null

    Invoke-ExternalStep -Stage "factory_bundle_validate" -Executable "python" -Arguments @("-m", "tools.codex.factory", "bundle-validate", "--run-id", $RunId, "--workers", $WorkersCsv) | Out-Null

    Invoke-ExternalStep -Stage "factory_integrate" -Executable "python" -Arguments @("-m", "tools.codex.factory", "integrate", "--run-id", $RunId, "--workers", $WorkersCsv) | Out-Null

    Invoke-ExternalStep -Stage "factory_guardrails" -Executable "python" -Arguments @(
        "tools/codex/dispatch/validator.py",
        "validate-guardrails",
        "--run-id",
        $RunId
    ) | Out-Null

    Invoke-ExternalStep -Stage "factory_memory_record" -Executable "python" -Arguments @(
        "tools/codex/factory/memory_layer.py",
        "record-run",
        "--run-id",
        $RunId
    ) | Out-Null

    Update-DispatchRunManifest -ReadinessTimeoutSeconds $effectiveReadinessTimeout -DispatchPhases @($dispatchDocsPayload, $dispatchZPayload)

    Write-Log "Run completed successfully."
}
catch {
    $finalVerdict = "FAIL"
    $fatalMessage = $_.Exception.Message
    $fatalRepr = $_.Exception.ToString()
    $fatalTrace = ($_ | Out-String)
    Write-Log "[FATAL] $fatalMessage"
    Write-Log "[FATAL_EXCEPTION] $fatalRepr"
    Write-Log "[FATAL_TRACEBACK]`n$fatalTrace"
    Write-DebugArtifact -FileName "DISPATCH_FATAL_EXCEPTION.txt" -Content $fatalRepr
    Write-DebugArtifact -FileName "DISPATCH_FATAL_TRACEBACK.txt" -Content $fatalTrace
}
finally {
    try {
        if (-not (Test-Path $LogsDir)) {
            New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
        }
        if (-not $script:RunLogPath) {
            Initialize-Logs
        }

        Update-DispatchRunManifest -ReadinessTimeoutSeconds $effectiveReadinessTimeout -DispatchPhases @($dispatchDocsPayload, $dispatchZPayload)
        Build-DispatchReport -Verdict $finalVerdict -ErrorMessage $fatalMessage -EffectiveWindowReadyTimeout $effectiveWindowReadyTimeout -EffectiveReadinessTimeout $effectiveReadinessTimeout -EffectiveWorkerDoneTimeout $effectiveWorkerDoneTimeout -EffectiveBetweenWorkersDelayMs $effectiveBetweenWorkersDelayMs
        Write-Log "Dispatch report written to $ReportPath"
    } catch {
        Write-Host "Failed to write dispatch report: $($_.Exception.Message)"
        if (-not [string]::IsNullOrWhiteSpace($fatalMessage)) {
            Write-Host "Original failure: $fatalMessage"
        }
        $finalVerdict = "FAIL"
    }

    Pop-Location

    if ($finalVerdict -ne "PASS") {
        exit 2
    }

    exit 0
}
