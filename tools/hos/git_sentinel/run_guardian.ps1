param(
    [int]$IntervalSec = 0,
    [switch]$Apply,
    [switch]$ApplyCleanup,
    [switch]$ApplyRepair,
    [ValidateSet("safe", "strict", "aggressive")]
    [string]$Profile = "safe",
    [int]$Iterations = 0,
    [string]$Config = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Set-Location $RepoRoot

$argsList = @(
    "tools/hos/git_sentinel/cli_sentinel.py",
    "guardian",
    "--interval-sec", "$IntervalSec",
    "--iterations", "$Iterations",
    "--profile", "$Profile"
)

if ($Apply) {
    $argsList += "--apply"
}
if ($ApplyCleanup) {
    $argsList += "--apply-cleanup"
}
if ($ApplyRepair) {
    $argsList += "--apply-repair"
}
if ($Config -ne "") {
    $argsList += @("--config", $Config)
}

Write-Host "[git-sentinel] repo=$RepoRoot interval=$IntervalSec profile=$Profile apply=$($Apply.IsPresent) apply_cleanup=$($ApplyCleanup.IsPresent) apply_repair=$($ApplyRepair.IsPresent) iterations=$Iterations"
python @argsList
