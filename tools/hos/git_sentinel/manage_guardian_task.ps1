param(
    [ValidateSet("install", "uninstall", "status", "start", "stop", "restart")]
    [string]$Action = "status",
    [string]$TaskName = "HITECH-OS-GitSentinel-Guardian",
    [int]$IntervalSec = 600,
    [switch]$Apply = $true,
    [switch]$ApplyCleanup,
    [switch]$ApplyRepair,
    [switch]$NoIgnoreUpdate = $true,
    [ValidateSet("safe", "strict", "aggressive")]
    [string]$Profile = "safe",
    [string]$Config = "",
    [switch]$RunNow,
    [switch]$NoExecute
)

$ErrorActionPreference = "Stop"

function Assert-ScheduledTasksSupport {
    if (-not (Get-Command Register-ScheduledTask -ErrorAction SilentlyContinue)) {
        throw "ScheduledTasks module is not available on this system."
    }
}

function Resolve-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
}

function Get-SafeInterval {
    param([int]$Interval)
    return [Math]::Max(60, $Interval)
}

function Build-GuardianArgs {
    param(
        [string]$ScriptPath,
        [int]$Interval,
        [bool]$EnableApply,
        [bool]$EnableApplyCleanup,
        [bool]$EnableApplyRepair,
        [bool]$DisableIgnoreUpdate,
        [string]$ProfileName,
        [string]$ConfigPath
    )

    $args = @(
        "`"$ScriptPath`"",
        "guardian",
        "--iterations", "1",
        "--interval-sec", "$Interval",
        "--profile", "$ProfileName"
    )

    if ($EnableApply) {
        $args += "--apply"
    }
    if ($EnableApplyCleanup) {
        $args += "--apply-cleanup"
    }
    if ($EnableApplyRepair) {
        $args += "--apply-repair"
    }

    if ($DisableIgnoreUpdate) {
        $args += "--no-ignore-update"
    }

    if ($ConfigPath -ne "") {
        $resolvedConfig = $ConfigPath
        if (-not [System.IO.Path]::IsPathRooted($resolvedConfig)) {
            $resolvedConfig = (Resolve-Path (Join-Path (Resolve-RepoRoot) $resolvedConfig)).Path
        } else {
            $resolvedConfig = (Resolve-Path $resolvedConfig).Path
        }
        $args += @("--config", "`"$resolvedConfig`"")
    }

    return ($args -join " ")
}

function Get-TaskInfo {
    param([string]$Name)

    $task = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
    if (-not $task) {
        return $null
    }
    $info = Get-ScheduledTaskInfo -TaskName $Name
    return [PSCustomObject]@{
        TaskName     = $task.TaskName
        State        = [string]$task.State
        LastRunTime  = $info.LastRunTime
        LastTaskResult = $info.LastTaskResult
        NextRunTime  = $info.NextRunTime
    }
}

function Invoke-GuardianTaskAction {
    param(
        [string]$RequestedAction,
        [string]$TaskNameValue,
        [int]$IntervalValue,
        [bool]$EnableApply,
        [bool]$EnableApplyCleanup,
        [bool]$EnableApplyRepair,
        [bool]$DisableIgnoreUpdate,
        [string]$ProfileValue,
        [string]$ConfigValue,
        [bool]$ShouldRunNow
    )

    $repoRoot = Resolve-RepoRoot
    $python = (Get-Command python -ErrorAction Stop).Source
    $cliScript = (Resolve-Path (Join-Path $repoRoot "tools/hos/git_sentinel/cli_sentinel.py")).Path
    $safeInterval = Get-SafeInterval -Interval $IntervalValue

    switch ($RequestedAction) {
        "install" {
            Assert-ScheduledTasksSupport

            $triggerStart = if ($ShouldRunNow) {
                (Get-Date).AddSeconds($safeInterval)
            } else {
                (Get-Date).AddMinutes(1)
            }

            $trigger = New-ScheduledTaskTrigger `
                -Once `
                -At $triggerStart `
                -RepetitionInterval ([TimeSpan]::FromSeconds($safeInterval)) `
                -RepetitionDuration ([TimeSpan]::FromDays(3650))

            $argumentLine = Build-GuardianArgs `
                -ScriptPath $cliScript `
                -Interval $safeInterval `
                -EnableApply $EnableApply `
                -EnableApplyCleanup $EnableApplyCleanup `
                -EnableApplyRepair $EnableApplyRepair `
                -DisableIgnoreUpdate $DisableIgnoreUpdate `
                -ProfileName $ProfileValue `
                -ConfigPath $ConfigValue
            $taskAction = New-ScheduledTaskAction -Execute $python -Argument $argumentLine -WorkingDirectory $repoRoot
            $settings = New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -StartWhenAvailable `
                -MultipleInstances IgnoreNew
            $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

            Register-ScheduledTask `
                -TaskName $TaskNameValue `
                -Action $taskAction `
                -Trigger $trigger `
                -Settings $settings `
                -Principal $principal `
                -Force | Out-Null

            if ($ShouldRunNow) {
                Start-ScheduledTask -TaskName $TaskNameValue
            }

            $status = Get-TaskInfo -Name $TaskNameValue
            Write-Output "[git-sentinel] guardian_task=installed name=$TaskNameValue interval_sec=$safeInterval profile=$ProfileValue apply=$EnableApply apply_cleanup=$EnableApplyCleanup apply_repair=$EnableApplyRepair no_ignore_update=$DisableIgnoreUpdate"
            if ($status) {
                Write-Output "[git-sentinel] state=$($status.State) last_result=$($status.LastTaskResult) next_run=$($status.NextRunTime)"
            }
            break
        }

        "uninstall" {
            Assert-ScheduledTasksSupport
            $task = Get-ScheduledTask -TaskName $TaskNameValue -ErrorAction SilentlyContinue
            if ($task) {
                Unregister-ScheduledTask -TaskName $TaskNameValue -Confirm:$false
                Write-Output "[git-sentinel] guardian_task=removed name=$TaskNameValue"
            } else {
                Write-Output "[git-sentinel] guardian_task=absent name=$TaskNameValue"
            }
            break
        }

        "start" {
            Assert-ScheduledTasksSupport
            Start-ScheduledTask -TaskName $TaskNameValue
            Write-Output "[git-sentinel] guardian_task=started name=$TaskNameValue"
            break
        }

        "stop" {
            Assert-ScheduledTasksSupport
            Stop-ScheduledTask -TaskName $TaskNameValue
            Write-Output "[git-sentinel] guardian_task=stopped name=$TaskNameValue"
            break
        }

        "restart" {
            Assert-ScheduledTasksSupport
            Stop-ScheduledTask -TaskName $TaskNameValue -ErrorAction SilentlyContinue
            Start-ScheduledTask -TaskName $TaskNameValue
            Write-Output "[git-sentinel] guardian_task=restarted name=$TaskNameValue"
            break
        }

        "status" {
            Assert-ScheduledTasksSupport
            $status = Get-TaskInfo -Name $TaskNameValue
            if (-not $status) {
                Write-Output "[git-sentinel] guardian_task=absent name=$TaskNameValue"
                exit 1
            }
            Write-Output "[git-sentinel] guardian_task=present name=$TaskNameValue state=$($status.State) last_result=$($status.LastTaskResult)"
            Write-Output "[git-sentinel] last_run=$($status.LastRunTime) next_run=$($status.NextRunTime)"
            break
        }
    }
}

if ($NoExecute.IsPresent) {
    return
}

Invoke-GuardianTaskAction `
    -RequestedAction $Action `
    -TaskNameValue $TaskName `
    -IntervalValue $IntervalSec `
    -EnableApply $Apply.IsPresent `
    -EnableApplyCleanup $ApplyCleanup.IsPresent `
    -EnableApplyRepair $ApplyRepair.IsPresent `
    -DisableIgnoreUpdate $NoIgnoreUpdate.IsPresent `
    -ProfileValue $Profile `
    -ConfigValue $Config `
    -ShouldRunNow $RunNow.IsPresent
