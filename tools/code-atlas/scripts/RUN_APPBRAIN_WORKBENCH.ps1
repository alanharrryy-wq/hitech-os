$ErrorActionPreference = 'Stop'
$RepoRoot = if($env:CODE_ATLAS_REPO_ROOT){$env:CODE_ATLAS_REPO_ROOT}else{'F:\repos\hitech-os'}
$OutRoot = if($env:CODE_ATLAS_OUTPUT_ROOT){$env:CODE_ATLAS_OUTPUT_ROOT}else{'F:\descargasf'}
$CodeAtlasRoot = Join-Path $RepoRoot 'tools\code-atlas'
$SrcRoot = Join-Path $CodeAtlasRoot 'src'
$PythonExe = (Get-Command py.exe -ErrorAction SilentlyContinue).Source
$PythonArgs = @()
if($PythonExe){ $PythonArgs=@('-3') } else { $PythonExe=(Get-Command python.exe -ErrorAction Stop).Source }
$env:PYTHONPATH = if($env:PYTHONPATH){ "$SrcRoot;$env:PYTHONPATH" } else { $SrcRoot }
Write-Host "[AppBrain Workbench] Repo: $RepoRoot"
Write-Host "[AppBrain Workbench] Output: $OutRoot"
& $PythonExe @PythonArgs -m code_atlas.appbrain_workbench.cli --repo $RepoRoot --out $OutRoot --label 'appbrain-workbench'
if($LASTEXITCODE -ne 0){ throw "AppBrain Workbench failed with exit code $LASTEXITCODE" }
