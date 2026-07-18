#requires -Version 5.1
[CmdletBinding()]
param(
  [ValidateSet('all','chart-lab','web','tablet','pc','mobile','control-center')]
  [string]$Surface = 'all',

  [ValidateRange(1,18)]
  [int]$Workers = 6,

  [ValidateRange(1,18)]
  [int]$Shards = 1,

  [switch]$Strict,
  [switch]$AllowPartial,
  [switch]$NoScreenshots,

  [ValidateRange(1000,180000)]
  [int]$GotoTimeoutMs = 45000,

  [ValidateRange(0,5)]
  [int]$GotoRetries = 2,

  [ValidateRange(1000,120000)]
  [int]$ScreenshotTimeoutMs = 15000,

  [ValidateRange(100,30000)]
  [int]$ProbeTimeoutMs = 1400,

  [ValidateRange(240,3840)]
  [int]$ViewportWidth = 1365,

  [ValidateRange(320,2160)]
  [int]$ViewportHeight = 768,

  [ValidateRange(0,10000)]
  [int]$SettleMs = 700
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LegacyRun = Join-Path $ToolRoot 'RUN.ps1'
$AuthorityScript = Join-Path $ToolRoot 'legal_evidence\mam_legal_authority.py'
$PostprocessScript = Join-Path $ToolRoot 'legal_evidence\mam_legal_postprocess.py'
$OutputRoot = 'F:\descargasf'
$TrashRoot = 'F:\Trash-old'
$RepoRoot = 'F:\repos\hitech-os'
$NdcRoot = 'F:\PRISMA_CTX\NDC'
$MotorsRoot = 'F:\PRISMA_CTX\MOTORES'

function Resolve-Python {
  foreach ($candidate in @('py.exe','python.exe','python3.exe','py','python3','python')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) {
      if ($candidate -in @('py.exe','py')) {
        return [pscustomobject]@{ Exe=$cmd.Source; Prefix=@('-3') }
      }
      return [pscustomobject]@{ Exe=$cmd.Source; Prefix=@() }
    }
  }
  throw 'PYTHON_RUNTIME_NOT_FOUND'
}

function Resolve-PowerShell {
  foreach ($candidate in @('powershell.exe','pwsh.exe','powershell','pwsh')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) { return $cmd.Source }
  }
  throw 'POWERSHELL_RUNTIME_NOT_FOUND'
}

function Get-FileSha256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Write-JsonFile([string]$Path, [object]$Value) {
  $parent = Split-Path -Parent $Path
  if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
  $Value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Move-StageToTrash([string]$StageDir, [string]$RunName, [string]$Reason) {
  if (-not (Test-Path -LiteralPath $StageDir)) { return $null }
  New-Item -ItemType Directory -Force -Path $TrashRoot | Out-Null
  $dest = Join-Path $TrashRoot ($RunName + ' stage ' + (Get-Date -Format 'ddMM HHmmss'))
  $counter = 2
  while (Test-Path -LiteralPath $dest) {
    $dest = Join-Path $TrashRoot ($RunName + ' stage ' + (Get-Date -Format 'ddMM HHmmss') + " $counter")
    $counter++
  }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $manifest = [ordered]@{
    schema='PRISMA_TRASH_MOVE_MANIFEST_V1'
    generated_at=(Get-Date).ToString('o')
    reason=$Reason
    source=$StageDir
    destination=$dest
  }
  Write-JsonFile (Join-Path $dest 'manifest.json') $manifest
  @"
# Mamastrophic legal staging move

- Source: `$StageDir`
- Destination: `$dest`
- Reason: $Reason
"@ | Set-Content -LiteralPath (Join-Path $dest 'manifest.md') -Encoding UTF8
  Move-Item -LiteralPath $StageDir -Destination (Join-Path $dest (Split-Path -Leaf $StageDir)) -Force
  return $dest
}

if (-not (Test-Path -LiteralPath $LegacyRun)) { throw "Missing legacy RUN.ps1: $LegacyRun" }
if (-not (Test-Path -LiteralPath $AuthorityScript)) { throw "Missing authority helper: $AuthorityScript" }
if (-not (Test-Path -LiteralPath $PostprocessScript)) { throw "Missing postprocessor: $PostprocessScript" }

New-Item -ItemType Directory -Force -Path $OutputRoot,$TrashRoot | Out-Null

$Stamp = Get-Date -Format 'ddMM HHmmss'
$RunId = 'mamlegal-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$RunName = "mamlegal $Stamp"
$Stage = Join-Path $OutputRoot ('.mamlegal_' + [guid]::NewGuid().ToString('N'))
$RawRoot = Join-Path $Stage 'raw'
$PackageRoot = Join-Path $Stage 'package'
$LogsRoot = Join-Path $Stage 'logs'
$ReportsRoot = Join-Path $Stage 'reports'
$AuthorityJson = Join-Path $ReportsRoot 'AUTHORITY_CHAIN.json'
$SurfaceResultsJson = Join-Path $ReportsRoot 'SURFACE_RESULTS.json'
$ResultZip = Join-Path $OutputRoot ($RunName + ' result.zip')
$FailZip = Join-Path $OutputRoot ($RunName + ' fail.zip')

New-Item -ItemType Directory -Force -Path $RawRoot,$PackageRoot,$LogsRoot,$ReportsRoot | Out-Null

$Python = Resolve-Python
$PowerShell = Resolve-PowerShell
$OriginalEnv = @{
  PRISMA_MAM_LEGAL_EVIDENCE = $env:PRISMA_MAM_LEGAL_EVIDENCE
  PRISMA_MAM_LEGAL_RUN_ID = $env:PRISMA_MAM_LEGAL_RUN_ID
  PRISMA_MAM_LEGAL_REDACTION_POLICY = $env:PRISMA_MAM_LEGAL_REDACTION_POLICY
  PYTHONUTF8 = $env:PYTHONUTF8
  PYTHONIOENCODING = $env:PYTHONIOENCODING
  PYTHONDONTWRITEBYTECODE = $env:PYTHONDONTWRITEBYTECODE
}

$SurfaceCatalog = @('chart-lab','web','tablet','pc','mobile','control-center')
$Selected = if ($Surface -eq 'all') { $SurfaceCatalog } else { @($Surface) }
$SurfaceRows = New-Object System.Collections.Generic.List[object]
$OverallStatus = 'PASS'
$StartedAt = Get-Date

try {
  $env:PRISMA_MAM_LEGAL_EVIDENCE = '1'
  $env:PRISMA_MAM_LEGAL_RUN_ID = $RunId
  $env:PRISMA_MAM_LEGAL_REDACTION_POLICY = 'mamlegal1-strict-v1'
  $env:PYTHONUTF8 = '1'
  $env:PYTHONIOENCODING = 'utf-8'
  $env:PYTHONDONTWRITEBYTECODE = '1'

  Write-Host "MAMLEGAL run=$RunId surface=$Surface workers=$Workers shards=$Shards" -ForegroundColor Cyan
  Write-Host 'Policy: one external capture at a time; internal Playwright workers allowed.' -ForegroundColor DarkCyan
  Write-Host 'No start, no kill, no DB, no deploy, no dependency install.' -ForegroundColor DarkCyan

  & $Python.Exe @($Python.Prefix) $AuthorityScript `
    --output-root $OutputRoot `
    --ndc-root $NdcRoot `
    --motors-root $MotorsRoot `
    --out $AuthorityJson
  if ($LASTEXITCODE -ne 0) { throw "Authority validation failed with exit code $LASTEXITCODE" }

  $index = 0
  foreach ($SurfaceName in $Selected) {
    $index++
    $SurfaceRoot = Join-Path $RawRoot $SurfaceName
    $StdOut = Join-Path $LogsRoot ($SurfaceName + '.stdout.log')
    $StdErr = Join-Path $LogsRoot ($SurfaceName + '.stderr.log')
    New-Item -ItemType Directory -Force -Path $SurfaceRoot | Out-Null

    $Args = @(
      '-NoLogo','-NoProfile','-ExecutionPolicy','Bypass',
      '-File',$LegacyRun,
      '-Mode','visualqa',
      '-Surface',$SurfaceName,
      '-Workers',[string]$Workers,
      '-Shards',[string]$Shards,
      '-SurfaceParallel','off',
      '-ArtifactRoot',$SurfaceRoot,
      '-NoZip',
      '-GpuMode','off',
      '-GotoTimeoutMs',[string]$GotoTimeoutMs,
      '-GotoRetries',[string]$GotoRetries,
      '-ScreenshotTimeoutMs',[string]$ScreenshotTimeoutMs,
      '-ProbeTimeoutMs',[string]$ProbeTimeoutMs,
      '-ViewportWidth',[string]$ViewportWidth,
      '-ViewportHeight',[string]$ViewportHeight,
      '-SettleMs',[string]$SettleMs
    )
    if ($Strict) { $Args += '-Strict' }
    if ($AllowPartial) { $Args += '-AllowPartial' }
    if ($NoScreenshots) { $Args += '-NoScreenshots' }

    Write-Host ("[{0}/{1}] capture {2}" -f $index,$Selected.Count,$SurfaceName) -ForegroundColor Cyan
    $started = Get-Date
    $output = & $PowerShell @Args 2>&1
    $exitCode = $LASTEXITCODE
    $outputText = ($output | Out-String)
    $outputText | Set-Content -LiteralPath $StdOut -Encoding UTF8
    '' | Set-Content -LiteralPath $StdErr -Encoding UTF8

    $summaryPath = Join-Path $SurfaceRoot 'reports\summary.json'
    $status = if ($exitCode -eq 0) { 'PASS' } else { 'FAIL' }
    $summary = $null
    if (Test-Path -LiteralPath $summaryPath) {
      try {
        $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($summary.status) { $status = [string]$summary.status }
      } catch {
        $status = if ($exitCode -eq 0) { 'PARTIAL' } else { 'FAIL' }
      }
    }

    if ($status -eq 'FAIL' -or $exitCode -ne 0) {
      $OverallStatus = 'FAIL'
    } elseif ($status -in @('PARTIAL','PARTIAL_PASS') -and $OverallStatus -ne 'FAIL') {
      $OverallStatus = 'PARTIAL'
    }

    [void]$SurfaceRows.Add([ordered]@{
      surface=$SurfaceName
      status=$status
      exit_code=$exitCode
      artifact_root=$SurfaceRoot
      summary_path=if(Test-Path -LiteralPath $summaryPath){$summaryPath}else{$null}
      started_at=$started.ToString('o')
      finished_at=(Get-Date).ToString('o')
      stdout=$StdOut
      stderr=$StdErr
    })

    Write-Host ("surface={0} status={1} exit={2}" -f $SurfaceName,$status,$exitCode) -ForegroundColor ($(if($exitCode -eq 0){'Green'}else{'Red'}))
  }

  Write-JsonFile $SurfaceResultsJson @($SurfaceRows)
  $OutputZip = if ($OverallStatus -eq 'FAIL') { $FailZip } else { $ResultZip }

  & $Python.Exe @($Python.Prefix) $PostprocessScript `
    --raw-root $RawRoot `
    --package-root $PackageRoot `
    --output-zip $OutputZip `
    --run-id $RunId `
    --repo-root $RepoRoot `
    --tool-root $ToolRoot `
    --surface-results $SurfaceResultsJson `
    --authority-json $AuthorityJson `
    --status $OverallStatus
  $PostCode = $LASTEXITCODE

  if (-not (Test-Path -LiteralPath $OutputZip)) {
    throw "Postprocessor produced no final ZIP: $OutputZip"
  }

  $ZipHash = Get-FileSha256 $OutputZip
  Write-Host "FINAL_ZIP=$OutputZip" -ForegroundColor Green
  Write-Host "FINAL_SHA256=$ZipHash" -ForegroundColor DarkCyan

  $trash = Move-StageToTrash -StageDir $Stage -RunName $RunName -Reason 'Final Mamastrophic legal evidence ZIP created; staging retained in Trash-old.'
  if ($trash) { Write-Host "STAGE_MOVED_TO=$trash" -ForegroundColor DarkCyan }

  if ($PostCode -ne 0 -or $OverallStatus -eq 'FAIL') { exit 2 }
  exit 0
}
catch {
  $message = ($_ | Out-String)
  Write-Error $message
  try {
    Write-JsonFile (Join-Path $PackageRoot 'WRAPPER_FAILURE.json') ([ordered]@{
      schema='PRISMA_MAM_LEGAL_WRAPPER_FAIL_V1'
      run_id=$RunId
      status='FAIL'
      error=$message
      started_at=$StartedAt.ToString('o')
      finished_at=(Get-Date).ToString('o')
      no_touch=[ordered]@{
        db_write=$false
        git_write=$false
        process_kill=$false
        port_free=$false
        server_start=$false
        dependency_install=$false
      }
    })
    @"
# Mamastrophic legal failure

- Run: `$RunId`
- Error: see `WRAPPER_FAILURE.json`
- No process, port, DB, Git or dependency mutation was performed by the legal wrapper.
"@ | Set-Content -LiteralPath (Join-Path $PackageRoot 'CONTINUATION.md') -Encoding UTF8

    if (-not (Test-Path -LiteralPath $FailZip)) {
      Compress-Archive -Path (Join-Path $PackageRoot '*') -DestinationPath $FailZip -CompressionLevel Optimal -Force
    }
    Write-Host "FINAL_ZIP=$FailZip" -ForegroundColor Red
  } catch {}
  try {
    Move-StageToTrash -StageDir $Stage -RunName $RunName -Reason 'Mamastrophic legal run failed; staging retained for diagnosis.' | Out-Null
  } catch {}
  exit 2
}
finally {
  $env:PRISMA_MAM_LEGAL_EVIDENCE = $OriginalEnv.PRISMA_MAM_LEGAL_EVIDENCE
  $env:PRISMA_MAM_LEGAL_RUN_ID = $OriginalEnv.PRISMA_MAM_LEGAL_RUN_ID
  $env:PRISMA_MAM_LEGAL_REDACTION_POLICY = $OriginalEnv.PRISMA_MAM_LEGAL_REDACTION_POLICY
  $env:PYTHONUTF8 = $OriginalEnv.PYTHONUTF8
  $env:PYTHONIOENCODING = $OriginalEnv.PYTHONIOENCODING
  $env:PYTHONDONTWRITEBYTECODE = $OriginalEnv.PYTHONDONTWRITEBYTECODE
}
