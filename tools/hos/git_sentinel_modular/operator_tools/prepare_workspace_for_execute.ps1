param(
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$DownloadsRoot = "F:\OneDrive\Descargas",
    [string]$WorkspaceRoot,
    [string]$PromotionPolicyPath,
    [string]$CutoverPolicyPath
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot -DownloadsRoot $DownloadsRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechOutputDirectories -Paths $paths

$resolvedWorkspace = Resolve-HitechWorkspaceRoot -ShadowRoot $paths.ShadowRoot -WorkspaceRoot $WorkspaceRoot
if (!$resolvedWorkspace) { throw "No hay shadow workspace válido." }

$logPath = Start-HitechLogTranscript -Paths $paths -LogPrefix "prepare_workspace_for_execute" -WorkspaceRoot $resolvedWorkspace
try {
    $null = Set-HitechPythonEnv -ModularRoot $paths.ModularRoot

    Show-HitechExecutionBanner -Title "HITECH Prepare Workspace For Execute" -WorkspaceRoot $resolvedWorkspace -TargetRoot "" -ModularRoot $paths.ModularRoot -DownloadsRoot $paths.DownloadsRoot
    Write-HitechProgress -Activity "Preparando workspace para execute" -Step 1 -TotalSteps 6

    $hasPromotion = Test-HitechWorkspaceHasFile -WorkspaceRoot $resolvedWorkspace -RelativePath "review_bundle\promotion_review.json"
    $hasCutover = Test-HitechWorkspaceHasFile -WorkspaceRoot $resolvedWorkspace -RelativePath "cutover_bundle\release_candidate_summary.json"

    if (-not $hasPromotion -or -not $hasCutover) {
        Write-Host "Faltan bundles en el workspace. Intentando restaurar desde Descargas..."
        foreach ($bundle in @("review_bundle","cutover_bundle")) {
            Restore-HitechBundleFromDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName $bundle | Out-Null
        }
    }

    $hasPromotion = Test-HitechWorkspaceHasFile -WorkspaceRoot $resolvedWorkspace -RelativePath "review_bundle\promotion_review.json"
    if (-not $hasPromotion) {
        Write-Host "No hay promotion_review en workspace. Ejecutando sentinel_promotion..."
        $args = @("--workspace-root",$resolvedWorkspace)
        if ($PromotionPolicyPath) { $args += "--policy"; $args += $PromotionPolicyPath }
        Invoke-HitechPythonModule -ModuleName "sentinel_promotion" -Arguments $args
        Export-HitechBundleToDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName "review_bundle" | Out-Null
    }

    Write-HitechProgress -Activity "Preparando workspace para execute" -Step 4 -TotalSteps 6

    $hasCutover = Test-HitechWorkspaceHasFile -WorkspaceRoot $resolvedWorkspace -RelativePath "cutover_bundle\release_candidate_summary.json"
    if (-not $hasCutover) {
        Write-Host "No hay cutover_summary en workspace. Ejecutando sentinel_cutover..."
        $args = @("--workspace-root",$resolvedWorkspace)
        if ($CutoverPolicyPath) { $args += "--policy"; $args += $CutoverPolicyPath }
        Invoke-HitechPythonModule -ModuleName "sentinel_cutover" -Arguments $args
        Export-HitechBundleToDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName "cutover_bundle" | Out-Null
    }

    Write-HitechProgress -Activity "Preparando workspace para execute" -Step 6 -TotalSteps 6
    Write-Host ""
    Write-Host "Workspace listo para execute."
    Write-Host "Workspace:"
    Write-Host $resolvedWorkspace
    Write-Host "Log:"
    Write-Host $logPath
}
finally { Stop-HitechLogTranscript }
