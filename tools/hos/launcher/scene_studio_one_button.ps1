param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..\..")

Write-Host "[scene-studio-onebutton] repoRoot=$repoRoot"

Push-Location $repoRoot
try {
  pnpm --filter @hitech/keystone run keystone:scene:onebutton
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} finally {
  Pop-Location
}
