[CmdletBinding()]
param(
    [string]$BaseUrl = "http://localhost:3100",
    [switch]$IncludeApi,
    [int]$DelayMs = 250,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Normalize-BaseUrl {
    param([string]$Value)

    $trimmed = $Value.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) {
        throw "BaseUrl no puede estar vacio."
    }
    return $trimmed.TrimEnd("/")
}

$base = Normalize-BaseUrl -Value $BaseUrl

$uiPaths = @(
    "/",
    "/pitch",
    "/pitch/01-double-engine",
    "/pitch/02-industrial-flow",
    "/pitch/03-hitech-os",
    "/pitch/04-valuation",
    "/pitch/05-inventory-foundation",
    "/pitch/06-shipments-receiving"
)

$apiPaths = @(
    "/api/runs",
    "/api/activity",
    "/api/widgets"
)

$allUrls = New-Object System.Collections.Generic.List[string]
foreach ($path in $uiPaths) {
    $allUrls.Add("$base$path") | Out-Null
}
if ($IncludeApi) {
    foreach ($path in $apiPaths) {
        $allUrls.Add("$base$path") | Out-Null
    }
}

foreach ($url in $allUrls) {
    if ($DryRun) {
        Write-Host "[dry-run] $url"
    }
    else {
        Start-Process $url
        if ($DelayMs -gt 0) {
            Start-Sleep -Milliseconds $DelayMs
        }
    }
}

Write-Host ""
Write-Host ("Opened URLs: {0}" -f $allUrls.Count)
Write-Host ("BaseUrl: {0}" -f $base)
Write-Host ("IncludeApi: {0}" -f [bool]$IncludeApi)
