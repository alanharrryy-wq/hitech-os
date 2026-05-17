$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "all-local-cloudflare" @args
exit $LASTEXITCODE
