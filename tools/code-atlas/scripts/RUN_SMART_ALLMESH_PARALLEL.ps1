param(
  [Parameter(Mandatory=$false)]
  [string[]]$Task = @(),
  [string]$TaskSpec = '',
  [string]$Repo = 'F:\repos\hitech-os',
  [string]$OutRoot = 'F:\descargasf',
  [string]$BudgetRoot = 'F:\descargasf\.prisma_automesh_worker_budget',
  [ValidateRange(1,18)]
  [int]$Parallel = 4,
  [ValidateRange(1,18)]
  [int]$Workers = 18,
  [ValidateRange(1,216)]
  [int]$Shards = 54,
  [ValidateRange(1,5000)]
  [int]$MaxFiles = 120,
  [ValidateRange(1,4096)]
  [int]$MaxMB = 40,
  [string]$RunId = ''
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'
$env:PYTHONUNBUFFERED = '1'

if (($Task.Count -lt 2) -and [string]::IsNullOrWhiteSpace($TaskSpec)) {
  throw 'Entrega al menos dos -Task o un -TaskSpec JSON con dos o más tareas.'
}

$CodeAtlasRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Supervisor = Join-Path $CodeAtlasRoot 'src\code_atlas\motors\smart_allmesh_parallel.py'
if (!(Test-Path -LiteralPath $Supervisor)) {
  throw "No existe smart_allmesh_parallel.py: $Supervisor"
}

$PythonExe = $null
$PythonPrefix = @()
try {
  & py -3 --version *> $null
  if ($LASTEXITCODE -eq 0) {
    $PythonExe = (Get-Command py -ErrorAction Stop).Source
    $PythonPrefix = @('-3')
  }
} catch {}
if (-not $PythonExe) {
  foreach ($Candidate in @('python', 'python3')) {
    try {
      & $Candidate --version *> $null
      if ($LASTEXITCODE -eq 0) {
        $PythonExe = (Get-Command $Candidate -ErrorAction Stop).Source
        break
      }
    } catch {}
  }
}
if (-not $PythonExe) {
  throw 'No encontré Python para Smart AllMesh Parallel.'
}

$ArgsList = @()
$ArgsList += $PythonPrefix
$ArgsList += $Supervisor
$ArgsList += @(
  '--repo', $Repo,
  '--out-root', $OutRoot,
  '--budget-root', $BudgetRoot,
  '--parallel', [string]$Parallel,
  '--workers', [string]$Workers,
  '--shards', [string]$Shards,
  '--max-files', [string]$MaxFiles,
  '--max-mb', [string]$MaxMB
)

foreach ($TaskValue in $Task) {
  if (-not [string]::IsNullOrWhiteSpace($TaskValue)) {
    $ArgsList += @('--task', $TaskValue.Trim())
  }
}
if (-not [string]::IsNullOrWhiteSpace($TaskSpec)) {
  $ArgsList += @('--task-spec', $TaskSpec)
}
if (-not [string]::IsNullOrWhiteSpace($RunId)) {
  $ArgsList += @('--run-id', $RunId.Trim())
}

Write-Host "[SmartAllMesh Parallel] Repo=$Repo Parallel=$Parallel RequestedWorkers=$Workers GlobalContract=18" -ForegroundColor Cyan
& $PythonExe @ArgsList
exit $LASTEXITCODE
