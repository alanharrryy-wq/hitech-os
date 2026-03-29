[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$DownloadsRoot,
    [Parameter(Mandatory = $true)][string]$SummaryDir,
    [Parameter(Mandatory = $true)][string]$StagingRoot,
    [Parameter(Mandatory = $true)][string]$DocsRoot,
    [string]$MirrorStatus = 'not-requested',
    [int]$MirroredFilesCount = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Add-Check {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [string]$Id,
        [string]$Title,
        [string]$Status,
        [string]$Severity,
        [string]$Details
    )
    $Checks.Add([pscustomobject]@{
        id = $Id
        title = $Title
        status = $Status
        severity = $Severity
        details = $Details
    }) | Out-Null
}

$verificationTxt = Join-Path $SummaryDir 'verification_report.txt'
$verificationJson = Join-Path $SummaryDir 'verification_report.json'
$checks = New-Object 'System.Collections.Generic.List[object]'

$docsToCheck = @(
    '10_MUTATION_MODEL.md',
    '18_RUNTIME_MUTATION_BRIDGE.md',
    '40_ARCHITECTURAL_DECISIONS.md',
    '50_MUTATION_CLIENT_BRIDGE_CONTRACT.md',
    '70_MUTATION_INTEGRATION_HARDENING_OVERVIEW.md',
    '72_POST_INSTALL_VERIFICATION_MODEL.md',
    '73_SMOKE_CHECKS_AND_EVIDENCE.md'
)
$stageToCheck = @(
    'source\mutation-client\index.ts',
    'source\mutation-integration\index.ts',
    'verify_live_scene_composer_mutation_integration_hardening_v1.ps1',
    'invoke_live_scene_composer_mutation_smoke_checks_v1.ps1'
)

$allRequiredPassed = $true
foreach ($doc in $docsToCheck) {
    $path = Join-Path $DocsRoot $doc
    if (Test-Path -LiteralPath $path) {
        Add-Check -Checks $checks -Id ('doc-' + $doc) -Title ('Doc present: ' + $doc) -Status 'passed' -Severity 'info' -Details $path
    }
    else {
        Add-Check -Checks $checks -Id ('doc-' + $doc) -Title ('Doc present: ' + $doc) -Status 'failed' -Severity 'error' -Details 'Missing canonical doc in repo docs root.'
        $allRequiredPassed = $false
    }
}
foreach ($item in $stageToCheck) {
    $path = Join-Path $StagingRoot $item
    if (Test-Path -LiteralPath $path) {
        Add-Check -Checks $checks -Id ('stage-' + $item) -Title ('Stage present: ' + $item) -Status 'passed' -Severity 'info' -Details $path
    }
    else {
        Add-Check -Checks $checks -Id ('stage-' + $item) -Title ('Stage present: ' + $item) -Status 'failed' -Severity 'error' -Details 'Missing staged file.'
        $allRequiredPassed = $false
    }
}

if ($MirrorStatus -eq 'mirrored') {
    Add-Check -Checks $checks -Id 'mirror-status' -Title 'Mirror status' -Status 'passed' -Severity 'info' -Details ('Mirrored files: {0}' -f $MirroredFilesCount)
}
elseif ($MirrorStatus -eq 'ambiguous' -or $MirrorStatus -eq 'missing' -or $MirrorStatus -eq 'not-requested') {
    Add-Check -Checks $checks -Id 'mirror-status' -Title 'Mirror status' -Status 'skipped' -Severity 'warn' -Details ('Mirror status: {0}' -f $MirrorStatus)
}
else {
    Add-Check -Checks $checks -Id 'mirror-status' -Title 'Mirror status' -Status 'skipped' -Severity 'warn' -Details ('Mirror status: {0}' -f $MirrorStatus)
}

$verificationStatus = if ($allRequiredPassed) { 'passed' } else { 'failed' }
$payload = [ordered]@{
    package_name = 'live_scene_composer_mutation_integration_hardening_verification_pack_v1'
    repo_root = $RepoRoot
    downloads_root = $DownloadsRoot
    docs_root = $DocsRoot
    staging_root = $StagingRoot
    mirror_status = $MirrorStatus
    mirrored_files_count = $MirroredFilesCount
    verification_status = $verificationStatus
    checks = $checks
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $verificationJson -Encoding UTF8
@(
    ('Package: {0}' -f $payload.package_name),
    ('Verification status: {0}' -f $verificationStatus),
    ('Repo root: {0}' -f $RepoRoot),
    ('Docs root: {0}' -f $DocsRoot),
    ('Staging root: {0}' -f $StagingRoot),
    ('Mirror status: {0}' -f $MirrorStatus),
    ('Mirrored files count: {0}' -f $MirroredFilesCount),
    '',
    'Checks:'
) + ($checks | ForEach-Object { ' - [{0}] {1}: {2}' -f $_.status, $_.title, $_.details }) | Set-Content -LiteralPath $verificationTxt -Encoding UTF8
