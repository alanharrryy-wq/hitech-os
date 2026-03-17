param(
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$DownloadsRoot = "F:\OneDrive\Descargas",
    [string]$WorkspaceRoot
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot -DownloadsRoot $DownloadsRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechOutputDirectories -Paths $paths | Out-Null

$resolvedWorkspace = Resolve-HitechWorkspaceRoot -ShadowRoot $paths.ShadowRoot -WorkspaceRoot $WorkspaceRoot
if (!$resolvedWorkspace) {
    throw "No hay shadow workspace válido."
}

$bundles = @("review_bundle", "cutover_bundle", "execution_bundle")
foreach ($bundle in $bundles) {
    $moved = Move-HitechBundleToDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName $bundle
    if ($moved) {
        Write-Host "Movido:"
        Write-Host $moved
    }
}
