param(
    [string]$RepoRoot = "F:\repos\hitech-os"
)

$target = Join-Path $RepoRoot "tools\hos\git_sentinel_modular"
$downloads = "F:\OneDrive\Descargas"
$zip = Join-Path $downloads "git_sentinel_phase2_guardrails.zip"

Write-Host "HITECH Sentinel Phase2 Installer"
Write-Host "Target repo: $target"
Write-Host ""

if (!(Test-Path $zip)) {
    Write-Host "ZIP not found in $downloads"
    exit 1
}

Write-Host "Extracting guardrails..."

Expand-Archive -Path $zip -DestinationPath $target -Force

Write-Host ""
Write-Host "Guardrails installed in:"
Write-Host "$target\guardrails"
Write-Host ""
Write-Host "Done."
