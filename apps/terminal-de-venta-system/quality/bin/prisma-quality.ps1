$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$QualityRoot = Split-Path -Parent $ScriptRoot
$Bin = Join-Path $QualityRoot "bin\prisma-quality.mjs"
node $Bin @args
exit $LASTEXITCODE
