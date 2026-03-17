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
    throw "No hay shadow workspace válido. Primero crea uno o pasa -WorkspaceRoot."
}

$pythonPath = Set-HitechPythonEnv -ModularRoot $paths.ModularRoot
Show-HitechExecutionBanner `
    -Title "HITECH Diagnose sentinel_execute" `
    -WorkspaceRoot $resolvedWorkspace `
    -TargetRoot $paths.ModularRoot `
    -ModularRoot $paths.ModularRoot

$scriptPath = Join-Path $scriptDir "diagnose_workspace.py"
$args = @("--workspace-root", $resolvedWorkspace)
Invoke-HitechPythonScriptLogged -ScriptPath $scriptPath -Arguments $args -LogsRoot $paths.LogsRoot -LogPrefix "diagnose_workspace" | Out-Null

Write-Host ""
Write-Host "Diagnóstico completado."
