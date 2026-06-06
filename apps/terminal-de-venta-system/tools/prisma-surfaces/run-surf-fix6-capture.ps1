param(
  [ValidateSet('critical','quick','full')][string]$Mode = 'full',
  [int]$Workers = 6,
  [int]$Shards = 1,
  [switch]$NoScreenshots,
  [switch]$FullPage
)
$ErrorActionPreference = 'Stop'

function Show-ProgressLine([int]$pct, [string]$msg) {
  $pct = [Math]::Max(0, [Math]::Min(100, $pct))
  $filled = [Math]::Floor($pct * 28 / 100)
  $bar = ('#' * $filled).PadRight(28, '.')
  $remaining = 100 - $pct
  Write-Host ("PROGRESS {0:d3}% [{1}] remaining {2:d3}% :: {3}" -f $pct, $bar, $remaining, $msg) -ForegroundColor Cyan
}

function Add-UniquePath([System.Collections.Generic.List[string]]$list, [string]$path) {
  if ([string]::IsNullOrWhiteSpace($path)) { return }
  try { $resolved = (Resolve-Path -LiteralPath $path -ErrorAction Stop).Path } catch { return }
  if (-not ($list -contains $resolved)) { [void]$list.Add($resolved) }
}

function Find-RepoRoot() {
  $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
  $candidate = Resolve-Path -LiteralPath (Join-Path $scriptRoot '..\..') -ErrorAction Stop
  return $candidate.Path
}

function Test-HttpPort([int]$port) {
  try {
    $uri = "http://127.0.0.1:$port/"
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $uri -TimeoutSec 2 -ErrorAction Stop
    return $true
  } catch {
    return $false
  }
}

function Invoke-NodeResolve([string]$nodeExe, [string]$root, [string]$moduleName) {
  $js = @'
const path = process.argv[1];
const mod = process.argv[2];
try {
  const resolved = require.resolve(mod, { paths: [path] });
  console.log(resolved);
} catch (error) {
  process.exit(7);
}
'@
  $out = & $nodeExe -e $js $root $moduleName 2>$null
  if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($out)) {
    $first = @($out)[0]
    if (Test-Path -LiteralPath $first) { return $first }
  }
  return $null
}

function Test-PlaywrightHelpHasTest([scriptblock]$runner) {
  try {
    $output = & $runner 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -and $output -match '(?m)\btest\b') { return $true }
  } catch {}
  return $false
}

function Resolve-PlaywrightInvocation([string]$repoRoot, [string]$nodeExe, [string[]]$searchRoots) {
  $attempts = New-Object System.Collections.Generic.List[string]

  foreach ($root in $searchRoots) {
    $resolvedCli = Invoke-NodeResolve $nodeExe $root '@playwright/test/cli'
    if ($resolvedCli -and (Test-Path -LiteralPath $resolvedCli)) {
      return @{ Kind='node-cli'; Exe=$nodeExe; Prefix=@($resolvedCli, 'test'); Root=$root; Detail="require.resolve @playwright/test/cli from $root"; Attempts=$attempts }
    }
    [void]$attempts.Add("missing require.resolve @playwright/test/cli from $root")

    $resolvedPkg = Invoke-NodeResolve $nodeExe $root '@playwright/test'
    if ($resolvedPkg) {
      $pkgDir = Split-Path -Parent $resolvedPkg
      $siblingCli = Join-Path $pkgDir 'cli.js'
      if (Test-Path -LiteralPath $siblingCli) {
        return @{ Kind='node-cli'; Exe=$nodeExe; Prefix=@($siblingCli, 'test'); Root=$root; Detail="require.resolve @playwright/test then sibling cli.js from $root"; Attempts=$attempts }
      }
    }
    [void]$attempts.Add("missing require.resolve @playwright/test sibling cli.js from $root")
  }

  foreach ($root in $searchRoots) {
    $candidates = @(
      (Join-Path $root 'node_modules\@playwright\test\cli.js'),
      (Join-Path $root 'node_modules\playwright\cli.js')
    )
    foreach ($cli in $candidates) {
      if (Test-Path -LiteralPath $cli) {
        return @{ Kind='node-cli'; Exe=$nodeExe; Prefix=@($cli, 'test'); Root=$root; Detail="direct cli path $cli"; Attempts=$attempts }
      }
      [void]$attempts.Add("missing direct cli path $cli")
    }
  }

  foreach ($root in $searchRoots) {
    $cmd = Join-Path $root 'node_modules\.bin\playwright.cmd'
    if (Test-Path -LiteralPath $cmd) {
      $ok = Test-PlaywrightHelpHasTest { & $cmd --help }
      if ($ok) {
        return @{ Kind='cmd-bin'; Exe=$cmd; Prefix=@('test'); Root=$root; Detail="local node_modules .bin playwright.cmd from $root"; Attempts=$attempts }
      }
      [void]$attempts.Add("found $cmd but help did not advertise test")
    } else {
      [void]$attempts.Add("missing local .bin $cmd")
    }
  }

  $npx = Get-Command npx -ErrorAction SilentlyContinue
  if ($npx) {
    $ok = Test-PlaywrightHelpHasTest { Push-Location $repoRoot; try { & $npx.Source --no-install playwright --help } finally { Pop-Location } }
    if ($ok) {
      return @{ Kind='npx-no-install'; Exe=$npx.Source; Prefix=@('--no-install','playwright','test'); Root=$repoRoot; Detail='npx --no-install playwright test'; Attempts=$attempts }
    }
    [void]$attempts.Add('npx --no-install playwright --help did not expose test or failed')
  } else {
    [void]$attempts.Add('npx not found')
  }

  $pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
  if ($pnpm) {
    $ok = Test-PlaywrightHelpHasTest { Push-Location $repoRoot; try { & $pnpm.Source exec playwright --help } finally { Pop-Location } }
    if ($ok) {
      return @{ Kind='pnpm-exec'; Exe=$pnpm.Source; Prefix=@('exec','playwright','test'); Root=$repoRoot; Detail='pnpm exec playwright test'; Attempts=$attempts }
    }
    [void]$attempts.Add('pnpm exec playwright --help did not expose test or failed')
  } else {
    [void]$attempts.Add('pnpm not found')
  }

  $corepack = Get-Command corepack -ErrorAction SilentlyContinue
  if ($corepack) {
    $ok = Test-PlaywrightHelpHasTest { Push-Location $repoRoot; try { & $corepack.Source pnpm exec playwright --help } finally { Pop-Location } }
    if ($ok) {
      return @{ Kind='corepack-pnpm-exec'; Exe=$corepack.Source; Prefix=@('pnpm','exec','playwright','test'); Root=$repoRoot; Detail='corepack pnpm exec playwright test'; Attempts=$attempts }
    }
    [void]$attempts.Add('corepack pnpm exec playwright --help did not expose test or failed')
  } else {
    [void]$attempts.Add('corepack not found')
  }

  return @{ Kind='missing'; Attempts=$attempts }
}

function New-DiagnosticZip([string]$repoRoot, [string]$reason, [object]$resolver, [string]$specPath) {
  $stamp = Get-Date -Format 'ddMM HHmm'
  $safeStamp = $stamp -replace ' ', ' '
  $outDir = Join-Path 'F:\descargasf' ("surf fix6 $safeStamp fix6 capture diagnostic")
  if (Test-Path -LiteralPath $outDir) { Remove-Item -LiteralPath $outDir -Recurse -Force }
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  $report = [ordered]@{
    status = 'FAIL'
    reason = $reason
    repoRoot = $repoRoot
    specPath = $specPath
    mode = $Mode
    workers = $Workers
    shards = $Shards
    resolver = $resolver
    node = (Get-Command node -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue)
    cwd = (Get-Location).Path
    createdAt = (Get-Date).ToString('o')
  }
  $json = $report | ConvertTo-Json -Depth 12
  Set-Content -LiteralPath (Join-Path $outDir 'report.json') -Value $json -Encoding UTF8
  Set-Content -LiteralPath (Join-Path $outDir 'CONTINUATION.md') -Value @"
# SURF FIX6 FIX6 CAPTURE DIAGNOSTIC

Status: FAIL
Reason: $reason

The runner tried to locate a real Playwright Test CLI without relying on a global PATH alias.
It checked require.resolve('@playwright/test/cli'), require.resolve('@playwright/test'), direct node_modules paths, local node_modules/.bin/playwright.cmd, npx --no-install, pnpm exec, and corepack pnpm exec.

Next action: ensure dependencies are installed in the workspace that owns this repo, or run the repository's existing ALL_PLAYWRIGHT command once and rerun this capture.
"@ -Encoding UTF8
  $zipPath = "F:\descargasf\surf fix6 $stamp fix6 capture fail.zip"
  if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
  Compress-Archive -LiteralPath (Join-Path $outDir '*') -DestinationPath $zipPath -Force
  Write-Host "FAIL ZIP: $zipPath" -ForegroundColor Red
}

Show-ProgressLine 005 'validando repo y spec'
$repoRoot = Find-RepoRoot
Set-Location $repoRoot
$specPath = Join-Path $repoRoot 'tests\prisma-surfaces\surf-fix6.internal-surfaces.spec.js'
if (-not (Test-Path -LiteralPath $specPath)) { throw "No encontré spec: $specPath" }

Show-ProgressLine 010 'probando puertos una sola vez'
$ports = @(3000,3110,3120,3130,3140,3150)
$online = @()
foreach ($p in $ports) { if (Test-HttpPort $p) { $online += $p } }
Write-Host ('Puertos online: ' + ($online -join ',')) -ForegroundColor Green

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) { throw 'No encontré node en PATH.' }

Show-ProgressLine 020 'resolviendo Node y Playwright Test CLI local/flexible'
$roots = New-Object System.Collections.Generic.List[string]
Add-UniquePath $roots $repoRoot
Add-UniquePath $roots (Join-Path $repoRoot 'products\pc\app')
Add-UniquePath $roots (Join-Path $repoRoot 'products\tablet')
Add-UniquePath $roots (Join-Path $repoRoot 'products\mobile')
$d = $repoRoot
while ($true) {
  $parent = Split-Path -Parent $d
  if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $d) { break }
  Add-UniquePath $roots $parent
  $d = $parent
}

$resolver = Resolve-PlaywrightInvocation $repoRoot $node.Source @($roots)
if ($resolver.Kind -eq 'missing') {
  Show-ProgressLine 100 'captura FAIL; diagnóstico generado'
  New-DiagnosticZip $repoRoot 'No encontré un Playwright Test CLI local ni ejecutable por npx/pnpm/corepack.' $resolver $specPath
  throw 'No encontré Playwright Test CLI local/flexible. Revisa el fail zip generado.'
}
Write-Host ("Playwright resolver: {0} :: {1}" -f $resolver.Kind, $resolver.Detail) -ForegroundColor Green

$env:PRISMA_SURF_MODE = $Mode
$env:PRISMA_SURF_ONLINE_PORTS = ($online -join ',')
$env:PRISMA_SURF_SCREENSHOTS = if ($NoScreenshots) { '0' } else { '1' }
$env:PRISMA_SURF_FULLPAGE = if ($FullPage) { '1' } else { '0' }

$args = @()
$args += $resolver.Prefix
$args += $specPath
$args += '--workers'
$args += [string]$Workers
$args += '--reporter=line'
if ($Mode -eq 'critical') { $args += '--grep'; $args += 'lifecycle|Control Center Data Lifecycle|data lifecycle' }
elseif ($Mode -eq 'quick') { $args += '--grep'; $args += 'Control Center|lifecycle|Chart Lab' }

Show-ProgressLine 035 ("ejecutando capture mode=$Mode workers=$Workers shards=$Shards")
$exitCode = 0
if ($Shards -gt 1) {
  for ($i = 1; $i -le $Shards; $i++) {
    Show-ProgressLine ([Math]::Min(90, 35 + [Math]::Floor(($i - 1) * 55 / $Shards))) ("shard $i/$Shards")
    $runArgs = @($args + @('--shard', "$i/$Shards"))
    Push-Location $resolver.Root
    try {
      & $resolver.Exe @runArgs
      if ($LASTEXITCODE -ne 0) { $exitCode = $LASTEXITCODE; break }
    } finally { Pop-Location }
  }
} else {
  Push-Location $resolver.Root
  try {
    & $resolver.Exe @args
    if ($LASTEXITCODE -ne 0) { $exitCode = $LASTEXITCODE }
  } finally { Pop-Location }
}

if ($exitCode -ne 0) {
  Show-ProgressLine 100 'captura FAIL; Playwright terminó con error'
  New-DiagnosticZip $repoRoot "Playwright terminó con código $exitCode" $resolver $specPath
  throw "Playwright terminó con código $exitCode"
}

Show-ProgressLine 100 'PASS'
