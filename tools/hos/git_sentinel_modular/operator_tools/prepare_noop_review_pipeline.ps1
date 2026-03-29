param(
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$WorkspaceRoot,
    [string]$PromotionPolicyPath,
    [string]$CutoverPolicyPath
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
    -Title "HITECH Prepare No-Op Review Pipeline" `
    -WorkspaceRoot $resolvedWorkspace `
    -TargetRoot $paths.ModularRoot `
    -ModularRoot $paths.ModularRoot

$scriptPath = Join-Path $scriptDir "prepare_noop_pipeline.py"
$args = @(
    "--modular-root", $paths.ModularRoot,
    "--workspace-root", $resolvedWorkspace
)

if ($PromotionPolicyPath) {
    $args += "--promotion-policy"
    $args += $PromotionPolicyPath
}
if ($CutoverPolicyPath) {
    $args += "--cutover-policy"
    $args += $CutoverPolicyPath
}

Invoke-HitechPythonScriptLogged -ScriptPath $scriptPath -Arguments $args -LogsRoot $paths.LogsRoot -LogPrefix "prepare_noop_pipeline" | Out-Null

Write-Host ""
Write-Host "Pipeline no-op preparado correctamente."
