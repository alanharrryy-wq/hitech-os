#requires -Version 7.0
param(
    [string]$RepoRoot = 'F:\repos\hitech-os',
    [string]$Logs = 'F:\descargasf',
    [switch]$NoOpen
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$TerminalRoot = Join-Path $RepoRoot 'apps\terminal-de-venta-system'
$EitRoot = Join-Path $RepoRoot 'apps\external_interaction_template'
$RunId = Get-Date -Format 'yyMMdd_HHmm'
$Log = Join-Path $Logs ('prisma_cloudflare_industrial_' + $RunId + '.log')
$Config = Join-Path $env:USERPROFILE '.cloudflared\config.yml'

New-Item -ItemType Directory -Force -Path $Logs | Out-Null

function Log {
    param([string]$Text = '')
    $Text | Tee-Object -FilePath $Log -Append | Out-Null
}

function Header {
    param([Parameter(Mandatory)][string]$Text)
    Log ''
    Log ('[' + $Text + ']')
    Write-Host ('`n[' + $Text + ']') -ForegroundColor Cyan
}

function Test-HttpUrl {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Url,
        [int]$TimeoutSec = 15
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
        $bytes = if ($null -ne $response.RawContentLength) { $response.RawContentLength } else { -1 }
        $line = 'OK    ' + $Name + '    ' + $response.StatusCode + '    ' + $Url + '    bytes=' + $bytes
        Write-Host $line -ForegroundColor Green
        Log $line
        return $true
    }
    catch {
        $line = 'FAIL  ' + $Name + '    ' + $Url + '    :: ' + $_.Exception.Message
        Write-Host $line -ForegroundColor Red
        Log $line
        return $false
    }
}

function Test-AnyHttpUrl {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string[]]$Urls,
        [int]$TimeoutSec = 15
    )

    foreach ($url in $Urls) {
        if (Test-HttpUrl -Name $Name -Url $url -TimeoutSec $TimeoutSec) {
            return $true
        }
    }
    return $false
}

function Get-PortOwner {
    param([Parameter(Mandatory)][int]$Port)

    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $conn) { return $null }

    $proc = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $conn.OwningProcess) -ErrorAction SilentlyContinue
    return [pscustomobject]@{
        Port = $Port
        OwnerPid = [int]$conn.OwningProcess
        CommandLine = [string]$proc.CommandLine
    }
}

function Stop-EitSafely {
    Header 'EIT safe stop'

    $owners = @(Get-NetTCPConnection -LocalPort 3110 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)

    foreach ($ownerPid in $owners) {
        if (-not $ownerPid) { continue }

        $proc = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $ownerPid) -ErrorAction SilentlyContinue
        $cmd = [string]$proc.CommandLine
        Log ('EIT candidate PID ' + $ownerPid + ' :: ' + $cmd)

        $low = $cmd.ToLowerInvariant()
        $eitRootLower = $EitRoot.ToLowerInvariant()

        $looksLikeEit = (
            $low.Contains($eitRootLower) -or
            ($low.Contains('external_interaction_template') -and $low.Contains('next')) -or
            ($low.Contains('next') -and $low.Contains('3110'))
        )

        if ($looksLikeEit) {
            Write-Host ('Stopping EIT PID ' + $ownerPid) -ForegroundColor Yellow
            Log ('STOP PID ' + $ownerPid)
            Stop-Process -Id $ownerPid -Force -ErrorAction SilentlyContinue
        }
        else {
            Write-Host ('Skip PID ' + $ownerPid + ' because it does not look like EIT.') -ForegroundColor DarkYellow
            Log ('SKIP PID ' + $ownerPid + ' not EIT')
        }
    }

    $eitRootLower2 = $EitRoot.ToLowerInvariant()
    $procs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -and $_.CommandLine.ToLowerInvariant().Contains($eitRootLower2)
    }

    foreach ($p in $procs) {
        Write-Host ('Stopping EIT process PID ' + $p.ProcessId) -ForegroundColor Yellow
        Log ('STOP EIT CMD PID ' + $p.ProcessId)
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }

    Start-Sleep -Seconds 2
}

function Get-PnpmCommandPath {
    $pnpmCmd = Get-Command pnpm.cmd -ErrorAction SilentlyContinue
    if (-not $pnpmCmd) {
        $pnpmCmd = Get-Command pnpm -ErrorAction Stop
    }
    return $pnpmCmd.Source
}

function Start-Eit {
    Header 'Starting EIT local 3110'

    if (-not (Test-Path -LiteralPath $EitRoot)) {
        Log ('FAIL missing EIT root: ' + $EitRoot)
        return $false
    }

    $eitPackageJson = Join-Path $EitRoot 'package.json'
    if (-not (Test-Path -LiteralPath $eitPackageJson)) {
        Log ('FAIL missing EIT package.json: ' + $eitPackageJson)
        return $false
    }

    Stop-EitSafely

    Remove-Item -Recurse -Force -LiteralPath (Join-Path $EitRoot '.next') -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force -LiteralPath (Join-Path $EitRoot 'node_modules\.cache') -ErrorAction SilentlyContinue

    $pnpm = Get-PnpmCommandPath
    $eitOutLog = Join-Path $Logs 'eit-3110.out.log'
    $eitErrLog = Join-Path $Logs 'eit-3110.err.log'

    Start-Process `
        -FilePath $pnpm `
        -ArgumentList @('-C', $EitRoot, 'exec', 'next', 'dev', '-p', '3110', '--webpack') `
        -WorkingDirectory $EitRoot `
        -RedirectStandardOutput $eitOutLog `
        -RedirectStandardError $eitErrLog `
        -WindowStyle Hidden | Out-Null

    Start-Sleep -Seconds 8

    for ($i = 1; $i -le 35; $i++) {
        if (Test-HttpUrl -Name 'EIT local' -Url 'http://127.0.0.1:3110/' -TimeoutSec 20) {
            return $true
        }
        Start-Sleep -Seconds 3
    }

    Log 'EIT failed to respond after restart.'

    if (Test-Path -LiteralPath $eitErrLog) {
        Log '--- EIT ERR tail ---'
        Get-Content -LiteralPath $eitErrLog -Tail 80 | Tee-Object -FilePath $Log -Append | Out-Null
    }

    if (Test-Path -LiteralPath $eitOutLog) {
        Log '--- EIT OUT tail ---'
        Get-Content -LiteralPath $eitOutLog -Tail 80 | Tee-Object -FilePath $Log -Append | Out-Null
    }

    return $false
}

function Ensure-MainApps {
    Header 'Checking local Tablet PC Mobile'

    $tablet = Test-AnyHttpUrl -Name 'Tablet local' -Urls @(
        'http://127.0.0.1:3120/',
        'http://127.0.0.1:3120/prisma-dark-pos-reference'
    ) -TimeoutSec 8

    $pc = Test-HttpUrl -Name 'PC local' -Url 'http://127.0.0.1:3130/' -TimeoutSec 8
    $mobile = Test-HttpUrl -Name 'Mobile local' -Url 'http://127.0.0.1:3140/' -TimeoutSec 8

    if ($tablet -and $pc -and $mobile) {
        return $true
    }

    $startAll = Join-Path $TerminalRoot 'terminal_de_venta_start_all.cmd'
    if (-not (Test-Path -LiteralPath $startAll)) {
        Log ('FAIL missing start_all launcher: ' + $startAll)
        return $false
    }

    Header 'Starting Tablet PC Mobile via start_all'
    Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $startAll) -WorkingDirectory $TerminalRoot -WindowStyle Normal | Out-Null
    Start-Sleep -Seconds 12

    for ($i = 1; $i -le 20; $i++) {
        $tablet = Test-AnyHttpUrl -Name 'Tablet local' -Urls @(
            'http://127.0.0.1:3120/',
            'http://127.0.0.1:3120/prisma-dark-pos-reference'
        ) -TimeoutSec 8

        $pc = Test-HttpUrl -Name 'PC local' -Url 'http://127.0.0.1:3130/' -TimeoutSec 8
        $mobile = Test-HttpUrl -Name 'Mobile local' -Url 'http://127.0.0.1:3140/' -TimeoutSec 8

        if ($tablet -and $pc -and $mobile) {
            return $true
        }
        Start-Sleep -Seconds 3
    }

    return $false
}

function Open-StableUrl {
    param([Parameter(Mandatory)][string]$Url)

    if ($NoOpen) {
        Log ('NOOPEN ' + $Url)
        return
    }

    try {
        Start-Process $Url
        Log ('OPEN ' + $Url)
    }
    catch {
        Log ('WARN open failed ' + $Url + ' :: ' + $_.Exception.Message)
    }
}

try {
    'PRISMA Cloudflare Industrial Launcher - ' + (Get-Date) | Tee-Object -FilePath $Log | Out-Null
    Log '================================================='
    Log 'Mode: stable industrial Cloudflare service. No trycloudflare.com quick tunnels.'
    Log ('Log: ' + $Log)
    Log ('RepoRoot: ' + $RepoRoot)

    Header 'Preflight'

    if (-not (Test-Path -LiteralPath $TerminalRoot)) {
        throw ('Missing terminal root: ' + $TerminalRoot)
    }

    $cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
    if (-not $cloudflared) {
        throw 'cloudflared not found in PATH.'
    }
    Log ('cloudflared: ' + $cloudflared.Source)

    if (-not (Test-Path -LiteralPath $Config)) {
        throw ('Missing cloudflared config: ' + $Config)
    }

    $svc = Get-Service cloudflared -ErrorAction SilentlyContinue
    if (-not $svc) {
        throw 'cloudflared service is not installed.'
    }

    Log (($svc | Format-List Name,Status,DisplayName | Out-String))

    if ($svc.Status -ne 'Running') {
        Write-Host 'cloudflared service is stopped. Starting...' -ForegroundColor Yellow
        Start-Service cloudflared
        Start-Sleep -Seconds 4
    }

    Header 'Validating cloudflared config'
    $raw = Get-Content -LiteralPath $Config -Raw

    $required = @(
        @{ Host = 'tablet.hitechrts.com'; Service = 'http://127.0.0.1:3120' },
        @{ Host = 'pc.hitechrts.com'; Service = 'http://127.0.0.1:3130' },
        @{ Host = 'prisma.hitechrts.com'; Service = 'http://127.0.0.1:3140' },
        @{ Host = 'eit.hitechrts.com'; Service = 'http://127.0.0.1:3110' }
    )

    $configOk = $true
    foreach ($route in $required) {
        $hostOk = $raw -match ('hostname:\s*' + [regex]::Escape($route.Host))
        $serviceOk = $raw -match ('service:\s*' + [regex]::Escape($route.Service))

        if ($hostOk -and $serviceOk) {
            Log ('OK config route ' + $route.Host + ' -> ' + $route.Service)
        }
        else {
            Write-Host ('FAIL config route missing ' + $route.Host + ' -> ' + $route.Service) -ForegroundColor Red
            Log ('FAIL config route missing ' + $route.Host + ' -> ' + $route.Service)
            $configOk = $false
        }
    }

    if ($raw -notmatch '(?m)^\s{2}-\sservice:\shttp_status:404\s*$') {
        Write-Host 'FAIL config fallback is missing or badly indented.' -ForegroundColor Red
        Log 'FAIL config fallback is missing or badly indented.'
        $configOk = $false
    }
    else {
        Log 'OK config fallback indentation'
    }

    $mainLocalOk = Ensure-MainApps
    $eitLocalOk = Test-HttpUrl -Name 'EIT local' -Url 'http://127.0.0.1:3110/' -TimeoutSec 20
    if (-not $eitLocalOk) {
        $eitLocalOk = Start-Eit
    }

    Header 'Testing public URLs'
    $tabletPublic = Test-HttpUrl -Name 'Tablet public' -Url 'https://tablet.hitechrts.com/' -TimeoutSec 20
    $pcPublic = Test-HttpUrl -Name 'PC public' -Url 'https://pc.hitechrts.com/' -TimeoutSec 20
    $mobilePublic = Test-HttpUrl -Name 'Mobile public' -Url 'https://prisma.hitechrts.com/' -TimeoutSec 20
    $installPublic = Test-HttpUrl -Name 'Mobile WhatsApp install' -Url 'https://prisma.hitechrts.com/prisma-app/install?from=whatsapp' -TimeoutSec 20
    $eitPublic = Test-HttpUrl -Name 'EIT public' -Url 'https://eit.hitechrts.com/' -TimeoutSec 25

    if ($mainLocalOk -and $eitLocalOk -and (-not ($tabletPublic -and $pcPublic -and $mobilePublic -and $installPublic -and $eitPublic))) {
        Header 'Public failed while local is OK. Restarting cloudflared once'
        try {
            Restart-Service cloudflared -Force
            Start-Sleep -Seconds 6
        }
        catch {
            Log ('WARN cloudflared restart failed: ' + $_.Exception.Message)
        }

        $tabletPublic = Test-HttpUrl -Name 'Tablet public retry' -Url 'https://tablet.hitechrts.com/' -TimeoutSec 20
        $pcPublic = Test-HttpUrl -Name 'PC public retry' -Url 'https://pc.hitechrts.com/' -TimeoutSec 20
        $mobilePublic = Test-HttpUrl -Name 'Mobile public retry' -Url 'https://prisma.hitechrts.com/' -TimeoutSec 20
        $installPublic = Test-HttpUrl -Name 'Mobile WhatsApp install retry' -Url 'https://prisma.hitechrts.com/prisma-app/install?from=whatsapp' -TimeoutSec 20
        $eitPublic = Test-HttpUrl -Name 'EIT public retry' -Url 'https://eit.hitechrts.com/' -TimeoutSec 25
    }

    Header 'Opening stable URLs'
    if ($tabletPublic) { Open-StableUrl 'https://tablet.hitechrts.com/' }
    if ($pcPublic) { Open-StableUrl 'https://pc.hitechrts.com/' }
    if ($mobilePublic) { Open-StableUrl 'https://prisma.hitechrts.com/' }
    if ($installPublic) { Open-StableUrl 'https://prisma.hitechrts.com/prisma-app/install?from=whatsapp' }
    if ($eitPublic) { Open-StableUrl 'https://eit.hitechrts.com/' }

    Header 'Result'
    $ready = $configOk -and $mainLocalOk -and $eitLocalOk -and $tabletPublic -and $pcPublic -and $mobilePublic -and $installPublic -and $eitPublic

    if ($ready) {
        Log '[RESULT] READY'
        Write-Host '[RESULT] READY' -ForegroundColor Green
        exit 0
    }

    if ($mainLocalOk -and $eitLocalOk) {
        Log '[RESULT] READY_WITH_CAVEATS'
        Write-Host '[RESULT] READY_WITH_CAVEATS - Local apps OK, but at least one public URL/config check failed.' -ForegroundColor Yellow
        Write-Host ('Log: ' + $Log) -ForegroundColor Yellow
        exit 1
    }

    Log '[RESULT] BLOCKED'
    Write-Host '[RESULT] BLOCKED - One or more local apps failed.' -ForegroundColor Red
    Write-Host ('Log: ' + $Log) -ForegroundColor Yellow
    exit 2
}
catch {
    Header 'Fatal error'
    Log ('FATAL ' + $_.Exception.Message)
    Write-Host ('FATAL: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host ('Log: ' + $Log) -ForegroundColor Yellow
    exit 3
}
