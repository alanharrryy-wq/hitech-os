param(
  [ValidateSet('menu','capture','studio','discovery')]
  [string]$Action = 'menu',

  [string[]]$Apps = @(),
  [string[]]$Phases = @(),

  [ValidateSet('off','auto','on')]
  [string]$GpuMode = 'off',

  [int]$Workers = 6,
  [int]$Shards = 1,
  [switch]$AllowPartial,
  [switch]$FullPage,
  [switch]$NoScreenshots,
  [string]$StudioPath = '/',
  [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$ToolRoot = 'F:\repos\hitech-os\tools\Plawright Mamastrophic'
$Runner = Join-Path $ToolRoot 'RUN.ps1'
$RepoRoot = 'F:\repos\hitech-os\apps\terminal-de-venta-system'
$OutDir = 'F:\descargasf'

$SurfaceCatalog = @(
  [pscustomobject]@{ Key = '1'; Surface = 'chart-lab';      Aliases = @('chart','chart_lab','chartlab','3000');       Port = 3000; Label = 'Chart Lab';             BaseUrl = 'http://127.0.0.1:3000' },
  [pscustomobject]@{ Key = '2'; Surface = 'web';            Aliases = @('eit','eit_web','web_eit','3110');           Port = 3110; Label = 'EIT / Web';             BaseUrl = 'http://127.0.0.1:3110' },
  [pscustomobject]@{ Key = '3'; Surface = 'tablet';         Aliases = @('pos','tablet_pos','3120');                  Port = 3120; Label = 'Tablet / POS';          BaseUrl = 'http://127.0.0.1:3120' },
  [pscustomobject]@{ Key = '4'; Surface = 'pc';             Aliases = @('backoffice','pc_backoffice','3130');         Port = 3130; Label = 'PC Backoffice';         BaseUrl = 'http://127.0.0.1:3130' },
  [pscustomobject]@{ Key = '5'; Surface = 'mobile';         Aliases = @('app','app_mobile','3140');                  Port = 3140; Label = 'App / Mobile';          BaseUrl = 'http://127.0.0.1:3140' },
  [pscustomobject]@{ Key = '6'; Surface = 'control-center'; Aliases = @('control','control_center','3150');          Port = 3150; Label = 'Prisma Control Center'; BaseUrl = 'http://127.0.0.1:3150' },
  [pscustomobject]@{ Key = '7'; Surface = 'all';            Aliases = @('todo','todos','all_surfaces');              Port = 0;    Label = 'ALL - todas';           BaseUrl = '' }
)

$PhaseCatalog = @(
  [pscustomobject]@{ Key = '1'; Phase = 'discovery'; Label = 'Discovery - radar de superficies' },
  [pscustomobject]@{ Key = '2'; Phase = 'quick';     Label = 'Quick - subset rapido' },
  [pscustomobject]@{ Key = '3'; Phase = 'critical';  Label = 'Critical - rutas delicadas' },
  [pscustomobject]@{ Key = '4'; Phase = 'full';      Label = 'Full - barredora completa' }
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
      return $PhaseCatalog
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
  Write-Host '  6) all         todas las fases' -ForegroundColor White
}

function Invoke-CaptureRun {
  param(
    [object[]]$SelectedSurfaces,
    [object[]]$SelectedPhases
  )
  if (-not (Test-Path -LiteralPath $Runner)) { throw "No encuentro Mamastrophic RUN.ps1: $Runner" }
  if ($SelectedSurfaces.Count -eq 0) { throw 'No hay superficies seleccionadas.' }
  if ($SelectedPhases.Count -eq 0) { throw 'No hay fases seleccionadas.' }

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

    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$Runner,'-Mode',$job.Phase,'-Surface',$job.Surface,'-Workers',[string]$Workers,'-Shards',[string]$Shards,'-GpuMode',$GpuMode)
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
  Write-Host 'Default GPU: off. No start, no kill, no DB, no deploy.' -ForegroundColor Gray
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
  $testPhases = Resolve-Phases @('discovery,quick,critical,full')
  $comboPhases = Resolve-Phases @('1,5')
  $menuFive = Resolve-Phases @('5')
  $menuSix = Resolve-Phases @('6')
  if ($testSurfaces.Count -ne 6) { throw 'SelfTest fallo: surface catalog incompleto.' }
  if ($testPhases.Count -ne 4) { throw 'SelfTest fallo: phase catalog incompleto.' }
  if (($comboPhases | ForEach-Object { $_.Phase }) -join ',' -ne 'discovery,quick,full') { throw 'SelfTest fallo: fases 1,5 no resolvieron discovery,quick,full.' }
  if (($menuFive | ForEach-Object { $_.Phase }) -join ',' -ne 'quick,full') { throw 'SelfTest fallo: fase 5 no resolvio quick,full.' }
  if ($menuSix.Count -ne 4) { throw 'SelfTest fallo: fase 6/all no resolvio todas las fases.' }
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
