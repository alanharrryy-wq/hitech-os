param([string]$RepoRoot = "F:\repos\hitech-os",[string]$DownloadsRoot = "F:\OneDrive\Descargas",[string]$WorkspaceRoot,[string]$PolicyPath)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot -DownloadsRoot $DownloadsRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechOutputDirectories -Paths $paths

$resolvedWorkspace = Resolve-HitechWorkspaceRoot -ShadowRoot $paths.ShadowRoot -WorkspaceRoot $WorkspaceRoot
if (!$resolvedWorkspace) { throw "No hay shadow workspace válido." }

$logPath = Start-HitechLogTranscript -Paths $paths -LogPrefix "sentinel_cutover" -WorkspaceRoot $resolvedWorkspace
try {
    $null = Set-HitechPythonEnv -ModularRoot $paths.ModularRoot
    Show-HitechExecutionBanner -Title "HITECH Sentinel Cutover Runner" -WorkspaceRoot $resolvedWorkspace -TargetRoot "" -ModularRoot $paths.ModularRoot -DownloadsRoot $paths.DownloadsRoot
    $args = @("--workspace-root",$resolvedWorkspace)
    if ($PolicyPath) { $args += "--policy"; $args += $PolicyPath }
    Write-HitechProgress -Activity "Ejecutando sentinel_cutover" -Step 4 -TotalSteps 5
    Invoke-HitechPythonModule -ModuleName "sentinel_cutover" -Arguments $args
    $exported = Export-HitechBundleToDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName "cutover_bundle"
    Write-HitechProgress -Activity "Finalizando runner de sentinel_cutover" -Step 5 -TotalSteps 5
    Write-Host ""
    Write-Host "Runner terminado correctamente."
    if ($exported) { Write-Host "Bundle copiado a:"; Write-Host $exported }
    Write-Host "Log:"; Write-Host $logPath
}
finally { Stop-HitechLogTranscript }
