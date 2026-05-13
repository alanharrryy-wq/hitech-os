$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "all-cloudflare" @args
exit $LASTEXITCODE
