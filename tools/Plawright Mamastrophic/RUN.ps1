param(
  [ValidateSet('discovery','quick','full','critical')]
  [string]$Mode = 'quick',

  [ValidateSet('all','chart-lab','chart_lab','3000','web','eit-web','eit_web','3110','tablet','tablet-pos','tablet_pos','pos','3120','pc','backoffice','pc-backoffice','pc_backoffice','3130','mobile','app','app-mobile','app_mobile','3140','control-center','control_center','prisma-control-center','prisma_control_center','3150')]
  [string]$Surface = 'all',

  [int]$Workers = 6,

  [switch]$NoScreenshots,

  [int]$Shards = 1,

  [switch]$FullPage,

  [switch]$AllowPartial,

  [switch]$Strict,

  [ValidateSet('off','auto','on')]
  [string]$GpuMode = 'off'
)

$ErrorActionPreference = 'Stop'

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$CoreRunner = Join-Path $Here 'core\run-surf8-capture.ps1'

if (!(Test-Path -LiteralPath $CoreRunner)) {
  throw "No encontre core runner: $CoreRunner"
}

Write-Host "PRISMA Plawright Mamastrophic arr5 fix2" -ForegroundColor Cyan
Write-Host "Root: $Here" -ForegroundColor DarkCyan
Write-Host "Mode: $Mode | Surface: $Surface | Workers: $Workers | Shards: $Shards | GpuMode: $GpuMode" -ForegroundColor DarkCyan
Write-Host "Policy: no start, no kill, no DB, no deploy" -ForegroundColor DarkCyan

$argsList = @('-Mode', $Mode, '-Surface', $Surface, '-Workers', $Workers, '-Shards', $Shards, '-GpuMode', $GpuMode)
if ($NoScreenshots) { $argsList += '-NoScreenshots' }
if ($FullPage) { $argsList += '-FullPage' }
if ($AllowPartial) { $argsList += '-AllowPartial' }
if ($Strict) { $argsList += '-Strict' }

& powershell -NoProfile -ExecutionPolicy Bypass -File $CoreRunner @argsList
exit $LASTEXITCODE
