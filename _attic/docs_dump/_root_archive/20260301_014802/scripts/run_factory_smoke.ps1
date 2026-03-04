param(
  [string]$ProjectRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path -Path $ProjectRoot
Push-Location $root
try {
  pnpm run factory:build
  if ($LASTEXITCODE -ne 0) {
    throw "factory:build failed with code $LASTEXITCODE"
  }

  pnpm run factory:smoke
  if ($LASTEXITCODE -ne 0) {
    throw "factory:smoke failed with code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
