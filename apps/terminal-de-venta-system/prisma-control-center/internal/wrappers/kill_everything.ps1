$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "kill-everything" @args
exit $LASTEXITCODE
