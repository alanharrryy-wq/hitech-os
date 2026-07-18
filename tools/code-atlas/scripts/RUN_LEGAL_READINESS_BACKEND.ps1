#requires -Version 5.1
[CmdletBinding()]
param(
  [ValidateSet('plan','static','full','runtime-only')]
  [string]$Profile = 'plan',

  [switch]$IncludeRuntime,

  [ValidateSet('all','chart-lab','web','tablet','pc','mobile','control-center')]
  [string]$Surface = 'all',

  [ValidateRange(1,18)]
  [int]$Workers = 6,

  [ValidateRange(1,18)]
  [int]$Shards = 1,

  [switch]$Strict,
  [switch]$PrintPlan,
  [switch]$AuthorityOnly,

  [string]$CancelFile = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Src = Join-Path $Root 'src'

function Resolve-Python {
  foreach ($candidate in @('py.exe','python.exe','python3.exe','py','python3','python')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) {
      if ($candidate -in @('py.exe','py')) {
        return [pscustomobject]@{ Exe=$cmd.Source; Prefix=@('-3') }
      }
      return [pscustomobject]@{ Exe=$cmd.Source; Prefix=@() }
    }
  }
  throw 'PYTHON_RUNTIME_NOT_FOUND'
}

$Python = Resolve-Python
$OldPath = $env:PYTHONPATH
$OldUtf8 = $env:PYTHONUTF8
$OldIo = $env:PYTHONIOENCODING
$OldNoBytecode = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONPATH = if($OldPath){"$Src;$OldPath"}else{$Src}
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONDONTWRITEBYTECODE='1'

try {
  $Args = @(
    '-m','code_atlas.legal_readiness.cli',
    '--profile',$Profile,
    '--surface',$Surface,
    '--workers',[string]$Workers,
    '--shards',[string]$Shards
  )
  if($IncludeRuntime){$Args += '--include-runtime'}
  if($Strict){$Args += '--strict'}
  if($CancelFile){$Args += @('--cancel-file',$CancelFile)}
  if($PrintPlan){$Args += '--print-plan'}
  if($AuthorityOnly){$Args += '--authority-only'}

  & $Python.Exe @($Python.Prefix) @Args
  exit $LASTEXITCODE
}
finally {
  $env:PYTHONPATH=$OldPath
  $env:PYTHONUTF8=$OldUtf8
  $env:PYTHONIOENCODING=$OldIo
  $env:PYTHONDONTWRITEBYTECODE=$OldNoBytecode
}
