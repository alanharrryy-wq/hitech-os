$ErrorActionPreference = 'Stop'
Write-Host 'Code Atlas Debug Launcher' -ForegroundColor Cyan
Write-Host 'ProjectRoot: F:\repos\hitech-os\tools\code-atlas'
Write-Host 'Launcher   : F:\repos\hitech-os\tools\code-atlas\launcher'
& 'F:\repos\hitech-os\tools\code-atlas\launcher\Launch-CodeAtlas.ps1'
Write-Host 'Si no abrió, revisa F:\descargasf\code-atlas-error.txt' -ForegroundColor Yellow
