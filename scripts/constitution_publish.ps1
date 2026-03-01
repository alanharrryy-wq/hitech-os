param(
  [Parameter(Mandatory=$false)]
  [string]$RepoRoot = ".",

  [Parameter(Mandatory=$false)]
  [switch]$Validate,

  [Parameter(Mandatory=$false)]
  [switch]$Strict,

  [Parameter(Mandatory=$false)]
  [switch]$AutoInstallDeps
)

$ErrorActionPreference = "Stop"

function Resolve-PathSafe([string]$p) {
  try { return (Resolve-Path -LiteralPath $p).Path } catch { return $p }
}

$repo = Resolve-PathSafe $RepoRoot
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { throw "python not found in PATH" }

$render = Join-Path $repo "tools\hos\constitution\render_tables_md.py"
if (-not (Test-Path -LiteralPath $render)) { throw "render script not found: $render" }

Write-Host "Rendering tables -> docs/constitution/TABLES_RENDERED.md" -ForegroundColor Cyan
& python $render --root $repo
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Validate) {
  $check = Join-Path $repo "scripts\constitution_check.ps1"
  if (-not (Test-Path -LiteralPath $check)) { throw "check script not found: $check" }

  Write-Host "Validating tables..." -ForegroundColor Cyan
  $args = @("-RepoRoot", $repo)
  if ($Strict) { $args += "-Strict" }
  if ($AutoInstallDeps) { $args += "-AutoInstallDeps" }

  & pwsh -NoProfile -ExecutionPolicy Bypass -File $check @args
  exit $LASTEXITCODE
}

Write-Host "✅ Publish complete" -ForegroundColor Green
