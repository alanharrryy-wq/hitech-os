# PRISMA_CLOUD_COMMAND_CENTER_3160_WRAPPER_V5_VSCODE_FOREGROUND_SAFE
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
      foreach ($nested in @($arg)) {
        if ($null -ne $nested) { $items.Add([string]$nested) }
      }
      continue
    }
    $items.Add([string]$arg)
  }
  return [string[]]$items.ToArray()
}

[void]$Code

if ($Detached -and $Foreground) {
  throw "cloud_command_center_3160.ps1 invalido: usa -Foreground o -Detached, no ambos."
}
if ($OpenBrowser -and $NoBrowser) {
  throw "cloud_command_center_3160.ps1 invalido: usa -OpenBrowser o -NoBrowser, no ambos."
}

$Launcher = Join-Path $PSScriptRoot "_launcher_common.ps1"
if (-not (Test-Path -LiteralPath $Launcher)) {
  throw "No encontre launcher comun requerido: $Launcher"
}

# Los parametros nombrados se pasan con hashtable splatting.
# Los argumentos remanentes se pasan aparte como array posicional.
$launcherParams = @{
  Profile = "cloud-command-center-3160"
}

# Default homologado del 3160: misma terminal, foreground, sin navegador automatico y reset de puerto delegado a _launcher_common.ps1.
if ($Detached) {
  $launcherParams["Detached"] = $true
} else {
  $launcherParams["Foreground"] = $true
}

if ($OpenBrowser) {
  $launcherParams["OpenBrowser"] = $true
} else {
  $launcherParams["NoBrowser"] = $true
}

$forward = @(ConvertTo-ForwardArgs -ArgsValue $ForwardArgs)

& $Launcher @launcherParams @forward
exit $LASTEXITCODE
