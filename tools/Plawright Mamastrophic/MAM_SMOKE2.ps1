param(
  [string]$ToolRoot = 'F:\repos\hitech-os\tools\Plawright Mamastrophic',
  [string]$OutRoot = 'F:\descargasf',
  [switch]$SkipRuntime
)
$ErrorActionPreference = 'Stop'
$Temp = Join-Path $env:TEMP ('mam_smoke2_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $Temp | Out-Null
$PyPath = Join-Path $Temp 'RUN_MAM_SMOKE2.py'
@'
from __future__ import annotations
import json, os, sys, subprocess, socket, datetime as dt, shutil, zipfile, traceback
from pathlib import Path
TOOL=Path(os.environ.get('MAM_TOOL_ROOT', r'F:\repos\hitech-os\tools\Plawright Mamastrophic'))
OUT=Path(os.environ.get('MAM_OUT_ROOT', r'F:\descargasf'))
SKIP_RUNTIME=os.environ.get('MAM_SKIP_RUNTIME','0')=='1'
OUT.mkdir(parents=True, exist_ok=True)
stamp=dt.datetime.now().strftime('%d%m %H%M')
name=f'mam smoke2 {stamp}'
work=OUT/name
logs=work/'logs'; reports=work/'reports'; runs=work/'official_runs'
for d in [logs,reports,runs]: d.mkdir(parents=True, exist_ok=True)
fail=[]; warn=[]; log=[]; step=0; total=12
SURF=[('chart-lab',3000),('web',3110),('tablet',3120),('pc',3130),('mobile',3140),('control-center',3150)]
REQ=['RUN.ps1','core/run-surf8-capture.ps1','core/run-point-probe.ps1','tests/surf8.point-probe.cjs','MAM_SMOKE2.ps1']
def p(msg):
 global step; step+=1; pct=int(step/total*100); rem=100-pct; bar='█'*int(pct*28/100)+'░'*(28-int(pct*28/100)); print(f'[{bar}] {pct:3d}% avanzado | {rem:3d}% restante | {msg}', flush=True); log.append(msg)
def run(name,cmd,cwd=None,timeout=90,critical=True):
 fp=logs/(name.replace(' ','_').replace('/','_')+'.log')
 try:
  pr=subprocess.run(cmd,cwd=str(cwd) if cwd else None,capture_output=True,text=True,timeout=timeout)
  fp.write_text('CMD:\n'+' '.join(map(str,cmd))+'\n\nCODE='+str(pr.returncode)+'\n\nSTDOUT:\n'+pr.stdout+'\n\nSTDERR:\n'+pr.stderr,encoding='utf-8',errors='replace')
  if pr.returncode!=0:
   (fail if critical else warn).append(f'{name} exit={pr.returncode} log={fp}')
  return {'name':name,'code':pr.returncode,'log':str(fp),'stdoutTail':pr.stdout[-4000:],'stderrTail':pr.stderr[-4000:]}
 except subprocess.TimeoutExpired:
  fp.write_text('TIMEOUT',encoding='utf-8')
  (fail if critical else warn).append(f'{name} timeout log={fp}')
  return {'name':name,'code':-998,'log':str(fp)}
def which(names):
 for n in names:
  x=shutil.which(n)
  if x: return x
 return None
def port(port):
 row={'port':port,'online':False,'error':''}
 try:
  s=socket.create_connection(('127.0.0.1',port),timeout=1.0); s.close(); row['online']=True
 except Exception as e: row['error']=str(e)
 return row
def zipit(src,dst):
 if dst.exists(): dst.unlink()
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
  for f in src.rglob('*'):
   if f.is_file(): z.write(f,f.relative_to(src).as_posix())
try:
 p('rutas')
 if not TOOL.exists(): fail.append(f'No existe {TOOL}')
 (reports/'paths.json').write_text(json.dumps({'tool':str(TOOL),'out':str(OUT),'skipRuntime':SKIP_RUNTIME},indent=2),encoding='utf-8')
 p('archivos requeridos')
 req=[]
 for r in REQ:
  exists=(TOOL/r).exists(); req.append({'path':r,'exists':exists})
  if not exists: fail.append(f'Falta {r}')
 (reports/'required_files.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
 p('toolchain')
 ps=which(['powershell.exe','powershell','pwsh.exe','pwsh']); node=which(['node.exe','node']); py=which(['python.exe','python']); pyl=which(['py.exe','py'])
 pycmd=[pyl,'-3'] if pyl else ([py] if py else [])
 if not ps: fail.append('No PowerShell')
 if not node: fail.append('No Node')
 (reports/'toolchain.json').write_text(json.dumps({'ps':ps,'node':node,'py':py,'pylauncher':pyl},indent=2),encoding='utf-8')
 p('parse powershell')
 if ps:
  for r in ['RUN.ps1','core/run-point-probe.ps1','MAM_SMOKE2.ps1']:
   f=TOOL/r
   if f.exists():
    code=f"$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('{str(f).replace(chr(39), chr(39)*2)}',[ref]$t,[ref]$e)|Out-Null;if($e.Count){{$e|%{{$_.ToString()}};exit 1}}else{{'PARSE_OK'}}"
    run('ps_parse_'+r,[ps,'-NoProfile','-Command',code],TOOL,30,True)
 p('node check')
 if node:
  for r in ['tests/surf8.point-probe.cjs','tests/surf8.visualqa.engine.cjs','tests/surf8.all-surfaces.engine.cjs']:
   f=TOOL/r
   if f.exists(): run('node_check_'+r,[node,'--check',str(f)],TOOL,30,True)
 p('puertos')
 ports=[]
 for s,po in SURF:
  row=port(po); row['surface']=s; ports.append(row)
 (reports/'ports.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
 online=[r for r in ports if r['online']]
 p('discovery all ligero')
 if ps and (TOOL/'RUN.ps1').exists() and not fail:
  run('official_discovery_all',[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(TOOL/'RUN.ps1'),'-Mode','discovery','-Surface','all','-Workers','1','-NoScreenshots','-DeepScroll','off','-SurfaceParallelMax','2','-ArtifactRoot',str(runs/'discovery_all'),'-NoZip'],TOOL,120,True)
 p('planes recursivos')
 plans=list((runs/'discovery_all').rglob('surf8.capture-plan.json'))
 summaries=[]
 for pp in plans:
  try:
   data=json.loads(pp.read_text(encoding='utf-8',errors='replace')); summaries.append({'path':str(pp.relative_to(work)),'targetCount':data.get('targetCount'),'macroCount':len(data.get('macros') or [])})
  except Exception as e: summaries.append({'path':str(pp.relative_to(work)),'error':str(e)})
 if not SKIP_RUNTIME and not plans and not fail: fail.append('Discovery no produjo surf8.capture-plan.json recursivos')
 (reports/'capture_plans_recursive.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
 p('point-probe tablet liviano')
 if not SKIP_RUNTIME and any(r['surface']=='tablet' and r['online'] for r in online) and ps:
  run('point_probe_tablet',[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(TOOL/'RUN.ps1'),'-Mode','point-probe','-Surface','tablet','-Route','/pos','-NoScreenshots','-AllowPartial','-GotoTimeoutMs','12000','-ArtifactRoot',str(runs/'point_tablet'),'-NoZip'],TOOL,60,False)
 else: warn.append('point-probe runtime saltado: tablet offline o SkipRuntime')
 p('critical online ligero')
 if not SKIP_RUNTIME and ps and (TOOL/'RUN.ps1').exists():
  for r in online:
   surf=r['surface']
   run('critical_'+surf,[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(TOOL/'RUN.ps1'),'-Mode','critical','-Surface',surf,'-Workers','1','-NoScreenshots','-AllowPartial','-DeepScroll','off','-GotoTimeoutMs','15000','-GotoRetries','1','-ProbeTimeoutMs','800','-ScreenshotTimeoutMs','5000','-TestTimeoutMs','90000','-GpuMode','off','-ArtifactRoot',str(runs/('critical_'+surf)),'-NoZip'],TOOL,140,False)
 else: warn.append('critical runtime saltado')
 p('reporte')
 status='FAIL' if fail else ('PARTIAL_PASS' if warn else 'PASS')
 final={'status':status,'tool':str(TOOL),'failures':fail,'warnings':warn,'createdAt':dt.datetime.now().isoformat(),'policy':'no kill, no start, no prisma'}
 (reports/'FINAL_REPORT.json').write_text(json.dumps(final,indent=2,ensure_ascii=False),encoding='utf-8')
 (reports/'FINAL_REPORT.md').write_text('# Mamastrophic smoke2\n\n- status: `'+status+'`\n\n## Failures\n'+''.join(f'\n- {x}' for x in fail)+'\n\n## Warnings\n'+''.join(f'\n- {x}' for x in warn)+'\n',encoding='utf-8')
 (reports/'RUN_LOG.txt').write_text('\n'.join(log),encoding='utf-8')
 target=OUT/(f'{name} '+('fail' if fail else 'result')+'.zip')
 p('zip')
 zipit(work,target); shutil.rmtree(work,ignore_errors=True); print('SMOKE2_ZIP='+str(target), flush=True)
 sys.exit(1 if fail else 0)
except Exception:
 err=traceback.format_exc(); print(err, file=sys.stderr)
 try:
  (reports/'ERROR.txt').write_text(err,encoding='utf-8')
  target=OUT/(f'{name} fail.zip'); zipit(work,target); shutil.rmtree(work,ignore_errors=True); print('SMOKE2_FAIL_ZIP='+str(target), flush=True)
 except Exception as e: print('No pude crear fail zip '+str(e), file=sys.stderr)
 sys.exit(1)
'@ | Set-Content -Path $PyPath -Encoding UTF8
$env:MAM_TOOL_ROOT = $ToolRoot
$env:MAM_OUT_ROOT = $OutRoot
$env:MAM_SKIP_RUNTIME = if ($SkipRuntime) { '1' } else { '0' }
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $Python) { throw 'No encontré python ni py en PATH.' }
if ($Python.Name -eq 'py.exe' -or $Python.Name -eq 'py') { & $Python.Source -3 $PyPath } else { & $Python.Source $PyPath }
$Code = $LASTEXITCODE
Remove-Item -Recurse -Force $Temp -ErrorAction SilentlyContinue
if ($Code -ne 0) { throw "MAM_SMOKE2 falló. Revisa ZIP fail en $OutRoot" }
