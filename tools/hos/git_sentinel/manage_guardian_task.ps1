param(
    [ValidateSet("install", "uninstall", "status", "start", "stop", "restart")]
    [string]$Action = "status",
    [string]$TaskName = "HITECH-OS-GitSentinel-Guardian",
    [int]$IntervalSec = 600,
    [switch]$Apply = $true,
    [switch]$NoIgnoreUpdate = $true,
    [string]$Config = "",
    [switch]$RunNow
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

function Build-GuardianArgs {
    param(
        [string]$ScriptPath,
        [int]$Interval,
        [bool]$EnableApply,
        [bool]$DisableIgnoreUpdate,
        [string]$ConfigPath
    )

    $args = @(
        "`"$ScriptPath`"",
        "guardian",
        "--iterations", "1",
        "--interval-sec", "$Interval"
    )

    if ($EnableApply) {
        $args += "--apply"
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

$repoRoot = Resolve-RepoRoot
$python = (Get-Command python -ErrorAction Stop).Source
$cliScript = (Resolve-Path (Join-Path $repoRoot "tools/hos/git_sentinel/cli_sentinel.py")).Path
$safeInterval = [Math]::Max(60, $IntervalSec)

switch ($Action) {
    "install" {
        Assert-ScheduledTasksSupport

        $triggerStart = if ($RunNow.IsPresent) {
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
            -EnableApply $Apply.IsPresent `
            -DisableIgnoreUpdate $NoIgnoreUpdate.IsPresent `
            -ConfigPath $Config
        $taskAction = New-ScheduledTaskAction -Execute $python -Argument $argumentLine -WorkingDirectory $repoRoot
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -MultipleInstances IgnoreNew
        $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

        Register-ScheduledTask `
            -TaskName $TaskName `
            -Action $taskAction `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -Force | Out-Null

        if ($RunNow.IsPresent) {
            Start-ScheduledTask -TaskName $TaskName
        }

        $status = Get-TaskInfo -Name $TaskName
        Write-Output "[git-sentinel] guardian_task=installed name=$TaskName interval_sec=$safeInterval apply=$($Apply.IsPresent) no_ignore_update=$($NoIgnoreUpdate.IsPresent)"
        if ($status) {
            Write-Output "[git-sentinel] state=$($status.State) last_result=$($status.LastTaskResult) next_run=$($status.NextRunTime)"
        }
        break
    }

    "uninstall" {
        Assert-ScheduledTasksSupport
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Output "[git-sentinel] guardian_task=removed name=$TaskName"
        } else {
            Write-Output "[git-sentinel] guardian_task=absent name=$TaskName"
        }
        break
    }

    "start" {
        Assert-ScheduledTasksSupport
        Start-ScheduledTask -TaskName $TaskName
        Write-Output "[git-sentinel] guardian_task=started name=$TaskName"
        break
    }

    "stop" {
        Assert-ScheduledTasksSupport
        Stop-ScheduledTask -TaskName $TaskName
        Write-Output "[git-sentinel] guardian_task=stopped name=$TaskName"
        break
    }

    "restart" {
        Assert-ScheduledTasksSupport
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Start-ScheduledTask -TaskName $TaskName
        Write-Output "[git-sentinel] guardian_task=restarted name=$TaskName"
        break
    }

    "status" {
        Assert-ScheduledTasksSupport
        $status = Get-TaskInfo -Name $TaskName
        if (-not $status) {
            Write-Output "[git-sentinel] guardian_task=absent name=$TaskName"
            exit 1
        }
        Write-Output "[git-sentinel] guardian_task=present name=$TaskName state=$($status.State) last_result=$($status.LastTaskResult)"
        Write-Output "[git-sentinel] last_run=$($status.LastRunTime) next_run=$($status.NextRunTime)"
        break
    }
}
