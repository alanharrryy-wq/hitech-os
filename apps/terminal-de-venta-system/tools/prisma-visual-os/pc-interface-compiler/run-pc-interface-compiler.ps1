param(
  [string]$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system",
  [string]$OutRoot = "F:\descargasf",
  [switch]$Strict
)

$ErrorActionPreference = "Stop"

function Find-Python {
  $candidates = @("py", "python", "python3")
  foreach ($cmd in $candidates) {
    try {
      $null = & $cmd --version 2>$null
      if ($LASTEXITCODE -eq 0) { return $cmd }
    } catch {}
  }
  throw "No encontré Python en PATH. Instala Python o habilita el launcher 'py'."
}

$Python = Find-Python
$Engine = Join-Path $Root "tools\prisma-visual-os\pc-interface-compiler\prisma_pc_interface_compiler.py"
if (-not (Test-Path -LiteralPath $Engine)) {
  throw "No existe el engine: $Engine"
}

$argsList = @($Engine, "--root", $Root, "--outroot", $OutRoot)
if ($Strict) { $argsList += "--strict" }

& $Python @argsList
exit $LASTEXITCODE
