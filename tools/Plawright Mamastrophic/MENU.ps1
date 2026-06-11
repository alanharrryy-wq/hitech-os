param(
  [ValidateSet('menu','capture','studio','discovery')]
  [string]$Action = 'menu',

  [string[]]$Apps = @(),
  [string[]]$Phases = @(),

  [ValidateSet('off','auto','on')]
  [string]$GpuMode = 'off',

  [int]$TestTimeoutMs = 0,
  [int]$GotoTimeoutMs = 45000,
  [int]$GotoRetries = 2,
  [int]$ScreenshotTimeoutMs = 15000,
  [int]$ProbeTimeoutMs = 1400,

  [ValidateSet('auto','on','off')]
  [string]$SurfaceParallel = 'auto',
  [int]$SurfaceParallelMax = 4,
  [int]$SurfaceChildWorkers = 1,

  [int]$Workers = 6,
  [int]$Shards = 1,
  [switch]$AllowPartial,
  [switch]$FullPage,
  [switch]$NoScreenshots,
  [ValidateSet('auto','on','off')]
  [string]$DeepScroll = 'auto',
  [int]$MaxPageTiles = 180,
  [int]$MaxScrollContainers = 36,
  [int]$MaxContainerTiles = 120,
  [int]$TileOverlapPx = 80,
  [string]$StudioPath = '/',
  [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$ToolRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Runner = Join-Path $ToolRoot 'RUN.ps1'
$RepoRoot = if ($env:PRISMA_TERMINAL_ROOT -and -not [string]::IsNullOrWhiteSpace($env:PRISMA_TERMINAL_ROOT)) { $env:PRISMA_TERMINAL_ROOT } else { 'F:\repos\hitech-os\apps\terminal-de-venta-system' }
$OutDir = 'F:\descargasf'

$SurfaceCatalog = @(
  [pscustomobject]@{ Key = '1'; Surface = 'chart-lab';      Aliases = @('chart','chart_lab','chartlab','3000');       Port = 3000; Label = 'Chart Lab';             BaseUrl = 'http://127.0.0.1:3000' },
  [pscustomobject]@{ Key = '2'; Surface = 'web';            Aliases = @('eit','eit_web','web_eit','3110');           Port = 3110; Label = 'EIT / Web';             BaseUrl = 'http://127.0.0.1:3110' },
  [pscustomobject]@{ Key = '3'; Surface = 'tablet';         Aliases = @('pos','tablet_pos','3120');                  Port = 3120; Label = 'Tablet / POS';          BaseUrl = 'http://127.0.0.1:3120' },
  [pscustomobject]@{ Key = '4'; Surface = 'pc';             Aliases = @('backoffice','pc_backoffice','3130');         Port = 3130; Label = 'PC Backoffice';         BaseUrl = 'http://127.0.0.1:3130' },
  [pscustomobject]@{ Key = '5'; Surface = 'mobile';         Aliases = @('app','app_mobile','3140');                  Port = 3140; Label = 'App / Mobile';          BaseUrl = 'http://127.0.0.1:3140' },
  [pscustomobject]@{ Key = '6'; Surface = 'control-center'; Aliases = @('control','control_center','3150');          Port = 3150; Label = 'Prisma Control Center'; BaseUrl = 'http://127.0.0.1:3150' },
  [pscustomobject]@{ Key = '7'; Surface = 'all';            Aliases = @('todo','todos','all_surfaces');              Port = 0;    Label = 'ALL - todas paralelo';  BaseUrl = '' }
)

$PhaseCatalog = @(
  [pscustomobject]@{ Key = '1'; Phase = 'discovery'; Label = 'Discovery - radar de superficies' },
  [pscustomobject]@{ Key = '2'; Phase = 'quick';     Label = 'Quick - subset rapido' },
  [pscustomobject]@{ Key = '3'; Phase = 'critical';  Label = 'Critical - rutas delicadas' },
  [pscustomobject]@{ Key = '4'; Phase = 'full';          Label = 'Full - barredora completa' },
  [pscustomobject]@{ Key = '7'; Phase = 'visualqa';      Label = 'VisualQA - DOM/computed/render layers' },
  [pscustomobject]@{ Key = '8'; Phase = 'screenshots';   Label = 'Screenshots only - evidencia visual sin QA pesado' },
  [pscustomobject]@{ Key = '9'; Phase = 'screenshotsqa'; Label = 'Screenshots + QA - capturas con DOM/computed/render layers' }
)

function Write-Banner {
  param([string]$Title)
  Write-Host ''
  Write-Host '============================================================' -ForegroundColor Cyan
  Write-Host $Title -ForegroundColor Cyan
  Write-Host '============================================================' -ForegroundColor Cyan
}

function Show-ProgressLine {
  param([int]$Index, [int]$Total, [string]$Message)
  $pct = [Math]::Floor(($Index / [Math]::Max($Total, 1)) * 100)
  $filled = [Math]::Floor($pct * 20 / 100)
  $bar = ('#' * $filled).PadRight(20, '.')
  $remaining = 100 - $pct
  Write-Host ("PROGRESS {0:000}% [{1}] remaining {2:000}% :: {3}" -f $pct, $bar, $remaining, $Message) -ForegroundColor DarkCyan
}

function Test-PortOpen {
  param([int]$Port)
  if ($Port -le 0) { return $true }
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(350, $false)
    if ($ok) { $client.EndConnect($iar) }
    $client.Close()
    return [bool]$ok
  } catch {
    return $false
  }
}

function Normalize-Token {
  param([string]$Value)
  return (($Value -replace '-', '_' -replace ' ', '_').Trim().ToLowerInvariant())
}

function Split-InputTokens {
  param([string[]]$Values)
  $tokens = @()
  foreach ($v in $Values) {
    if ($null -eq $v) { continue }
    foreach ($part in ([string]$v -split '[,; ]+')) {
      $p = $part.Trim()
      if ($p.Length -gt 0) { $tokens += $p }
    }
  }
  return $tokens
}

function Resolve-Surfaces {
  param([string[]]$Values)
  $tokens = Split-InputTokens $Values
  if ($tokens.Count -eq 0) { return @() }
  $selected = @()
  foreach ($token in $tokens) {
    $norm = Normalize-Token $token
    $match = $SurfaceCatalog | Where-Object {
      (Normalize-Token $_.Key) -eq $norm -or
      (Normalize-Token $_.Surface) -eq $norm -or
      ([string]$_.Port) -eq $token -or
      ($_.Aliases | ForEach-Object { Normalize-Token $_ }) -contains $norm
    } | Select-Object -First 1
    if (-not $match) { throw "Superficie invalida: $token" }
    if ($match.Surface -eq 'all') { return @($match) }
    if (-not ($selected | Where-Object { $_.Surface -eq $match.Surface })) { $selected += $match }
  }
  return $selected
}

function Add-UniquePhase {
  param(
    [object[]]$Current,
    [object]$PhaseItem
  )
  if ($null -eq $PhaseItem) { return @($Current) }
  if (-not ($Current | Where-Object { $_.Phase -eq $PhaseItem.Phase })) {
    return @($Current + $PhaseItem)
  }
  return @($Current)
}

function Resolve-Phases {
  param([string[]]$Values)
  $tokens = Split-InputTokens $Values
  if ($tokens.Count -eq 0) { return @() }
  $selected = @()
  foreach ($token in $tokens) {
    $norm = Normalize-Token $token

    # Menu option 6 can appear alone or inside comma lists, for example: 1,6.
    if ($norm -in @('6','all','todas','todo','allphases','all_phases')) {
      return @($PhaseCatalog | Where-Object { $_.Phase -in @('discovery','quick','critical','full','visualqa') })
    }

    # Menu option 5 is the quick+full combo. It must work alone and inside lists,
    # for example: 5, 1,5, discovery,5, or quick_full.
    if ($norm -in @('5','quick_full','quickfull','quick+full','quick-full','qf')) {
      foreach ($p in @('quick','full')) {
        $phaseItem = $PhaseCatalog | Where-Object { $_.Phase -eq $p } | Select-Object -First 1
        $selected = Add-UniquePhase -Current $selected -PhaseItem $phaseItem
      }
      continue
    }

    $match = $PhaseCatalog | Where-Object {
      (Normalize-Token $_.Key) -eq $norm -or (Normalize-Token $_.Phase) -eq $norm
    } | Select-Object -First 1
    if (-not $match) { throw "Fase invalida: $token" }
    $selected = Add-UniquePhase -Current $selected -PhaseItem $match
  }
  return $selected
}

function Show-SurfaceStatus {
  Write-Host ''
  Write-Host 'Apps / superficies:' -ForegroundColor Cyan
  foreach ($s in $SurfaceCatalog) {
    $portText = if ($s.Port -gt 0) { ':' + $s.Port } else { '' }
    $state = if ($s.Port -gt 0) { if (Test-PortOpen $s.Port) { 'ONLINE ' } else { 'OFFLINE' } } else { 'mixed  ' }
    $color = if ($state -like 'ONLINE*') { 'Green' } elseif ($state -like 'OFFLINE*') { 'Yellow' } else { 'Gray' }
    Write-Host ("  {0}) {1,-24} {2,-6} {3,-7} -> {4}" -f $s.Key, $s.Label, $portText, $state, $s.Surface) -ForegroundColor $color
  }
}

function Show-PhaseList {
  Write-Host ''
  Write-Host 'Fases:' -ForegroundColor Cyan
  foreach ($p in $PhaseCatalog) {
    Write-Host ("  {0}) {1,-10} {2}" -f $p.Key, $p.Phase, $p.Label) -ForegroundColor White
  }
  Write-Host '  5) quick,full  combo comun' -ForegroundColor White
  Write-Host '  6) all         fases base: discovery, quick, critical, full, visualqa' -ForegroundColor White
  Write-Host '  8) screenshots solo capturas, sin QA pesado' -ForegroundColor White
  Write-Host '  9) screenshotsqa capturas + QA DOM/computed/render layers' -ForegroundColor White
}


function New-MenuZipFromDir {
  param([string]$SourceDir, [string]$ZipPath)
  if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
  if (-not (Test-Path -LiteralPath $SourceDir)) { throw "No existe carpeta para ZIP: $SourceDir" }
  Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force
}

function Move-MenuStageToTrash {
  param([string]$StageDir, [string]$RunName)
  if (-not (Test-Path -LiteralPath $StageDir)) { return }
  $trashRoot = 'F:\Trash-old'
  New-Item -ItemType Directory -Force -Path $trashRoot | Out-Null
  $dest = Join-Path $trashRoot ($RunName + ' stage ' + (Get-Date -Format 'ddMM HHmmss'))
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $manifest = [ordered]@{ movedAt=(Get-Date).ToString('o'); source=$StageDir; destination=$dest; reason='Mamastrophic menu staging moved after final app ZIPs were created' }
  $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $dest 'manifest.json') -Encoding UTF8
  Set-Content -LiteralPath (Join-Path $dest 'manifest.md') -Encoding UTF8 -Value "# Mamastrophic moved stage`r`n`r`n- source: `$StageDir`r`n- destination: `$dest`r`n- reason: final app ZIPs already contain the evidence."
  Move-Item -LiteralPath $StageDir -Destination (Join-Path $dest (Split-Path -Leaf $StageDir)) -Force
}

function Get-AppPhaseStatus {
  param([string]$AppRoot)
  $records = @()
  foreach ($phaseDir in @(Get-ChildItem -LiteralPath (Join-Path $AppRoot 'phases') -Directory -ErrorAction SilentlyContinue)) {
    $summaryPath = Join-Path $phaseDir.FullName 'reports\summary.json'
    $fatalPath = Join-Path $phaseDir.FullName 'reports\fatal.json'
    $status = 'UNKNOWN'
    $mode = $phaseDir.Name
    $exitCode = $null
    if (Test-Path -LiteralPath $summaryPath) {
      try {
        $sum = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
        if ($sum.status) { $status = [string]$sum.status }
        if ($sum.mode) { $mode = [string]$sum.mode }
        if ($sum.playwrightExitCode -ne $null) { $exitCode = $sum.playwrightExitCode }
      } catch { $status = 'SUMMARY_PARSE_FAIL' }
    } elseif (Test-Path -LiteralPath $fatalPath) {
      $status = 'FAIL'
    }
    $records += [ordered]@{ phase=$mode; status=$status; exitCode=$exitCode; path=$phaseDir.FullName }
  }
  return @($records)
}

function Invoke-BundledAllAppsRun {
  param([object[]]$SelectedPhases)
  if (-not (Test-Path -LiteralPath $Runner)) { throw "No encuentro Mamastrophic RUN.ps1: $Runner" }
  $stamp = Get-Date -Format 'ddMM HHmmss'
  $bundleRoot = Join-Path $OutDir "mambundle $stamp"
  New-Item -ItemType Directory -Force -Path $bundleRoot | Out-Null
  $phaseFailures = 0

  Write-Banner 'BUNDLE ALL APPS :: maximo 6 ZIPs finales'
  Write-Host "Bundle root temporal: $bundleRoot" -ForegroundColor DarkCyan
  Write-Host 'Cada fase corre Surface all pero sin ZIP hijo; al final se empaqueta 1 ZIP por app.' -ForegroundColor DarkCyan

  $phaseIndex = 0
  foreach ($phase in $SelectedPhases) {
    $phaseIndex++
    Write-Banner ("BUNDLE PHASE {0}/{1} :: {2}" -f $phaseIndex, $SelectedPhases.Count, $phase.Phase)
    Show-ProgressLine -Index $phaseIndex -Total $SelectedPhases.Count -Message ("fase {0} all apps" -f $phase.Phase)
    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$Runner,'-Mode',$phase.Phase,'-Surface','all','-Workers',[string]$Workers,'-Shards',[string]$Shards,'-GpuMode',$GpuMode,'-TestTimeoutMs',[string]$TestTimeoutMs,'-GotoTimeoutMs',[string]$GotoTimeoutMs,'-GotoRetries',[string]$GotoRetries,'-ScreenshotTimeoutMs',[string]$ScreenshotTimeoutMs,'-ProbeTimeoutMs',[string]$ProbeTimeoutMs,'-SurfaceParallel',$SurfaceParallel,'-SurfaceParallelMax',[string]$SurfaceParallelMax,'-SurfaceChildWorkers',[string]$SurfaceChildWorkers,'-DeepScroll',$DeepScroll,'-MaxPageTiles',[string]$MaxPageTiles,'-MaxScrollContainers',[string]$MaxScrollContainers,'-MaxContainerTiles',[string]$MaxContainerTiles,'-TileOverlapPx',[string]$TileOverlapPx,'-ArtifactRoot',$bundleRoot,'-NoZip')
    if ($AllowPartial) { $args += '-AllowPartial' }
    if ($FullPage) { $args += '-FullPage' }
    if ($NoScreenshots) { $args += '-NoScreenshots' }
    Write-Host ("powershell {0}" -f ($args -join ' ')) -ForegroundColor DarkCyan
    & powershell @args
    $code = $LASTEXITCODE
    if ($code -ne 0) { $phaseFailures++; Write-Host ("WARN bundle phase={0} exit={1}; sigo para empaquetar evidencia." -f $phase.Phase, $code) -ForegroundColor Yellow }
  }

  $appsRoot = Join-Path $bundleRoot 'apps'
  $appSurfaces = @($SurfaceCatalog | Where-Object { $_.Surface -ne 'all' })
  $created = @()
  foreach ($app in $appSurfaces) {
    $appRoot = Join-Path $appsRoot $app.Surface
    if (-not (Test-Path -LiteralPath $appRoot)) { New-Item -ItemType Directory -Force -Path $appRoot | Out-Null }
    $records = @(Get-AppPhaseStatus -AppRoot $appRoot)
    $appFail = @($records | Where-Object { [string]$_['status'] -in @('FAIL','UNKNOWN','SUMMARY_PARSE_FAIL') }).Count -gt 0
    $zipStatus = if ($appFail) { 'fail' } else { 'result' }
    $summary = [ordered]@{ app=$app.Surface; label=$app.Label; status=$zipStatus.ToUpperInvariant(); phases=@($records); maxZipPolicy='1 zip per app, max 6 final zips'; generatedAt=(Get-Date).ToString('o') }
    $summary | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath (Join-Path $appRoot 'APP_BUNDLE_SUMMARY.json') -Encoding UTF8
    $md = @('# Mamastrophic app bundle', '', "- app: $($app.Surface)", "- status: $($zipStatus.ToUpperInvariant())", '- policy: max 6 final ZIPs, one per app', '', '## Phases')
    foreach ($r in $records) { $md += "- $($r.phase): $($r.status)" }
    Set-Content -LiteralPath (Join-Path $appRoot 'APP_BUNDLE_SUMMARY.md') -Encoding UTF8 -Value ($md -join "`r`n")
    $zip = Join-Path $OutDir ("mamshot $($app.Surface) bundle $stamp $zipStatus.zip")
    New-MenuZipFromDir -SourceDir $appRoot -ZipPath $zip
    $created += $zip
    Write-Host ("APP BUNDLE ZIP {0}: {1}" -f $zipStatus.ToUpperInvariant(), $zip) -ForegroundColor ($(if ($appFail) { 'Red' } else { 'Green' }))
  }

  Move-MenuStageToTrash -StageDir $bundleRoot -RunName 'mambundle'
  Write-Banner 'BUNDLE FINAL'
  Write-Host 'ZIPs finales creados:' -ForegroundColor Cyan
  foreach ($z in $created) { Write-Host "  $z" -ForegroundColor White }
  if ($phaseFailures -gt 0 -or (@($created | Where-Object { $_ -match ' fail\.zip$' }).Count -gt 0)) { exit 2 }
  exit 0
}

function Invoke-CaptureRun {
  param(
    [object[]]$SelectedSurfaces,
    [object[]]$SelectedPhases
  )
  if (-not (Test-Path -LiteralPath $Runner)) { throw "No encuentro Mamastrophic RUN.ps1: $Runner" }
  if ($SelectedSurfaces.Count -eq 0) { throw 'No hay superficies seleccionadas.' }
  if ($SelectedPhases.Count -eq 0) { throw 'No hay fases seleccionadas.' }

  if (($SelectedSurfaces | Where-Object { $_.Surface -eq 'all' }).Count -gt 0 -and $SelectedPhases.Count -gt 1) {
    Invoke-BundledAllAppsRun -SelectedPhases $SelectedPhases
  }

  $jobs = @()
  foreach ($phase in $SelectedPhases) {
    foreach ($surface in $SelectedSurfaces) {
      $jobs += [pscustomobject]@{ Phase = $phase.Phase; Surface = $surface.Surface; Label = $surface.Label; Port = $surface.Port }
    }
  }

  $failures = 0
  $index = 0
  foreach ($job in $jobs) {
    $index++
    Write-Banner ("CAPTURE :: {0} :: {1}" -f $job.Phase, $job.Surface)
    Show-ProgressLine -Index $index -Total $jobs.Count -Message ("lanzando {0} {1}" -f $job.Phase, $job.Surface)

    if ($job.Port -gt 0) {
      $online = Test-PortOpen $job.Port
      if (-not $online) {
        Write-Host ("Aviso: puerto {0} offline. Mamastrophic decidira PASS/PARTIAL/FAIL segun fase." -f $job.Port) -ForegroundColor Yellow
      }
    }

    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$Runner,'-Mode',$job.Phase,'-Surface',$job.Surface,'-Workers',[string]$Workers,'-Shards',[string]$Shards,'-GpuMode',$GpuMode,'-TestTimeoutMs',[string]$TestTimeoutMs,'-GotoTimeoutMs',[string]$GotoTimeoutMs,'-GotoRetries',[string]$GotoRetries,'-ScreenshotTimeoutMs',[string]$ScreenshotTimeoutMs,'-ProbeTimeoutMs',[string]$ProbeTimeoutMs,'-SurfaceParallel',$SurfaceParallel,'-SurfaceParallelMax',[string]$SurfaceParallelMax,'-SurfaceChildWorkers',[string]$SurfaceChildWorkers,'-DeepScroll',$DeepScroll,'-MaxPageTiles',[string]$MaxPageTiles,'-MaxScrollContainers',[string]$MaxScrollContainers,'-MaxContainerTiles',[string]$MaxContainerTiles,'-TileOverlapPx',[string]$TileOverlapPx)
    if ($AllowPartial) { $args += '-AllowPartial' }
    if ($FullPage) { $args += '-FullPage' }
    if ($NoScreenshots) { $args += '-NoScreenshots' }

    Write-Host ("powershell {0}" -f ($args -join ' ')) -ForegroundColor DarkCyan
    & powershell @args
    $code = $LASTEXITCODE
    if ($code -ne 0) {
      $failures++
      Write-Host ("FAIL fase={0} surface={1} exit={2}" -f $job.Phase, $job.Surface, $code) -ForegroundColor Red
    } else {
      Write-Host ("OK fase={0} surface={1}" -f $job.Phase, $job.Surface) -ForegroundColor Green
    }
  }

  if ($failures -gt 0) { exit 2 }
  exit 0
}

function Find-PlaywrightCommand {
  $pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
  if ($pnpm) { return [pscustomobject]@{ Exe = $pnpm.Source; Prefix = @('exec','playwright','codegen') } }
  $npx = Get-Command npx -ErrorAction SilentlyContinue
  if ($npx) { return [pscustomobject]@{ Exe = $npx.Source; Prefix = @('playwright','codegen') } }
  $pw = Get-Command playwright -ErrorAction SilentlyContinue
  if ($pw) { return [pscustomobject]@{ Exe = $pw.Source; Prefix = @('codegen') } }
  throw 'No encontre pnpm, npx ni playwright para abrir Studio/codegen.'
}

function Invoke-StudioRun {
  param([object[]]$SelectedSurfaces)
  if ($SelectedSurfaces.Count -eq 0) { throw 'No hay superficies seleccionadas para Studio.' }
  if ($SelectedSurfaces | Where-Object { $_.Surface -eq 'all' }) {
    throw 'Studio no abre all de golpe. Elige apps concretas: pc, tablet, web, mobile, chart-lab o control-center.'
  }
  $cmd = Find-PlaywrightCommand
  $cwd = Join-Path $RepoRoot 'products\pc\app'
  if (-not (Test-Path -LiteralPath $cwd)) { $cwd = $RepoRoot }

  foreach ($s in $SelectedSurfaces) {
    Write-Banner ("STUDIO :: {0}" -f $s.Surface)
    if (-not (Test-PortOpen $s.Port)) {
      Write-Host ("SKIP: puerto {0} offline. No levanto servicios por politica." -f $s.Port) -ForegroundColor Yellow
      continue
    }
    $path = $StudioPath
    if (-not $path.StartsWith('/')) { $path = '/' + $path }
    $url = $s.BaseUrl.TrimEnd('/') + $path
    $args = @()
    $args += $cmd.Prefix
    $args += $url
    Write-Host ("cwd: {0}" -f $cwd) -ForegroundColor DarkGray
    Write-Host ("{0} {1}" -f $cmd.Exe, ($args -join ' ')) -ForegroundColor DarkCyan
    Push-Location $cwd
    try {
      & $cmd.Exe @args
    } finally {
      Pop-Location
    }
  }
}

function Start-InteractiveMenu {
  Clear-Host
  Write-Banner 'PRISMA Mamastrophic Menu por fases'
  Write-Host 'Default GPU: off. Opcion 7 en Apps = ALL superficies. DeepScroll auto = ON. No start, no kill, no DB, no deploy.' -ForegroundColor Gray
  Write-Host ''
  Write-Host '1) Capturas por fases' -ForegroundColor White
  Write-Host '2) Studio / Playwright codegen por app' -ForegroundColor White
  Write-Host '3) Discovery all' -ForegroundColor White
  Write-Host '0) Salir' -ForegroundColor White
  Write-Host ''
  $actionChoice = Read-Host 'Opcion'

  if ($actionChoice -eq '0') { exit 0 }
  if ($actionChoice -eq '3') {
    Invoke-CaptureRun -SelectedSurfaces (Resolve-Surfaces @('all')) -SelectedPhases (Resolve-Phases @('discovery'))
  }

  Show-SurfaceStatus
  Write-Host ''
  $appInput = Read-Host 'Apps, numeros o puertos separados por coma. Ej: 4 o pc,tablet o 3130,3120'
  $selectedSurfaces = Resolve-Surfaces @($appInput)

  if ($actionChoice -eq '2') {
    $pathInput = Read-Host 'Ruta para Studio/codegen, default /'
    if ($pathInput.Trim().Length -gt 0) { $script:StudioPath = $pathInput.Trim() }
    Invoke-StudioRun -SelectedSurfaces $selectedSurfaces
    exit 0
  }

  Show-PhaseList
  Write-Host ''
  $phaseInput = Read-Host 'Fases separadas por coma. Ej: quick o discovery,quick o 1,5'
  if ($phaseInput.Trim() -eq '5') { $phaseInput = 'quick,full' }
  if ($phaseInput.Trim() -eq '6') { $phaseInput = 'all' }
  $selectedPhases = Resolve-Phases @($phaseInput)

  $workersInput = Read-Host 'Workers default 6'
  if ($workersInput.Trim().Length -gt 0) { $script:Workers = [int]$workersInput.Trim() }

  $gpuInput = Read-Host 'GpuMode off/auto/on default off'
  if ($gpuInput.Trim().Length -gt 0) { $script:GpuMode = $gpuInput.Trim().ToLowerInvariant() }
  if ($script:GpuMode -notin @('off','auto','on')) { throw "GpuMode invalido: $script:GpuMode" }

  $partialInput = Read-Host 'AllowPartial? S/n default S'
  if ($partialInput.Trim().Length -eq 0 -or $partialInput.Trim().ToLowerInvariant().StartsWith('s') -or $partialInput.Trim().ToLowerInvariant().StartsWith('y')) {
    $script:AllowPartial = $true
  }

  Invoke-CaptureRun -SelectedSurfaces $selectedSurfaces -SelectedPhases $selectedPhases
}

if ($SelfTest) {
  if (-not (Test-Path -LiteralPath $Runner)) { throw "No encuentro RUN.ps1: $Runner" }
  $testSurfaces = Resolve-Surfaces @('pc,tablet,web,mobile,chart-lab,control-center')
  $testPhases = Resolve-Phases @('discovery,quick,critical,full,visualqa')
  $comboPhases = Resolve-Phases @('1,5')
  $menuFive = Resolve-Phases @('5')
  $menuSix = Resolve-Phases @('6')
  if ($testSurfaces.Count -ne 6) { throw 'SelfTest fallo: surface catalog incompleto.' }
  if ($SurfaceParallel -notin @('auto','on','off')) { throw 'SelfTest fallo: SurfaceParallel invalido.' }
  if ($DeepScroll -notin @('auto','on','off')) { throw 'SelfTest fallo: DeepScroll invalido.' }
  if ($testPhases.Count -ne 5) { throw 'SelfTest fallo: phase catalog incompleto.' }
  if (($comboPhases | ForEach-Object { $_.Phase }) -join ',' -ne 'discovery,quick,full') { throw 'SelfTest fallo: fases 1,5 no resolvieron discovery,quick,full.' }
  if (($menuFive | ForEach-Object { $_.Phase }) -join ',' -ne 'quick,full') { throw 'SelfTest fallo: fase 5 no resolvio quick,full.' }
  if ($menuSix.Count -ne 5) { throw 'SelfTest fallo: fase 6/all no resolvio todas las fases.' }
  Write-Host 'SELFTEST PASS: MENU.ps1 catalogos y RUN.ps1 disponibles.' -ForegroundColor Green
  exit 0
}

if ($Action -eq 'capture') {
  $selectedSurfaces = Resolve-Surfaces $Apps
  $selectedPhases = Resolve-Phases $Phases
  Invoke-CaptureRun -SelectedSurfaces $selectedSurfaces -SelectedPhases $selectedPhases
}

if ($Action -eq 'studio') {
  $selectedSurfaces = Resolve-Surfaces $Apps
  Invoke-StudioRun -SelectedSurfaces $selectedSurfaces
  exit 0
}

if ($Action -eq 'discovery') {
  $selectedSurfaces = if ($Apps.Count -gt 0) { Resolve-Surfaces $Apps } else { Resolve-Surfaces @('all') }
  Invoke-CaptureRun -SelectedSurfaces $selectedSurfaces -SelectedPhases (Resolve-Phases @('discovery'))
}

Start-InteractiveMenu
