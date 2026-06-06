$ErrorActionPreference = 'Stop'

$ProjectRoot = 'F:\repos\hitech-os\tools\code-atlas'
$RepoRoot = 'F:\repos\hitech-os'
$Downloads = 'F:\descargasf'

$env:CODE_ATLAS_APP_ROOT = $ProjectRoot
$env:CODE_ATLAS_REPO_ROOT = $RepoRoot
$env:CODE_ATLAS_PROJECT_ROOT = $ProjectRoot
$env:CODE_ATLAS_DOWNLOADS_ROOT = $Downloads
$env:CODE_ATLAS_DEFAULT_OUTPUT_ROOT = $Downloads
$env:PYTHONPATH = "$ProjectRoot;$RepoRoot"

$Log = Join-Path $Downloads 'code-atlas.log'
$Err = Join-Path $Downloads 'code-atlas-error.txt'

function Add-CodeAtlasLog {
  param([string]$Text)
  ("[{0}] {1}" -f (Get-Date).ToString('s'), $Text) | Add-Content -Path $Log -Encoding UTF8
}

try {
  [System.IO.Directory]::CreateDirectory($Downloads) | Out-Null
  Set-Location -Path $ProjectRoot

  $Main = Join-Path $ProjectRoot 'code-atlas.py'
  if(-not (Test-Path -Path $Main)) {
    throw "No encontré code-atlas.py en $ProjectRoot"
  }

  Add-CodeAtlasLog "Opening Code Atlas: $Main"

  if(Get-Command pyw -ErrorAction SilentlyContinue) {
    Start-Process -FilePath 'pyw' -ArgumentList @('-3', "$Main") -WorkingDirectory $ProjectRoot
  } elseif(Get-Command pythonw -ErrorAction SilentlyContinue) {
    Start-Process -FilePath 'pythonw' -ArgumentList @("$Main") -WorkingDirectory $ProjectRoot
  } elseif(Get-Command py -ErrorAction SilentlyContinue) {
    Start-Process -FilePath 'py' -ArgumentList @('-3', "$Main") -WorkingDirectory $ProjectRoot
  } elseif(Get-Command python -ErrorAction SilentlyContinue) {
    Start-Process -FilePath 'python' -ArgumentList @("$Main") -WorkingDirectory $ProjectRoot
  } else {
    throw 'No encontré Python: pyw/pythonw/py/python.'
  }
} catch {
  $msg = ($_ | Out-String)
  $msg | Set-Content -Path $Err -Encoding UTF8
  Add-CodeAtlasLog ("ERROR: " + $msg)
  Start-Process powershell.exe -ArgumentList @(
    '-NoExit',
    '-NoProfile',
    '-Command',
    "Write-Host 'Code Atlas no pudo abrir. Revisa F:\descargasf\code-atlas-error.txt' -ForegroundColor Red; if(Test-Path 'F:\descargasf\code-atlas-error.txt'){Get-Content 'F:\descargasf\code-atlas-error.txt' -Raw}"
  )
}
