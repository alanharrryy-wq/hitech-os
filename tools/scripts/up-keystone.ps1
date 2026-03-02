[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$SkipClean,
    [switch]$SkipInstall,
    [switch]$KeystoneDev,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    $stamp = (Get-Date).ToString("HH:mm:ss")
    Write-Host "[$stamp] $Message"
}

function Invoke-External {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )

    if ($DryRun) {
        Write-Step "[dry-run] $FilePath $($Arguments -join ' ')"
        return 0
    }

    $pushed = $false
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        Push-Location $WorkingDirectory
        $pushed = $true
    }

    try {
        & $FilePath @Arguments 2>&1 | ForEach-Object { Write-Host $_ }
        if ($null -eq $LASTEXITCODE) {
            return 0
        }
        return [int]$LASTEXITCODE
    }
    finally {
        if ($pushed) {
            Pop-Location
        }
    }
}

function Get-ListeningPids {
    param([int]$Port)
    $conns = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($null -eq $conns) { return @() }
    return @($conns | Select-Object -ExpandProperty OwningProcess -Unique)
}

function Stop-Ports {
    param([int[]]$Ports)

    $seen = New-Object System.Collections.Generic.HashSet[int]
    foreach ($port in $Ports) {
        $procIds = Get-ListeningPids -Port $port
        foreach ($procId in $procIds) {
            if (-not $seen.Add([int]$procId)) { continue }
            if ($DryRun) {
                Write-Step "[dry-run] stop pid=$procId on port=$port"
                continue
            }
            try {
                Stop-Process -Id $procId -Force -ErrorAction Stop
                Write-Step "Stopped process pid=$procId (port $port)"
            }
            catch {
                Write-Step "WARN: could not stop pid=$procId (port $port): $($_.Exception.Message)"
            }
        }
    }
}

function Wait-Http {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 60
    )

    if ($DryRun) {
        Write-Step "[dry-run] wait http $Url"
        return $true
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
            Start-Sleep -Milliseconds 700
        }
    }
    return $false
}

function Find-KeystoneUrl {
    param(
        [int]$StartPort = 3100,
        [int]$EndPort = 3125,
        [int]$TimeoutSeconds = 75
    )

    if ($DryRun) {
        return "http://127.0.0.1:3100"
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        foreach ($port in $StartPort..$EndPort) {
            try {
                $resp = Invoke-WebRequest -Uri ("http://127.0.0.1:{0}" -f $port) -UseBasicParsing -TimeoutSec 2
                if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
                    return ("http://127.0.0.1:{0}" -f $port)
                }
            }
            catch {
                continue
            }
        }
        Start-Sleep -Milliseconds 700
    }
    return ""
}

function Start-DevWindow {
    param(
        [string]$Name,
        [string]$Command
    )

    if ($DryRun) {
        Write-Step "[dry-run] start $Name => $Command"
        return 0
    }

    $proc = Start-Process -FilePath "pwsh" -ArgumentList @("-NoExit", "-Command", $Command) -PassThru
    Write-Step "Started $Name pid=$($proc.Id)"
    return [int]$proc.Id
}

$repo = (Resolve-Path $RepoRoot).Path
Set-Location $repo
Write-Step "Repo root: $repo"

$pnpmCmd = Get-Command pnpm -ErrorAction SilentlyContinue
if ($null -eq $pnpmCmd) {
    throw "pnpm no esta disponible en PATH"
}

$portsToStop = @(3001) + (3100..3125)
Stop-Ports -Ports $portsToStop

$rootNodeModules = Join-Path $repo "node_modules"
if (-not $SkipClean) {
    if (Test-Path $rootNodeModules) {
        if ($DryRun) {
            Write-Step "[dry-run] remove $rootNodeModules"
        }
        else {
            Write-Step "Removing $rootNodeModules"
            Remove-Item -Recurse -Force $rootNodeModules
        }
    }
    else {
        Write-Step "node_modules already clean"
    }
}
else {
    Write-Step "SkipClean enabled"
}

if (-not $SkipInstall) {
    Write-Step "Installing workspace deps (pnpm -r install --force)"
    $rc = Invoke-External -FilePath $pnpmCmd.Source -Arguments @("-r", "install", "--force") -WorkingDirectory $repo
    if ($rc -ne 0) {
        throw "pnpm -r install --force fallo con rc=$rc"
    }
}
else {
    Write-Step "SkipInstall enabled"
}

$coreCmd = "Set-Location '$repo'; pnpm --filter @hitech/core-api dev"
$keystoneVerb = if ($KeystoneDev) { "dev" } else { "start" }
$keystoneCmd = "Set-Location '$repo'; pnpm --filter @hitech/keystone $keystoneVerb"

$corePid = Start-DevWindow -Name "core-api" -Command $coreCmd
$coreHealthy = Wait-Http -Url "http://127.0.0.1:3001/health" -TimeoutSeconds 60
if (-not $coreHealthy) {
    Write-Step "WARN: core-api no respondio /health dentro de 60s"
}
else {
    Write-Step "core-api healthy en http://127.0.0.1:3001/health"
}

$keystonePid = Start-DevWindow -Name "keystone" -Command $keystoneCmd
$keystoneUrl = Find-KeystoneUrl -StartPort 3100 -EndPort 3125 -TimeoutSeconds 75
if ([string]::IsNullOrWhiteSpace($keystoneUrl)) {
    Write-Step "WARN: keystone no respondio HTTP en 3100..3125"
}
else {
    Write-Step "keystone online en $keystoneUrl"
}

$result = [ordered]@{
    repo = $repo
    core_api = [ordered]@{
        pid = $corePid
        healthy = $coreHealthy
        url = "http://127.0.0.1:3001/health"
    }
    keystone = [ordered]@{
        pid = $keystonePid
        url = $keystoneUrl
    }
    dry_run = [bool]$DryRun
}

Write-Host ""
Write-Host ($result | ConvertTo-Json -Depth 5)
