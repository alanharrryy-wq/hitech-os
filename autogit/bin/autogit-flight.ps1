$ErrorActionPreference = 'Stop'
$env:AUTOGIT_MODE = 'audit'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $Here 'autogit.ps1') @args
