Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$StartPath
    )

    $current = (Resolve-Path -LiteralPath $StartPath).Path
    while ($true) {
        if (Test-Path -LiteralPath (Join-Path $current "KERNEL_CONTEXT.md")) {
            return $current
        }
        $parent = Split-Path -Path $current -Parent
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            throw "Unable to locate repo root from: $StartPath"
        }
        $current = $parent
    }
}

function Test-BoolEnv {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }
    switch ($Value.Trim().ToLowerInvariant()) {
        "1" { return $true }
        "true" { return $true }
        "yes" { return $true }
        "on" { return $true }
        default { return $false }
    }
}

function Resolve-RunId {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $pinned = [string]$env:HOS_RUN_ID
    if (-not [string]::IsNullOrWhiteSpace($pinned)) {
        return $pinned.Trim()
    }

    $runsRoot = Join-Path $RepoRoot "tools/codex/runs"
    if (-not (Test-Path -LiteralPath $runsRoot)) {
        throw "Runs root not found: $runsRoot"
    }

    $candidates = @(Get-ChildItem -LiteralPath $runsRoot -Directory |
        Where-Object { $_.Name -match '^\d{8}_\d+$' } |
        Sort-Object -Property Name -Descending)

    foreach ($candidate in $candidates) {
        $dispatchLogs = @(Get-ChildItem -LiteralPath $candidate.FullName -Recurse -Filter "AHK_DISPATCH.log" -File -ErrorAction SilentlyContinue)
        if ($dispatchLogs.Count -gt 0) {
            return $candidate.Name
        }
    }

    throw "No run directory with AHK_DISPATCH.log was found under: $runsRoot"
}

function Resolve-PreferredLogPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RunRoot,
        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    $candidates = @(Get-ChildItem -LiteralPath $RunRoot -Recurse -Filter $FileName -File -ErrorAction SilentlyContinue |
        Sort-Object -Property FullName)
    if ($candidates.Count -eq 0) {
        throw "Missing $FileName under run root: $RunRoot"
    }

    $preferred = $candidates | Where-Object { $_.FullName -match [regex]::Escape("\_debug\$FileName") } | Select-Object -First 1
    if ($null -ne $preferred) {
        return $preferred.FullName
    }

    return $candidates[0].FullName
}

function Parse-DispatchLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $entries = New-Object System.Collections.Generic.List[object]
    $rawLines = Get-Content -LiteralPath $Path -Encoding UTF8
    foreach ($line in $rawLines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        $parts = $line.Split("|")
        if ($parts.Length -lt 8) {
            continue
        }
        $entries.Add([pscustomobject]@{
                Index = $entries.Count
                Raw = $line
                Seq = $parts[0]
                Timestamp = $parts[1]
                Worker = $parts[2]
                Step = $parts[3]
                Hwnd = $parts[4]
                Status = $parts[5]
                Detail = $parts[6]
                Flag = $parts[7].Trim().ToLowerInvariant()
            })
    }
    return $entries
}

function Parse-ResultLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $entries = New-Object System.Collections.Generic.List[object]
    $rawLines = Get-Content -LiteralPath $Path -Encoding UTF8
    foreach ($line in $rawLines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        $parts = $line.Split("|", 3)
        if ($parts.Length -lt 2) {
            continue
        }
        $worker = $parts[0].TrimStart([char]0xFEFF).Trim()
        $status = $parts[1].Trim()
        $detail = if ($parts.Length -eq 3) { $parts[2] } else { "" }
        $entries.Add([pscustomobject]@{
                Worker = $worker
                Status = $status
                Detail = $detail
                Raw = $line
            })
    }
    return $entries
}

Describe "Dispatch hardening invariants" {
    BeforeAll {
        $script:RepoRoot = Resolve-RepoRoot -StartPath $PSScriptRoot
        $script:RunId = Resolve-RunId -RepoRoot $script:RepoRoot
        $script:RunRoot = Join-Path $script:RepoRoot ("tools/codex/runs/" + $script:RunId)

        $script:DispatchLogPath = Resolve-PreferredLogPath -RunRoot $script:RunRoot -FileName "AHK_DISPATCH.log"
        $script:ResultsLogPath = Resolve-PreferredLogPath -RunRoot $script:RunRoot -FileName "AHK_WORKER_RESULTS.log"

        $script:DispatchEntries = Parse-DispatchLog -Path $script:DispatchLogPath
        $script:ResultEntries = Parse-ResultLog -Path $script:ResultsLogPath
        $script:StrictMode = Test-BoolEnv -Value ([string]$env:HOS_STRICT)
    }

    It "locates dispatch and worker result logs for the selected run" {
        Test-Path -LiteralPath $script:DispatchLogPath | Should Be $true
        Test-Path -LiteralPath $script:ResultsLogPath | Should Be $true
        $script:DispatchEntries.Count | Should BeGreaterThan 0
    }

    It "logs fallback_title_scan and fallback_recent_code_window after each new_hwnd_timeout" {
        $timeouts = @($script:DispatchEntries | Where-Object {
                $_.Step -eq "detect_new_hwnd" -and
                $_.Status -eq "FAIL" -and
                $_.Detail -match "new_hwnd_timeout"
            })

        foreach ($timeout in $timeouts) {
            $start = [int]$timeout.Index + 1
            $end = [Math]::Min($script:DispatchEntries.Count - 1, $start + 40)
            $window = if ($start -le $end) { $script:DispatchEntries[$start..$end] } else { @() }
            $windowForWorker = @($window | Where-Object { $_.Worker -eq $timeout.Worker })

            ($windowForWorker.Step -contains "fallback_title_scan") | Should Be $true
            ($windowForWorker.Step -contains "fallback_recent_code_window") | Should Be $true
        }
    }

    It "keeps guarded keystroke steps marked with |true" {
        $guardedSteps = @("open_codex_sidebar", "paste_prompt", "submit_prompt")
        foreach ($step in $guardedSteps) {
            $matches = @($script:DispatchEntries | Where-Object { $_.Step -eq $step -and $_.Status -eq "OK" })
            if ($matches.Count -eq 0) {
                $true | Should Be $true
            } else {
                foreach ($entry in $matches) {
                    $entry.Flag | Should Be "true"
                }
            }
        }
    }

    It "uses single_enter_submission for successful submit_prompt steps" {
        $submits = @($script:DispatchEntries | Where-Object { $_.Step -eq "submit_prompt" -and $_.Status -eq "OK" })
        if ($submits.Count -eq 0) {
            $true | Should Be $true
        } else {
            foreach ($entry in $submits) {
                $entry.Detail | Should Match "single_enter_submission"
                $entry.Detail | Should Not Match "ctrl.?enter|retry"
            }
        }
    }

    It "contains at most one result line per worker" {
        $groups = $script:ResultEntries | Group-Object -Property Worker
        foreach ($group in $groups) {
            ([int]$group.Count -le 1) | Should Be $true
        }
    }

    It "requires exactly one result line for A/B/C/D in strict mode" {
        if (-not $script:StrictMode) {
            $true | Should Be $true
        } else {
            foreach ($worker in @("A_core", "B_tooling", "C_features", "D_validation")) {
                $count = @($script:ResultEntries | Where-Object { $_.Worker -eq $worker }).Count
                [int]$count | Should Be 1
            }
        }
    }
}
