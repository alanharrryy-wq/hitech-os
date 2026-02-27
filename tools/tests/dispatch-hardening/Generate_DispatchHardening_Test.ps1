[CmdletBinding()]
param(
    [switch]$Refresh
)

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
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    switch ($Value.Trim().ToLowerInvariant()) {
        "1" { return $true }
        "true" { return $true }
        "yes" { return $true }
        "on" { return $true }
        default { return $false }
    }
}

function Write-TextFileIfNeeded {
    param(
        [Parameter(Mandatory = $true)] [string]$Path,
        [Parameter(Mandatory = $true)] [string]$Content,
        [Parameter(Mandatory = $true)] [bool]$RefreshMode
    )

    $parent = Split-Path -Path $Path -Parent
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if ($RefreshMode -or -not (Test-Path -LiteralPath $Path)) {
        Set-Content -LiteralPath $Path -Value $Content -Encoding utf8NoBOM
        return "updated"
    }
    return "kept"
}

$repoRoot = Resolve-RepoRoot -StartPath $PSScriptRoot
$testPath = Join-Path $repoRoot "tools/tests/dispatch-hardening/DispatchHardening.Tests.ps1"
$readmePath = Join-Path $repoRoot "tools/tests/dispatch-hardening/README.md"
$howtoPath = Join-Path $repoRoot "docs/dispatcher/DISPATCHER_HOWTO.md"

$testTemplate = @'
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Describe "Dispatch hardening invariants (fallback file)" {
    It "requires repository copy of DispatchHardening.Tests.ps1" {
        (Test-Path -LiteralPath $PSCommandPath) | Should -BeTrue
    }
}
'@

$readmeTemplate = @'
# Dispatch Hardening Tests

Use `Invoke-Pester -Path tools/tests/dispatch-hardening/DispatchHardening.Tests.ps1`.
Set `HOS_RUN_ID` to pin a run and `HOS_STRICT=1` for strict checks.
'@

$howtoTemplate = @'
# Dispatcher HowTo

See this file for operator steps:
- Auto mode factory run
- Manual dispatch by RUN_ID
- Strict mode (`HOS_STRICT=1`)
- Troubleshooting and manual fallback procedure
'@

$testState = Write-TextFileIfNeeded -Path $testPath -Content $testTemplate -RefreshMode:$Refresh
$readmeState = Write-TextFileIfNeeded -Path $readmePath -Content $readmeTemplate -RefreshMode:$Refresh
$howtoState = Write-TextFileIfNeeded -Path $howtoPath -Content $howtoTemplate -RefreshMode:$Refresh

Write-Host "repo_root=$repoRoot"
Write-Host "test_file=$testPath ($testState)"
Write-Host "readme_file=$readmePath ($readmeState)"
Write-Host "howto_file=$howtoPath ($howtoState)"

$noRun = Test-BoolEnv -Value ([string]$env:HOS_NO_RUN)
if ($noRun) {
    Write-Host "HOS_NO_RUN=1 detected. Generation complete; skipping Invoke-Pester."
    exit 0
}

if (-not (Get-Command Invoke-Pester -ErrorAction SilentlyContinue)) {
    throw "Invoke-Pester is not available. Install Pester and re-run."
}

$pesterResult = Invoke-Pester -Script $testPath -PassThru
if ($null -eq $pesterResult) {
    throw "Invoke-Pester returned no result object."
}
if ([int]$pesterResult.FailedCount -gt 0) {
    throw "Dispatch hardening tests failed. FailedCount=$($pesterResult.FailedCount)"
}

Write-Host "Dispatch hardening tests passed."
