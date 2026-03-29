param(
  [Parameter(Mandatory=$false)]
  [string]$RepoRoot = ".",

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

$script = Join-Path $repo "tools\hos\constitution\validate_tables.py"
if (-not (Test-Path -LiteralPath $script)) { throw "validator not found: $script" }

# Optional dependency install
if ($AutoInstallDeps) {
  Write-Host "Installing validator dependencies (jsonschema)..." -ForegroundColor Yellow
  & python -m pip install --upgrade pip | Out-Null
  & python -m pip install jsonschema --quiet | Out-Null
}

$argStrict = @()
if ($Strict) { $argStrict = @("--strict") }

Write-Host "HITECH OS Constitution Check -> $repo"
& python $script --root $repo @argStrict
exit $LASTEXITCODE
