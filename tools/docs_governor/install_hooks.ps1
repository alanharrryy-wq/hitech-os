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
    'report_dir="$repo_root/.git/docs-governor-reports"'
    'mkdir -p "$report_dir"'
    'if command -v python >/dev/null 2>&1; then'
    '  python "$repo_root/tools/docs_governor/docs_governor.py" --repo "$repo_root" --report-dir "$report_dir" || exit 1'
    'elif command -v py >/dev/null 2>&1; then'
    '  py -3 "$repo_root/tools/docs_governor/docs_governor.py" --repo "$repo_root" --report-dir "$report_dir" || exit 1'
    'else'
    '  echo "docs-governor: python runtime not found"'
    '  exit 1'
    'fi'
    $markerEnd
)
$snippet = ($snippetLines -join "`n")
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Convert-ToLf {
    param([string]$Text)
    if ($null -eq $Text) {
        return ""
    }
    $normalized = $Text.Replace("`r`n", "`n").Replace("`r", "`n")
    # Remove UTF-8 BOM if present in decoded content.
    return $normalized.TrimStart([char]0xFEFF)
}

$existing = if (Test-Path -Path $hookFile -PathType Leaf) {
    [System.IO.File]::ReadAllText($hookFile)
}
else {
    "#!/bin/sh`n"
}
$existing = Convert-ToLf -Text $existing

$pattern = "(?s)" + [regex]::Escape($markerStart) + ".*?" + [regex]::Escape($markerEnd)
if ([regex]::IsMatch($existing, $pattern)) {
    $updated = [regex]::Replace($existing, $pattern, $snippet, 1)
    $action = "Updated marker section"
}
else {
    $updated = $existing
    if (-not [string]::IsNullOrEmpty($updated) -and -not $updated.EndsWith("`n")) {
        $updated += "`n"
    }
    $updated += $snippet
    $action = "Installed marker section"
}

$updated = Convert-ToLf -Text $updated
if (-not $updated.EndsWith("`n")) {
    $updated += "`n"
}

[System.IO.File]::WriteAllText($hookFile, $updated, $utf8NoBom)
Write-Output "$action in $hookFile (UTF-8 no BOM, LF)"
