$ErrorActionPreference='Stop'
$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = (Join-Path $Root 'src') + [IO.Path]::PathSeparator + $env:PYTHONPATH
$Out = Join-Path $Root 'reports\atlas_plus'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m code_atlas.cli gate --project-root $Root --out $Out --allow-unknown-missing }
elseif (Get-Command python -ErrorAction SilentlyContinue) { & python -m code_atlas.cli gate --project-root $Root --out $Out --allow-unknown-missing }
else { throw 'No encontré Python.' }
