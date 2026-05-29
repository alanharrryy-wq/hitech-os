$ErrorActionPreference = 'Stop'
$env:AUTOGIT_MODE = 'audit'
& (Join-Path $PSScriptRoot 'autogit.ps1')
