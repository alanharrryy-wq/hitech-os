param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$repoRoot = (Resolve-Path (Join-Path $appRoot "..\..")).Path
$localRoot = Join-Path $repoRoot "tools\_local"
$tmpDir = Join-Path $localRoot "tmp"

$pidFile = Join-Path $tmpDir "synapse-x-watch.pid"
$stopFile = Join-Path $tmpDir "synapse-x-watch.stop"

New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
Set-Content -LiteralPath $stopFile -Value (Get-Date).ToString("o") -Encoding UTF8

$watchPid = $null
if (Test-Path -LiteralPath $pidFile) {
    $rawPid = Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    $parsedPid = 0
    if ($rawPid -and [int]::TryParse($rawPid, [ref]$parsedPid)) {
        $watchPid = $parsedPid
        for ($i = 0; $i -lt 40; $i++) {
            $proc = Get-Process -Id $watchPid -ErrorAction SilentlyContinue
            if (-not $proc) {
                break
            }
            Start-Sleep -Milliseconds 250
        }
        $stillRunning = Get-Process -Id $watchPid -ErrorAction SilentlyContinue
        if ($stillRunning) {
            Stop-Process -Id $watchPid -Force -ErrorAction SilentlyContinue
        }
    }
}

Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $stopFile -ErrorAction SilentlyContinue

$result = [ordered]@{
    status = "ok"
    pid = $watchPid
    message = "watch stop signal sent"
}
$result | ConvertTo-Json -Depth 4
