$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "web-control-local-cloudflare" @args
exit $LASTEXITCODE
