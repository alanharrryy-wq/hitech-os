$ErrorActionPreference='Stop'
$RepoRoot = if($env:PRISMA_REPO_ROOT){$env:PRISMA_REPO_ROOT}else{'F:\repos\hitech-os'}
$OutRoot = if($env:PRISMA_OUT_ROOT){$env:PRISMA_OUT_ROOT}else{'F:\descargasf'}
$SrcRoot = Join-Path $RepoRoot 'tools\code-atlas\src'
$env:PYTHONPATH = if($env:PYTHONPATH){$SrcRoot + ';' + $env:PYTHONPATH}else{$SrcRoot}
$Python = (Get-Command py.exe -ErrorAction SilentlyContinue).Source
$Args = @()
if($Python){$Args=@('-3')}else{$Python=(Get-Command python.exe -ErrorAction Stop).Source}
$ModuleArgs = @('-m','code_atlas.appbrain_batch_packager','--repo',$RepoRoot,'--out',$OutRoot)
if($env:APPBRAIN_WORKBENCH_ZIP){$ModuleArgs += @('--source',$env:APPBRAIN_WORKBENCH_ZIP)}
if($env:APPBRAIN_BATCH_ID){$ModuleArgs += @('--batch',$env:APPBRAIN_BATCH_ID)}
if($env:APPBRAIN_APP){$ModuleArgs += @('--app',$env:APPBRAIN_APP)}
if($env:APPBRAIN_SEMANTIC_GROUP){$ModuleArgs += @('--semantic-group',$env:APPBRAIN_SEMANTIC_GROUP)}
& $Python @Args @ModuleArgs
if($LASTEXITCODE -ne 0){ throw "AppBrain Batch Packager failed with exit code $LASTEXITCODE" }
