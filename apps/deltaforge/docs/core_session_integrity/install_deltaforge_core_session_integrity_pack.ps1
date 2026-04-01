param(
    [string]$ZipPath = "F:\OneDrive\Descargas\deltaforge_core_session_integrity_pack_v1.zip",
    [string]$ExtractRoot = "F:\OneDrive\Descargas\DeltaForge_Core_Session_Integrity_Pack_v1",
    [string]$RepoPath = "F:\repos\hitech-os\apps\deltaforge"
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param(
        [int]$Percent,
        [string]$Status
    )
    Write-Progress -Activity "DeltaForge Core Session Integrity Pack" -Status $Status -PercentComplete $Percent
}

try {
    Write-Step -Percent 5 -Status "Validando rutas"

    if (-not (Test-Path -LiteralPath $ZipPath)) {
        throw "No encontré el zip en: $ZipPath"
    }

    if (-not (Test-Path -LiteralPath (Split-Path -Parent $ExtractRoot))) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $ExtractRoot) -Force | Out-Null
    }

    Write-Step -Percent 20 -Status "Preparando carpeta destino"
    if (Test-Path -LiteralPath $ExtractRoot) {
        Remove-Item -LiteralPath $ExtractRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null

    Write-Step -Percent 45 -Status "Extrayendo paquete"
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractRoot -Force

    $DocsTarget = Join-Path $RepoPath "docs\core_session_integrity"
    Write-Step -Percent 70 -Status "Intentando copiar docs al repo"
    if (Test-Path -LiteralPath $RepoPath) {
        if (Test-Path -LiteralPath $DocsTarget) {
            Remove-Item -LiteralPath $DocsTarget -Recurse -Force
        }
        New-Item -ItemType Directory -Path $DocsTarget -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $ExtractRoot "*") -Destination $DocsTarget -Recurse -Force
    }

    Write-Step -Percent 100 -Status "Listo"
    Write-Progress -Activity "DeltaForge Core Session Integrity Pack" -Completed

    Write-Host ""
    Write-Host "OK: paquete extraído en $ExtractRoot"
    if (Test-Path -LiteralPath $RepoPath) {
        Write-Host "OK: docs copiadas a $DocsTarget"
    } else {
        Write-Host "AVISO: no encontré el repo en $RepoPath; solo extraje el paquete."
    }
}
catch {
    Write-Progress -Activity "DeltaForge Core Session Integrity Pack" -Completed
    Write-Host "ERROR: $($_.Exception.Message)"
    exit 1
}
