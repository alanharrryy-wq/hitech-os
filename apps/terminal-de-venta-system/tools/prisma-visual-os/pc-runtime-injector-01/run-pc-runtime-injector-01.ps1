param(
  [string]$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system",
  [string]$OutRoot = "F:\descargasf",
  [switch]$Strict
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $ScriptDir 'pc_runtime_injector_01.py'

if (-not (Test-Path -LiteralPath $Py)) {
  throw "No existe motor Python: $Py"
}

$ArgsList = @('--root', $Root, '--outroot', $OutRoot)
if ($Strict) { $ArgsList += '--strict' }

python $Py @ArgsList
