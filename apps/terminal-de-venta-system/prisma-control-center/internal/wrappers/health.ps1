$ErrorActionPreference = "Stop"
$ControlRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$Python = if ($env:PYTHON_EXE) { $env:PYTHON_EXE } elseif ($env:PYTHON) { $env:PYTHON } else { "python" }
$env:PYTHONDONTWRITEBYTECODE = "1"
& $Python (Join-Path $ControlRoot "internal\py\prisma_control_center.py") health @args
exit $LASTEXITCODE
