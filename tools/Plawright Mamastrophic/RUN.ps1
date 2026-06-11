param(
  [ValidateSet('discovery','quick','full','critical','visualqa','screenshots','screenshotsqa')]
  [string]$Mode = 'quick',

  [ValidateSet('all','7','todo','todos','all-surfaces','all_surfaces','chart-lab','chart_lab','3000','web','eit-web','eit_web','3110','tablet','tablet-pos','tablet_pos','pos','3120','pc','backoffice','pc-backoffice','pc_backoffice','3130','mobile','app','app-mobile','app_mobile','3140','control-center','control_center','prisma-control-center','prisma_control_center','3150')]
  [string]$Surface = 'all',

  [int]$Workers = 6,
  [switch]$NoScreenshots,
  [int]$Shards = 1,
  [switch]$FullPage,
  [switch]$AllowPartial,
  [switch]$Strict,
  [ValidateSet('off','auto','on')][string]$GpuMode = 'off',
  [int]$TestTimeoutMs = 0,
  [int]$GotoTimeoutMs = 45000,
  [int]$GotoRetries = 2,
  [int]$ScreenshotTimeoutMs = 15000,
  [int]$ProbeTimeoutMs = 1400,
  [ValidateSet('auto','on','off')][string]$SurfaceParallel = 'auto',
  [int]$SurfaceParallelMax = 4,
  [int]$SurfaceChildWorkers = 1,
  [ValidateSet('auto','on','off')][string]$DeepScroll = 'auto',
  [int]$MaxPageTiles = 180,
  [int]$MaxScrollContainers = 36,
  [int]$MaxContainerTiles = 120,
  [int]$TileOverlapPx = 80,
  [string]$ArtifactRoot = '',
  [switch]$NoZip
)

$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$CoreRunner = Join-Path $Here 'core\run-surf8-capture.ps1'
if (!(Test-Path -LiteralPath $CoreRunner)) { throw "No encontre core runner: $CoreRunner" }

function Normalize-MamSurface {
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
  return $Value
}

function ConvertTo-MamCommandLineArg {
  param([object]$Value)
  if ($null -eq $Value) { return '""' }
  $s = [string]$Value
  if ($s.Length -eq 0) { return '""' }
  if ($s -notmatch '[\s"]') { return $s }
  return '"' + ($s.Replace('"','\"')) + '"'
}

function New-MamZipFromDir {
  param([string]$SourceDir, [string]$ZipPath)
  if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
  $items = @(Get-ChildItem -LiteralPath $SourceDir -Force -ErrorAction SilentlyContinue)
  if ($items.Count -eq 0) {
    $empty = Join-Path $SourceDir 'EMPTY.txt'
    Set-Content -LiteralPath $empty -Encoding UTF8 -Value 'No artifacts were produced.'
  }
  Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force
}

function Move-MamStageToTrash {
  param([string]$StageDir, [string]$RunName)
  if ([string]::IsNullOrWhiteSpace($StageDir) -or -not (Test-Path -LiteralPath $StageDir)) { return }
  $trashRoot = 'F:\Trash-old'
  New-Item -ItemType Directory -Force -Path $trashRoot | Out-Null
  $dest = Join-Path $trashRoot ($RunName + ' stage ' + (Get-Date -Format 'ddMM HHmmss'))
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $manifest = [ordered]@{ movedAt=(Get-Date).ToString('o'); reason='Mamastrophic staging moved after final app ZIPs were created'; source=$StageDir; destination=$dest }
  $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $dest 'manifest.json') -Encoding UTF8
  Set-Content -LiteralPath (Join-Path $dest 'manifest.md') -Encoding UTF8 -Value "# Moved Mamastrophic stage`r`n`r`n- source: `$StageDir`r`n- destination: `$dest`r`n- reason: final evidence was packaged into per-app ZIPs in F:\descargasf."
  Move-Item -LiteralPath $StageDir -Destination (Join-Path $dest (Split-Path -Leaf $StageDir)) -Force
}

function Get-MamSurfaceCatalog {
  return @(
    [pscustomobject]@{ Surface='chart-lab'; Label='Chart Lab'; Port=3000 },
    [pscustomobject]@{ Surface='web'; Label='EIT / Web'; Port=3110 },
    [pscustomobject]@{ Surface='tablet'; Label='Tablet / POS'; Port=3120 },
    [pscustomobject]@{ Surface='pc'; Label='PC Backoffice'; Port=3130 },
    [pscustomobject]@{ Surface='mobile'; Label='App / Mobile'; Port=3140 },
    [pscustomobject]@{ Surface='control-center'; Label='Prisma Control Center'; Port=3150 }
  )
}

function Get-LastUsefulLine {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return '' }
  try {
    $lines = @(Get-Content -LiteralPath $Path -Tail 80 -ErrorAction SilentlyContinue | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $progress = @($lines | Where-Object { $_ -match '^\[MAM-PROGRESS\]' } | Select-Object -Last 1)
    if ($progress.Count -gt 0) { return [string]$progress[0] }
    if ($lines.Count -gt 0) { return [string]$lines[-1] }
  } catch {}
  return ''
}

function Write-MamDashboard {
  param([object[]]$Running, [int]$Completed, [int]$Total, [datetime]$StartedAt)
  $elapsed = [int]((Get-Date) - $StartedAt).TotalSeconds
  Write-Host ("LIVE {0:HH:mm:ss} | done {1}/{2} | running {3} | elapsed {4}s" -f (Get-Date), $Completed, $Total, @($Running).Count, $elapsed) -ForegroundColor Cyan
  foreach ($r in @($Running | Sort-Object Surface)) {
    $last = Get-LastUsefulLine $r.StdOut
    $age = [int]((Get-Date) - $r.StartedAt).TotalSeconds
    if ([string]::IsNullOrWhiteSpace($last)) { $last = 'arrancando / esperando primer evento vivo' }
    if ($last.Length -gt 180) { $last = $last.Substring(0, 177) + '...' }
    Write-Host ("  {0,-15} phase={1,-13} alive={2,4}s :: {3}" -f $r.Surface, $Mode, $age, $last) -ForegroundColor DarkCyan
  }
}

function Build-CoreArgs {
  param([string]$SurfaceName, [int]$ChildWorkers, [string]$ChildArtifactRoot, [bool]$ChildNoZip)
  $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$CoreRunner,'-Mode',$Mode,'-Surface',$SurfaceName,'-Workers',[string]$ChildWorkers,'-Shards',[string]$Shards,'-GpuMode',$GpuMode,'-TestTimeoutMs',[string]$TestTimeoutMs,'-GotoTimeoutMs',[string]$GotoTimeoutMs,'-GotoRetries',[string]$GotoRetries,'-ScreenshotTimeoutMs',[string]$ScreenshotTimeoutMs,'-ProbeTimeoutMs',[string]$ProbeTimeoutMs,'-DeepScroll',$DeepScroll,'-MaxPageTiles',[string]$MaxPageTiles,'-MaxScrollContainers',[string]$MaxScrollContainers,'-MaxContainerTiles',[string]$MaxContainerTiles,'-TileOverlapPx',[string]$TileOverlapPx)
  if ($NoScreenshots) { $args += '-NoScreenshots' }
  if ($FullPage) { $args += '-FullPage' }
  if ($AllowPartial) { $args += '-AllowPartial' }
  if ($Strict) { $args += '-Strict' }
  if (-not [string]::IsNullOrWhiteSpace($ChildArtifactRoot)) { $args += @('-ArtifactRoot', $ChildArtifactRoot) }
  if ($ChildNoZip) { $args += '-NoZip' }
  return $args
}

function Invoke-SingleSurfaceCore {
  $surfaceKey = Normalize-MamSurface $Surface
  $args = Build-CoreArgs -SurfaceName $surfaceKey -ChildWorkers $Workers -ChildArtifactRoot $ArtifactRoot -ChildNoZip ([bool]$NoZip)
  & powershell @args
  exit $LASTEXITCODE
}

function Invoke-MamAllSurfacesParallel {
  $surfaces = @(Get-MamSurfaceCatalog)
  $outRoot = 'F:\descargasf'
  New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
  $stamp = Get-Date -Format 'ddMM HHmmss'
  $runName = "mamshot all $Mode $stamp"
  $runDir = if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) { Join-Path $outRoot $runName } else { $ArtifactRoot }
  $orchestratorDir = Join-Path $runDir '_orchestrator'
  $logsDir = Join-Path $orchestratorDir 'logs'
  $reportsDir = Join-Path $orchestratorDir 'reports'
  New-Item -ItemType Directory -Force -Path $logsDir,$reportsDir | Out-Null

  $maxParallel = [Math]::Max(1, [Math]::Min([Math]::Max(1, $SurfaceParallelMax), $surfaces.Count))
  $childWorkers = [Math]::Max(1, $SurfaceChildWorkers)
  $queue = New-Object System.Collections.Queue
  foreach ($s in $surfaces) { [void]$queue.Enqueue($s) }
  $running = @()
  $records = New-Object System.Collections.Generic.List[object]
  $completed = 0
  $launched = 0
  $startedAt = Get-Date
  $lastDashboard = (Get-Date).AddSeconds(-10)

  Write-Host ''
  Write-Host '============================================================' -ForegroundColor Cyan
  Write-Host 'ALL SURFACES :: 1 ZIP por app, progreso vivo' -ForegroundColor Cyan
  Write-Host '============================================================' -ForegroundColor Cyan
  Write-Host "Surface workers simultaneos: $maxParallel | Playwright workers por superficie: $childWorkers" -ForegroundColor DarkCyan
  Write-Host "Artifact root: $runDir" -ForegroundColor DarkCyan
  Write-Host 'Regla: maximo 6 ZIPs finales, uno por app. No ZIP padre por fase.' -ForegroundColor DarkCyan

  $psExe = (Get-Command powershell -ErrorAction SilentlyContinue)
  if (-not $psExe) { $psExe = Get-Command pwsh -ErrorAction SilentlyContinue }
  if (-not $psExe) { throw 'No encontre powershell/pwsh para lanzar workers por superficie.' }

  while ($queue.Count -gt 0 -or $running.Count -gt 0) {
    while ($queue.Count -gt 0 -and $running.Count -lt $maxParallel) {
      $surfaceItem = $queue.Dequeue()
      $surfaceName = $surfaceItem.Surface
      $safeSurface = $surfaceName.Replace('-', '_')
      $appRoot = Join-Path $runDir ("apps\$surfaceName")
      $phaseRoot = Join-Path $appRoot ("phases\$Mode")
      $appLogs = Join-Path $appRoot 'logs'
      New-Item -ItemType Directory -Force -Path $phaseRoot,$appLogs | Out-Null
      $stdout = Join-Path $appLogs ("$Mode.stdout.log")
      $stderr = Join-Path $appLogs ("$Mode.stderr.log")
      $childArgs = Build-CoreArgs -SurfaceName $surfaceName -ChildWorkers $childWorkers -ChildArtifactRoot $phaseRoot -ChildNoZip $true
      $argLine = ($childArgs | ForEach-Object { ConvertTo-MamCommandLineArg $_ }) -join ' '
      Set-Content -LiteralPath (Join-Path $appLogs ("$Mode.command.txt")) -Encoding UTF8 -Value ($psExe.Source + ' ' + $argLine)
      $proc = Start-Process -FilePath $psExe.Source -ArgumentList $argLine -WorkingDirectory $Here -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
      $launched++
      $running += [pscustomobject]@{ Process=$proc; Surface=$surfaceName; Label=$surfaceItem.Label; Port=$surfaceItem.Port; StdOut=$stdout; StdErr=$stderr; Command=$psExe.Source + ' ' + $argLine; StartedAt=Get-Date; AppRoot=$appRoot; PhaseRoot=$phaseRoot }
      Write-Host ("START surface={0} worker={1}/{2} phase={3}" -f $surfaceName, $launched, $surfaces.Count, $Mode) -ForegroundColor Cyan
    }

    Start-Sleep -Milliseconds 900
    if (((Get-Date) - $lastDashboard).TotalSeconds -ge 3 -and @($running).Count -gt 0) {
      Write-MamDashboard -Running $running -Completed $completed -Total $surfaces.Count -StartedAt $startedAt
      $lastDashboard = Get-Date
    }

    $still = @()
    foreach ($r in $running) {
      if ($r.Process.HasExited) {
        $completed++
        try { $r.Process.Refresh(); $r.Process.WaitForExit() } catch {}
        $exitCode = [int]$r.Process.ExitCode
        $summaryPath = Join-Path $r.PhaseRoot 'reports\summary.json'
        $status = if ($exitCode -eq 0) { 'PASS' } else { 'FAIL' }
        $summaryObj = $null
        if (Test-Path -LiteralPath $summaryPath) {
          try { $summaryObj = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json; if ($summaryObj.status) { $status = [string]$summaryObj.status } } catch {}
        }
        $last = Get-LastUsefulLine $r.StdOut
        $record = [ordered]@{ surface=$r.Surface; label=$r.Label; port=$r.Port; mode=$Mode; status=$status; exitCode=$exitCode; artifactRoot=$r.PhaseRoot; stdout=$r.StdOut; stderr=$r.StdErr; lastEvent=$last; finishedAt=(Get-Date).ToString('o') }
        [void]$records.Add($record)
        $record | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $r.AppRoot "phase-$Mode-status.json") -Encoding UTF8
        Write-Host ("{0} surface={1} phase={2} exit={3} :: {4}" -f $status, $r.Surface, $Mode, $exitCode, $last) -ForegroundColor ($(if ($exitCode -eq 0) { 'Green' } else { 'Red' }))
      } else {
        $still += $r
      }
    }
    $running = @($still)
  }

  $manifest = [ordered]@{ status='DONE'; mode=$Mode; surface='all'; maxFinalZips=6; startedAt=$startedAt.ToString('o'); finishedAt=(Get-Date).ToString('o'); runDir=$runDir; records=@($records) }
  $manifest | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath (Join-Path $reportsDir 'all-surfaces-manifest.json') -Encoding UTF8

  $failures = @($records | Where-Object { [int]$_['exitCode'] -ne 0 -or [string]$_['status'] -eq 'FAIL' }).Count
  if (-not $NoZip) {
    foreach ($s in $surfaces) {
      $appRoot = Join-Path $runDir ("apps\$($s.Surface)")
      if (-not (Test-Path -LiteralPath $appRoot)) { continue }
      $appRecords = @($records | Where-Object { [string]$_['surface'] -eq $s.Surface })
      $appFail = @($appRecords | Where-Object { [int]$_['exitCode'] -ne 0 -or [string]$_['status'] -eq 'FAIL' }).Count -gt 0
      $appStatus = if ($appFail) { 'fail' } else { 'result' }
      $appSummary = [ordered]@{ app=$s.Surface; label=$s.Label; mode=$Mode; status=($appStatus.ToUpperInvariant()); records=$appRecords; note='One final ZIP per app. Phase artifacts live under phases/<mode>.' }
      $appSummary | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath (Join-Path $appRoot 'APP_SUMMARY.json') -Encoding UTF8
      $md = @("# Mamastrophic app summary", "", "- app: $($s.Surface)", "- mode: $Mode", "- status: $($appStatus.ToUpperInvariant())", "", "## Records")
      foreach ($rr in $appRecords) { $md += "- $($rr.mode): $($rr.status) exit=$($rr.exitCode) last=$($rr.lastEvent)" }
      Set-Content -LiteralPath (Join-Path $appRoot 'APP_SUMMARY.md') -Encoding UTF8 -Value ($md -join "`r`n")
      $zipName = "mamshot $($s.Surface) $Mode $stamp $appStatus.zip"
      $zipPath = Join-Path $outRoot $zipName
      New-MamZipFromDir -SourceDir $appRoot -ZipPath $zipPath
      Write-Host ("APP ZIP {0}: {1}" -f $appStatus.ToUpperInvariant(), $zipPath) -ForegroundColor ($(if ($appFail) { 'Red' } else { 'Green' }))
    }
    if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) { Move-MamStageToTrash -StageDir $runDir -RunName "mamshot $Mode" }
  } else {
    Write-Host "ALL SURFACES ARTIFACT ROOT: $runDir" -ForegroundColor Yellow
  }

  if ($failures -gt 0) { exit 2 }
  exit 0
}

$surfaceKey = Normalize-MamSurface $Surface
Write-Host "PRISMA Plawright Mamastrophic arr13 app-zips/live-progress" -ForegroundColor Cyan
Write-Host "Root: $Here" -ForegroundColor DarkCyan
Write-Host "Mode: $Mode | Surface: $surfaceKey | Workers: $Workers | Shards: $Shards | GpuMode: $GpuMode" -ForegroundColor DarkCyan
Write-Host "SurfaceParallel: $SurfaceParallel | MaxSurfaceWorkers: $SurfaceParallelMax | ChildWorkers: $SurfaceChildWorkers" -ForegroundColor DarkCyan
Write-Host "DeepScroll: $DeepScroll | FullPageSwitch: $([bool]$FullPage) | MaxPageTiles: $MaxPageTiles | MaxContainers: $MaxScrollContainers | MaxContainerTiles: $MaxContainerTiles" -ForegroundColor DarkCyan
Write-Host "ArtifactRoot: $ArtifactRoot | NoZip: $([bool]$NoZip)" -ForegroundColor DarkCyan
Write-Host "Policy: no start, no kill, no DB, no deploy" -ForegroundColor DarkCyan

if ($surfaceKey -eq 'all') { Invoke-MamAllSurfacesParallel }
Invoke-SingleSurfaceCore
