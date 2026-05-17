$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "panel" @args
exit $LASTEXITCODE
