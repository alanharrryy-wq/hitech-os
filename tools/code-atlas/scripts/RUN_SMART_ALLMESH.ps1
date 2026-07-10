param(
  [string]$RootPath = '',
  [string]$Surface = 'auto',
  [ValidateSet('auto','authority','data_ocr_licenses','operational','ui_surface','ndc_canon')]
  [string]$Intent = 'auto',
  [string]$Repo = 'F:\repos\hitech-os',
  [string]$OutRoot = 'F:\descargasf'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'

$AppRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Controller = Join-Path $AppRoot 'src\code_atlas\motors\smart_allmesh_controller.py'

if (!(Test-Path -LiteralPath $Controller)) {
  throw "No existe smart_allmesh_controller.py: $Controller"
}

$Python = $null
try { & py -3 --version *> $null; if ($LASTEXITCODE -eq 0) { $Python = 'py' } } catch {}
if (-not $Python) {
  try { & python --version *> $null; if ($LASTEXITCODE -eq 0) { $Python = 'python' } } catch {}
}
if (-not $Python) {
  try { & python3 --version *> $null; if ($LASTEXITCODE -eq 0) { $Python = 'python3' } } catch {}
}
if (-not $Python) {
  throw 'No encontré Python para Smart AllMesh.'
}

Write-Host "[SmartAllMesh] RootPath=$RootPath Surface=$Surface Intent=$Intent Repo=$Repo" -ForegroundColor Cyan

if ($Python -eq 'py') {
  & py -3 $Controller --root-path $RootPath --surface $Surface --intent $Intent --repo $Repo --out-root $OutRoot
} else {
  & $Python $Controller --root-path $RootPath --surface $Surface --intent $Intent --repo $Repo --out-root $OutRoot
}
exit $LASTEXITCODE
