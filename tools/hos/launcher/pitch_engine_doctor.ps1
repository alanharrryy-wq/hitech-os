param(
  [switch]$SkipBrowserInstall
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..\..")

Write-Host "[pitch-engine-doctor] repoRoot=$repoRoot"

$extra = @()
if ($SkipBrowserInstall) {
  $extra += "--skip-browser-install"
}

Push-Location $repoRoot
try {
  pnpm --filter @hitech/keystone run keystone:pitch:doctor -- $extra
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} finally {
  Pop-Location
}
