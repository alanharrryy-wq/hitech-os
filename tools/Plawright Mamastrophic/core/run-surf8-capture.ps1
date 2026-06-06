param(
  [ValidateSet('discovery','critical','quick','full')][string]$Mode = 'full',
  [ValidateSet('all','chart-lab','chart_lab','3000','web','eit-web','eit_web','3110','tablet','tablet-pos','tablet_pos','pos','3120','pc','backoffice','pc-backoffice','pc_backoffice','3130','mobile','app','app-mobile','app_mobile','3140','control-center','control_center','prisma-control-center','prisma_control_center','3150')][string]$Surface = 'all',
  [int]$Workers = 6,
  [int]$Shards = 1,
  [switch]$NoScreenshots,
  [switch]$FullPage,
  [switch]$AllowPartial,
  [switch]$Strict,
  [ValidateSet('off','auto','on')][string]$GpuMode = 'off'
)
$ErrorActionPreference = 'Stop'
# PRISMA Plawright Mamastrophic arr5 fix2

function Normalize-Surf8Surface([string]$Value) {
  $raw = ([string]$Value).Trim().ToLowerInvariant().Replace(' ', '_')
  $map = @{
    'all'='all'; 'todo'='all'; 'todos'='all'; '*'='all';
    '3000'='chart-lab'; 'chart'='chart-lab'; 'chartlab'='chart-lab'; 'chart_lab'='chart-lab'; 'chart-lab'='chart-lab';
    '3110'='web'; 'web'='web'; 'eit'='web'; 'eit_web'='web'; 'eit-web'='web';
    '3120'='tablet'; 'tablet'='tablet'; 'pos'='tablet'; 'tablet_pos'='tablet'; 'tablet-pos'='tablet';
    '3130'='pc'; 'pc'='pc'; 'backoffice'='pc'; 'pc_backoffice'='pc'; 'pc-backoffice'='pc';
    '3140'='mobile'; 'mobile'='mobile'; 'app'='mobile'; 'app_mobile'='mobile'; 'app-mobile'='mobile';
    '3150'='control-center'; 'control'='control-center'; 'control_center'='control-center'; 'control-center'='control-center'; 'prisma_control_center'='control-center'; 'prisma-control-center'='control-center'
  }
  if ($map.ContainsKey($raw)) { return $map[$raw] }
  throw "Surface invalida: $Value"
}
function Get-Surf8RunStem([string]$Mode, [string]$SurfaceKey, [string]$Stamp, [string]$GpuModeValue = 'off') {
  $gpuSuffix = if ($GpuModeValue -and $GpuModeValue -ne 'off') { " gpu-$GpuModeValue" } else { '' }
  if ($SurfaceKey -eq 'all') { return "surf8 $Mode$gpuSuffix $Stamp" }
  return "surf8 $SurfaceKey $Mode$gpuSuffix $Stamp"
}
$SurfaceKey = Normalize-Surf8Surface $Surface

function Get-Surf8GpuProfile([string]$ModeValue) {
  $m = ([string]$ModeValue).Trim().ToLowerInvariant()
  $profiles = @{
    off = @{
      mode = 'off'
      description = 'Default estable: no agrega flags GPU al Chromium de Playwright.'
      chromiumArgs = @()
      aggressive = $false
    }
    auto = @{
      mode = 'auto'
      description = 'Intento razonable: habilita GPU/WebGL/canvas acelerado, con fallback normal de Chromium.'
      chromiumArgs = @(
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--enable-accelerated-2d-canvas',
        '--enable-webgl',
        '--enable-gpu-rasterization',
        '--use-gl=angle'
      )
      aggressive = $false
    }
    on = @{
      mode = 'on'
      description = 'Forzado agresivo: añade zero-copy y evita rasterizador software cuando Chromium lo respete.'
      chromiumArgs = @(
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--enable-accelerated-2d-canvas',
        '--enable-webgl',
        '--enable-gpu-rasterization',
        '--enable-zero-copy',
        '--use-gl=angle',
        '--disable-software-rasterizer',
        '--enable-features=CanvasOopRasterization'
      )
      aggressive = $true
    }
  }
  if (-not $profiles.ContainsKey($m)) { throw "GpuMode invalido: $ModeValue" }
  return $profiles[$m]
}
function New-Surf8GpuMarkdown([hashtable]$GpuProfile) {
  $lines = New-Object System.Collections.Generic.List[string]
  [void]$lines.Add('# Surf8 GPU profile')
  [void]$lines.Add('')
  [void]$lines.Add(('- mode: `{0}`' -f $GpuProfile.mode))
  [void]$lines.Add(('- aggressive: `{0}`' -f $GpuProfile.aggressive))
  [void]$lines.Add("- description: $($GpuProfile.description)")
  [void]$lines.Add('')
  [void]$lines.Add('## Chromium args')
  if (@($GpuProfile.chromiumArgs).Count -eq 0) {
    [void]$lines.Add('')
    [void]$lines.Add('_none_')
  } else {
    foreach ($arg in @($GpuProfile.chromiumArgs)) { [void]$lines.Add(('- `{0}`' -f $arg)) }
  }
  [void]$lines.Add('')
  [void]$lines.Add('## Notes')
  [void]$lines.Add('- `off` is the reproducible baseline.')
  [void]$lines.Add('- `auto` should be compared against `off` using the same Mode/Surface/Workers.')
  [void]$lines.Add('- `on` can be faster on glass/WebGL-heavy screens, but may create visual flakes; use it after `auto`.')
  return ($lines -join "`r`n")
}
$GpuProfile = Get-Surf8GpuProfile $GpuMode

function Show-ProgressLine([int]$pct, [string]$msg) {
  $pct = [Math]::Max(0, [Math]::Min(100, $pct))
  $filled = [Math]::Floor($pct * 28 / 100)
  $bar = ('#' * $filled).PadRight(28, '.')
  $remaining = 100 - $pct
  Write-Host ("PROGRESS {0:d3}% [{1}] remaining {2:d3}% :: {3}" -f $pct, $bar, $remaining, $msg) -ForegroundColor Cyan
}
function Write-Utf8([string]$Path, [string]$Text) {
  $parent = Split-Path -Parent $Path
  if ($parent -and !(Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
  [System.IO.File]::WriteAllText($Path, $Text, [System.Text.Encoding]::UTF8)
}
function ConvertTo-CmdArg([object]$Arg) {
  if ($null -eq $Arg) { return '""' }
  $s = [string]$Arg
  if ($s.Length -eq 0) { return '""' }
  if ($s -notmatch '[\s"]') { return $s }
  return '"' + $s.Replace('"','\"') + '"'
}
function Invoke-NativeCapture([string]$Exe, [object[]]$Arguments, [string]$Cwd, [string]$LogPath) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $Exe
  $psi.WorkingDirectory = $Cwd
  $psi.UseShellExecute = $false
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  try { $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
  try { $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8 } catch {}
  $psi.Arguments = (($Arguments | ForEach-Object { ConvertTo-CmdArg $_ }) -join ' ')
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  $started = $p.Start()
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  $combined = "COMMAND:`r`n$Exe $($psi.Arguments)`r`n`r`nCWD:`r`n$Cwd`r`n`r`nSTDOUT:`r`n$stdout`r`n`r`nSTDERR:`r`n$stderr`r`n"
  Write-Utf8 $LogPath $combined
  return [pscustomobject]@{ ExitCode=$p.ExitCode; StdOut=$stdout; StdErr=$stderr; Text=$combined; Command=(@($Exe) + @($Arguments)); Cwd=$Cwd }
}
function Get-PythonLauncher() {
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { return @($py.Source, '-3') }
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) { return @($python.Source) }
  throw 'No encontre Python en PATH.'
}
function Test-HttpPort([int]$port) {
  try {
    $client = New-Object Net.Sockets.TcpClient
    $iar = $client.BeginConnect('127.0.0.1', $port, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(900, $false)
    if ($ok) { $client.EndConnect($iar) }
    $client.Close()
    return [bool]$ok
  } catch { return $false }
}
function Invoke-NodeResolve([string]$nodeExe, [string]$root, [string]$moduleName) {
  $js = @'
const root = process.argv[1];
const mod = process.argv[2];
try {
  console.log(require.resolve(mod, { paths: [root] }));
} catch (error) {
  process.exit(7);
}
'@
  $out = & $nodeExe -e $js $root $moduleName 2>$null
  if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($out)) { return @($out)[0] }
  return $null
}
function Resolve-PlaywrightInvocation([string]$pcRoot) {
  $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
  if (-not $nodeCmd) { throw 'No encontre node en PATH.' }
  $node = $nodeCmd.Source
  $attempts = New-Object System.Collections.Generic.List[string]
  foreach ($mod in @('@playwright/test/cli', '@playwright/test/cli.js')) {
    $cli = Invoke-NodeResolve $node $pcRoot $mod
    if ($cli -and (Test-Path -LiteralPath $cli)) {
      return @{ Kind='node-resolve-cli'; Exe=$node; ArgsPrefix=@($cli, 'test'); Cwd=$pcRoot; Detail="require.resolve $mod desde PC app"; Attempts=$attempts }
    }
    [void]$attempts.Add("missing $mod desde $pcRoot")
  }
  $pkg = Invoke-NodeResolve $node $pcRoot '@playwright/test/package.json'
  if ($pkg) {
    $pkgDir = Split-Path -Parent $pkg
    $cli = Join-Path $pkgDir 'cli.js'
    if (Test-Path -LiteralPath $cli) {
      return @{ Kind='node-package-cli'; Exe=$node; ArgsPrefix=@($cli, 'test'); Cwd=$pcRoot; Detail='@playwright/test package cli.js desde PC app'; Attempts=$attempts }
    }
    [void]$attempts.Add("package resolved but cli missing $cli")
  }
  $cmd = Join-Path $pcRoot 'node_modules\.bin\playwright.cmd'
  if (Test-Path -LiteralPath $cmd) {
    return @{ Kind='local-bin'; Exe=$cmd; ArgsPrefix=@('test'); Cwd=$pcRoot; Detail='PC app node_modules .bin playwright.cmd'; Attempts=$attempts }
  }
  $pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
  if ($pnpm) {
    return @{ Kind='pnpm-C'; Exe=$pnpm.Source; ArgsPrefix=@('-C', $pcRoot, 'exec', 'playwright', 'test'); Cwd=$pcRoot; Detail='pnpm -C PC app exec playwright test'; Attempts=$attempts }
  }
  return @{ Kind='missing'; Attempts=$attempts }
}
function New-ZipFromDir([string]$dir, [string]$zipPath) {
  if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::CreateFromDirectory($dir, $zipPath)
}
function Write-JsonFile([string]$Path, [object]$Value, [int]$Depth = 12) {
  Write-Utf8 $Path ($Value | ConvertTo-Json -Depth $Depth)
}
function ConvertTo-Surf8SingleLine([object]$Value, [int]$Max = 240) {
  if ($null -eq $Value) { return '' }
  $s = ([string]$Value) -replace '\s+', ' '
  $s = $s.Trim()
  if ($s.Length -gt $Max) { return ($s.Substring(0, [Math]::Max(0, $Max - 3)) + '...') }
  return $s
}
function Get-Surf8Prop([object]$Value, [string]$Name) {
  if ($null -eq $Value) { return $null }
  $prop = $Value.PSObject.Properties[$Name]
  if ($prop) { return $prop.Value }
  return $null
}
function Get-Surf8RecordErrorMessage([object]$Record) {
  $err = Get-Surf8Prop $Record 'error'
  if ($err) {
    $msg = Get-Surf8Prop $err 'message'
    if (-not [string]::IsNullOrWhiteSpace([string]$msg)) { return (ConvertTo-Surf8SingleLine $msg) }
  }
  $msg = Get-Surf8Prop $Record 'screenshotError'
  if (-not [string]::IsNullOrWhiteSpace([string]$msg)) { return (ConvertTo-Surf8SingleLine $msg) }
  return ''
}
function Add-Surf8ReportStatuses([object]$Suite, [hashtable]$Map) {
  if ($null -eq $Suite) { return }
  foreach ($spec in @($Suite.specs)) {
    $title = [string](Get-Surf8Prop $spec 'title')
    if ([string]::IsNullOrWhiteSpace($title)) { continue }
    $parts = $title -split '\s+'
    if ($parts.Count -lt 2) { continue }
    $targetId = [string]$parts[1]
    if ([string]::IsNullOrWhiteSpace($targetId)) { continue }

    $statuses = New-Object System.Collections.Generic.List[string]
    foreach ($testCase in @($spec.tests)) {
      $testStatus = Get-Surf8Prop $testCase 'status'
      if (-not [string]::IsNullOrWhiteSpace([string]$testStatus)) { [void]$statuses.Add([string]$testStatus) }
      foreach ($result in @($testCase.results)) {
        $resultStatus = Get-Surf8Prop $result 'status'
        if (-not [string]::IsNullOrWhiteSpace([string]$resultStatus)) { [void]$statuses.Add([string]$resultStatus) }
      }
    }

    $status = 'captured'
    if (@($statuses | Where-Object { $_ -in @('unexpected','failed','timedOut','interrupted') }).Count -gt 0 -or (Get-Surf8Prop $spec 'ok') -eq $false) {
      $status = 'failed'
    } elseif (@($statuses | Where-Object { $_ -eq 'skipped' }).Count -gt 0) {
      $status = 'skipped'
    }

    $Map[$targetId] = [ordered]@{
      status = $status
      title = $title
      rawStatuses = @($statuses)
      ok = Get-Surf8Prop $spec 'ok'
    }
  }
  foreach ($child in @($Suite.suites)) { Add-Surf8ReportStatuses $child $Map }
}
function New-Surf8CaptureManifest([object]$PlanObj, [string]$ScreensDir, [string]$JsonReportPath) {
  $recordFiles = @(Get-ChildItem -LiteralPath $ScreensDir -Filter '*.json' -File -ErrorAction SilentlyContinue)
  $screenshotFiles = @(Get-ChildItem -LiteralPath $ScreensDir -Filter '*.png' -File -ErrorAction SilentlyContinue)
  $recordsByTarget = @{}
  $recordParseErrors = New-Object System.Collections.Generic.List[object]

  foreach ($file in $recordFiles) {
    try {
      $record = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
      $targetId = [string](Get-Surf8Prop $record 'targetId')
      if ([string]::IsNullOrWhiteSpace($targetId)) {
        [void]$recordParseErrors.Add([ordered]@{ file=$file.FullName; error='missing targetId' })
        continue
      }
      if (-not $recordsByTarget.ContainsKey($targetId)) { $recordsByTarget[$targetId] = New-Object System.Collections.ArrayList }
      $status = [string](Get-Surf8Prop $record 'status')
      if ([string]::IsNullOrWhiteSpace($status)) { $status = 'captured' }
      [void]$recordsByTarget[$targetId].Add([ordered]@{
        file = $file.Name
        path = $file.FullName
        status = $status
        screenshot = Get-Surf8Prop $record 'screenshot'
        url = Get-Surf8Prop $record 'url'
        error = Get-Surf8RecordErrorMessage $record
        reason = Get-Surf8Prop $record 'reason'
        reasonType = Get-Surf8Prop $record 'reasonType'
      })
    } catch {
      [void]$recordParseErrors.Add([ordered]@{ file=$file.FullName; error=($_ | Out-String).Trim() })
    }
  }

  $reportStatuses = @{}
  $reportParseError = ''
  if (Test-Path -LiteralPath $JsonReportPath) {
    try {
      $report = Get-Content -LiteralPath $JsonReportPath -Raw | ConvertFrom-Json
      foreach ($suite in @($report.suites)) { Add-Surf8ReportStatuses $suite $reportStatuses }
    } catch {
      $reportParseError = ($_ | Out-String).Trim()
    }
  } else {
    $reportParseError = "missing $JsonReportPath"
  }

  $captured = New-Object System.Collections.ArrayList
  $failed = New-Object System.Collections.ArrayList
  $skipped = New-Object System.Collections.ArrayList
  $missing = New-Object System.Collections.ArrayList
  $targetRecordCount = 0

  foreach ($target in @($PlanObj.targets)) {
    $targetId = [string]$target.id
    $targetRecords = @()
    if ($recordsByTarget.ContainsKey($targetId)) { $targetRecords = @($recordsByTarget[$targetId]) }
    if ($targetRecords.Count -gt 0) { $targetRecordCount += 1 }
    $recordStatuses = @($targetRecords | ForEach-Object { [string]$_['status'] })
    $reportEntry = $null
    if ($reportStatuses.ContainsKey($targetId)) { $reportEntry = $reportStatuses[$targetId] }
    $reportStatus = ''
    if ($reportEntry) { $reportStatus = [string]$reportEntry['status'] }
    $base = [ordered]@{
      macro = [string]$target.macro
      targetId = $targetId
      kind = [string]$target.kind
      route = Get-Surf8Prop $target 'route'
      baseUrl = Get-Surf8Prop $target 'baseUrl'
      reportStatus = $reportStatus
      recordCount = $targetRecords.Count
      records = @($targetRecords)
    }

    if ($reportStatus -eq 'failed' -or @($recordStatuses | Where-Object { $_ -eq 'failed' }).Count -gt 0) {
      $reason = ''
      $failureRecord = @($targetRecords | Where-Object { [string]$_['status'] -eq 'failed' } | Select-Object -First 1)
      if ($failureRecord.Count -gt 0) { $reason = [string]$failureRecord[0]['error'] }
      if ([string]::IsNullOrWhiteSpace($reason) -and $reportEntry) { $reason = [string]$reportEntry['title'] }
      $base['reason'] = ConvertTo-Surf8SingleLine $reason
      [void]$failed.Add([pscustomobject]$base)
    } elseif ($reportStatus -eq 'skipped' -or @($recordStatuses | Where-Object { $_ -eq 'skipped' }).Count -gt 0) {
      $skipRecord = @($targetRecords | Where-Object { [string]$_['status'] -eq 'skipped' } | Select-Object -First 1)
      if ($skipRecord.Count -gt 0) { $base['reason'] = ConvertTo-Surf8SingleLine ([string]$skipRecord[0]['reason']) }
      [void]$skipped.Add([pscustomobject]$base)
    } elseif ($targetRecords.Count -gt 0 -or $reportStatus -eq 'captured') {
      [void]$captured.Add([pscustomobject]$base)
    } else {
      $base['reason'] = 'No screen record and no Playwright status for this target.'
      [void]$missing.Add([pscustomobject]$base)
    }
  }

  $macroNames = @($PlanObj.targets | ForEach-Object { [string]$_.macro } | Sort-Object -Unique)
  $byMacro = foreach ($macro in $macroNames) {
    [ordered]@{
      macro = $macro
      expected = @($PlanObj.targets | Where-Object { [string]$_.macro -eq $macro }).Count
      captured = @($captured | Where-Object { $_.macro -eq $macro }).Count
      failed = @($failed | Where-Object { $_.macro -eq $macro }).Count
      skipped = @($skipped | Where-Object { $_.macro -eq $macro }).Count
      missing = @($missing | Where-Object { $_.macro -eq $macro }).Count
    }
  }

  $capturedArray = @($captured.ToArray())
  $failedArray = @($failed.ToArray())
  $skippedArray = @($skipped.ToArray())
  $missingArray = @($missing.ToArray())
  $recordParseErrorArray = @($recordParseErrors.ToArray())
  $skippedOfflineArray = @($skippedArray | Where-Object {
    $records = @($_.records)
    (@($records | Where-Object { ([string]$_['reasonType']) -eq 'offline_port' -or ([string]$_['reason']) -match 'offline|was offline|puerto|port' }).Count -gt 0)
  })

  return [ordered]@{
    targetCount = [int]$PlanObj.targetCount
    recordCount = $recordFiles.Count
    targetRecordCount = $targetRecordCount
    screenshotCount = $screenshotFiles.Count
    capturedCount = $capturedArray.Count
    failedCount = $failedArray.Count
    skippedCount = $skippedArray.Count
    missingCount = $missingArray.Count
    skippedOfflineCount = $skippedOfflineArray.Count
    byMacro = @($byMacro)
    captured = $capturedArray
    failed = $failedArray
    skipped = $skippedArray
    missing = $missingArray
    recordParseErrors = $recordParseErrorArray
    reportParseError = $reportParseError
  }
}
function Format-Surf8StatusSection([string]$Title, [object[]]$Items) {
  $lines = New-Object System.Collections.Generic.List[string]
  [void]$lines.Add("## $Title ($(@($Items).Count))")
  if (@($Items).Count -eq 0) {
    [void]$lines.Add('')
    [void]$lines.Add('- none')
    return ($lines -join "`r`n")
  }
  foreach ($group in @($Items | Group-Object macro | Sort-Object Name)) {
    [void]$lines.Add('')
    [void]$lines.Add("### $($group.Name) ($($group.Count))")
    foreach ($item in @($group.Group | Sort-Object targetId)) {
      $detail = [string]$item.targetId
      if (-not [string]::IsNullOrWhiteSpace([string]$item.route)) { $detail += " route=$($item.route)" }
      if (-not [string]::IsNullOrWhiteSpace([string]$item.reason)) { $detail += " :: $(ConvertTo-Surf8SingleLine $item.reason 220)" }
      [void]$lines.Add("- $detail")
    }
  }
  return ($lines -join "`r`n")
}

function New-Surf8DiscoveryMarkdown([object]$PlanObj, [object[]]$PortRows, [string]$Mode, [string]$SurfaceKey) {
  $lines = New-Object System.Collections.Generic.List[string]
  [void]$lines.Add('# surf8 discovery')
  [void]$lines.Add('')
  [void]$lines.Add("- mode: $Mode")
  [void]$lines.Add("- surface: $SurfaceKey")
  [void]$lines.Add("- targets selected: $($PlanObj.targetCount)")
  [void]$lines.Add("- terminal root: $($PlanObj.terminalRoot)")
  [void]$lines.Add('')
  [void]$lines.Add('## Macro inventory')
  [void]$lines.Add('')
  [void]$lines.Add('| macro | port | online | root exists | targets | filtered | dynamic skipped |')
  [void]$lines.Add('| --- | ---: | :---: | :---: | ---: | ---: | ---: |')
  foreach ($m in @($PlanObj.macroSummaries)) {
    $portRow = @($PortRows | Where-Object { [string]$_.macro -eq [string]$m.macro } | Select-Object -First 1)
    $online = if ($portRow.Count -gt 0 -and $portRow[0].online) { 'yes' } else { 'no' }
    [void]$lines.Add("| $($m.macro) | $($m.port) | $online | $($m.rootExists) | $($m.expectedTargets) | $($m.filteredOut) | $($m.dynamicSkipped) |")
  }
  [void]$lines.Add('')
  [void]$lines.Add('## Selected targets')
  if (@($PlanObj.targets).Count -eq 0) {
    [void]$lines.Add('')
    [void]$lines.Add('- none')
  } else {
    foreach ($group in @($PlanObj.targets | Group-Object macro | Sort-Object Name)) {
      [void]$lines.Add('')
      [void]$lines.Add("### $($group.Name) ($($group.Count))")
      foreach ($t in @($group.Group | Sort-Object id)) {
        $route = if ($t.route) { " route=$($t.route)" } else { '' }
        [void]$lines.Add("- $($t.id)$route kind=$($t.kind) source=$($t.source)")
      }
    }
  }
  [void]$lines.Add('')
  [void]$lines.Add('## Filtered out')
  if (@($PlanObj.filteredOut).Count -eq 0) { [void]$lines.Add('- none') } else {
    foreach ($f in @($PlanObj.filteredOut | Sort-Object macro,id)) { [void]$lines.Add("- $($f.macro) $($f.id) :: $($f.reason)") }
  }
  [void]$lines.Add('')
  [void]$lines.Add('## Dynamic skipped')
  if (@($PlanObj.dynamicSkipped).Count -eq 0) { [void]$lines.Add('- none') } else {
    foreach ($d in @($PlanObj.dynamicSkipped | Sort-Object macro,id)) { [void]$lines.Add("- $($d.macro) $($d.id) route=$($d.route) :: $($d.reason)") }
  }
  return ($lines -join "`r`n")
}

function New-Surf8ExpectedMarkdown([object]$Summary, [object]$Manifest, [string]$OnlinePortsText) {
  $lines = New-Object System.Collections.Generic.List[string]
  [void]$lines.Add('# surf8 expected vs captured')
  [void]$lines.Add('')
  [void]$lines.Add("- status: $($Summary.status)")
  [void]$lines.Add("- targets expected: $($Summary.targetCount)")
  [void]$lines.Add("- screen records: $($Summary.recordCount)")
  [void]$lines.Add("- represented targets: $($Summary.targetRecordCount)")
  [void]$lines.Add("- screenshots: $($Summary.screenshotCount)")
  [void]$lines.Add("- online ports: $OnlinePortsText")
  [void]$lines.Add("- workers: $($Summary.workers)")
  [void]$lines.Add("- playwrightExitCode: $($Summary.playwrightExitCode)")
  [void]$lines.Add('')
  [void]$lines.Add('## Macro summary')
  [void]$lines.Add('')
  [void]$lines.Add('| macro | expected | captured | failed | skipped | missing |')
  [void]$lines.Add('| --- | ---: | ---: | ---: | ---: | ---: |')
  foreach ($row in @($Manifest.byMacro)) {
    [void]$lines.Add("| $($row.macro) | $($row.expected) | $($row.captured) | $($row.failed) | $($row.skipped) | $($row.missing) |")
  }
  [void]$lines.Add('')
  [void]$lines.Add((Format-Surf8StatusSection 'Captured' @($Manifest.captured)))
  [void]$lines.Add('')
  [void]$lines.Add((Format-Surf8StatusSection 'Failed' @($Manifest.failed)))
  [void]$lines.Add('')
  [void]$lines.Add((Format-Surf8StatusSection 'Skipped' @($Manifest.skipped)))
  [void]$lines.Add('')
  [void]$lines.Add((Format-Surf8StatusSection 'Missing' @($Manifest.missing)))
  [void]$lines.Add('')
  [void]$lines.Add('See surf8.capture-plan.json, capture-manifest.json, ports.json, playwright-list.log, playwright.log, playwright-report.json, and screens/*.json/png.')
  return ($lines -join "`r`n")
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$defaultTermRoot = 'F:\repos\hitech-os\apps\terminal-de-venta-system'
$termRootCandidate = if ($env:PRISMA_TERMINAL_ROOT -and -not [string]::IsNullOrWhiteSpace($env:PRISMA_TERMINAL_ROOT)) { $env:PRISMA_TERMINAL_ROOT } else { $defaultTermRoot }
$termRoot = (Resolve-Path -LiteralPath $termRootCandidate).Path
$pcRoot = Join-Path $termRoot 'products\pc\app'
$specRel = 'tests/prisma-surfaces/surf8.all-surfaces.spec.cjs'
$specPath = Join-Path $pcRoot ($specRel -replace '/', '\')
$specArg = $specRel
$discovery = Join-Path $scriptRoot 'surf8_discovery.py'
if (-not (Test-Path -LiteralPath (Join-Path $termRoot 'products\pc\app\package.json'))) { throw "Terminal root invalido: $termRoot" }
if (-not (Test-Path -LiteralPath $specPath)) { throw "No encontre spec bridge en PC app: $specPath" }
if (-not (Test-Path -LiteralPath $discovery)) { throw "No encontre discovery central: $discovery" }

$stamp = Get-Date -Format 'ddMM HHmmssfff'
$runStem = Get-Surf8RunStem $Mode $SurfaceKey $stamp $GpuMode
$outDir = Join-Path 'F:\descargasf' $runStem
$reports = Join-Path $outDir 'reports'
$screens = Join-Path $outDir 'screens'
$pwArtifacts = Join-Path $reports 'playwright-artifacts'
New-Item -ItemType Directory -Force -Path $reports,$screens,$pwArtifacts | Out-Null
Write-JsonFile (Join-Path $reports 'gpu-profile.json') $GpuProfile 10
Write-Utf8 (Join-Path $reports 'gpu-profile.md') (New-Surf8GpuMarkdown $GpuProfile)
$plan = Join-Path $reports 'surf8.capture-plan.json'
$resultZip = Join-Path 'F:\descargasf' ("$runStem result.zip")
$failZip = Join-Path 'F:\descargasf' ("$runStem fail.zip")
$logPath = Join-Path $reports 'run.log'
$runLines = New-Object System.Collections.Generic.List[string]
function Add-RunLog([string]$line) {
  $msg = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $line
  [void]$runLines.Add($msg)
  Write-Utf8 $logPath (($runLines -join "`r`n") + "`r`n")
}

try {
  Show-ProgressLine 10 'generando discovery plan'
  Add-RunLog "termRoot=$termRoot"
  Add-RunLog "surface=$SurfaceKey"
  Add-RunLog "gpuMode=$GpuMode chromiumArgs=$($GpuProfile.chromiumArgs -join ' ')"
  Add-RunLog "pcRoot=$pcRoot"
  Add-RunLog "specArg=$specArg"
  Add-RunLog "specPath=$specPath"
  $env:PYTHONDONTWRITEBYTECODE = '1'
  $py = Get-PythonLauncher
  $discArgs = @()
  if ($py.Count -gt 1) { $discArgs += @($py[1..($py.Count-1)] | Where-Object { $_ }) }
  $discArgs += @($discovery, '--repo-root', $termRoot, '--out', $plan, '--mode', $Mode, '--surface', $SurfaceKey, '--workers', [string]$Workers)
  $discResult = Invoke-NativeCapture -Exe $py[0] -Arguments $discArgs -Cwd $termRoot -LogPath (Join-Path $reports 'discovery.log')
  Add-RunLog "discoveryExitCode=$($discResult.ExitCode)"
  if ($discResult.ExitCode -ne 0) { throw "Discovery fallo con codigo $($discResult.ExitCode). Ver reports/discovery.log" }
  $planObj = Get-Content -LiteralPath $plan -Raw | ConvertFrom-Json
  Add-RunLog "targets=$($planObj.targetCount) macros=$(@($planObj.macros).Count) surface=$SurfaceKey"
  if ([int]$planObj.targetCount -le 0) { throw 'Discovery genero 0 targets. Esto no es verde.' }

  Show-ProgressLine 25 'preflight puertos 3000-3150'
  $portRows = @()
  $onlinePorts = New-Object System.Collections.Generic.List[string]
  foreach ($m in $planObj.macros) {
    $ok = Test-HttpPort ([int]$m.port)
    if ($ok) { [void]$onlinePorts.Add([string]$m.port) }
    $portRows += [pscustomobject]@{ macro=$m.id; port=$m.port; online=$ok; baseUrl=$m.baseUrl }
  }
  Write-JsonFile (Join-Path $reports 'ports.json') $portRows
  Write-Utf8 (Join-Path $reports 'discovery.md') (New-Surf8DiscoveryMarkdown $planObj @($portRows) $Mode $SurfaceKey)
  Add-RunLog "onlinePorts=$($onlinePorts -join ',')"

  if ($Mode -eq 'discovery') {
    Show-ProgressLine 100 'discovery listo'
    Write-JsonFile (Join-Path $reports 'summary.json') ([ordered]@{ status='PASS'; mode=$Mode; surface=$SurfaceKey; gpuMode=$GpuMode; gpuAggressive=[bool]$GpuProfile.aggressive; targetCount=[int]$planObj.targetCount; macroCount=@($planObj.macros).Count; onlinePorts=@($onlinePorts); resultZip=$resultZip; macroSummaries=@($planObj.macroSummaries) })
    New-ZipFromDir $outDir $resultZip
    Write-Host "ZIP result: $resultZip" -ForegroundColor Green
    exit 0
  }

  if ($onlinePorts.Count -eq 0) { throw 'Ningun puerto macro esta online; no hay nada capturable.' }

  $macroTotal = @($planObj.macros).Count
  if ($onlinePorts.Count -lt $macroTotal) {
    Write-Host "Advertencia: solo $($onlinePorts.Count)/$macroTotal macros online. Offline sera PARTIAL_PASS si no hay fallos reales." -ForegroundColor Yellow
    Add-RunLog "WARNING partial online macros: $($onlinePorts.Count)/$macroTotal"
  }

  Show-ProgressLine 40 'resolviendo Playwright desde PC app'
  $resolver = Resolve-PlaywrightInvocation $pcRoot
  Write-JsonFile (Join-Path $reports 'playwright_resolver.json') $resolver
  Add-RunLog "playwrightResolver=$($resolver['Kind']) exe=$($resolver['Exe'])"
  if ($resolver['Kind'] -eq 'missing') { throw 'No pude resolver Playwright CLI desde PC app.' }

  $env:PRISMA_SURF_PLAN_JSON = $plan
  $env:PRISMA_SURF_OUT_DIR = $screens
  $env:PRISMA_SURF_SCREENSHOTS = if ($NoScreenshots) { '0' } else { '1' }
  $env:PRISMA_SURF_FULLPAGE = if ($FullPage) { '1' } else { '0' }
  $env:PRISMA_SURF_ONLINE_PORTS = ($onlinePorts -join ',')
  $env:PRISMA_SURF_WORKERS = [string]$Workers
  $env:PRISMA_SURF_SURFACE = $SurfaceKey
  $env:PRISMA_SURF_GPU_MODE = $GpuMode
  $env:PRISMA_SURF_GPU_ARGS_JSON = ($GpuProfile.chromiumArgs | ConvertTo-Json -Compress)
  $env:PRISMA_SURF_CENTRAL_ROOT = (Resolve-Path -LiteralPath (Join-Path $scriptRoot '..')).Path
  $jsonReport = Join-Path $reports 'playwright-report.json'
  $env:PLAYWRIGHT_JSON_OUTPUT_NAME = $jsonReport

  $listLog = Join-Path $reports 'playwright-list.log'
  $listSummaryPath = Join-Path $reports 'playwright-list-summary.json'
  $listArgs = @()
  $listArgs += @($resolver['ArgsPrefix'])
  $listArgs += @($specArg, '--list')

  Show-ProgressLine 50 'preflight Playwright --list'
  Add-RunLog "playwrightListCommand=$($resolver['Exe']) $($listArgs -join ' ')"
  $listResult = Invoke-NativeCapture -Exe $resolver['Exe'] -Arguments $listArgs -Cwd $pcRoot -LogPath $listLog
  $listText = $listResult.Text
  $detectedTests = 0
  if ($listText -match 'Total:\s*(\d+)\s+tests?') {
    $detectedTests = [int]$Matches[1]
  } else {
    $detectedTests = @($listText -split "`n" | Where-Object { $_ -match '›' -or $_ -match [regex]::Escape($specArg) }).Count
  }
  $listSummary = [ordered]@{
    status = if ($listResult.ExitCode -eq 0 -and $detectedTests -gt 0) { 'PASS' } else { 'FAIL' }
    exitCode = $listResult.ExitCode
    detectedTestCount = $detectedTests
    specArg = $specArg
    specPath = $specPath
    cwd = $pcRoot
    command = @($resolver['Exe']) + @($listArgs)
    note = 'arr3 uses native process capture to avoid blank PowerShell NativeCommandError and bridge module resolution issues.'
  }
  Write-JsonFile $listSummaryPath $listSummary
  Add-RunLog "playwrightListExitCode=$($listResult.ExitCode) detectedTests=$detectedTests"
  if ($listResult.ExitCode -ne 0) { throw "Playwright --list fallo con codigo $($listResult.ExitCode). Ver $listLog" }
  if ($detectedTests -le 0) { throw "Playwright --list no detecto tests para $specArg. Ver $listLog" }

  Show-ProgressLine 65 'ejecutando Playwright paralelo'
  $pwArgs = @()
  $pwArgs += @($resolver['ArgsPrefix'])
  $pwArgs += @($specArg, "--workers=$Workers", '--reporter=list,json', "--output=$pwArtifacts")
  if ($Shards -gt 1) { $pwArgs += "--shard=1/$Shards" }
  Add-RunLog "playwrightRunCommand=$($resolver['Exe']) $($pwArgs -join ' ')"
  $pwResult = Invoke-NativeCapture -Exe $resolver['Exe'] -Arguments $pwArgs -Cwd $pcRoot -LogPath (Join-Path $reports 'playwright.log')
  $pwCode = $pwResult.ExitCode
  Add-RunLog "playwrightExitCode=$pwCode"

  Show-ProgressLine 85 'manifest expected vs captured'
  $manifest = New-Surf8CaptureManifest $planObj $screens $jsonReport
  Write-JsonFile (Join-Path $reports 'capture-manifest.json') $manifest 30
  $zeroRecordFailure = ([int]$planObj.targetCount -gt 0 -and [int]$manifest['recordCount'] -eq 0)
  $hasRealFailure = ($pwCode -ne 0 -or $zeroRecordFailure -or [int]$manifest['failedCount'] -gt 0 -or [int]$manifest['missingCount'] -gt 0)
  $hasSkipped = ([int]$manifest['skippedCount'] -gt 0)
  $runStatus = if (-not $hasRealFailure -and -not $hasSkipped) {
    'PASS'
  } elseif (-not $hasRealFailure -and $hasSkipped -and -not $Strict) {
    'PARTIAL_PASS'
  } else {
    'FAIL'
  }
  $summary = [ordered]@{
    status = $runStatus
    mode = $Mode
    surface = $SurfaceKey
    terminalRoot = $termRoot
    centralRoot = $env:PRISMA_SURF_CENTRAL_ROOT
    targetCount = [int]$planObj.targetCount
    recordCount = [int]$manifest['recordCount']
    targetRecordCount = [int]$manifest['targetRecordCount']
    screenshotCount = [int]$manifest['screenshotCount']
    capturedCount = [int]$manifest['capturedCount']
    failedCount = [int]$manifest['failedCount']
    skippedCount = [int]$manifest['skippedCount']
    missingCount = [int]$manifest['missingCount']
    skippedOfflineCount = [int]$manifest['skippedOfflineCount']
    strict = [bool]$Strict
    allowPartial = [bool]$AllowPartial
    onlinePorts = @($onlinePorts)
    workers = $Workers
    gpuMode = $GpuMode
    gpuAggressive = [bool]$GpuProfile.aggressive
    chromiumArgs = @($GpuProfile.chromiumArgs)
    playwrightExitCode = $pwCode
    playwrightListDetectedTestCount = $detectedTests
    resultZip = $resultZip
    failZip = $failZip
  }
  Write-JsonFile (Join-Path $reports 'summary.json') $summary
  Write-Utf8 (Join-Path $reports 'expected_vs_captured.md') (New-Surf8ExpectedMarkdown $summary $manifest ($onlinePorts -join ', '))

  Show-ProgressLine 100 'empaquetando resultado'
  if ($summary.status -in @('PASS','PARTIAL_PASS')) {
    New-ZipFromDir $outDir $resultZip
    if ($summary.status -eq 'PASS') { Write-Host "ZIP result: $resultZip" -ForegroundColor Green } else { Write-Host "ZIP partial result: $resultZip" -ForegroundColor Yellow }
    exit 0
  } else {
    New-ZipFromDir $outDir $failZip
    Write-Host "ZIP fail: $failZip" -ForegroundColor Red
    if ($pwCode -ne 0) { exit $pwCode } else { exit 1 }
  }
} catch {
  $errorText = ($_ | Out-String).Trim()
  $message = $_.Exception.Message
  if ([string]::IsNullOrWhiteSpace($message)) { $message = $errorText }
  $err = [ordered]@{
    status='FAIL'
    error=$message
    errorRecord=$errorText
    mode=$Mode
    surface=$SurfaceKey
    outDir=$outDir
    terminalRoot=$termRoot
    specArg=$specArg
    specPath=$specPath
    createdAt=(Get-Date).ToString('o')
  }
  Write-JsonFile (Join-Path $reports 'fatal.json') $err
  Write-Utf8 (Join-Path $reports 'fatal.txt') $errorText
  Add-RunLog "FATAL=$message"
  New-ZipFromDir $outDir $failZip
  Write-Host "FALLO: $message" -ForegroundColor Red
  Write-Host "ZIP fail: $failZip" -ForegroundColor Red
  exit 1
}
