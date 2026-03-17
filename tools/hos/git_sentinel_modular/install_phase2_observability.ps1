param(
    [string]$RepoRoot = "F:\repos\hitech-os"
)

$downloads = "F:\OneDrive\Descargas"
$zip = "$downloads\git_sentinel_phase2_observability.zip"
$target = Join-Path $RepoRoot "tools\hos\git_sentinel_modular"

Write-Host ""
Write-Host "==== Installing Sentinel Observability Pack ===="
Write-Host ""

if (!(Test-Path $zip)) {
    Write-Host "ERROR: ZIP not found in $downloads"
    exit 1
}

for ($i=0; $i -le 100; $i+=10) {
    Write-Progress -Activity "Installing Observability Pack" -Status "$i% completed" -PercentComplete $i
    Start-Sleep -Milliseconds 120
}

Expand-Archive -Path $zip -DestinationPath $target -Force

Write-Host ""
Write-Host "Observability modules installed:"
Write-Host "$target\sentinel_observability"
Write-Host ""
Write-Host "Done."
