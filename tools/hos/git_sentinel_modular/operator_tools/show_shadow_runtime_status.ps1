param(
    [string]$RepoRoot = "F:\repos\hitech-os"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot
Assert-HitechRepoPaths -Paths $paths
Ensure-HitechRuntimeDirectories -Paths $paths | Out-Null

$workspaces = Get-ChildItem -Path $paths.ShadowRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

Write-Host ""
Write-Host "===== HITECH Shadow Runtime Status ====="
Write-Host "RuntimeRoot: $($paths.RuntimeRoot)"
Write-Host "ShadowRoot:  $($paths.ShadowRoot)"
Write-Host ""

if (!$workspaces -or $workspaces.Count -eq 0) {
    Write-Host "No hay workspaces todavía."
    Write-Host "Crea uno con:"
    Write-Host "powershell -ExecutionPolicy Bypass -File $($scriptDir)\create_shadow_workspace.ps1"
    exit 0
}

Write-Host "Workspaces detectados: $($workspaces.Count)"
$top = $workspaces | Select-Object -First 10
foreach ($w in $top) {
    Write-Host (" - " + $w.FullName)
}
