param(
  [switch]$NoOpen,
  [string]$LogDir = 'F:\descargasf'
)

$ErrorActionPreference = 'Stop'

$WrapperRoot = $PSScriptRoot
$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $WrapperRoot '..\..')).Path
$AtlasRoot = Join-Path $ControlRoot 'internal\docs\dependency-atlas'
$HtmlName = 'code_atlas_dependency_visual_v04_2_terminal-de-venta-system_prisma-control-center_Black_Glass_Atlas_260521_180055.html'
$HtmlPath = Join-Path $AtlasRoot $HtmlName
$SummaryPath = Join-Path $AtlasRoot 'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_summary.json'
$ManifestPath = Join-Path $AtlasRoot 'DEPENDENCY_ATLAS_MANIFEST.json'

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$RunRoot = Join-Path $env:TEMP 'PRISMA_DEPENDENCY_ATLAS_OPEN_RUNS'
$RunDir = Join-Path $RunRoot ('DEPENDENCY_ATLAS_OPEN_{0}' -f $Stamp)
$ZipPath = Join-Path $LogDir ('DEPENDENCY_ATLAS_OPEN_{0}.zip' -f $Stamp)
$LatestZip = Join-Path $LogDir 'latest_DEPENDENCY_ATLAS_OPEN.zip'
$SummaryOut = Join-Path $RunDir 'summary.json'
$TranscriptPath = Join-Path $RunDir 'transcript.log'

New-Item -ItemType Directory -Force -Path $LogDir, $RunDir | Out-Null
$TranscriptStarted = $false

try {
  Start-Transcript -Path $TranscriptPath -Force | Out-Null
  $TranscriptStarted = $true

  if (-not (Test-Path -LiteralPath $AtlasRoot)) { throw "Atlas dir not found: $AtlasRoot" }
  if (-not (Test-Path -LiteralPath $HtmlPath)) { throw "Atlas HTML not found: $HtmlPath" }
  if (-not (Test-Path -LiteralPath $SummaryPath)) { throw "Atlas summary not found: $SummaryPath" }
  if (-not (Test-Path -LiteralPath $ManifestPath)) { throw "Atlas manifest not found: $ManifestPath" }

  $Summary = Get-Content -LiteralPath $SummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
  $Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

  $Result = [ordered]@{
    ok = $true
    status = 'READY'
    opened = -not $NoOpen
    controlRoot = $ControlRoot
    atlasRoot = $AtlasRoot
    htmlPath = $HtmlPath
    generatedAt = [string]$Summary.generated_at
    filesScanned = [int]$Summary.dependency_summary.files_scanned
    sourceFiles = [int]$Summary.dependency_summary.source_files
    edges = [int]$Summary.dependency_summary.edges
    internalEdges = [int]$Summary.dependency_summary.internal_edges
    externalEdges = [int]$Summary.dependency_summary.external_edges
    unresolvedEdges = [int]$Summary.dependency_summary.unresolved_edges
    languages = @($Summary.project_profile.languages)
    bundleId = [string]$Manifest.bundleId
    runDir = $RunDir
  }

  $Result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $SummaryOut -Encoding UTF8

  Write-Host ''
  Write-Host '[PRISMA] Dependency Atlas listo.' -ForegroundColor Cyan
  Write-Host ('[PRISMA] Files scanned: {0}, source files: {1}, edges: {2}, unresolved: {3}' -f $Result.filesScanned, $Result.sourceFiles, $Result.edges, $Result.unresolvedEdges) -ForegroundColor DarkCyan
  Write-Host ('[PRISMA] HTML: {0}' -f $HtmlPath) -ForegroundColor DarkGray

  if (-not $NoOpen) {
    Start-Process -FilePath $HtmlPath
  }

  exit 0
} catch {
  $Err = [ordered]@{
    ok = $false
    status = 'FAILED'
    error = $_.Exception.Message
    controlRoot = $ControlRoot
    atlasRoot = $AtlasRoot
    runDir = $RunDir
  }
  $Err | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $SummaryOut -Encoding UTF8
  Write-Host ('[PRISMA] ERROR: {0}' -f $_.Exception.Message) -ForegroundColor Red
  exit 1
} finally {
  if ($TranscriptStarted) {
    try { Stop-Transcript | Out-Null } catch {}
  }
  try {
    Compress-Archive -LiteralPath (Join-Path $RunDir '*') -DestinationPath $ZipPath -Force
    Copy-Item -LiteralPath $ZipPath -Destination $LatestZip -Force
  } catch {}
}
