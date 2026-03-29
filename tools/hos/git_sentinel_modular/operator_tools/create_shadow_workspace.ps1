param(
    [string]$RepoRoot = "F:\repos\hitech-os",
    [string]$RunId
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechRuntimeDirectories -Paths $paths | Out-Null
$pythonPath = Set-HitechPythonEnv -ModularRoot $paths.ModularRoot

Write-HitechProgress -Activity "Creando shadow workspace" -Step 1 -TotalSteps 4
Show-HitechExecutionBanner `
    -Title "HITECH Shadow Workspace Creator" `
    -WorkspaceRoot "" `
    -TargetRoot "" `
    -ModularRoot $paths.ModularRoot

$scriptPath = Join-Path $scriptDir "shadow_prepare.py"

$args = @(
    "--modular-root",
    $paths.ModularRoot
)

if ($RunId) {
    $args += "--run-id"
    $args += $RunId
}

Write-HitechProgress -Activity "Creando shadow workspace" -Step 3 -TotalSteps 4
Invoke-HitechPythonScript -ScriptPath $scriptPath -Arguments $args

Write-HitechProgress -Activity "Creando shadow workspace" -Step 4 -TotalSteps 4
Write-Host ""
Write-Host "Shadow workspace creado correctamente."
