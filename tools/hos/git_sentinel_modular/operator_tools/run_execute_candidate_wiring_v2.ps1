[CmdletBinding()]
param(
    [string]$RepoRoot = 'F:\repos\hitech-os',
    [string]$DownloadsRoot = 'F:\OneDrive\Descargas',
    [string]$RuntimeRoot = 'C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime',
    [string]$WorkspaceRoot,
    [string]$TargetRoot,
    [string]$OverlayCandidateRoot,
    [string]$FullCandidateRoot,
    [switch]$KeepCandidateWired
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step {
    param([int]$Percent, [string]$Status)
    Write-Progress -Id 1 -Activity 'Wiring candidate into sentinel_execute' -Status $Status -PercentComplete $Percent
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
    if (-not (Test-Path -LiteralPath $shadowRoot)) {
        throw "No existe shadow_mode en runtime: $shadowRoot"
    }
    $dir = Get-ChildItem -LiteralPath $shadowRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $dir) {
        throw "No se encontró ningún shadow workspace en: $shadowRoot"
    }
    return $dir.FullName
}

function Remove-PathIfExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Copy-TreeWithProgress {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string]$Activity
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "No existe la ruta fuente: $Source"
    }

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
            Write-Progress -Id 2 -Activity $Activity -Status $relative -PercentComplete $pc
        }
    }
    Write-Progress -Id 2 -Activity $Activity -Completed
}

function Get-FileCount {
    param([Parameter(Mandatory = $true)][string]$Root)
    if (-not (Test-Path -LiteralPath $Root)) { return 0 }
    return @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force).Count
}

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return $raw | ConvertFrom-Json
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Object
    )
    $parent = Split-Path -Parent $Path
    Ensure-Directory -Path $parent
    $json = $Object | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

function Set-OrAddNoteProperty {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        $Value
    )
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
    else {
        $prop.Value = $Value
    }
}

function Patch-JsonHints {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$WorkspaceCandidateRoot,
        [Parameter(Mandatory = $true)][string]$ResolvedTargetRoot,
        [string]$ResolvedOverlayRoot
    )

    $obj = Read-JsonFile -Path $Path
    if ($null -eq $obj) { return $false }

    Set-OrAddNoteProperty -Object $obj -Name 'candidate_root' -Value $WorkspaceCandidateRoot
    Set-OrAddNoteProperty -Object $obj -Name 'target_root' -Value $ResolvedTargetRoot
    if ($ResolvedOverlayRoot) {
        Set-OrAddNoteProperty -Object $obj -Name 'overlay_candidate_root' -Value $ResolvedOverlayRoot
    }

    $pathsProp = $obj.PSObject.Properties['paths']
    if ($null -ne $pathsProp -and $null -ne $pathsProp.Value) {
        $pathsObj = $pathsProp.Value
        Set-OrAddNoteProperty -Object $pathsObj -Name 'candidate_root' -Value $WorkspaceCandidateRoot
        Set-OrAddNoteProperty -Object $pathsObj -Name 'target_root' -Value $ResolvedTargetRoot
    }

    $workspaceProp = $obj.PSObject.Properties['workspace']
    if ($null -ne $workspaceProp -and $null -ne $workspaceProp.Value) {
        $workspaceObj = $workspaceProp.Value
        Set-OrAddNoteProperty -Object $workspaceObj -Name 'candidate_root' -Value $WorkspaceCandidateRoot
        Set-OrAddNoteProperty -Object $workspaceObj -Name 'target_root' -Value $ResolvedTargetRoot
    }

    Write-JsonFile -Path $Path -Object $obj
    return $true
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$startTime = Get-Date
$outerLogPath = Join-Path $DownloadsRoot ("execute_candidate_wiring_v2_" + $stamp + ".log")
$resultJsonPath = Join-Path $DownloadsRoot ("execute_candidate_wiring_v2_result_" + $stamp + ".json")
$resultMdPath = Join-Path $DownloadsRoot ("execute_candidate_wiring_v2_result_" + $stamp + ".md")

$resolvedWorkspace = $null
$resolvedTarget = $null
$workspaceCandidate = $null
$resolvedOverlay = $null
$sourceMode = $null
$backupRoot = $null
$originalCandidateBackup = $null
$jsonBackupRoot = $null
$stageCandidateRoot = $null
$childExitCode = $null
$runScriptPath = $null
$executionArtifacts = @()
$jsonPatched = @()
$restoreAttempted = $false
$restoreSucceeded = $false
$failureText = $null

Ensure-Directory -Path $DownloadsRoot
Start-Transcript -Path $outerLogPath -Force | Out-Null

try {
    Write-Step -Percent 5 -Status 'Resolviendo rutas base'
    $runScriptPath = Join-Path $RepoRoot 'tools\hos\git_sentinel_modular\operator_tools\run_sentinel_execute.ps1'
    if (-not (Test-Path -LiteralPath $runScriptPath)) {
        throw "No existe run_sentinel_execute.ps1 en: $runScriptPath"
    }

    if ($WorkspaceRoot) {
        $resolvedWorkspace = $WorkspaceRoot
    }
    else {
        $resolvedWorkspace = Get-LatestWorkspace -RuntimeRoot $RuntimeRoot
    }
    if (-not (Test-Path -LiteralPath $resolvedWorkspace)) {
        throw "No existe WorkspaceRoot: $resolvedWorkspace"
    }

    if ($TargetRoot) {
        $resolvedTarget = $TargetRoot
    }
    else {
        $resolvedTarget = Join-Path $RepoRoot 'tools\hos\git_sentinel_modular'
    }
    if (-not (Test-Path -LiteralPath $resolvedTarget)) {
        throw "No existe TargetRoot: $resolvedTarget"
    }

    $workspaceCandidate = Join-Path $resolvedWorkspace 'candidate'
    if (-not (Test-Path -LiteralPath $workspaceCandidate)) {
        throw "No existe el candidate base del workspace: $workspaceCandidate"
    }

    if ($FullCandidateRoot) {
        if (-not (Test-Path -LiteralPath $FullCandidateRoot)) {
            throw "No existe FullCandidateRoot: $FullCandidateRoot"
        }
        $sourceMode = 'full_candidate'
    }
    else {
        if (-not $OverlayCandidateRoot) {
            $OverlayCandidateRoot = Join-Path $resolvedWorkspace 'controlled_diff_lab\overlay_candidate'
        }
        if (-not (Test-Path -LiteralPath $OverlayCandidateRoot)) {
            throw "No existe overlay candidate. Esperado en: $OverlayCandidateRoot"
        }
        $resolvedOverlay = $OverlayCandidateRoot
        $sourceMode = 'base_plus_overlay'
    }

    Write-Step -Percent 15 -Status 'Preparando backup y staging'
    $backupRoot = Join-Path $resolvedWorkspace ("candidate_wiring_backups\wire_" + $stamp)
    $originalCandidateBackup = Join-Path $backupRoot 'candidate_original'
    $jsonBackupRoot = Join-Path $backupRoot 'json_before'
    $stageCandidateRoot = Join-Path $backupRoot 'candidate_wired_stage'
    Ensure-Directory -Path $backupRoot
    Ensure-Directory -Path $jsonBackupRoot

    Copy-TreeWithProgress -Source $workspaceCandidate -Destination $originalCandidateBackup -Activity 'Respaldando candidate original'

    if ($sourceMode -eq 'full_candidate') {
        Copy-TreeWithProgress -Source $FullCandidateRoot -Destination $stageCandidateRoot -Activity 'Copiando full candidate cableado'
    }
    else {
        Copy-TreeWithProgress -Source $workspaceCandidate -Destination $stageCandidateRoot -Activity 'Copiando candidate base al staging'
        Copy-TreeWithProgress -Source $resolvedOverlay -Destination $stageCandidateRoot -Activity 'Aplicando overlay al staging'
    }

    Write-Step -Percent 35 -Status 'Respaldando y corrigiendo metadata del workspace'
    $jsonRelativePaths = @(
        'review_bundle\promotion_review.json',
        'cutover_bundle\release_candidate_summary.json',
        'execution_bundle\execution_plan.json'
    )

    foreach ($rel in $jsonRelativePaths) {
        $src = Join-Path $resolvedWorkspace $rel
        if (Test-Path -LiteralPath $src) {
            $backup = Join-Path $jsonBackupRoot $rel
            $backupParent = Split-Path -Parent $backup
            Ensure-Directory -Path $backupParent
            Copy-Item -LiteralPath $src -Destination $backup -Force
            if (Patch-JsonHints -Path $src -WorkspaceCandidateRoot $workspaceCandidate -ResolvedTargetRoot $resolvedTarget -ResolvedOverlayRoot $resolvedOverlay) {
                $jsonPatched += $src
            }
        }
    }

    Write-Step -Percent 50 -Status 'Inyectando candidate cableado al workspace'
    Remove-PathIfExists -Path $workspaceCandidate
    Copy-TreeWithProgress -Source $stageCandidateRoot -Destination $workspaceCandidate -Activity 'Materializando workspace\\candidate cableado'

    Write-Step -Percent 70 -Status 'Ejecutando run_sentinel_execute.ps1 -Mode plan'
    & powershell.exe -ExecutionPolicy Bypass -File $runScriptPath -Mode plan -RepoRoot $RepoRoot -DownloadsRoot $DownloadsRoot -WorkspaceRoot $resolvedWorkspace -TargetRoot $resolvedTarget
    $childExitCode = $LASTEXITCODE
    if ($null -eq $childExitCode) { $childExitCode = 0 }

    Write-Step -Percent 82 -Status 'Reuniendo artefactos exportados'
    $executionArtifacts = @(Get-ChildItem -LiteralPath $DownloadsRoot -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
        $_.LastWriteTime -ge $startTime -and (
            $_.Name -match 'execution' -or
            $_.Name -match 'sentinel_execute' -or
            $_.Name -match 'planned_actions' -or
            $_.Name -match 'promotion'
        )
    } | Sort-Object LastWriteTime, FullName | Select-Object -ExpandProperty FullName)

    if ($childExitCode -ne 0) {
        throw "run_sentinel_execute.ps1 regresó exit code $childExitCode"
    }
}
catch {
    $failureText = $_.Exception.Message
    if ($null -eq $childExitCode) { $childExitCode = 1 }
    Write-Host "ERROR: $failureText" -ForegroundColor Red
}
finally {
    try {
        if (-not $KeepCandidateWired -and $resolvedWorkspace -and $workspaceCandidate -and $originalCandidateBackup -and (Test-Path -LiteralPath $originalCandidateBackup)) {
            Write-Step -Percent 90 -Status 'Restaurando candidate y metadata original'
            $restoreAttempted = $true
            Remove-PathIfExists -Path $workspaceCandidate
            Copy-TreeWithProgress -Source $originalCandidateBackup -Destination $workspaceCandidate -Activity 'Restaurando candidate original'

            foreach ($rel in @('review_bundle\promotion_review.json','cutover_bundle\release_candidate_summary.json','execution_bundle\execution_plan.json')) {
                $backup = Join-Path $jsonBackupRoot $rel
                $dst = Join-Path $resolvedWorkspace $rel
                if (Test-Path -LiteralPath $backup) {
                    $parent = Split-Path -Parent $dst
                    Ensure-Directory -Path $parent
                    Copy-Item -LiteralPath $backup -Destination $dst -Force
                }
            }
            $restoreSucceeded = $true
        }
        elseif ($KeepCandidateWired) {
            $restoreAttempted = $false
            $restoreSucceeded = $false
        }
    }
    catch {
        $restoreAttempted = $true
        $restoreSucceeded = $false
        if (-not $failureText) {
            $failureText = "Falló restauración: $($_.Exception.Message)"
        }
        else {
            $failureText = $failureText + " | Falló restauración: " + $_.Exception.Message
        }
    }

    $result = [pscustomobject]@{
        timestamp = $stamp
        status = if ($failureText) { 'failed' } else { 'ok' }
        child_exit_code = $childExitCode
        failure = $failureText
        repo_root = $RepoRoot
        downloads_root = $DownloadsRoot
        runtime_root = $RuntimeRoot
        workspace_root = $resolvedWorkspace
        target_root = $resolvedTarget
        run_script_path = $runScriptPath
        source_mode = $sourceMode
        workspace_candidate_root = $workspaceCandidate
        overlay_candidate_root = $resolvedOverlay
        full_candidate_root = $FullCandidateRoot
        original_candidate_backup = $originalCandidateBackup
        stage_candidate_root = $stageCandidateRoot
        json_patched = $jsonPatched
        outer_log_path = $outerLogPath
        execution_artifacts = $executionArtifacts
        restore_attempted = $restoreAttempted
        restore_succeeded = $restoreSucceeded
        keep_candidate_wired = [bool]$KeepCandidateWired
        base_candidate_file_count = if ($originalCandidateBackup -and (Test-Path -LiteralPath $originalCandidateBackup)) { Get-FileCount -Root $originalCandidateBackup } else { 0 }
        effective_candidate_file_count = if ($workspaceCandidate -and (Test-Path -LiteralPath $workspaceCandidate)) { Get-FileCount -Root $workspaceCandidate } else { 0 }
        overlay_file_count = if ($resolvedOverlay -and (Test-Path -LiteralPath $resolvedOverlay)) { Get-FileCount -Root $resolvedOverlay } else { 0 }
    }

    Write-JsonFile -Path $resultJsonPath -Object $result

    $lines = @()
    $lines += '# execute candidate wiring v2'
    $lines += ''
    $lines += "- status: $($result.status)"
    $lines += "- child_exit_code: $($result.child_exit_code)"
    if ($result.failure) { $lines += "- failure: $($result.failure)" }
    $lines += "- workspace_root: $($result.workspace_root)"
    $lines += "- target_root: $($result.target_root)"
    $lines += "- source_mode: $($result.source_mode)"
    $lines += "- workspace_candidate_root: $($result.workspace_candidate_root)"
    if ($result.overlay_candidate_root) { $lines += "- overlay_candidate_root: $($result.overlay_candidate_root)" }
    if ($result.full_candidate_root) { $lines += "- full_candidate_root: $($result.full_candidate_root)" }
    $lines += "- original_candidate_backup: $($result.original_candidate_backup)"
    $lines += "- stage_candidate_root: $($result.stage_candidate_root)"
    $lines += "- restore_attempted: $($result.restore_attempted)"
    $lines += "- restore_succeeded: $($result.restore_succeeded)"
    $lines += "- outer_log_path: $($result.outer_log_path)"
    $lines += "- base_candidate_file_count: $($result.base_candidate_file_count)"
    $lines += "- effective_candidate_file_count: $($result.effective_candidate_file_count)"
    $lines += "- overlay_file_count: $($result.overlay_file_count)"
    $lines += ''
    $lines += '## patched_json'
    if ($jsonPatched.Count -gt 0) {
        foreach ($p in $jsonPatched) { $lines += "- $p" }
    }
    else {
        $lines += '- none'
    }
    $lines += ''
    $lines += '## execution_artifacts'
    if ($executionArtifacts.Count -gt 0) {
        foreach ($p in $executionArtifacts) { $lines += "- $p" }
    }
    else {
        $lines += '- none_detected_after_run'
    }

    [System.IO.File]::WriteAllText($resultMdPath, ($lines -join "`r`n"), [System.Text.UTF8Encoding]::new($false))

    Write-Step -Percent 100 -Status 'Resultado exportado a Descargas'
    Write-Host ''
    Write-Host '=== EXECUTE CANDIDATE WIRING V2 ===' -ForegroundColor Green
    Write-Host "JSON: $resultJsonPath" -ForegroundColor White
    Write-Host "MD:   $resultMdPath" -ForegroundColor White
    Write-Host "LOG:  $outerLogPath" -ForegroundColor White

    Stop-Transcript | Out-Null
    Write-Progress -Id 1 -Activity 'Wiring candidate into sentinel_execute' -Completed

    if ($failureText) {
        throw $failureText
    }
}
