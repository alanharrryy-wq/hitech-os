[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Resolve-RepoRoot {
    $fallback = "F:\repos\hitech-os"
    $scriptHint = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

    if (Get-Command git -ErrorAction SilentlyContinue) {
        try {
            $viaScript = (& git -C $scriptHint rev-parse --show-toplevel 2>$null | Select-Object -First 1).Trim()
            if ($viaScript) {
                return $viaScript
            }
        } catch {
        }
        try {
            $viaCwd = (& git rev-parse --show-toplevel 2>$null | Select-Object -First 1).Trim()
            if ($viaCwd) {
                return $viaCwd
            }
        } catch {
        }
    }

    return $fallback
}

function Resolve-PythonInvocation {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{ Exe = $python.Source; Prefix = @() }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{ Exe = $py.Source; Prefix = @("-3") }
    }

    throw "Python is not available (neither 'python' nor 'py')."
}

function Parse-FactoryArgs {
    param(
        [string[]]$Args
    )

    $parsed = [ordered]@{
        dry_only = $false
        resume = $null
        gc = $false
        keep_days = 14
        keep_count = 20
    }

    $i = 0
    while ($i -lt $Args.Count) {
        $token = [string]$Args[$i]
        switch ($token) {
            "--dry-only" {
                $parsed.dry_only = $true
                $i += 1
                continue
            }
            "--resume" {
                if ($i + 1 -ge $Args.Count) {
                    throw "--resume requires a RUN_ID value"
                }
                $parsed.resume = [string]$Args[$i + 1]
                $i += 2
                continue
            }
            "--gc" {
                $parsed.gc = $true
                $i += 1
                continue
            }
            "--keep-days" {
                if ($i + 1 -ge $Args.Count) {
                    throw "--keep-days requires an integer value"
                }
                $next = 0
                if (-not [int]::TryParse([string]$Args[$i + 1], [ref]$next)) {
                    throw "--keep-days value must be an integer"
                }
                $parsed.keep_days = $next
                $i += 2
                continue
            }
            "--keep-count" {
                if ($i + 1 -ge $Args.Count) {
                    throw "--keep-count requires an integer value"
                }
                $next = 0
                if (-not [int]::TryParse([string]$Args[$i + 1], [ref]$next)) {
                    throw "--keep-count value must be an integer"
                }
                $parsed.keep_count = $next
                $i += 2
                continue
            }
            default {
                throw "Unknown argument: $token"
            }
        }
    }

    return $parsed
}

function Invoke-Runtime {
    param(
        [string]$RepoRoot,
        [hashtable]$PythonInvocation,
        [string[]]$RuntimeArgs,
        [string]$LogPath,
        [string]$ProgressStatus,
        [int]$PercentComplete
    )

    Write-Progress -Activity "HITECH-OS Factory One-Button" -Status $ProgressStatus -PercentComplete $PercentComplete

    $exe = [string]$PythonInvocation.Exe
    $prefix = @($PythonInvocation.Prefix)
    $entry = "tools/hos/launcher/one_button_executor.py"
    $args = @($prefix + @($entry) + $RuntimeArgs)

    "[$([DateTime]::UtcNow.ToString('o'))] CMD: $exe $($args -join ' ')" | Out-File -FilePath $LogPath -Append -Encoding utf8

    $previousErrorPreference = $ErrorActionPreference
    $previousNativePreference = $null
    try {
        if ($PSVersionTable.PSVersion.Major -ge 7) {
            $previousNativePreference = $PSNativeCommandUseErrorActionPreference
            $PSNativeCommandUseErrorActionPreference = $false
        }
        $ErrorActionPreference = "Continue"
        & $exe @args 2>&1 | Tee-Object -FilePath $LogPath -Append | Out-Host
        $rc = $LASTEXITCODE
        return [int]$rc
    }
    finally {
        $ErrorActionPreference = $previousErrorPreference
        if ($PSVersionTable.PSVersion.Major -ge 7 -and $null -ne $previousNativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
    }
}

function Read-LastRuntimeResult {
    param([string]$RepoRoot)

    $path = Join-Path $RepoRoot "tools/codex/_debug/last_runtime_result.json"
    if (-not (Test-Path $path)) {
        return $null
    }
    try {
        return Get-Content -Raw -Path $path -Encoding utf8 | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

$parsed = Parse-FactoryArgs -Args $CliArgs
$repoRoot = Resolve-RepoRoot
if (-not (Test-Path $repoRoot)) {
    throw "Resolved repo root does not exist: $repoRoot"
}

$python = Resolve-PythonInvocation
$debugRoot = Join-Path $repoRoot "tools/codex/_debug"
New-Item -ItemType Directory -Path $debugRoot -Force | Out-Null
$stamp = [DateTime]::UtcNow.ToString("yyyyMMdd_HHmmss")
$wrapperLog = Join-Path $debugRoot "hos_factory_one_button_$stamp.log"

Push-Location $repoRoot
try {
    if ($parsed.gc) {
        $gcArgs = @("--gc", "--keep-days", [string]$parsed.keep_days, "--keep-count", [string]$parsed.keep_count)
        $gcRc = Invoke-Runtime -RepoRoot $repoRoot -PythonInvocation $python -RuntimeArgs $gcArgs -LogPath $wrapperLog -ProgressStatus "Running snapshot GC" -PercentComplete 40
        Write-Progress -Activity "HITECH-OS Factory One-Button" -Completed
        exit $gcRc
    }

    $baseArgs = @()
    if ($parsed.resume) {
        $baseArgs += @("--resume-run-id", [string]$parsed.resume)
    }

    $dryRc = Invoke-Runtime -RepoRoot $repoRoot -PythonInvocation $python -RuntimeArgs (@("--dry-run") + $baseArgs) -LogPath $wrapperLog -ProgressStatus "Running dry-run preflight" -PercentComplete 30
    if ($dryRc -ne 0) {
        Write-Progress -Activity "HITECH-OS Factory One-Button" -Completed
        exit $dryRc
    }

    if (-not $parsed.dry_only) {
        $realRc = Invoke-Runtime -RepoRoot $repoRoot -PythonInvocation $python -RuntimeArgs $baseArgs -LogPath $wrapperLog -ProgressStatus "Running real execution" -PercentComplete 75
        if ($realRc -ne 0) {
            Write-Progress -Activity "HITECH-OS Factory One-Button" -Completed
            exit $realRc
        }
    }

    Write-Progress -Activity "HITECH-OS Factory One-Button" -Status "Finalizing" -PercentComplete 100
    $last = Read-LastRuntimeResult -RepoRoot $repoRoot
    if ($null -ne $last -and $last.run_root) {
        try {
            Invoke-Item ([string]$last.run_root)
        }
        catch {
            "[$([DateTime]::UtcNow.ToString('o'))] WARN: failed to open run folder: $($_.Exception.Message)" | Out-File -FilePath $wrapperLog -Append -Encoding utf8
        }
    }

    Write-Progress -Activity "HITECH-OS Factory One-Button" -Completed
    exit 0
}
finally {
    Pop-Location
}
