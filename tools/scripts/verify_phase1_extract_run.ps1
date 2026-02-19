param(
  [string]$RunId = "RUN_PHASE1_EXTRACT_017"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $repoRoot
try {
  $cmd = @(
    "-m",
    "tools.codex.verify.verify_phase1_extract_run",
    "--run-id",
    $RunId
  )
  Write-Host "[verify] python $($cmd -join ' ')"
  & python @cmd
  $rc = $LASTEXITCODE

  $verdictPath = Join-Path $repoRoot "tools\codex\runs\$RunId\VERIFY_VERDICT.md"
  if (Test-Path -LiteralPath $verdictPath) {
    Write-Host "[verify] verdict: $verdictPath"
    $head = Get-Content -LiteralPath $verdictPath -TotalCount 20
    foreach ($line in $head) {
      Write-Host $line
    }
  } else {
    Write-Host "[verify] verdict file not found: $verdictPath"
  }

  exit $rc
}
finally {
  Pop-Location
}
