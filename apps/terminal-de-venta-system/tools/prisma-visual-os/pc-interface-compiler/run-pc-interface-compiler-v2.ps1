param(
  [string]$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system",
  [string]$OutRoot = "F:\descargasf",
  [switch]$Strict
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $ScriptDir 'pc_interface_compiler_v2.py'

if (-not (Test-Path -LiteralPath $Py)) {
  throw "No existe compiler v2: $Py"
}

$Generated = Join-Path $Root 'docs\design\pc-runtime-injector-01\generated'
New-Item -ItemType Directory -Force -Path $Generated | Out-Null

$ArgsList = @('--root', $Root, '--outroot', $OutRoot)
if ($Strict) { $ArgsList += '--strict' }

python $Py @ArgsList
