# PRISMA_CLOUD_COMMAND_CENTER_3160_WRAPPER_V2
param(
  [switch]$Foreground,
  [switch]$Detached,
  [switch]$OpenBrowser,
  [switch]$NoBrowser,
  [object]$Code = $null,
  [Parameter(ValueFromRemainingArguments = $true)]
  [object[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

function ConvertTo-ForwardArgs {
  param([object[]]$ArgsValue)
  $items = New-Object System.Collections.Generic.List[string]
  foreach ($arg in @($ArgsValue)) {
    if ($null -eq $arg) { continue }
    if ($arg -is [System.Array]) {
      foreach ($nested in @($arg)) { if ($null -ne $nested) { $items.Add([string]$nested) } }
      continue
    }
    $items.Add([string]$arg)
  }
  return [string[]]$items.ToArray()
}

$forward = @(ConvertTo-ForwardArgs -ArgsValue $ForwardArgs)
[void]$Code
$launcherArgs = @("-Profile", "cloud-command-center-3160")

if ($Detached -and $Foreground) { throw "cloud_command_center_3160.ps1 invalido: usa -Foreground o -Detached, no ambos." }
if ($OpenBrowser -and $NoBrowser) { throw "cloud_command_center_3160.ps1 invalido: usa -OpenBrowser o -NoBrowser, no ambos." }

# Default homologado del 3160: foreground, sin navegador automatico.
if ($Detached) { $launcherArgs += "-Detached" } else { $launcherArgs += "-Foreground" }
if ($OpenBrowser) { $launcherArgs += "-OpenBrowser" } else { $launcherArgs += "-NoBrowser" }

& (Join-Path $PSScriptRoot "_launcher_common.ps1") @launcherArgs @forward
exit $LASTEXITCODE
