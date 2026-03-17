param(
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$DownloadsRoot = "F:\OneDrive\Descargas",
    [string]$WorkspaceRoot,
    [string]$PolicyPath
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

$logPath = Start-HitechLogTranscript -Paths $paths -LogPrefix "sentinel_promotion" -WorkspaceRoot $resolvedWorkspace

try {
    $pythonPath = Set-HitechPythonEnv -ModularRoot $paths.ModularRoot

    Show-HitechExecutionBanner `
        -Title "HITECH Sentinel Promotion Runner" `
        -WorkspaceRoot $resolvedWorkspace `
        -TargetRoot "" `
        -ModularRoot $paths.ModularRoot `
        -DownloadsRoot $paths.DownloadsRoot

    $args = @(
        "--workspace-root",
        $resolvedWorkspace
    )

    if ($PolicyPath) {
        $args += "--policy"
        $args += $PolicyPath
    }

    Write-HitechProgress -Activity "Ejecutando sentinel_promotion" -Step 4 -TotalSteps 5
    Invoke-HitechPythonModule -ModuleName "sentinel_promotion" -Arguments $args

    $moved = Move-HitechBundleToDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName "review_bundle"

    Write-HitechProgress -Activity "Finalizando runner de sentinel_promotion" -Step 5 -TotalSteps 5
    Write-Host ""
    Write-Host "Runner terminado correctamente."
    if ($moved) {
        Write-Host "Bundle movido a:"
        Write-Host $moved
    }
    Write-Host "Log:"
    Write-Host $logPath
}
finally {
    Stop-HitechLogTranscript
}
