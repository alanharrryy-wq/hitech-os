$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "chart-lab-local" @args
exit $LASTEXITCODE
