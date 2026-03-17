param(
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$WorkspaceRoot
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechRuntimeDirectories -Paths $paths | Out-Null

$resolvedWorkspace = Resolve-HitechWorkspaceRoot -ShadowRoot $paths.ShadowRoot -WorkspaceRoot $WorkspaceRoot
if (!$resolvedWorkspace) {
    throw "No hay shadow workspace válido. Primero crea uno con create_shadow_workspace.ps1."
}

Show-HitechExecutionBanner `
    -Title "HITECH Pipeline Validation Runner" `
    -WorkspaceRoot $resolvedWorkspace `
    -TargetRoot $paths.ModularRoot `
    -ModularRoot $paths.ModularRoot

Write-HitechProgress -Activity "Diagnóstico del workspace" -Step 1 -TotalSteps 3
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $scriptDir "diagnose_sentinel_execute.ps1") -RepoRoot $RepoRoot -WorkspaceRoot $resolvedWorkspace

Write-HitechProgress -Activity "Preparando pipeline no-op" -Step 2 -TotalSteps 3
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $scriptDir "prepare_noop_review_pipeline.ps1") -RepoRoot $RepoRoot -WorkspaceRoot $resolvedWorkspace

Write-HitechProgress -Activity "Corriendo execute plan" -Step 3 -TotalSteps 3
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $scriptDir "run_sentinel_execute.ps1") -RepoRoot $RepoRoot -WorkspaceRoot $resolvedWorkspace -Mode plan

Write-Host ""
Write-Host "Validación completa."
