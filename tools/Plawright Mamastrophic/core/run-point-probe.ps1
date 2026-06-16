param(
  [ValidateSet('all','chart-lab','chart_lab','3000','web','eit-web','eit_web','3110','tablet','tablet-pos','tablet_pos','pos','3120','pc','backoffice','pc-backoffice','pc_backoffice','3130','mobile','app','app-mobile','app_mobile','3140','control-center','control_center','prisma-control-center','prisma_control_center','3150')]
  [string]$Surface = 'tablet',
  [string]$Route = '',
  [int]$PointX = -1,
  [int]$PointY = -1,
  [int]$ViewportWidth = 1365,
  [int]$ViewportHeight = 768,
  [int]$GotoTimeoutMs = 15000,
  [int]$GotoRetries = 1,
  [int]$ScreenshotTimeoutMs = 15000,
  [int]$ProbeTimeoutMs = 1400,
  [int]$SettleMs = 700,
  [switch]$NoScreenshots,
  [switch]$AllowPartial,
  [string]$ArtifactRoot = '',
  [switch]$NoZip
)

$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolRoot = Split-Path -Parent $Here
$NodeScript = Join-Path $ToolRoot 'tests\surf8.point-probe.cjs'
if (!(Test-Path -LiteralPath $NodeScript)) { throw "No encontré point-probe CJS: $NodeScript" }

function Normalize-PointSurface {
  param([string]$Value)
  $k = ([string]$Value).Trim().ToLowerInvariant().Replace(' ', '_').Replace('-', '_')
  $map = @{
    'all'='all'; 'todo'='all'; 'todos'='all'; '*'='all'; '7'='all'; 'all_surfaces'='all';
    '3000'='chart-lab'; 'chart'='chart-lab'; 'chart_lab'='chart-lab'; 'chartlab'='chart-lab';
    '3110'='web'; 'web'='web'; 'eit'='web'; 'eit_web'='web';
    '3120'='tablet'; 'tablet'='tablet'; 'pos'='tablet'; 'tablet_pos'='tablet';
    '3130'='pc'; 'pc'='pc'; 'backoffice'='pc'; 'pc_backoffice'='pc';
    '3140'='mobile'; 'mobile'='mobile'; 'app'='mobile'; 'app_mobile'='mobile';
    '3150'='control-center'; 'control'='control-center'; 'control_center'='control-center'; 'prisma_control_center'='control-center'
  }
  if ($map.ContainsKey($k)) { return $map[$k] }
  throw "Surface inválida: $Value"
}

function Get-PointSurfaceCatalog {
  return @(
    [pscustomobject]@{ Surface='chart-lab'; Label='Chart Lab'; Port=3000; Route='/' },
    [pscustomobject]@{ Surface='web'; Label='EIT / Web'; Port=3110; Route='/' },
    [pscustomobject]@{ Surface='tablet'; Label='Tablet / POS'; Port=3120; Route='/pos' },
    [pscustomobject]@{ Surface='pc'; Label='PC Backoffice'; Port=3130; Route='/catalog' },
    [pscustomobject]@{ Surface='mobile'; Label='App / Mobile'; Port=3140; Route='/' },
    [pscustomobject]@{ Surface='control-center'; Label='Prisma Control Center'; Port=3150; Route='/' }
  )
}

function Find-PrismaRepoRoot {
  param([string]$Start)
  $item = Get-Item -LiteralPath $Start
  while ($null -ne $item) {
    $full = $item.FullName
    if (Test-Path -LiteralPath (Join-Path $full '.git')) { return $full }
    if ((Test-Path -LiteralPath (Join-Path $full 'apps\terminal-de-venta-system')) -and (Test-Path -LiteralPath (Join-Path $full 'package.json'))) { return $full }
    if ($item.Name -eq 'hitech-os') { return $full }
    $item = $item.Parent
  }
  $fallback = Split-Path -Parent (Split-Path -Parent $ToolRoot)
  return $fallback
}

function ConvertTo-Arg([object]$Value) {
  if ($null -eq $Value) { return '""' }
  $s = [string]$Value
  if ($s.Length -eq 0) { return '""' }
  if ($s -notmatch '[\s"]') { return $s }
  return '"' + ($s.Replace('"','\"')) + '"'
}

function New-PointZipFromDir {
  param([string]$SourceDir, [string]$ZipPath)
  if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
  $items = @(Get-ChildItem -LiteralPath $SourceDir -Force -ErrorAction SilentlyContinue)
  if ($items.Count -eq 0) { Set-Content -LiteralPath (Join-Path $SourceDir 'EMPTY.txt') -Encoding UTF8 -Value 'No point-probe artifacts were produced.' }
  Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force
}

function Show-PointProgress {
  param([int]$Done,[int]$Total,[string]$Msg)
  $safeTotal = [Math]::Max(1, [int]$Total)
  $pct = [int][Math]::Floor(([double]$Done / [double]$safeTotal) * 100.0)
  if ($pct -lt 0) { $pct = 0 }
  if ($pct -gt 100) { $pct = 100 }
  $rem = [int](100 - $pct)
  $fill = [int][Math]::Floor(([double]$pct * 28.0) / 100.0)
  if ($fill -lt 0) { $fill = 0 }
  if ($fill -gt 28) { $fill = 28 }
  $bar = ('#' * $fill).PadRight(28,'.')
  $pctText = ([string]$pct).PadLeft(3, ' ')
  $remText = ([string]$rem).PadLeft(3, ' ')
  Write-Host ('POINT ' + $pctText + '% [' + $bar + '] remaining ' + $remText + '% :: ' + $Msg) -ForegroundColor Cyan
}

$SurfaceKey = Normalize-PointSurface $Surface
$Node = Get-Command node -ErrorAction SilentlyContinue
if (-not $Node) { throw 'No encontré node en PATH.' }

$RepoRoot = Find-PrismaRepoRoot -Start $ToolRoot
$AppRoot = Join-Path $RepoRoot 'apps\terminal-de-venta-system'
if (!(Test-Path -LiteralPath $AppRoot)) { $AppRoot = $RepoRoot }
$PcAppRoot = Join-Path $AppRoot 'products\pc\app'
$OutRoot = 'F:\descargasf'
New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null
$stamp = Get-Date -Format 'ddMM HHmmss'
if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) { $ArtifactRoot = Join-Path $OutRoot ("mam point $SurfaceKey $stamp") }
New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null

$resolveRoots = @($AppRoot, $PcAppRoot, $RepoRoot, $ToolRoot, (Split-Path -Parent $ToolRoot), (Split-Path -Parent $RepoRoot)) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
$env:PRISMA_TOOL_ROOT = $ToolRoot
$env:PRISMA_REPO_ROOT = $RepoRoot
$env:PRISMA_APP_ROOT = $AppRoot
$env:PRISMA_PC_APP_ROOT = $PcAppRoot
$env:PRISMA_POINT_RESOLVE_ROOTS = ($resolveRoots -join ';')
$env:PRISMA_POINT_VIEWPORT_W = [string]$ViewportWidth
$env:PRISMA_POINT_VIEWPORT_H = [string]$ViewportHeight
$env:PRISMA_POINT_GOTO_TIMEOUT_MS = [string]$GotoTimeoutMs
$env:PRISMA_POINT_GOTO_RETRIES = [string]$GotoRetries
$env:PRISMA_POINT_SETTLE_MS = [string]$SettleMs
$env:PRISMA_POINT_NO_SCREENSHOTS = if ($NoScreenshots) { '1' } else { '0' }

$preflightDir = Join-Path $ArtifactRoot '_preflight'
New-Item -ItemType Directory -Force -Path $preflightDir | Out-Null
$preArgs = @($NodeScript, '--selftest-resolve', '--out-dir', $preflightDir)
$preCmd = ($Node.Source + ' ' + (($preArgs | ForEach-Object { ConvertTo-Arg $_ }) -join ' '))
Set-Content -LiteralPath (Join-Path $preflightDir 'resolve.command.txt') -Encoding UTF8 -Value $preCmd
& $Node.Source @preArgs *>&1 | Tee-Object -FilePath (Join-Path $preflightDir 'resolve.log')
$preCode = $LASTEXITCODE
if ($preCode -ne 0) {
  if (-not $NoZip) {
    $zipPath = Join-Path $OutRoot ("mam point $SurfaceKey $stamp resolve-fail.zip")
    New-PointZipFromDir -SourceDir $ArtifactRoot -ZipPath $zipPath
    Write-Host "POINT_PROBE_RESOLVE_FAIL_ZIP=$zipPath" -ForegroundColor Yellow
  }
  exit 2
}

$catalog = @(Get-PointSurfaceCatalog)
if ($SurfaceKey -ne 'all') { $catalog = @($catalog | Where-Object { $_.Surface -eq $SurfaceKey }) }
$total = @($catalog).Count
$done = 0
$records = @()

foreach ($s in $catalog) {
  $done++
  $surfaceRoute = if ([string]::IsNullOrWhiteSpace($Route)) { [string]$s.Route } else { $Route }
  $surfaceOut = Join-Path $ArtifactRoot $s.Surface
  New-Item -ItemType Directory -Force -Path $surfaceOut | Out-Null
  Show-PointProgress -Done $done -Total $total -Msg "probing $($s.Surface) $surfaceRoute"
  $args = @(
    $NodeScript,
    '--surface', $s.Surface,
    '--port', [string]$s.Port,
    '--route', $surfaceRoute,
    '--x', [string]$PointX,
    '--y', [string]$PointY,
    '--out-dir', $surfaceOut
  )
  if ($AllowPartial) { $args += '--allow-partial' }
  $cmdText = ($Node.Source + ' ' + (($args | ForEach-Object { ConvertTo-Arg $_ }) -join ' '))
  Set-Content -LiteralPath (Join-Path $surfaceOut 'point-probe.command.txt') -Encoding UTF8 -Value $cmdText
  & $Node.Source @args *>&1 | Tee-Object -FilePath (Join-Path $surfaceOut 'point-probe.log')
  $code = $LASTEXITCODE
  $summary = Join-Path $surfaceOut 'reports\point-summary.json'
  $records += [pscustomobject]@{ surface=$s.Surface; route=$surfaceRoute; port=$s.Port; exitCode=$code; summary=$summary; outDir=$surfaceOut }
  if ($code -ne 0 -and -not $AllowPartial) { throw "point-probe falló para $($s.Surface) exit=$code" }
}

$reports = Join-Path $ArtifactRoot '_reports'
New-Item -ItemType Directory -Force -Path $reports | Out-Null
$records | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $reports 'point-probe-records.json') -Encoding UTF8
$failCount = @($records | Where-Object { [int]$_.exitCode -ne 0 }).Count
$status = if ($failCount -gt 0) { 'PARTIAL' } else { 'PASS' }
[pscustomobject]@{ status=$status; surface=$SurfaceKey; records=$records; createdAt=(Get-Date).ToString('o'); repoRoot=$RepoRoot; appRoot=$AppRoot; pcAppRoot=$PcAppRoot; resolveRoots=$resolveRoots; policy='no repo changes, no process kill, no dev server start' } | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath (Join-Path $reports 'summary.json') -Encoding UTF8

if (-not $NoZip) {
  $zipName = "mam point $SurfaceKey $stamp " + ($(if ($failCount -gt 0) { 'partial' } else { 'result' })) + '.zip'
  $zipPath = Join-Path $OutRoot $zipName
  New-PointZipFromDir -SourceDir $ArtifactRoot -ZipPath $zipPath
  Write-Host "POINT_PROBE_ZIP=$zipPath" -ForegroundColor Green
}
if ($failCount -gt 0 -and -not $AllowPartial) { exit 2 }
exit 0
