param(
    [int]$IntervalSec = 300,
    [switch]$Apply,
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
    "--iterations", "$Iterations"
)

if ($Apply) {
    $argsList += "--apply"
}
if ($Config -ne "") {
    $argsList += @("--config", $Config)
}

Write-Host "[git-sentinel] repo=$RepoRoot interval=$IntervalSec apply=$($Apply.IsPresent) iterations=$Iterations"
python @argsList

