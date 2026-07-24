$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = $PSScriptRoot
$Validator = Join-Path $Root 'generator\validate_atlas.py'
$Py = Get-Command 'py.exe' -ErrorAction SilentlyContinue
if ($Py) { & $Py.Source -3 -u $Validator $Root }
else { & (Get-Command 'python.exe' -ErrorAction Stop).Source -u $Validator $Root }
if ($LASTEXITCODE -ne 0) { throw "ATLASFINAL validation failed with code $LASTEXITCODE" }
Write-Host 'PASS: PRISMA Visual Family Atlas completo.' -ForegroundColor Green
Write-Host '27 páginas · 26 secciones · 418 elementos' -ForegroundColor Cyan
Start-Process (Join-Path $Root 'index.html')
