param([string]$RepoRoot = "F:\repos\hitech-os",[string]$DownloadsRoot = "F:\OneDrive\Descargas",[string]$WorkspaceRoot)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot -DownloadsRoot $DownloadsRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechOutputDirectories -Paths $paths

$resolvedWorkspace = Resolve-HitechWorkspaceRoot -ShadowRoot $paths.ShadowRoot -WorkspaceRoot $WorkspaceRoot
if (!$resolvedWorkspace) { throw "No hay shadow workspace válido." }

$logPath = Start-HitechLogTranscript -Paths $paths -LogPrefix "repair_workspace_bundles" -WorkspaceRoot $resolvedWorkspace
try {
    Write-HitechProgress -Activity "Reparando bundles del workspace desde Descargas" -Step 1 -TotalSteps 4
    $restored = @()
    foreach ($bundle in @("review_bundle","cutover_bundle")) {
        $out = Restore-HitechBundleFromDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName $bundle
        if ($out) { $restored += $bundle }
    }
    Write-HitechProgress -Activity "Reparando bundles del workspace desde Descargas" -Step 4 -TotalSteps 4
    Write-Host ""
    if ($restored.Count -gt 0) {
        Write-Host "Bundles restaurados al workspace:"
        $restored | ForEach-Object { Write-Host (" - " + $_) }
    } else {
        Write-Host "No encontré bundles para restaurar desde Descargas."
    }
    Write-Host "Workspace:"
    Write-Host $resolvedWorkspace
    Write-Host "Log:"
    Write-Host $logPath
}
finally { Stop-HitechLogTranscript }
