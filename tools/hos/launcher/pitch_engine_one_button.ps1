param(
  [string]$ProgramId = "hitech-pitch"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..\..")

Write-Host "[pitch-engine-onebutton] repoRoot=$repoRoot"
Write-Host "[pitch-engine-onebutton] programId=$ProgramId"

Push-Location $repoRoot
try {
  pnpm --filter @hitech/keystone run keystone:pitch:onebutton -- --programId=$ProgramId
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} finally {
  Pop-Location
}
