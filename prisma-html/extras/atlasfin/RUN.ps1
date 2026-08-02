param(
  [switch]$Open,
  [string]$UimapBatch,
  [string]$MamastrophicEvidence,
  [string]$ApplicationResult,
  [string]$ApplicationEvidence
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = $PSScriptRoot
$Validator = Join-Path $Root 'generator\validate_atlas.py'
$Generator = Join-Path $Root 'generator\build_canonical_visual_control.py'
$Py = Get-Command 'py.exe' -ErrorAction SilentlyContinue

function Invoke-AtlasPython {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
  if ($Py) { & $Py.Source -3 -u @Arguments }
  else { & (Get-Command 'python.exe' -ErrorAction Stop).Source -u @Arguments }
}

if ($UimapBatch) {
  $GeneratorArgs = @($Generator, $Root, '--uimap-batch', $UimapBatch)
  if ($MamastrophicEvidence) { $GeneratorArgs += @('--mamastrophic-evidence', $MamastrophicEvidence) }
  if ($ApplicationResult) { $GeneratorArgs += @('--application-result', $ApplicationResult) }
  if ($ApplicationEvidence) { $GeneratorArgs += @('--application-evidence', $ApplicationEvidence) }
  Invoke-AtlasPython @GeneratorArgs
  if ($LASTEXITCODE -ne 0) { throw "Atlasfin control generation failed with code $LASTEXITCODE" }
}

Invoke-AtlasPython $Validator $Root
if ($LASTEXITCODE -ne 0) { throw "ATLASFINAL validation failed with code $LASTEXITCODE" }
Write-Host 'PASS: PRISMA Visual Family Atlas completo; piloto V1 source-only y aplicación Cobrar gobernada.' -ForegroundColor Green
Write-Host '27 páginas · 26 secciones · 418 elementos · 1 piloto histórico · 1 resultado actual' -ForegroundColor Cyan
if ($Open) { Start-Process (Join-Path $Root 'index.html') }
