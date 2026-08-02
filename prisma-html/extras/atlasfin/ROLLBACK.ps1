$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Root = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $Root '..\..\..')).Path
$PilotPath = Join-Path $Root 'assets\data\visual-control.cobrar.pilot.json'
$Pilot = Get-Content -LiteralPath $PilotPath -Raw | ConvertFrom-Json

if ($Pilot.safety.runtimeMutationAllowed -ne $false -or
    $Pilot.safety.productApplicationAllowed -ne $false -or
    $Pilot.safety.sourceMutationPerformed -ne $false) {
  throw 'Rollback drill failed: the source-only mutation guard is not intact.'
}

foreach ($Entry in $Pilot.rollback.beforeHashes.PSObject.Properties) {
  $SourcePath = Join-Path $RepoRoot $Entry.Name
  if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
    throw "Rollback drill failed: protected source missing: $($Entry.Name)"
  }
  $Actual = (Get-FileHash -LiteralPath $SourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($Actual -ne [string]$Entry.Value) {
    throw "Rollback drill failed: protected source drift: $($Entry.Name)"
  }
}

$Validator = Join-Path $Root 'generator\validate_atlas.py'
$Py = Get-Command 'py.exe' -ErrorAction SilentlyContinue
if ($Py) { & $Py.Source -3 -u $Validator $Root }
else { & (Get-Command 'python.exe' -ErrorAction Stop).Source -u $Validator $Root }
if ($LASTEXITCODE -ne 0) { throw "Rollback validation failed with code $LASTEXITCODE" }

Write-Host 'PASS: no source mutation occurred; protected Cobrar files still match their before hashes.' -ForegroundColor Green
Write-Host 'Rollback action: none required for this source-only plan.' -ForegroundColor Cyan
exit 0
