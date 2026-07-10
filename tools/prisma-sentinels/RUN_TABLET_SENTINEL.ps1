$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) { & py -3 (Join-Path $PSScriptRoot 'prisma_tablet_integrity_sentinel.py') --fix --skip-install --repo $Root } else { & python (Join-Path $PSScriptRoot 'prisma_tablet_integrity_sentinel.py') --fix --skip-install --repo $Root }
