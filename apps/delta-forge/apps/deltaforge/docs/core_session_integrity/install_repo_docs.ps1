param(
    [string]$ZipPath = "F:\OneDrive\Descargas\deltaforge_core_session_integrity_repo_docs_v1.zip",
    [string]$RepoDocsPath = "F:\repos\hitech-os\apps\deltaforge\docs\core_session_integrity"
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([int]$Percent,[string]$Status)
    Write-Progress -Activity "DeltaForge Repo Docs" -Status $Status -PercentComplete $Percent
}

try {
    Write-Step -Percent 10 -Status "Validando zip"
    if (-not (Test-Path -LiteralPath $ZipPath)) {
        throw "No encontré el zip en: $ZipPath"
    }

    Write-Step -Percent 30 -Status "Preparando destino"
    if (Test-Path -LiteralPath $RepoDocsPath) {
        Remove-Item -LiteralPath $RepoDocsPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $RepoDocsPath -Force | Out-Null

    $TempDir = Join-Path $env:TEMP ("deltaforge_core_session_integrity_repo_docs_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

    Write-Step -Percent 60 -Status "Extrayendo docs"
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $TempDir -Force

    Write-Step -Percent 85 -Status "Copiando al repo"
    Copy-Item -LiteralPath (Join-Path $TempDir "*") -Destination $RepoDocsPath -Recurse -Force

    Remove-Item -LiteralPath $TempDir -Recurse -Force

    Write-Step -Percent 100 -Status "Listo"
    Write-Progress -Activity "DeltaForge Repo Docs" -Completed
    Write-Host "OK: docs instaladas en $RepoDocsPath"
}
catch {
    Write-Progress -Activity "DeltaForge Repo Docs" -Completed
    Write-Host "ERROR: $($_.Exception.Message)"
    exit 1
}
