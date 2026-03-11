Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$StartPath
    )

    $current = (Resolve-Path -LiteralPath $StartPath).Path
    while ($true) {
        if (Test-Path -LiteralPath (Join-Path $current "pnpm-workspace.yaml")) {
            return $current
        }
        $parent = Split-Path -Path $current -Parent
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            throw "Unable to locate repo root from: $StartPath"
        }
        $current = $parent
    }
}

Describe "Git Sentinel guardian task manager script" {
    BeforeAll {
        $script:RepoRoot = Resolve-RepoRoot -StartPath $PSScriptRoot
        $script:TaskScriptPath = Join-Path $script:RepoRoot "tools/hos/git_sentinel/manage_guardian_task.ps1"
        . $script:TaskScriptPath -NoExecute
    }

    It "clamps guardian interval to at least 60 seconds" {
        (Get-SafeInterval -Interval 1) | Should Be 60
        (Get-SafeInterval -Interval 600) | Should Be 600
    }

    It "builds guardian args including selected profile and apply toggles" {
        $scriptPath = Join-Path $script:RepoRoot "tools/hos/git_sentinel/cli_sentinel.py"
        $argsLine = Build-GuardianArgs `
            -ScriptPath $scriptPath `
            -Interval 420 `
            -EnableApply $true `
            -EnableApplyCleanup $true `
            -EnableApplyRepair $false `
            -DisableIgnoreUpdate $true `
            -ProfileName "strict" `
            -ConfigPath ""

        $argsLine | Should Match "guardian"
        $argsLine | Should Match "--interval-sec 420"
        $argsLine | Should Match "--profile strict"
        $argsLine | Should Match "--apply"
        $argsLine | Should Match "--apply-cleanup"
        $argsLine | Should Not Match "--apply-repair"
        $argsLine | Should Match "--no-ignore-update"
    }

    It "includes a quoted config path when config is provided" {
        $configPath = Join-Path $TestDrive "sentinel_config.json"
        Set-Content -LiteralPath $configPath -Value "{}" -Encoding UTF8

        $scriptPath = Join-Path $script:RepoRoot "tools/hos/git_sentinel/cli_sentinel.py"
        $argsLine = Build-GuardianArgs `
            -ScriptPath $scriptPath `
            -Interval 600 `
            -EnableApply $false `
            -EnableApplyCleanup $false `
            -EnableApplyRepair $true `
            -DisableIgnoreUpdate $false `
            -ProfileName "aggressive" `
            -ConfigPath $configPath

        $argsLine | Should Match "--apply-repair"
        $argsLine | Should Match "--profile aggressive"
        $argsLine | Should Match ([regex]::Escape("--config `"$configPath`""))
    }
}
