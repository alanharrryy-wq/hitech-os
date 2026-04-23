param(
    [string[]]$Path = @(),
    [int]$Interval = 30,
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$repoRoot = (Resolve-Path (Join-Path $appRoot "..\..")).Path
if (-not $Root) {
    $Root = $appRoot
}

$localRoot = Join-Path $repoRoot "tools\_local"
$tmpDir = Join-Path $localRoot "tmp"
$logDir = Join-Path $localRoot "logs"
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$pidFile = Join-Path $tmpDir "synapse-x-watch.pid"
$stopFile = Join-Path $tmpDir "synapse-x-watch.stop"
$stdoutLog = Join-Path $logDir "synapse-x-watch.out.log"
$stderrLog = Join-Path $logDir "synapse-x-watch.err.log"

Remove-Item -LiteralPath $stopFile -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue

$runner = Join-Path $appRoot "run_engine.py"
$args = @($runner, "--root", $Root, "watch", "--interval", "$Interval", "--pid-file", $pidFile, "--stop-file", $stopFile)
foreach ($item in $Path) {
    $args += @("--path", $item)
}

$process = Start-Process -FilePath "python" -ArgumentList $args -WorkingDirectory $appRoot -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru
Start-Sleep -Milliseconds 300
if ($process.HasExited) {
    throw "watch-on failed: watcher process exited immediately (code $($process.ExitCode))"
}

$result = [ordered]@{
    status = "ok"
    pid = $process.Id
    pid_file = $pidFile
    stop_file = $stopFile
    stdout_log = $stdoutLog
    stderr_log = $stderrLog
}
Write-Output ($result | ConvertTo-Json -Depth 4)
