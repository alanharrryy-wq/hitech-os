param(
  [string]$RootPath = '',
  [string]$Surface = 'auto',
  [ValidateSet('auto','authority','data_ocr_licenses','operational','ui_surface','ndc_canon')]
  [string]$Intent = 'auto',
  [string]$Repo = 'F:\repos\hitech-os',
  [string]$OutRoot = 'F:\descargasf',
  [ValidateRange(1,18)]
  [int]$Workers = 18,
  [ValidateRange(1,216)]
  [int]$Shards = 72,
  [ValidateRange(1,5000)]
  [int]$MaxFiles = 360,
  [ValidateRange(1,4096)]
  [int]$MaxMB = 140,
  [string]$RunId = '',
  [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'
$env:PYTHONUNBUFFERED = '1'

$AppRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Controller = Join-Path $AppRoot 'src\code_atlas\motors\smart_allmesh_controller.py'

if (!(Test-Path -LiteralPath $Controller)) {
  throw "No existe smart_allmesh_controller.py: $Controller"
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
  throw 'No encontré Python para Smart AllMesh.'
}

$ArgsList = @()
$ArgsList += $PythonPrefix
$ArgsList += $Controller

if ($SelfTest) {
  $ArgsList += '--self-test'
} else {
  $ArgsList += @(
    '--root-path', $RootPath,
    '--surface', $Surface,
    '--intent', $Intent,
    '--repo', $Repo,
    '--out-root', $OutRoot,
    '--workers', [string]$Workers,
    '--shards', [string]$Shards,
    '--max-files', [string]$MaxFiles,
    '--max-mb', [string]$MaxMB
  )
  if (-not [string]::IsNullOrWhiteSpace($RunId)) {
    $ArgsList += @('--run-id', $RunId.Trim())
  }
}

Write-Host "[SmartAllMesh v6] RootPath=$RootPath Surface=$Surface Intent=$Intent Repo=$Repo Workers=$Workers Shards=$Shards" -ForegroundColor Cyan
& $PythonExe @ArgsList
exit $LASTEXITCODE
