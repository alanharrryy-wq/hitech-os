$ErrorActionPreference = "Stop"

$TrashRoot = "F:\Trash-old"
$Stamp = Get-Date -Format "ddMM HHmmss"

$CurrentHub = "F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center\internal\prismo"
$CurrentDocs = "F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center\internal\docs\prismo-hub"
$PrevHub = "F:\Trash-old\prismo org1 0106 1143 internal_prismo_hub previous 01MM HHmmss\prismo"
$PrevDocs = "F:\Trash-old\prismo org1 0106 1143 docs_prismo_hub previous 01MM HHmmss\prismo-hub"

if (!(Test-Path -LiteralPath $TrashRoot)) {
  New-Item -ItemType Directory -Path $TrashRoot -Force | Out-Null
}

function Move-Current($Path, $Label) {
  if (Test-Path -LiteralPath $Path) {
    $Dest = Join-Path $TrashRoot "prismo org1 rollback $Label $Stamp"
    Move-Item -LiteralPath $Path -Destination $Dest -Force
    Write-Host "Moved current $Label to $Dest" -ForegroundColor Yellow
  }
}

Move-Current $CurrentHub "hub"
Move-Current $CurrentDocs "docs"

if ($PrevHub -and (Test-Path -LiteralPath $PrevHub)) {
  New-Item -ItemType Directory -Path (Split-Path $CurrentHub -Parent) -Force | Out-Null
  Move-Item -LiteralPath $PrevHub -Destination $CurrentHub -Force
  Write-Host "Restored previous PRISMO hub." -ForegroundColor Green
}

if ($PrevDocs -and (Test-Path -LiteralPath $PrevDocs)) {
  New-Item -ItemType Directory -Path (Split-Path $CurrentDocs -Parent) -Force | Out-Null
  Move-Item -LiteralPath $PrevDocs -Destination $CurrentDocs -Force
  Write-Host "Restored previous PRISMO docs hub." -ForegroundColor Green
}

Write-Host "Rollback complete." -ForegroundColor Green
