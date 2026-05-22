$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "module-cloudflare" @args
exit $LASTEXITCODE
