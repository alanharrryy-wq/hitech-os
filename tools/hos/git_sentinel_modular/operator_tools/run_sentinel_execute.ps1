param(
    [ValidateSet("plan", "execute")]
    [string]$Mode = "plan",
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$DownloadsRoot = "F:\OneDrive\Descargas",
    [string]$WorkspaceRoot,
    [string]$TargetRoot,
    [string]$PolicyPath,
    [switch]$DoExecute,
    [string]$ConfirmToken = "EXECUTE_MANUAL_PROMOTION"
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

$resolvedTarget = if ($TargetRoot) { $TargetRoot } else { $paths.ModularRoot }
$logPath = Start-HitechLogTranscript -Paths $paths -LogPrefix "sentinel_execute" -WorkspaceRoot $resolvedWorkspace

try {
    $pythonPath = Set-HitechPythonEnv -ModularRoot $paths.ModularRoot

    Show-HitechExecutionBanner `
        -Title "HITECH Sentinel Execute Runner" `
        -WorkspaceRoot $resolvedWorkspace `
        -TargetRoot $resolvedTarget `
        -ModularRoot $paths.ModularRoot `
        -DownloadsRoot $paths.DownloadsRoot

    $args = @()
    if ($Mode -eq "plan") {
        $args += "plan"
        $args += "--workspace-root"
        $args += $resolvedWorkspace
        $args += "--target-root"
        $args += $resolvedTarget
        if ($PolicyPath) {
            $args += "--policy"
            $args += $PolicyPath
        }

        Write-HitechProgress -Activity "Ejecutando sentinel_execute plan" -Step 4 -TotalSteps 6
        Invoke-HitechPythonModule -ModuleName "sentinel_execute" -Arguments $args
    }
    else {
        $args += "execute"
        $args += "--workspace-root"
        $args += $resolvedWorkspace
        $args += "--target-root"
        $args += $resolvedTarget
        if ($PolicyPath) {
            $args += "--policy"
            $args += $PolicyPath
        }
        if ($DoExecute) {
            $args += "--do-execute"
            $args += "--confirm-token"
            $args += $ConfirmToken
        }

        Write-HitechProgress -Activity "Ejecutando sentinel_execute execute" -Step 4 -TotalSteps 6
        Invoke-HitechPythonModule -ModuleName "sentinel_execute" -Arguments $args
    }

    $moved = Move-HitechBundleToDownloads -Paths $paths -WorkspaceRoot $resolvedWorkspace -BundleName "execution_bundle"

    Write-HitechProgress -Activity "Finalizando runner de sentinel_execute" -Step 6 -TotalSteps 6
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
