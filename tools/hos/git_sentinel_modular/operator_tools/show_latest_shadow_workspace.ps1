param(
    [string]$RepoRoot = "F:\repos\hitech-os"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechRuntimeDirectories -Paths $paths | Out-Null

$workspace = Resolve-HitechWorkspaceRoot -ShadowRoot $paths.ShadowRoot -WorkspaceRoot ""

if ($workspace) {
    Write-Host $workspace
    exit 0
}

Write-Host ""
Write-Host "No encontré ningún shadow workspace válido todavía."
Write-Host "ShadowRoot ya quedó asegurado en:"
Write-Host $paths.ShadowRoot
Write-Host ""
Write-Host "Siguiente paso recomendado:"
Write-Host "powershell -ExecutionPolicy Bypass -File $($scriptDir)\create_shadow_workspace.ps1"
exit 0
