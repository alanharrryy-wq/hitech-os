[CmdletBinding()]
param(
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $scriptDir "..\\..")).Path
}

$gitDir = Join-Path $RepoRoot ".git"
if (-not (Test-Path -Path $gitDir -PathType Container)) {
    throw "Invalid git repository: $RepoRoot"
}

$hooksDir = Join-Path $gitDir "hooks"
New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null

$hookFile = Join-Path $hooksDir "pre-commit"
$markerStart = "# >>> HITECH_DOCS_GOVERNOR >>>"
$markerEnd = "# <<< HITECH_DOCS_GOVERNOR <<<"

$snippetLines = @(
    $markerStart
    'repo_root=$(git rev-parse --show-toplevel 2>/dev/null)'
    'if [ -z "$repo_root" ]; then'
    '  repo_root="$(pwd)"'
    'fi'
    'if command -v python >/dev/null 2>&1; then'
    '  python "$repo_root/tools/docs_governor/docs_governor.py" --repo "$repo_root" || exit 1'
    'elif command -v py >/dev/null 2>&1; then'
    '  py -3 "$repo_root/tools/docs_governor/docs_governor.py" --repo "$repo_root" || exit 1'
    'else'
    '  echo "docs-governor: python runtime not found"'
    '  exit 1'
    'fi'
    $markerEnd
)
$snippet = ($snippetLines -join "`n")

if (-not (Test-Path -Path $hookFile -PathType Leaf)) {
    Set-Content -Path $hookFile -Value "#!/bin/sh`n" -Encoding UTF8
}

$existing = Get-Content -Path $hookFile -Raw
if ($existing -like "*$markerStart*") {
    Write-Output "Marker section already installed in $hookFile"
    exit 0
}

if (-not $existing.EndsWith("`n")) {
    Add-Content -Path $hookFile -Value "`n" -Encoding UTF8
}
Add-Content -Path $hookFile -Value $snippet -Encoding UTF8
Write-Output "Installed docs governor pre-commit hook at $hookFile"
