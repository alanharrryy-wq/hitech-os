[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RunId,

    [Parameter(Mandatory = $true)]
    [string]$PromptsPackPath,

    [Nullable[int]]$WindowReadyTimeout,
    [Nullable[int]]$ReadinessTimeout,
    [Nullable[int]]$WorkerDoneTimeout,
    [Nullable[int]]$BetweenWorkersDelayMs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$runIterPath = Join-Path $PSScriptRoot "run_iter.ps1"
if (-not (Test-Path $runIterPath)) {
    throw "run_iter.ps1 not found: $runIterPath"
}

$args = @()
if (-not [string]::IsNullOrWhiteSpace($RunId)) {
    $args += @("-RunId", $RunId)
}
$args += @("-PromptsPackPath", $PromptsPackPath, "-SkipInitialDispatch")
if ($null -ne $WindowReadyTimeout) {
    $args += @("-WindowReadyTimeout", [string]$WindowReadyTimeout)
}
if ($null -ne $ReadinessTimeout) {
    $args += @("-ReadinessTimeout", [string]$ReadinessTimeout)
}
if ($null -ne $WorkerDoneTimeout) {
    $args += @("-WorkerDoneTimeout", [string]$WorkerDoneTimeout)
}
if ($null -ne $BetweenWorkersDelayMs) {
    $args += @("-BetweenWorkersDelayMs", [string]$BetweenWorkersDelayMs)
}

& $runIterPath @args
exit $LASTEXITCODE
