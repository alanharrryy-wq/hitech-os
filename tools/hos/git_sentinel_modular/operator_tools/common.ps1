[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Write-HitechProgress {
    param([string]$Activity,[int]$Step,[int]$TotalSteps)
    if ($TotalSteps -le 0) { $TotalSteps = 1 }
    $pct = [math]::Min(100, [int](($Step / $TotalSteps) * 100))
    Write-Progress -Activity $Activity -Status "$pct% completado" -PercentComplete $pct
}

function Get-HitechPaths {
    param([string]$RepoRoot = "F:\repos\hitech-os",[string]$DownloadsRoot = "F:\OneDrive\Descargas")
    $modularRoot = Join-Path $RepoRoot "tools\hos\git_sentinel_modular"
    $runtimeRoot = "C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime"
    $shadowRoot = Join-Path $runtimeRoot "shadow_mode"
    return @{
        RepoRoot = $RepoRoot
        ModularRoot = $modularRoot
        RuntimeRoot = $runtimeRoot
        ShadowRoot = $shadowRoot
        DownloadsRoot = $DownloadsRoot
        OutputsRoot = Join-Path $DownloadsRoot "git_sentinel_outputs"
        LogsRoot = Join-Path $DownloadsRoot "git_sentinel_logs"
    }
}

function Assert-HitechRepoPaths {
    param([hashtable]$Paths)
    if (!(Test-Path $Paths.RepoRoot)) { throw "RepoRoot no existe: $($Paths.RepoRoot)" }
    if (!(Test-Path $Paths.ModularRoot)) { throw "ModularRoot no existe: $($Paths.ModularRoot)" }
    if (!(Test-Path $Paths.DownloadsRoot)) { throw "DownloadsRoot no existe: $($Paths.DownloadsRoot)" }
}

function Ensure-HitechOutputDirectories {
    param([hashtable]$Paths)
    foreach ($dir in @($Paths.OutputsRoot,$Paths.LogsRoot)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

function Resolve-HitechWorkspaceRoot {
    param([string]$ShadowRoot,[string]$WorkspaceRoot)
    if ($WorkspaceRoot) {
        if ($WorkspaceRoot -match "<run_id>") { throw "No uses '<run_id>' literal. Pasa una ruta real o deja que el script detecte la más reciente." }
        if (!(Test-Path $WorkspaceRoot)) { throw "WorkspaceRoot no existe: $WorkspaceRoot" }
        return (Resolve-Path $WorkspaceRoot).Path
    }
    if (!(Test-Path $ShadowRoot)) { return $null }
    $candidates = Get-ChildItem -Path $ShadowRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    foreach ($dir in $candidates) {
        $required = @((Join-Path $dir.FullName "baseline"),(Join-Path $dir.FullName "candidate"),(Join-Path $dir.FullName "manifests"))
        $ok = $true
        foreach ($path in $required) { if (!(Test-Path $path)) { $ok = $false; break } }
        if ($ok) { return $dir.FullName }
    }
    return $null
}

function Set-HitechPythonEnv {
    param([string]$ModularRoot)
    $current = $env:PYTHONPATH
    if ([string]::IsNullOrWhiteSpace($current)) { $env:PYTHONPATH = $ModularRoot }
    elseif ($current -notlike "*$ModularRoot*") { $env:PYTHONPATH = "$ModularRoot;$current" }
    return $env:PYTHONPATH
}

function Invoke-HitechPythonModule {
    param([string]$ModuleName,[string[]]$Arguments)
    & python -X utf8 -m $ModuleName @Arguments
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { throw "El módulo '$ModuleName' terminó con código $exitCode" }
}

function Get-HitechRunIdFromWorkspace {
    param([string]$WorkspaceRoot)
    return (Split-Path -Leaf $WorkspaceRoot)
}

function Get-HitechRunOutputRoot {
    param([hashtable]$Paths,[string]$WorkspaceRoot)
    $runId = Get-HitechRunIdFromWorkspace -WorkspaceRoot $WorkspaceRoot
    $runRoot = Join-Path $Paths.OutputsRoot $runId
    New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
    return $runRoot
}

function Export-HitechBundleToDownloads {
    param([hashtable]$Paths,[string]$WorkspaceRoot,[string]$BundleName)
    $source = Join-Path $WorkspaceRoot $BundleName
    $runRoot = Get-HitechRunOutputRoot -Paths $Paths -WorkspaceRoot $WorkspaceRoot
    $destination = Join-Path $runRoot $BundleName
    if (!(Test-Path $source)) { return $null }
    if (Test-Path $destination) { Remove-Item -Path $destination -Recurse -Force -ErrorAction SilentlyContinue }
    Copy-Item -Path $source -Destination $destination -Recurse -Force
    return $destination
}

function Restore-HitechBundleFromDownloads {
    param([hashtable]$Paths,[string]$WorkspaceRoot,[string]$BundleName)
    $runRoot = Get-HitechRunOutputRoot -Paths $Paths -WorkspaceRoot $WorkspaceRoot
    $source = Join-Path $runRoot $BundleName
    $destination = Join-Path $WorkspaceRoot $BundleName
    if (!(Test-Path $source)) { return $null }
    if (Test-Path $destination) { Remove-Item -Path $destination -Recurse -Force -ErrorAction SilentlyContinue }
    Copy-Item -Path $source -Destination $destination -Recurse -Force
    return $destination
}

function Test-HitechWorkspaceHasFile {
    param([string]$WorkspaceRoot,[string]$RelativePath)
    return (Test-Path (Join-Path $WorkspaceRoot $RelativePath))
}

function Start-HitechLogTranscript {
    param([hashtable]$Paths,[string]$LogPrefix,[string]$WorkspaceRoot)
    Ensure-HitechOutputDirectories -Paths $Paths
    $runId = if ($WorkspaceRoot) { Get-HitechRunIdFromWorkspace -WorkspaceRoot $WorkspaceRoot } else { "no_workspace" }
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logPath = Join-Path $Paths.LogsRoot ($LogPrefix + "_" + $runId + "_" + $timestamp + ".log")
    Start-Transcript -Path $logPath -Force | Out-Null
    return $logPath
}

function Stop-HitechLogTranscript {
    try { Stop-Transcript | Out-Null } catch {}
}

function Show-HitechExecutionBanner {
    param([string]$Title,[string]$WorkspaceRoot,[string]$TargetRoot,[string]$ModularRoot,[string]$DownloadsRoot)
    Write-Host ""
    Write-Host "===== $Title ====="
    if ($WorkspaceRoot) { Write-Host "WorkspaceRoot: $WorkspaceRoot" }
    if ($TargetRoot) { Write-Host "TargetRoot:    $TargetRoot" }
    Write-Host "ModularRoot:   $ModularRoot"
    Write-Host "DownloadsRoot: $DownloadsRoot"
    Write-Host ""
}
