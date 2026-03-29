param(
    [string]$RepoRoot = 'F:\repos\hitech-os',
    [string]$DownloadsRoot = 'F:\OneDrive\Descargas',
    [switch]$NoAutoElevate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Directory {
    param([string]$PathValue)
    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Resolve-PythonCommand {
    param([string]$RepoRootValue)

    $venvPython = Join-Path $RepoRootValue '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venvPython) {
        return @{ File = $venvPython; Prefix = @(); Display = $venvPython }
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return @{ File = $pythonCmd.Source; Prefix = @(); Display = $pythonCmd.Source }
    }

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        & $pyCmd.Source -3 -c "print('ok')" *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ File = $pyCmd.Source; Prefix = @('-3'); Display = "$($pyCmd.Source) -3" }
        }
    }

    throw 'No se pudo resolver Python.'
}

function Convert-DelayToSeconds {
    param([string]$Delay)

    if ([string]::IsNullOrWhiteSpace($Delay)) {
        return $null
    }

    $value = $Delay.Trim().ToUpperInvariant()
    if ($value -match '^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$') {
        $hours = if ($matches[1]) { [int]$matches[1] } else { 0 }
        $minutes = if ($matches[2]) { [int]$matches[2] } else { 0 }
        $seconds = if ($matches[3]) { [int]$matches[3] } else { 0 }
        return ($hours * 3600) + ($minutes * 60) + $seconds
    }

    return $null
}

function Get-TaskSnapshot {
    param([string]$TaskName)

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -eq $task) {
        return [pscustomobject]@{
            task_name = $TaskName
            exists = $false
        }
    }

    $info = Get-ScheduledTaskInfo -TaskName $TaskName
    $trigger = $task.Triggers | Select-Object -First 1
    $action = $task.Actions | Select-Object -First 1
    $triggerDelay = $null
    if ($trigger -and ($trigger.PSObject.Properties.Name -contains 'Delay')) {
        $triggerDelay = [string]$trigger.Delay
    }

    return [pscustomobject]@{
        task_name = $TaskName
        exists = $true
        state = [string]$task.State
        enabled = [bool]$task.Settings.Enabled
        principal_user = [string]$task.Principal.UserId
        run_level = [string]$task.Principal.RunLevel
        trigger_class = if ($trigger) { [string]$trigger.CimClass.CimClassName } else { $null }
        trigger_delay = $triggerDelay
        action_execute = if ($action) { [string]$action.Execute } else { $null }
        action_arguments = if ($action) { [string]$action.Arguments } else { $null }
        last_task_result = $info.LastTaskResult
        next_run_time = [string]$info.NextRunTime
    }
}

$runtimeRoot = Join-Path $DownloadsRoot 'engine_guardian'
$installRoot = Join-Path $runtimeRoot 'install'
Ensure-Directory -PathValue $DownloadsRoot
Ensure-Directory -PathValue $runtimeRoot
Ensure-Directory -PathValue $installRoot

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$runRoot = Join-Path $installRoot "privileged_activation_$timestamp"
Ensure-Directory -PathValue $runRoot

$logPath = Join-Path $runRoot 'activation.log'
$summaryPath = Join-Path $runRoot 'activation_summary.json'

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format s), $Message
    Add-Content -LiteralPath $logPath -Value $line
    Write-Host $line
}

function Write-Stage {
    param([int]$Index, [int]$Total, [string]$Status)
    $percent = if ($Total -le 0) { 0 } else { [int](($Index / [double]$Total) * 100) }
    Write-Progress -Activity 'Engine Guardian privileged activation' -Status $Status -PercentComplete $percent
    Write-Log $Status
}

$stepsTotal = 8
$step = 0

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin = Test-IsAdmin

if (-not $isAdmin) {
    if ($NoAutoElevate) {
        Write-Log 'No hay elevacion y NoAutoElevate esta activo.'
        throw 'Ejecuta este script en una terminal elevada (Administrador).'
    }

    Write-Log 'Contexto no elevado. Intentando relanzar una sola vez con UAC.'
    $elevatedExe = Join-Path $PSHOME 'powershell.exe'
    $arguments = @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', "`"$PSCommandPath`"",
        '-RepoRoot', "`"$RepoRoot`"",
        '-DownloadsRoot', "`"$DownloadsRoot`"",
        '-NoAutoElevate'
    )

    try {
        $proc = Start-Process -FilePath $elevatedExe -ArgumentList $arguments -Verb RunAs -PassThru -Wait
        Write-Log ("Proceso elevado finalizado con exit code: {0}" -f $proc.ExitCode)
        exit $proc.ExitCode
    }
    catch {
        Write-Log ("No se pudo abrir elevacion UAC: {0}" -f $_.Exception.Message)
        throw
    }
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Contexto elevado confirmado y entorno inicializado'

$pythonCmd = Resolve-PythonCommand -RepoRootValue $RepoRoot
$cliPath = Join-Path $RepoRoot 'engine_guardian\cli.py'
if (-not (Test-Path -LiteralPath $cliPath)) {
    throw "No existe CLI esperado: $cliPath"
}

$env:ENGINE_GUARDIAN_REPO_ROOT = $RepoRoot
$env:ENGINE_GUARDIAN_DOWNLOADS_ROOT = $DownloadsRoot
$env:ENGINE_GUARDIAN_RUNTIME_ROOT = $runtimeRoot

$runData = [ordered]@{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    elevated_context = $isAdmin
    identity = $identity.Name
    repo_root = $RepoRoot
    runtime_root = $runtimeRoot
    install_root = $installRoot
    run_root = $runRoot
    python = $pythonCmd.Display
    commands = @()
    scheduler_install = $null
    scheduler_contract_validation = $null
    scheduler_tasks = @()
    schtasks_query = @()
    cutover = $null
    runtime_files = @()
    errors = @()
    success = $false
}

trap {
    $message = $_.Exception.Message
    try { Write-Log (\"ERROR: $message\") } catch {}
    try {
        $runData.errors += $message
        $runData.success = $false
        $runData | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
    } catch {}
    Write-Progress -Activity 'Engine Guardian privileged activation' -Completed
    exit 1
}

function Invoke-Cli {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    $outFile = Join-Path $runRoot ("cli_{0}.log" -f $Name)
    & $pythonCmd.File @($pythonCmd.Prefix + @($cliPath) + $Arguments) *> $outFile
    $exitCode = $LASTEXITCODE

    $entry = [pscustomobject]@{
        name = $Name
        args = $Arguments
        exit_code = $exitCode
        output_log = $outFile
    }
    $runData.commands += $entry
    return $entry
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Bootstrap de runtime'
$bootstrap = Invoke-Cli -Name 'bootstrap' -Arguments @('bootstrap')
if ($bootstrap.exit_code -ne 0) {
    throw "bootstrap fallo. Ver: $($bootstrap.output_log)"
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Instalando scheduler oficial (real)'
$install = Invoke-Cli -Name 'install_scheduler' -Arguments @('install-scheduler', '--json-only')
$runData.scheduler_install = $install
if ($install.exit_code -ne 0) {
    Write-Log 'install-scheduler devolvio codigo no-cero. Se continuara para recolectar evidencia completa.'
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Leyendo contrato y resultado de scheduler'
$schedulerReportPath = Join-Path $runtimeRoot 'reports\scheduler_install_latest.json'
if (-not (Test-Path -LiteralPath $schedulerReportPath)) {
    throw "No existe reporte esperado: $schedulerReportPath"
}
$runSchedulerReportCopy = Join-Path $runRoot 'scheduler_install_latest.json'
Copy-Item -LiteralPath $schedulerReportPath -Destination $runSchedulerReportCopy -Force
$schedulerReport = Get-Content -LiteralPath $schedulerReportPath -Raw | ConvertFrom-Json

$contractChecks = @()
$requiredTaskNames = @('HITECH-EngineGuardian-Boot', 'HITECH-EngineGuardian-Pulse')
foreach ($taskName in $requiredTaskNames) {
    $contractTask = $schedulerReport.contract.tasks | Where-Object { $_.task_name -eq $taskName } | Select-Object -First 1
    $contractChecks += [pscustomobject]@{
        task_name = $taskName
        has_contract_entry = [bool]$contractTask
        trigger_atstartup = [bool]($contractTask -and $contractTask.trigger -eq 'AtStartup')
        delay_75 = [bool]($contractTask -and [int]$contractTask.delay_seconds -eq 75)
        run_as_system = [bool]($contractTask -and $contractTask.run_as -eq 'SYSTEM')
        run_level_highest = [bool]($contractTask -and $contractTask.run_level -eq 'HighestAvailable')
        canonical_python = if ($contractTask) { [string]$contractTask.python_path } else { $null }
        canonical_cli = if ($contractTask) { [string]$contractTask.cli_path } else { $null }
    }
}

$runData.scheduler_contract_validation = $contractChecks

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Validando tareas reales instaladas en Windows'
$taskSnapshots = @()
$schtasksChecks = @()
$taskValidationFailures = @()
foreach ($taskName in $requiredTaskNames) {
    $snapshot = Get-TaskSnapshot -TaskName $taskName
    $taskSnapshots += $snapshot

    $schtasksOut = Join-Path $runRoot ("schtasks_query_{0}.txt" -f ($taskName -replace '[^A-Za-z0-9_-]', '_'))
    schtasks /Query /TN $taskName /V /FO LIST *> $schtasksOut
    $schtasksExit = $LASTEXITCODE
    $schtasksChecks += [pscustomobject]@{ task_name = $taskName; exit_code = $schtasksExit; output_file = $schtasksOut }

    if (-not $snapshot.exists) {
        $taskValidationFailures += "$taskName no existe"
        continue
    }

    if ($snapshot.trigger_class -notlike '*Boot*') {
        $taskValidationFailures += "$taskName trigger no es AtStartup/Boot"
    }

    $delaySeconds = Convert-DelayToSeconds -Delay $snapshot.trigger_delay
    if ($delaySeconds -ne 75) {
        $taskValidationFailures += "$taskName delay no es 75 segundos (valor: $($snapshot.trigger_delay))"
    }

    if ($snapshot.principal_user -notin @('SYSTEM', 'S-1-5-18')) {
        $taskValidationFailures += "$taskName principal no es SYSTEM (valor: $($snapshot.principal_user))"
    }

    if ($snapshot.run_level -notin @('Highest', 'HighestAvailable')) {
        $taskValidationFailures += "$taskName run level no es highest (valor: $($snapshot.run_level))"
    }

    $contractTask = $schedulerReport.contract.tasks | Where-Object { $_.task_name -eq $taskName } | Select-Object -First 1
    if ($contractTask) {
        $expectedPython = [string]$contractTask.python_path
        $expectedCli = [string]$contractTask.cli_path
        $actionExecute = if ($null -ne $snapshot.action_execute) { [string]$snapshot.action_execute } else { '' }
        $actionArguments = if ($null -ne $snapshot.action_arguments) { [string]$snapshot.action_arguments } else { '' }
        if ($actionExecute.ToLowerInvariant() -ne $expectedPython.ToLowerInvariant()) {
            $taskValidationFailures += "$taskName action execute no coincide con python canonico"
        }
        if (-not ($actionArguments.ToLowerInvariant().Contains($expectedCli.ToLowerInvariant()))) {
            $taskValidationFailures += "$taskName argumentos no contienen cli canonico"
        }
    }

    if ($schtasksExit -ne 0) {
        $taskValidationFailures += "$taskName no es queryable por schtasks"
    }
}

$runData.scheduler_tasks = $taskSnapshots
$runData.schtasks_query = $schtasksChecks

$schedulerInstallOk = [bool]($install.exit_code -eq 0 -and $taskValidationFailures.Count -eq 0)
if (-not $schedulerInstallOk) {
    $runData.errors += $taskValidationFailures
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Revisando runtime state obligatorio'
$requiredRuntimeFiles = @(
    'state\resolved_tools.json',
    'state\boot_state.json',
    'state\engine_status_latest.json',
    'state\repo_analyzer_status.json',
    'state\last_actions.jsonl'
)
foreach ($relative in $requiredRuntimeFiles) {
    $pathValue = Join-Path $runtimeRoot $relative
    $exists = Test-Path -LiteralPath $pathValue
    $runData.runtime_files += [pscustomobject]@{ path = $pathValue; exists = $exists }
    if (-not $exists) {
        $runData.errors += "Falta runtime file: $pathValue"
    }
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Cutover legacy condicional'
$sentinelTaskName = 'HITECH-OS-GitSentinel-Guardian'
$sentinelBefore = Get-TaskSnapshot -TaskName $sentinelTaskName

if ($schedulerInstallOk) {
    $cutoverCmd = Invoke-Cli -Name 'disable_legacy_cloudflare_tasks_apply' -Arguments @('disable-legacy-cloudflare-tasks', '--apply', '--json-only')
    $legacyReportPath = Join-Path $runtimeRoot 'reports\legacy_cloudflare_task_cutover_latest.json'
    $legacyCopy = Join-Path $runRoot 'legacy_cloudflare_task_cutover_latest.json'
    if (Test-Path -LiteralPath $legacyReportPath) {
        Copy-Item -LiteralPath $legacyReportPath -Destination $legacyCopy -Force
    }

    $legacyReport = if (Test-Path -LiteralPath $legacyReportPath) {
        Get-Content -LiteralPath $legacyReportPath -Raw | ConvertFrom-Json
    } else {
        $null
    }

    $legacyChecks = @()
    if ($legacyReport) {
        foreach ($item in $legacyReport.legacy_tasks) {
            $exists = [bool]$item.query.exists
            $backupPath = [string]$item.backup_path
            $backupExists = if ($exists) { Test-Path -LiteralPath $backupPath } else { $false }
            $disableRc = if ($item.disable) { [int]$item.disable.returncode } else { 0 }
            $legacyChecks += [pscustomobject]@{
                task_name = [string]$item.task_name
                existed = $exists
                backup_path = $backupPath
                backup_exists = $backupExists
                disable_returncode = $disableRc
            }
            if ($exists -and -not $backupExists) {
                $runData.errors += "Cutover sin backup detectado para $($item.task_name)"
            }
            if ($exists -and $disableRc -ne 0) {
                $runData.errors += "Disable fallo para $($item.task_name)"
            }
        }
    }

    $runData.cutover = [pscustomobject]@{
        executed = $true
        cli_command = $cutoverCmd
        report_path = if (Test-Path -LiteralPath $legacyReportPath) { $legacyReportPath } else { $null }
        report_copy = if (Test-Path -LiteralPath $legacyCopy) { $legacyCopy } else { $null }
        checks = $legacyChecks
    }
}
else {
    $runData.cutover = [pscustomobject]@{
        executed = $false
        reason = 'Scheduler installation/validation did not succeed. Legacy cutover skipped by design.'
    }
}

$sentinelAfter = Get-TaskSnapshot -TaskName $sentinelTaskName
$runData.cutover | Add-Member -NotePropertyName sentinel_task_before -NotePropertyValue $sentinelBefore
$runData.cutover | Add-Member -NotePropertyName sentinel_task_after -NotePropertyValue $sentinelAfter

if ($sentinelBefore.exists -and $sentinelAfter.exists) {
    if (($sentinelBefore.enabled -ne $sentinelAfter.enabled) -or ($sentinelBefore.state -ne $sentinelAfter.state)) {
        $runData.errors += 'Se detecto cambio no esperado en HITECH-OS-GitSentinel-Guardian.'
    }
}

$step++; Write-Stage -Index $step -Total $stepsTotal -Status 'Escribiendo resumen final'
$runData.success = [bool]($runData.errors.Count -eq 0 -and $schedulerInstallOk)
$runData | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Progress -Activity 'Engine Guardian privileged activation' -Completed
Write-Log ("Resumen: $summaryPath")
Write-Log ("Success: $($runData.success)")

if ($runData.success) {
    exit 0
}

exit 1
