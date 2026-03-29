[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$RepoRoot = 'F:\repos\hitech-os',

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$RelativePythonScript = 'tools\graphviz\generate_repo_graphs.py',

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$LogRoot = 'F:\OneDrive\Hitech\3.Proyectos\CHAT GPT AI Estudio\HITECH_AISTUDIO_SYSTEM\00.Resplogs\LOGS',

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'

$script:RunId = Get-Date -Format 'yyyyMMdd_HHmmss'
$script:RunStart = Get-Date
$script:Status = 'UNKNOWN'
$script:ExitCode = 0
$script:RunFolder = $null
$script:JsonLogPath = $null
$script:ConsoleLogPath = $null
$script:SummaryPath = $null

function Write-RunLog {
    param(
        [Parameter(Mandatory)]
        [ValidateSet('DEBUG', 'INFO', 'WARN', 'ERROR')]
        [string]$Level,

        [Parameter(Mandatory)]
        [string]$Message,

        [hashtable]$Data = @{}
    )

    if (-not $script:JsonLogPath) {
        return
    }

    $entry = [ordered]@{
        ts      = (Get-Date).ToString('o')
        level   = $Level
        message = $Message
        data    = $Data
    }

    $line = $entry | ConvertTo-Json -Compress -Depth 10
    Add-Content -LiteralPath $script:JsonLogPath -Value $line -Encoding UTF8
}

function Resolve-PythonLauncher {
    $python = Get-Command -Name 'python' -ErrorAction SilentlyContinue
    if ($python) {
        return [pscustomobject]@{
            Command  = 'python'
            BaseArgs = @()
        }
    }

    $py = Get-Command -Name 'py' -ErrorAction SilentlyContinue
    if ($py) {
        return [pscustomobject]@{
            Command  = 'py'
            BaseArgs = @('-3')
        }
    }

    throw "No se encontro Python en PATH (ni 'python' ni 'py')."
}

try {
    Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Status 'Inicializando' -PercentComplete 5

    if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
        throw "RepoRoot no existe o no es carpeta: $RepoRoot"
    }
    $repoFull = (Resolve-Path -LiteralPath $RepoRoot).Path

    $scriptFull = Join-Path -Path $repoFull -ChildPath $RelativePythonScript
    if (-not (Test-Path -LiteralPath $scriptFull -PathType Leaf)) {
        throw "No existe el script Python: $scriptFull"
    }

    New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null
    $script:RunFolder = Join-Path -Path $LogRoot -ChildPath "graphviz_full_refresh_$($script:RunId)"
    New-Item -ItemType Directory -Path $script:RunFolder -Force | Out-Null

    $script:JsonLogPath = Join-Path -Path $script:RunFolder -ChildPath 'run.jsonl'
    $script:ConsoleLogPath = Join-Path -Path $script:RunFolder -ChildPath 'python_output.log'
    $script:SummaryPath = Join-Path -Path $script:RunFolder -ChildPath 'summary.json'

    Write-RunLog -Level 'INFO' -Message 'run_initialized' -Data @{
        run_id      = $script:RunId
        repo_root   = $repoFull
        script_path = $scriptFull
        log_folder  = $script:RunFolder
        dry_run     = [bool]$DryRun
        what_if     = [bool]$WhatIfPreference
    }

    Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Status 'Validando Python' -PercentComplete 20
    $launcher = Resolve-PythonLauncher
    Write-RunLog -Level 'INFO' -Message 'python_launcher_resolved' -Data @{
        command  = $launcher.Command
        baseArgs = @($launcher.BaseArgs)
    }

    Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Status 'Preflight de dependencias Python' -PercentComplete 35
    $probeCode = 'import sys, graphviz; print("python=" + sys.version.split()[0]); print("graphviz=" + graphviz.__version__)'
    $probeArgs = @()
    $probeArgs += $launcher.BaseArgs
    $probeArgs += '-c'
    $probeArgs += $probeCode

    $probeOutput = & $launcher.Command @probeArgs 2>&1
    foreach ($line in $probeOutput) {
        Write-RunLog -Level 'INFO' -Message 'python_probe' -Data @{ line = [string]$line }
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Preflight Python fallo (graphviz no disponible o Python invalido)."
    }

    $commandPreview = (@($launcher.Command) + @($launcher.BaseArgs) + @($scriptFull)) -join ' '
    Write-RunLog -Level 'INFO' -Message 'execution_plan' -Data @{ command = $commandPreview }

    if ($DryRun -or -not $PSCmdlet.ShouldProcess($scriptFull, 'Ejecutar generacion completa Graphviz (backup -> clean -> full scan -> regenerate)')) {
        Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Status 'Ejecucion omitida (DryRun/WhatIf)' -PercentComplete 100
        $script:Status = 'SKIPPED'
        Write-RunLog -Level 'WARN' -Message 'execution_skipped' -Data @{
            reason = if ($DryRun) { 'DryRun' } else { 'WhatIf/ShouldProcess=False' }
        }
    }
    else {
        Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Status 'Ejecutando flujo Graphviz' -PercentComplete 65

        $pythonExit = 0
        Push-Location -LiteralPath $repoFull
        try {
            & $launcher.Command @($launcher.BaseArgs + @($scriptFull)) 2>&1 | Tee-Object -LiteralPath $script:ConsoleLogPath
            $pythonExit = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }

        Write-RunLog -Level 'INFO' -Message 'python_execution_finished' -Data @{
            exit_code    = $pythonExit
            console_log  = $script:ConsoleLogPath
        }

        if ($pythonExit -ne 0) {
            throw "El script Python termino con codigo de salida $pythonExit."
        }

        Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Status 'Completado' -PercentComplete 100
        $script:Status = 'SUCCESS'
    }
}
catch {
    $script:Status = 'FAILED'
    $script:ExitCode = 1
    $errText = ($_ | Out-String).Trim()
    Write-RunLog -Level 'ERROR' -Message 'run_failed' -Data @{
        exception = $_.Exception.Message
        details   = $errText
    }
    Write-Error "Fallo la ejecucion: $($_.Exception.Message)"
}
finally {
    Write-Progress -Id 1 -Activity 'Graphviz Full Refresh Launcher' -Completed

    $duration = (Get-Date) - $script:RunStart
    $summary = [ordered]@{
        run_id         = $script:RunId
        status         = $script:Status
        repo_root      = $RepoRoot
        python_script  = $RelativePythonScript
        started_at     = $script:RunStart.ToString('o')
        finished_at    = (Get-Date).ToString('o')
        duration_sec   = [math]::Round($duration.TotalSeconds, 2)
        log_folder     = $script:RunFolder
        run_log_jsonl  = $script:JsonLogPath
        console_log    = $script:ConsoleLogPath
        summary_json   = $script:SummaryPath
    }

    if ($script:SummaryPath) {
        $tmpSummary = "$($script:SummaryPath).tmp"
        $summaryJson = $summary | ConvertTo-Json -Depth 10
        Set-Content -LiteralPath $tmpSummary -Value $summaryJson -Encoding UTF8
        Move-Item -LiteralPath $tmpSummary -Destination $script:SummaryPath -Force
    }

    if ($script:JsonLogPath) {
        Write-RunLog -Level 'INFO' -Message 'run_finished' -Data @{
            status       = $script:Status
            duration_sec = [math]::Round($duration.TotalSeconds, 2)
        }
    }

    Write-Host ''
    Write-Host '===== RESUMEN ====='
    Write-Host ("Status      : {0}" -f $script:Status)
    Write-Host ("Repo        : {0}" -f $RepoRoot)
    Write-Host ("Script      : {0}" -f $RelativePythonScript)
    Write-Host ("Duracion(s) : {0}" -f ([math]::Round($duration.TotalSeconds, 2)))
    Write-Host ("Logs        : {0}" -f $script:RunFolder)
    if ($script:SummaryPath) {
        Write-Host ("Summary     : {0}" -f $script:SummaryPath)
    }
    Write-Host '==================='
}

if ($script:Status -eq 'FAILED') {
    exit 1
}
exit 0
