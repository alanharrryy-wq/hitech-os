param(
    [Parameter(Mandatory = $true)]
    [string]$Action
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param(
        [string]$Activity,
        [string]$Status,
        [int]$Percent
    )
    Write-Progress -Activity $Activity -Status $Status -PercentComplete $Percent
}

function Resolve-RepoRoot {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    return (Resolve-Path (Join-Path $scriptDir '..')).Path
}

function Resolve-Python {
    param([string]$RepoRoot)
    $candidates = @(
        (Join-Path $RepoRoot '.venv\Scripts\python.exe'),
        'python',
        'py'
    )
    foreach ($candidate in $candidates) {
        if ($candidate -in @('python', 'py')) {
            $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        } elseif (Test-Path $candidate) {
            return $candidate
        }
    }
    throw 'No se pudo resolver Python para engine_guardian.'
}

$repoRoot = Resolve-RepoRoot
$cliPath = Join-Path $repoRoot 'engine_guardian\cli.py'
if (-not (Test-Path $cliPath)) {
    throw "No existe cli.py en $cliPath"
}

$python = Resolve-Python -RepoRoot $repoRoot
Write-Step -Activity 'Engine Guardian igniter' -Status 'Resolviendo entrypoint canónico' -Percent 25

switch ($Action) {
    'start_all' { $arguments = @($cliPath, 'cycle', '--reason', 'boot', '--repair') }
    'heal_all' { $arguments = @($cliPath, 'heal') }
    'validate_all' { $arguments = @($cliPath, 'validate') }
    'check_health' { $arguments = @($cliPath, 'status') }
    'report_status' { $arguments = @($cliPath, 'status', '--json-only') }
    'start_keystone' { $arguments = @($cliPath, 'cycle', '--reason', 'manual', '--repair') }
    'heal_cloudflare' { $arguments = @($cliPath, 'heal') }
    'restart_guardian' { $arguments = @($cliPath, 'install-scheduler') }
    'tail_logs' {
        $logDir = Join-Path 'F:\OneDrive\Descargas\engine_guardian' 'logs'
        if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
        Get-ChildItem -Path $logDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object {
            Get-Content -Path $_.FullName -Wait
        }
        exit 0
    }
    'open_repo_analyzer' { $arguments = @($cliPath, 'repo-analyzer-open') }
    'validate_repo_analyzer' { $arguments = @($cliPath, 'repo-analyzer-validate') }
    'heal_repo_analyzer' { $arguments = @($cliPath, 'repo-analyzer-heal') }
    'report_repo_analyzer_status' { $arguments = @($cliPath, 'repo-analyzer-status', '--json-only') }
    default { throw "Igniter no soportado: $Action" }
}

Write-Step -Activity 'Engine Guardian igniter' -Status "Ejecutando $Action" -Percent 60
& $python @arguments
$exitCode = $LASTEXITCODE
Write-Step -Activity 'Engine Guardian igniter' -Status 'Terminado' -Percent 100
exit $exitCode
