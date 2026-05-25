param(
  [object]$Code = $null,

  [string]$ServiceId = "",

  [Parameter(ValueFromRemainingArguments = $true)]
  [object[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $Utf8NoBom
$OutputEncoding = $Utf8NoBom
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8:replace"
$env:NO_COLOR = "1"

function ConvertTo-ExitCode {
  param([object]$Value, [int]$Default = 1)
  if ($null -eq $Value) { return [int]$Default }
  if ($Value -is [System.Array]) {
    $items = @($Value)
    for ($i = $items.Count - 1; $i -ge 0; $i--) {
      $candidate = ConvertTo-ExitCode -Value $items[$i] -Default ([int]::MinValue)
      if ($candidate -ne [int]::MinValue) { return [int]$candidate }
    }
    return [int]$Default
  }
  if ($Value -is [bool]) {
    if ($Value) { return 0 }
    return 1
  }
  $parsed = 0
  if ([int]::TryParse(([string]$Value).Trim(), [ref]$parsed)) { return [int]$parsed }
  return [int]$Default
}

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

$forward = @(ConvertTo-ForwardArgs -ArgsValue $ForwardArgs)
[void](ConvertTo-ExitCode -Value $Code -Default 0)
if ($ServiceId) {
  while ($forward.Count -gt 0 -and -not ([string]$forward[0]).StartsWith("-")) {
    $forward = @($forward | Select-Object -Skip 1)
  }
  & (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "module-cloudflare" -ServiceId $ServiceId @forward
  exit (ConvertTo-ExitCode -Value $LASTEXITCODE -Default 1)
}

& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "module-cloudflare" @forward
exit (ConvertTo-ExitCode -Value $LASTEXITCODE -Default 1)
