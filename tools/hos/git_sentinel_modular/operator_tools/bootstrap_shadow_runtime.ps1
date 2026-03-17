param(
    [string]$RepoRoot = "F:\repos\hitech-os"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$paths = Get-HitechPaths -RepoRoot $RepoRoot
Assert-HitechRepoPaths -Paths $paths

for ($i = 0; $i -le 100; $i += 10) {
    Write-HitechProgress -Activity "Creando runtime base de Git Sentinel" -Step ($i/10 + 1) -TotalSteps 11
    Start-Sleep -Milliseconds 45
}

$created = Ensure-HitechRuntimeDirectories -Paths $paths

Write-Host ""
Write-Host "Runtime preparado correctamente."
Write-Host "Rutas base:"
Write-Host " - RuntimeRoot: $($paths.RuntimeRoot)"
Write-Host " - ShadowRoot:  $($paths.ShadowRoot)"
Write-Host ""
Write-Host "Directorios asegurados:"
$created | ForEach-Object { Write-Host (" - " + $_) }
