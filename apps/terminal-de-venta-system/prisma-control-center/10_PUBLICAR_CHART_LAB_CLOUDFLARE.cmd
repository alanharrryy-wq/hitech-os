@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0."
set "LAUNCHER_ROOT=%~dp0."
set "STAMP=%DATE:/=-%_%TIME::=-%"
set "STAMP=%STAMP: =0%"
set "TEMP_PS=%TEMP%\PRISMA_CHART_LAB_CLOUDFLARE_DEPLOY_%RANDOM%_%RANDOM%.ps1"

echo.
echo ============================================================
echo PRISMA - publicar Chart Lab en Cloudflare Pages
echo Build + sanitize + verify + wrangler auth + deploy Pages
echo LauncherRoot: %LAUNCHER_ROOT%
echo Logs: F:\descargasf
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$raw = Get-Content -LiteralPath '%~f0' -Raw; $marker = '# POWERSHELL_PAYLOAD_BELOW_DO_NOT_EDIT'; $idx = $raw.LastIndexOf($marker); if ($idx -lt 0) { throw 'No encontre payload PowerShell embebido.' }; $payload = $raw.Substring($idx + $marker.Length).TrimStart([char]13,[char]10); Set-Content -LiteralPath '%TEMP_PS%' -Value $payload -Encoding UTF8"
if errorlevel 1 (
  echo [ERROR] No pude extraer el payload PowerShell.
  pause
  exit /b 1
)

where pwsh.exe >nul 2>nul
if "%ERRORLEVEL%"=="0" (
  pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TEMP_PS%" -LauncherRoot "%LAUNCHER_ROOT%" %*
) else (
  powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TEMP_PS%" -LauncherRoot "%LAUNCHER_ROOT%" %*
)

set "RC=%ERRORLEVEL%"
del "%TEMP_PS%" >nul 2>nul

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA Chart Lab Cloudflare deploy termino con exit code %RC%.
  echo Revisa F:\descargasf\latest_CHART_LAB_CLOUDFLARE_DEPLOY.zip
  pause
)

exit /b %RC%

# POWERSHELL_PAYLOAD_BELOW_DO_NOT_EDIT
param(
    [string]$LauncherRoot,
    [string]$Branch = "main",
    [string]$ProjectName = "prisma-chart-lab",
    [switch]$NoSanitize,
    [switch]$SkipLogin,
    [switch]$UseTokenWrapper,
    [switch]$OpenBrowser,
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$StartedAt = Get-Date
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"

$Downloads = "F:\descargasf"
$PrimaryLogRoot = "F:\OneDrive\Hitech\3.Proyectos\CHAT GPT AI Estudio\HITECH_AISTUDIO_SYSTEM\00.Resplogs\LOGS"
$LogRoot = if (Test-Path -LiteralPath $PrimaryLogRoot) { $PrimaryLogRoot } else { $Downloads }

$LauncherRoot = $LauncherRoot.Trim().Trim('"')
$LauncherRoot = (Resolve-Path -LiteralPath $LauncherRoot).Path.TrimEnd("\")

# Auto-detect real terminal-de-venta-system repo root.
# Supported placements:
# 1) F:\repos\hitech-os\apps\terminal-de-venta-system\10_PUBLICAR_CHART_LAB_CLOUDFLARE.cmd
# 2) F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center\10_PUBLICAR_CHART_LAB_CLOUDFLARE.cmd
$CandidateRoots = @(
    $LauncherRoot,
    (Split-Path -Parent $LauncherRoot),
    (Split-Path -Parent (Split-Path -Parent $LauncherRoot))
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique

$RepoRoot = $null
foreach ($Candidate in $CandidateRoots) {
    $CandidateApp = Join-Path $Candidate "products\chart-lab\app"
    $CandidatePkg = Join-Path $Candidate "package.json"
    if ((Test-Path -LiteralPath $CandidateApp) -and (Test-Path -LiteralPath $CandidatePkg)) {
        $RepoRoot = (Resolve-Path -LiteralPath $Candidate).Path.TrimEnd("\")
        break
    }
}

if (-not $RepoRoot) {
    throw "No pude detectar RepoRoot. LauncherRoot=$LauncherRoot. Esperaba encontrar products\chart-lab\app en esta carpeta o en su carpeta padre."
}

$ControlCenterRoot = if ((Split-Path -Leaf $LauncherRoot) -ieq "prisma-control-center") { $LauncherRoot } else { Join-Path $RepoRoot "prisma-control-center" }
$AppRoot = Join-Path $RepoRoot "products\chart-lab\app"
$OutRoot = Join-Path $AppRoot "out"
$RunDir = Join-Path $LogRoot ("CHART_LAB_CLOUDFLARE_DEPLOY_{0}" -f $Stamp)
$DownloadsRunDir = Join-Path $Downloads ("CHART_LAB_CLOUDFLARE_DEPLOY_{0}" -f $Stamp)
$ZipPath = Join-Path $Downloads ("CHART_LAB_CLOUDFLARE_DEPLOY_{0}.zip" -f $Stamp)
$LatestZip = Join-Path $Downloads "latest_CHART_LAB_CLOUDFLARE_DEPLOY.zip"
$TranscriptPath = Join-Path $RunDir "transcript.log"
$ReceiptPath = Join-Path $RunDir "deploy_receipt.json"

New-Item -ItemType Directory -Force -Path $Downloads, $RunDir, $DownloadsRunDir | Out-Null

$script:TranscriptStarted = $false
$script:DeploymentUrls = @()
$script:Warnings = New-Object System.Collections.Generic.List[string]
$script:Steps = New-Object System.Collections.Generic.List[object]
$script:SanitizeChanged = $false
$script:BackupZip = $null

function Write-Step {
    param(
        [int]$Percent,
        [string]$Message
    )
    Write-Progress -Activity "PRISMA Chart Lab Cloudflare Deploy" -Status $Message -PercentComplete $Percent
    Write-Host ("[{0}%] {1}" -f $Percent, $Message) -ForegroundColor Cyan
}

function Add-Step {
    param(
        [string]$Name,
        [string]$Status,
        [int]$ExitCode = 0,
        [string]$Log = $null
    )
    $script:Steps.Add([ordered]@{
        name = $Name
        status = $Status
        exitCode = $ExitCode
        log = $Log
        at = (Get-Date).ToString("s")
    }) | Out-Null
}

function Quote-Arg {
    param([string]$Value)
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"','\"') + '"'
    }
    return $Value
}

function Invoke-NativeLogged {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [switch]$AllowFail
    )

    $safeName = ($Name -replace '[^A-Za-z0-9_.-]', '_')
    $logFile = Join-Path $RunDir ("{0}.log" -f $safeName)
    $cmdLine = "$FilePath " + (($Arguments | ForEach-Object { Quote-Arg $_ }) -join " ")

    Write-Host ""
    Write-Host ">>> $Name" -ForegroundColor Yellow
    Write-Host $cmdLine -ForegroundColor DarkGray

    $output = & $FilePath @Arguments 2>&1
    $code = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }

    $output | Tee-Object -FilePath $logFile | Out-Host

    Add-Step -Name $Name -Status ($(if ($code -eq 0) { "PASS" } elseif ($AllowFail) { "WARN" } else { "FAIL" })) -ExitCode $code -Log $logFile

    if ($code -ne 0 -and -not $AllowFail) {
        throw "$Name fallo con exit code $code. Log: $logFile"
    }

    return [ordered]@{
        exitCode = $code
        output = ($output -join [Environment]::NewLine)
        logFile = $logFile
    }
}

function Test-RequiredPath {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "No existe $Label`: $Path"
    }
}

function ConvertTo-PublicSafeValue {
    param(
        [object]$Value,
        [string]$Key = ""
    )

    if ($null -eq $Value) { return $null }

    if ($Value -is [System.Collections.IDictionary]) {
        $result = [ordered]@{}
        foreach ($k in $Value.Keys) {
            $ks = [string]$k
            if ($ks -match '^(databasePaths)$') {
                $result[$ks] = [ordered]@{
                    tablet = "local-sqlite-snapshot"
                    pc = $null
                    canonical = $null
                }
                continue
            }
            if ($ks -match '^(evidence)$' -and $Value[$k] -is [System.Collections.IEnumerable] -and -not ($Value[$k] -is [string])) {
                $cleanEvidence = @()
                foreach ($item in $Value[$k]) {
                    if ($null -eq $item) { continue }
                    $itemText = [string]$item
                    if ($itemText -match '[A-Za-z]:[\\/]' -or $itemText -match '(?i)\.db\b|\.sqlite\b|tablet-pos\.db|repos\\|Users\\') {
                        if ($cleanEvidence -notcontains "public-safe-runtime-snapshot") {
                            $cleanEvidence += "public-safe-runtime-snapshot"
                        }
                    } else {
                        $cleanEvidence += $itemText
                    }
                }
                if ($cleanEvidence.Count -eq 0) { $cleanEvidence = @("public-safe-runtime-snapshot") }
                $result[$ks] = $cleanEvidence
                continue
            }
            $result[$ks] = ConvertTo-PublicSafeValue -Value $Value[$k] -Key $ks
        }
        return $result
    }

    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        $arr = @()
        foreach ($item in $Value) {
            $arr += ConvertTo-PublicSafeValue -Value $item -Key $Key
        }
        return $arr
    }

    if ($Value -is [string]) {
        $s = [string]$Value
        if ($s -match '[A-Za-z]:[\\/]' -or $s -match '(?i)Users[\\/]|repos[\\/]|tablet-pos\.db|\.sqlite\b|\.db\b') {
            if ($s -match '(?i)tablet-pos\.db|\.sqlite\b|\.db\b') {
                return "local-sqlite-snapshot"
            }
            return "PRISMA_LOCAL_PATH_REDACTED"
        }
        return $s
    }

    return $Value
}

function Sanitize-PublicSnapshot {
    if ($NoSanitize) {
        Write-Host "[PRISMA] Sanitizacion de snapshot omitida por -NoSanitize." -ForegroundColor Yellow
        return
    }

    $snapshotPath = Join-Path $AppRoot "src\prisma-charts\prisma-chart-runtime.snapshot.json"
    if (-not (Test-Path -LiteralPath $snapshotPath)) {
        $script:Warnings.Add("No encontre snapshot publico para sanitizar: $snapshotPath") | Out-Null
        return
    }

    $raw = Get-Content -LiteralPath $snapshotPath -Raw -Encoding UTF8
    $newRaw = $raw

    # IMPORTANTE:
    # No convertir JSON a objetos PowerShell y luego serializar.
    # Eso puede cambiar formas/arrays que Chart Lab espera y provocar errores tipo:
    # TypeError: a.flatMap is not a function.
    #
    # Este sanitizador es NO-STRUCTURAL: solo reemplaza strings peligrosos y preserva
    # llaves, arrays, objetos, numeros, booleanos y forma general del snapshot.

    # Rutas Windows escapadas en JSON: F:\\repos\\...
    $newRaw = [regex]::Replace(
        $newRaw,
        '(?i)[A-Z]:\\\\(?:[^"''`\r\n]|\\\\)+',
        'PRISMA_LOCAL_PATH_REDACTED'
    )

    # Rutas Windows sin escapar por si el snapshot se genero raro: F:\repos\...
    $newRaw = [regex]::Replace(
        $newRaw,
        '(?i)[A-Z]:\\(?:[^"''`\r\n])+',
        'PRISMA_LOCAL_PATH_REDACTED'
    )

    # Nombres de bases locales que no deben salir al bundle publico.
    $newRaw = [regex]::Replace($newRaw, '(?i)tablet-pos\.db', 'local-sqlite-snapshot')
    $newRaw = [regex]::Replace($newRaw, '(?i)[A-Za-z0-9_.-]+\.sqlite\b', 'local-sqlite-snapshot')
    $newRaw = [regex]::Replace($newRaw, '(?i)[A-Za-z0-9_.-]+\.db\b', 'local-sqlite-snapshot')

    # Evidencia con prefijos tipo tablet:F:\... manteniendo que siga siendo string.
    $newRaw = [regex]::Replace(
        $newRaw,
        '(?i)(tablet|pc|canonical):PRISMA_LOCAL_PATH_REDACTED',
        '$1:local-sqlite-snapshot'
    )

    if ($newRaw.Trim() -ne $raw.Trim()) {
        $script:BackupZip = Join-Path $Downloads ("PRISMA_CHART_LAB_PUBLIC_SNAPSHOT_SANITIZE_BACKUP_{0}.zip" -f $Stamp)
        Compress-Archive -LiteralPath $snapshotPath -DestinationPath $script:BackupZip -Force
        Set-Content -LiteralPath $snapshotPath -Value $newRaw -Encoding UTF8
        $script:SanitizeChanged = $true
        Write-Host "[PRISMA] Snapshot publico sanitizado sin cambiar estructura: $snapshotPath" -ForegroundColor Green
        Write-Host "[PRISMA] Backup: $script:BackupZip" -ForegroundColor Yellow
        Add-Step -Name "sanitize-public-snapshot" -Status "PATCHED-NONSTRUCTURAL" -ExitCode 0 -Log $script:BackupZip
    } else {
        Write-Host "[PRISMA] Snapshot publico ya estaba limpio." -ForegroundColor Green
        Add-Step -Name "sanitize-public-snapshot" -Status "PASS" -ExitCode 0
    }
}

function Restore-SnapshotBackup {
    if (-not $script:BackupZip) { return }
    if (-not (Test-Path -LiteralPath $script:BackupZip)) { return }

    $snapshotPath = Join-Path $AppRoot "src\prisma-charts\prisma-chart-runtime.snapshot.json"
    $restoreDir = Join-Path $env:TEMP ("PRISMA_CHART_LAB_RESTORE_{0}" -f $Stamp)

    try {
        if (Test-Path -LiteralPath $restoreDir) {
            Remove-Item -LiteralPath $restoreDir -Recurse -Force
        }
        New-Item -ItemType Directory -Force -Path $restoreDir | Out-Null
        Expand-Archive -LiteralPath $script:BackupZip -DestinationPath $restoreDir -Force
        $backupFile = Get-ChildItem -LiteralPath $restoreDir -Recurse -File -Filter "prisma-chart-runtime.snapshot.json" | Select-Object -First 1
        if ($backupFile) {
            Copy-Item -LiteralPath $backupFile.FullName -Destination $snapshotPath -Force
            $script:Warnings.Add("Snapshot restaurado desde backup despues de fallo: $script:BackupZip") | Out-Null
            Write-Host "[PRISMA] Snapshot restaurado desde backup por fallo." -ForegroundColor Yellow
            Add-Step -Name "restore-snapshot-backup" -Status "RESTORED" -ExitCode 0 -Log $script:BackupZip
        }
    } catch {
        $script:Warnings.Add("No pude restaurar snapshot desde backup: $($_.Exception.Message)") | Out-Null
    } finally {
        Remove-Item -LiteralPath $restoreDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Find-UnsafeOutMarkers {
    if (-not (Test-Path -LiteralPath $OutRoot)) { return @() }

    $patterns = @(
        "F:\",
        "C:\",
        "Users\",
        "repos\",
        "tablet-pos.db",
        ".sqlite",
        "CLOUDFLARE_API_TOKEN",
        "PRIVATE KEY",
        "PASSWORD="
    )

    $matches = Get-ChildItem -LiteralPath $OutRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in ".html", ".js", ".json", ".txt", ".css", ".map" } |
        Select-String -SimpleMatch -Pattern $patterns -ErrorAction SilentlyContinue |
        Select-Object -First 50 Path, LineNumber, Line

    return @($matches)
}

function Write-Receipt {
    param(
        [string]$Status,
        [int]$ExitCode,
        [string]$ErrorMessage = $null
    )

    $receipt = [ordered]@{
        schemaVersion = "1.0"
        tool = "PRISMA Chart Lab Cloudflare Deploy"
        status = $Status
        exitCode = $ExitCode
        startedAt = $StartedAt.ToString("s")
        finishedAt = (Get-Date).ToString("s")
        launcherRoot = $LauncherRoot
        repoRoot = $RepoRoot
        controlCenterRoot = $ControlCenterRoot
        appRoot = $AppRoot
        outRoot = $OutRoot
        projectName = $ProjectName
        branch = $Branch
        mainUrl = "https://prisma-chart-lab.pages.dev/"
        deploymentUrls = @($script:DeploymentUrls)
        noSanitize = [bool]$NoSanitize
        sanitizeChanged = [bool]$script:SanitizeChanged
        backupZip = $script:BackupZip
        useTokenWrapper = [bool]$UseTokenWrapper
        openBrowser = [bool]$OpenBrowser
        logRoot = $RunDir
        downloadsRunDir = $DownloadsRunDir
        zipPath = $ZipPath
        latestZip = $LatestZip
        warnings = @($script:Warnings)
        steps = @($script:Steps)
        error = $ErrorMessage
    }

    $receipt | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
    Copy-Item -LiteralPath $ReceiptPath -Destination (Join-Path $DownloadsRunDir "deploy_receipt.json") -Force
}

function Finalize-Zip {
    if ($script:TranscriptStarted) {
        try {
            Stop-Transcript | Out-Null
        } catch {}
        $script:TranscriptStarted = $false
    }

    try {
        Copy-Item -Path (Join-Path $RunDir "*") -Destination $DownloadsRunDir -Recurse -Force -ErrorAction SilentlyContinue
    } catch {}

    if (Test-Path -LiteralPath $ZipPath) {
        Remove-Item -LiteralPath $ZipPath -Force
    }
    Compress-Archive -Path (Join-Path $DownloadsRunDir "*") -DestinationPath $ZipPath -Force
    Copy-Item -LiteralPath $ZipPath -Destination $LatestZip -Force
}

try {
    Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null
    $script:TranscriptStarted = $true

    Write-Step 3 "Validando rutas y herramientas"

    Test-RequiredPath -Path $RepoRoot -Label "RepoRoot"
    Test-RequiredPath -Path $AppRoot -Label "Chart Lab AppRoot"
    Test-RequiredPath -Path (Join-Path $RepoRoot "package.json") -Label "package.json raiz"
    Test-RequiredPath -Path (Join-Path $AppRoot "package.json") -Label "package.json Chart Lab"
    Test-RequiredPath -Path (Join-Path $AppRoot "wrangler.jsonc") -Label "wrangler.jsonc"

    $pnpm = (Get-Command pnpm -ErrorAction Stop).Source
    $node = (Get-Command node -ErrorAction Stop).Source

    Write-Host "Launcher : $LauncherRoot" -ForegroundColor DarkCyan
    Write-Host "RepoRoot : $RepoRoot" -ForegroundColor DarkCyan
    Write-Host "Control  : $ControlCenterRoot" -ForegroundColor DarkCyan
    Write-Host "AppRoot  : $AppRoot" -ForegroundColor DarkCyan
    Write-Host "Project  : $ProjectName" -ForegroundColor DarkCyan
    Write-Host "Branch   : $Branch" -ForegroundColor DarkCyan
    Write-Host "pnpm     : $pnpm" -ForegroundColor DarkCyan
    Write-Host "node     : $node" -ForegroundColor DarkCyan

    if ($WhatIf) {
        Write-Receipt -Status "WHATIF" -ExitCode 0
        Write-Host "[WHATIF] Validacion inicial completa. No se ejecuto build/deploy." -ForegroundColor Yellow
        exit 0
    }

    Write-Step 12 "Sanitizando snapshot publico si hace falta"
    Sanitize-PublicSnapshot

    Write-Step 25 "Ejecutando build Cloudflare static export"
    Invoke-NativeLogged -Name "chart-lab-cf-build" -FilePath $pnpm -Arguments @("-C", $RepoRoot, "chart-lab:cf:build") | Out-Null

    Write-Step 42 "Verificando paquete Cloudflare y no-leak"
    Invoke-NativeLogged -Name "chart-lab-cf-verify" -FilePath $pnpm -Arguments @("-C", $RepoRoot, "chart-lab:cf:verify") | Out-Null

    Write-Step 50 "Escaneo extra de marcadores peligrosos en out"
    $unsafe = Find-UnsafeOutMarkers
    if ($unsafe.Count -gt 0) {
        $unsafePath = Join-Path $RunDir "unsafe_out_markers.txt"
        $unsafe | Format-List | Out-String | Set-Content -LiteralPath $unsafePath -Encoding UTF8
        throw "El out publico aun contiene marcadores peligrosos. Revisa: $unsafePath"
    }
    Add-Step -Name "extra-public-out-scan" -Status "PASS" -ExitCode 0

    Write-Step 60 "Verificando Wrangler"
    try {
        Invoke-NativeLogged -Name "wrangler-version" -FilePath $pnpm -Arguments @("-C", $AppRoot, "exec", "wrangler", "--version") | Out-Null
    } catch {
        $script:Warnings.Add("Wrangler fallo; intento reparacion con pnpm install --force y wrangler@latest.") | Out-Null
        Write-Host "[PRISMA] Wrangler fallo. Intento repararlo..." -ForegroundColor Yellow
        Invoke-NativeLogged -Name "pnpm-install-force" -FilePath $pnpm -Arguments @("-C", $RepoRoot, "install", "--force") | Out-Null
        Invoke-NativeLogged -Name "pnpm-add-wrangler" -FilePath $pnpm -Arguments @("-C", $AppRoot, "add", "-D", "wrangler@latest") | Out-Null
        Invoke-NativeLogged -Name "wrangler-version-after-repair" -FilePath $pnpm -Arguments @("-C", $AppRoot, "exec", "wrangler", "--version") | Out-Null
    }

    Write-Step 70 "Verificando autenticacion Cloudflare"
    $who = Invoke-NativeLogged -Name "wrangler-whoami" -FilePath $pnpm -Arguments @("-C", $AppRoot, "exec", "wrangler", "whoami") -AllowFail
    if ($who.exitCode -ne 0) {
        if ($SkipLogin) {
            throw "Wrangler no esta autenticado y se indico -SkipLogin."
        }
        Write-Host "[PRISMA] Wrangler no esta autenticado. Abriendo login Cloudflare..." -ForegroundColor Yellow
        Invoke-NativeLogged -Name "wrangler-login" -FilePath $pnpm -Arguments @("-C", $AppRoot, "exec", "wrangler", "login") | Out-Null
        Invoke-NativeLogged -Name "wrangler-whoami-after-login" -FilePath $pnpm -Arguments @("-C", $AppRoot, "exec", "wrangler", "whoami") | Out-Null
    }

    Write-Step 82 "Desplegando Chart Lab a Cloudflare Pages"

    if ($UseTokenWrapper) {
        if (-not $env:CLOUDFLARE_API_TOKEN) {
            throw "UseTokenWrapper requiere variable CLOUDFLARE_API_TOKEN en esta consola."
        }
        $deploy = Invoke-NativeLogged -Name "chart-lab-cf-deploy-wrapper" -FilePath $pnpm -Arguments @("-C", $RepoRoot, "chart-lab:cf:deploy")
    } else {
        $deploy = Invoke-NativeLogged -Name "wrangler-pages-deploy" -FilePath $pnpm -Arguments @(
            "-C", $AppRoot,
            "exec", "wrangler",
            "pages", "deploy", "out",
            "--project-name=$ProjectName",
            "--branch=$Branch",
            "--commit-dirty=true"
        )
    }

    $urlMatches = [regex]::Matches($deploy.output, 'https://[A-Za-z0-9.-]+\.prisma-chart-lab\.pages\.dev/?')
    foreach ($m in $urlMatches) {
        if ($script:DeploymentUrls -notcontains $m.Value) {
            $script:DeploymentUrls += $m.Value
        }
    }

    Write-Step 91 "Validando URLs publicas"
    $urlsToProbe = @()
    $urlsToProbe += "https://prisma-chart-lab.pages.dev/"
    $urlsToProbe += $script:DeploymentUrls

    foreach ($url in ($urlsToProbe | Select-Object -Unique)) {
        try {
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30
            $probeLog = Join-Path $RunDir ("probe_{0}.txt" -f (($url -replace '[^A-Za-z0-9]+','_').Trim('_')))
            "URL: $url`nStatusCode: $($resp.StatusCode)`nLength: $($resp.Content.Length)" | Set-Content -LiteralPath $probeLog -Encoding UTF8
            Add-Step -Name "probe-$url" -Status "PASS" -ExitCode 0 -Log $probeLog
        } catch {
            $script:Warnings.Add("Probe fallo para $url :: $($_.Exception.Message)") | Out-Null
            Add-Step -Name "probe-$url" -Status "WARN" -ExitCode 1
        }
    }

    if ($OpenBrowser) {
        Start-Process "https://prisma-chart-lab.pages.dev/"
        foreach ($url in $script:DeploymentUrls) { Start-Process $url }
    }

    Write-Step 97 "Escribiendo recibo y ZIP"
    Write-Receipt -Status "PASS" -ExitCode 0
    Finalize-Zip

    Write-Step 100 "Terminado"
    Write-Host ""
    Write-Host "=== PRISMA CHART LAB CLOUDFLARE DEPLOY FINAL ===" -ForegroundColor Green
    Write-Host "Status        : PASS" -ForegroundColor Green
    Write-Host "Main URL      : https://prisma-chart-lab.pages.dev/" -ForegroundColor Cyan
    if ($script:DeploymentUrls.Count -gt 0) {
        Write-Host "Deploy URL(s) :" -ForegroundColor Cyan
        foreach ($url in $script:DeploymentUrls) {
            Write-Host "  $url" -ForegroundColor White
        }
    }
    Write-Host "Receipt       : $ReceiptPath" -ForegroundColor Cyan
    Write-Host "Evidence ZIP  : $ZipPath" -ForegroundColor Cyan
    Write-Host "Latest ZIP    : $LatestZip" -ForegroundColor Cyan

    exit 0
} catch {
    $err = $_.Exception.Message
    Write-Host ""
    Write-Host "ERROR PRISMA CHART LAB CLOUDFLARE DEPLOY:" -ForegroundColor Red
    Write-Host $err -ForegroundColor Red

    try {
        Restore-SnapshotBackup
        Write-Receipt -Status "FAIL" -ExitCode 1 -ErrorMessage $err
        Finalize-Zip
        Write-Host ""
        Write-Host "Evidence ZIP : $ZipPath" -ForegroundColor Yellow
        Write-Host "Latest ZIP   : $LatestZip" -ForegroundColor Yellow
    } catch {
        Write-Host "[WARN] No pude finalizar ZIP: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    exit 1
} finally {
    Write-Progress -Activity "PRISMA Chart Lab Cloudflare Deploy" -Completed
    if ($script:TranscriptStarted) {
        try { Stop-Transcript | Out-Null } catch {}
    }
}
