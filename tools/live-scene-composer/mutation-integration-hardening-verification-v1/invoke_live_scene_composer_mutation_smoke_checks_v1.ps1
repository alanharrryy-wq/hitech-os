[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$SummaryDir,
    [Parameter(Mandatory = $true)][string]$StagingRoot,
    [Parameter(Mandatory = $true)][string]$DocsRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Add-Smoke {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$Id,
        [bool]$Passed,
        [string]$Details
    )
    $Checks.Add([pscustomobject]@{
        id = $Id
        status = $(if ($Passed) { 'passed' } else { 'failed' })
        details = $Details
    }) | Out-Null
}

$smokeTxt = Join-Path $SummaryDir 'smoke_report.txt'
$smokeJson = Join-Path $SummaryDir 'smoke_report.json'
$checks = New-Object 'System.Collections.Generic.List[object]'

$checksToRun = @(
    @{ Id = 'docs-root'; Path = $DocsRoot },
    @{ Id = 'staging-root'; Path = $StagingRoot },
    @{ Id = 'mutation-client-index'; Path = (Join-Path $StagingRoot 'source\mutation-client\index.ts') },
    @{ Id = 'mutation-integration-index'; Path = (Join-Path $StagingRoot 'source\mutation-integration\index.ts') },
    @{ Id = 'bridge-doc'; Path = (Join-Path $DocsRoot '18_RUNTIME_MUTATION_BRIDGE.md') },
    @{ Id = 'decision-doc'; Path = (Join-Path $DocsRoot '40_ARCHITECTURAL_DECISIONS.md') }
)

$allPassed = $true
foreach ($check in $checksToRun) {
    $exists = Test-Path -LiteralPath $check.Path
    Add-Smoke -Checks $checks -Id $check.Id -Passed $exists -Details $check.Path
    if (-not $exists) { $allPassed = $false }
}

$smokeStatus = if ($allPassed) { 'passed' } else { 'failed' }
$payload = [ordered]@{
    package_name = 'live_scene_composer_mutation_integration_hardening_verification_pack_v1'
    repo_root = $RepoRoot
    smoke_status = $smokeStatus
    checks = $checks
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $smokeJson -Encoding UTF8
@(
    ('Package: {0}' -f $payload.package_name),
    ('Smoke status: {0}' -f $smokeStatus),
    ('Repo root: {0}' -f $RepoRoot),
    '',
    'Checks:'
) + ($checks | ForEach-Object { ' - [{0}] {1}: {2}' -f $_.status, $_.id, $_.details }) | Set-Content -LiteralPath $smokeTxt -Encoding UTF8
