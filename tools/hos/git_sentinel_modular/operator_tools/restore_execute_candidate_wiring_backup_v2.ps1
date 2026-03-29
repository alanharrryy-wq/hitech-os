[CmdletBinding()]
param(
    [string]$RuntimeRoot = 'C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime',
    [string]$WorkspaceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step {
    param([int]$Percent, [string]$Status)
    Write-Progress -Id 1 -Activity 'Restoring execute candidate wiring backup' -Status $Status -PercentComplete $Percent
    Write-Host "[$Percent%] $Status" -ForegroundColor Cyan
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-LatestWorkspace {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)
    $shadowRoot = Join-Path $RuntimeRoot 'shadow_mode'
    $dir = Get-ChildItem -LiteralPath $shadowRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $dir) { throw "No se encontró ningún shadow workspace en: $shadowRoot" }
    return $dir.FullName
}

function Remove-PathIfExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Copy-Tree {
    param([Parameter(Mandatory = $true)][string]$Source,[Parameter(Mandatory = $true)][string]$Destination)
    Ensure-Directory -Path $Destination
    $items = Get-ChildItem -LiteralPath $Source -Recurse -Force
    $count = [Math]::Max($items.Count, 1)
    $i = 0
    foreach ($item in $items) {
        $i++
        $relative = $item.FullName.Substring($Source.Length).TrimStart('\\')
        $target = Join-Path $Destination $relative
        if ($item.PSIsContainer) {
            Ensure-Directory -Path $target
        }
        else {
            $parent = Split-Path -Parent $target
            Ensure-Directory -Path $parent
            Copy-Item -LiteralPath $item.FullName -Destination $target -Force
        }
        if (($i % 20) -eq 0 -or $i -eq $count) {
            $pc = [int](($i / $count) * 100)
            Write-Progress -Id 2 -Activity 'Restaurando archivos' -Status $relative -PercentComplete $pc
        }
    }
    Write-Progress -Id 2 -Activity 'Restaurando archivos' -Completed
}

Write-Step -Percent 10 -Status 'Resolviendo workspace y backup más reciente'
if (-not $WorkspaceRoot) {
    $WorkspaceRoot = Get-LatestWorkspace -RuntimeRoot $RuntimeRoot
}

$backupsRoot = Join-Path $WorkspaceRoot 'candidate_wiring_backups'
if (-not (Test-Path -LiteralPath $backupsRoot)) {
    throw "No existe candidate_wiring_backups en: $backupsRoot"
}

$backupDir = Get-ChildItem -LiteralPath $backupsRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $backupDir) {
    throw "No se encontró ningún backup en: $backupsRoot"
}

$originalCandidate = Join-Path $backupDir.FullName 'candidate_original'
$jsonBackupRoot = Join-Path $backupDir.FullName 'json_before'
$workspaceCandidate = Join-Path $WorkspaceRoot 'candidate'

if (-not (Test-Path -LiteralPath $originalCandidate)) {
    throw "No existe candidate_original en: $originalCandidate"
}

Write-Step -Percent 45 -Status 'Restaurando workspace candidate'
Remove-PathIfExists -Path $workspaceCandidate
Copy-Tree -Source $originalCandidate -Destination $workspaceCandidate

Write-Step -Percent 80 -Status 'Restaurando JSON respaldados'
foreach ($rel in @('review_bundle\promotion_review.json','cutover_bundle\release_candidate_summary.json','execution_bundle\execution_plan.json')) {
    $src = Join-Path $jsonBackupRoot $rel
    $dst = Join-Path $WorkspaceRoot $rel
    if (Test-Path -LiteralPath $src) {
        $parent = Split-Path -Parent $dst
        Ensure-Directory -Path $parent
        Copy-Item -LiteralPath $src -Destination $dst -Force
    }
}

Write-Step -Percent 100 -Status 'Restauración completada'
Write-Progress -Id 1 -Activity 'Restoring execute candidate wiring backup' -Completed
Write-Host ''
Write-Host '=== RESTORE COMPLETADO ===' -ForegroundColor Green
Write-Host "Workspace: $WorkspaceRoot" -ForegroundColor White
Write-Host "Backup:    $($backupDir.FullName)" -ForegroundColor White
