$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
python (Join-Path $Here 'tools\verify_prisma_factory_ledger.py') $Here
