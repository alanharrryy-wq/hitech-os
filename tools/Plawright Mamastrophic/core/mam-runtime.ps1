# MAMHOME3 local runtime helper
$__mamHelperPath = $MyInvocation.MyCommand.Path
$__mamCore = Split-Path -Parent $__mamHelperPath
$__mamToolRoot = Split-Path -Parent $__mamCore
$__mamRuntime = Join-Path $__mamToolRoot '.mam-runtime'
$__mamNodeModules = Join-Path $__mamRuntime 'node_modules'
$__mamBin = Join-Path $__mamNodeModules '.bin'
$__mamBrowsers = Join-Path $__mamRuntime '.ms-playwright'
if (Test-Path -LiteralPath $__mamRuntime) {
  $env:PLAYWRIGHT_BROWSERS_PATH = $__mamBrowsers
  $env:PRISMA_MAM_RUNTIME_ROOT = $__mamRuntime
  $env:PRISMA_MAM_NODE_MODULES = $__mamNodeModules
  if (Test-Path -LiteralPath $__mamNodeModules) {
    if ([string]::IsNullOrWhiteSpace($env:NODE_PATH)) { $env:NODE_PATH = $__mamNodeModules }
    elseif ($env:NODE_PATH -notlike "*$__mamNodeModules*") { $env:NODE_PATH = $__mamNodeModules + ';' + $env:NODE_PATH }
  }
  if (Test-Path -LiteralPath $__mamBin) {
    if ($env:PATH -notlike "*$__mamBin*") { $env:PATH = $__mamBin + ';' + $env:PATH }
  }
}
