$ErrorActionPreference='Stop'
$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = (Join-Path $Root 'src') + [IO.Path]::PathSeparator + $env:PYTHONPATH
$Out = Join-Path $Root 'reports\todo_el_show_plus'
[System.IO.Directory]::CreateDirectory($Out) | Out-Null
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m code_atlas.cli todo-plus --project-root $Root --out $Out }
elseif (Get-Command python -ErrorAction SilentlyContinue) { & python -m code_atlas.cli todo-plus --project-root $Root --out $Out }
else { throw 'No encontré Python.' }
Write-Host "Todo El Show Plus modular reports: $Out" -ForegroundColor Cyan
