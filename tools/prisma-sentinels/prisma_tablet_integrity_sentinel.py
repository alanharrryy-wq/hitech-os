import os, re, sys, json, shutil, zipfile, subprocess, traceback, argparse
from pathlib import Path
from datetime import datetime

OUT_BASE = Path(r"F:\descargasf")
DEFAULT_REPO = Path(r"F:\repos\hitech-os")
APP_REL = Path("apps/terminal-de-venta-system")
SKIP_DIRS = {".git","node_modules",".next","dist","build","coverage",".turbo",".cache",".wrangler",".vercel",".expo"}
TEXT_EXTS = {".ts",".tsx",".js",".jsx",".mjs",".cjs"}
RUN_NAME = "sentinel " + datetime.now().strftime("%d%m %H%M")
STAGE = OUT_BASE / RUN_NAME
ZIP_PATH = OUT_BASE / f"{RUN_NAME}.zip"
TRASH_BASE = Path(r"F:\Trash-old") / RUN_NAME
BACKUP_ROOT = STAGE / "backups" / "repo"
REPORT = {"status":"INIT","run_name":RUN_NAME,"changes":[],"findings_before":[],"findings_after":[],"warnings":[],"failures":[],"manual":{"exists":False},"ledger_gate":{"exists":False}}
_BACKED = {}

ATTR_LINE_RE = re.compile(r"^\s*(placeholder|className|value|type|data-[\w-]+|aria-[\w-]+|role|disabled|checked|on[A-Z][A-Za-z0-9_]*|name|id|min|max|step|inputMode|autoComplete|required|readOnly)\s*=")
EVENT_BROKEN_RE = re.compile(r"(\bon[A-Z][A-Za-z0-9_]*\s*=\s*\{\s*(?:\([^{}\n]*\)|[A-Za-z_$][\w$]*)\s*)=\s*(?!>)")
EVENT_BROKEN_SCAN_RE = re.compile(r"\bon[A-Z][A-Za-z0-9_]*\s*=\s*\{\s*(?:\([^{}\n]*\)|[A-Za-z_$][\w$]*)\s*=(?!>)")

def pct(step,total,msg):
    p = int((step/max(total,1))*100)
    print(f"[{p:3d}% | falta {100-p:3d}%] {msg}", flush=True)

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

def safe_rel(rel):
    rel = str(rel).replace('\\','/').lstrip('/')
    parts=[]
    for part in rel.split('/'):
        if not part or part in ('.','..'): continue
        parts.append(re.sub(r'[^\w .@()\-]+','_', part)[:120] or '_')
    return Path(*parts) if parts else Path('_')

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', errors='replace')

def detect_repo():
    cp = run(['git','rev-parse','--show-toplevel'], Path.cwd())
    if cp.returncode == 0:
        return Path(cp.stdout.strip())
    cp = run(['git','-C',str(DEFAULT_REPO),'rev-parse','--show-toplevel'])
    if cp.returncode == 0:
        return Path(cp.stdout.strip())
    if DEFAULT_REPO.exists():
        return DEFAULT_REPO
    raise RuntimeError('No encontré F:\\repos\\hitech-os ni Git root desde el directorio actual.')

def app_root(repo):
    p = repo / APP_REL
    return p if p.exists() else repo

def rel_to(repo, p):
    return str(Path(p).resolve().relative_to(repo.resolve())).replace('\\','/')

def backup_file(repo, path, reason):
    path = Path(path)
    rel = rel_to(repo, path)
    if rel in _BACKED:
        return
    item = {"rel":rel,"reason":reason,"existed":path.exists(),"backup_rel":None}
    if path.exists() and path.is_file():
        dst = BACKUP_ROOT / safe_rel(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
        item["backup_rel"] = str(dst.relative_to(STAGE)).replace('\\','/')
    REPORT["changes"].append(item)
    _BACKED[rel]=item

def rollback_now(repo):
    for item in reversed(REPORT.get('changes', [])):
        target = repo / item['rel']
        backup_rel = item.get('backup_rel')
        if item.get('existed') and backup_rel:
            src = STAGE / backup_rel
            if src.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
        else:
            if target.exists():
                trash = TRASH_BASE / 'rollback_new_files' / safe_rel(item['rel'])
                trash.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(trash))
    REPORT['rollback_executed'] = True

def should_skip(p):
    parts=set(p.parts)
    return bool(parts & SKIP_DIRS)

def iter_code_files(root):
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS and not should_skip(p):
            yield p

def line_context(lines, idx, span=2):
    start=max(0, idx-span); end=min(len(lines), idx+span+1)
    return '\n'.join(f"{i+1}: {lines[i]}" for i in range(start,end))

def scan_jsx_text(rel, text):
    findings=[]
    lines=text.splitlines()
    for m in EVENT_BROKEN_SCAN_RE.finditer(text):
        ln=text[:m.start()].count('\n')
        findings.append({"path":rel,"type":"broken_event_arrow_equals","line":ln+1,"context":line_context(lines,ln)})
    for i in range(len(lines)-1):
        if lines[i].strip()== '>' and lines[i+1].strip()=='>':
            findings.append({"path":rel,"type":"double_gt_line","line":i+1,"context":line_context(lines,i)})
        if lines[i].strip()=='>':
            j=i+1; attrs=[]
            while j < len(lines) and ATTR_LINE_RE.match(lines[j]):
                attrs.append(j); j+=1
            if attrs and j < len(lines) and lines[j].strip() == '/>':
                findings.append({"path":rel,"type":"attribute_after_closed_self_closing_tag","line":i+1,"context":line_context(lines,i,4)})
    return findings

def fix_jsx_text(text):
    changed=False
    text2, n = EVENT_BROKEN_RE.subn(r"\1=> ", text)
    if n:
        changed=True
        text=text2
    lines=text.splitlines()
    out=[]; i=0
    while i < len(lines):
        if i+1 < len(lines) and lines[i].strip()== '>' and lines[i+1].strip()=='>':
            out.append(lines[i])
            i += 2
            changed=True
            continue
        if lines[i].strip()=='>':
            j=i+1; attrs=[]
            while j < len(lines) and ATTR_LINE_RE.match(lines[j]):
                attrs.append(lines[j]); j += 1
            if attrs and j < len(lines) and lines[j].strip() == '/>':
                prev_indent = ''
                for k in range(len(out)-1, -1, -1):
                    if out[k].strip():
                        prev_indent = re.match(r'^(\s*)', out[k]).group(1)
                        break
                for a in attrs:
                    out.append(prev_indent + a.strip())
                i = j
                changed=True
                continue
        out.append(lines[i]); i += 1
    fixed='\n'.join(out)
    if text.endswith('\n'):
        fixed += '\n'
    return fixed, changed

def find_route(app, route_tail):
    matches=list(app.glob('**/' + route_tail))
    return sorted(matches, key=lambda p: len(str(p)))[0] if matches else None

def ensure_import_guard(text):
    imp='import { guardTabletFeatureForApi } from "@/server/licensing/tablet-license-api"; // PRISMA_LICENSE_SENTINEL_IMPORT'
    if 'guardTabletFeatureForApi' in text:
        return text, False
    lines=text.splitlines()
    last_import=-1
    for idx,line in enumerate(lines):
        if line.startswith('import '): last_import=idx
    if last_import >= 0:
        lines.insert(last_import+1, imp)
    else:
        lines.insert(0, imp)
    return '\n'.join(lines) + ('\n' if text.endswith('\n') else ''), True

def ensure_api_gate(text, feature):
    if f'guardTabletFeatureForApi("{feature}")' in text or f"guardTabletFeatureForApi('{feature}')" in text:
        return text, False, 'already_present'
    text, changed_import = ensure_import_guard(text)
    lines=text.splitlines()
    block=[
        f'  // PRISMA_LICENSE_SENTINEL_BEGIN:{feature}',
        f'  const prismaLicenseGate = await guardTabletFeatureForApi("{feature}");',
        '  if (prismaLicenseGate) return prismaLicenseGate;',
        f'  // PRISMA_LICENSE_SENTINEL_END:{feature}',
    ]
    for idx,line in enumerate(lines):
        if re.match(r'^export\s+async\s+function\s+(GET|POST|PUT|PATCH|DELETE)\s*\(\s*request\s*:', line.strip()):
            if '{' in line:
                lines[idx+1:idx+1]=block
                return '\n'.join(lines) + ('\n' if text.endswith('\n') else ''), True, 'inserted'
    return text, changed_import, 'function_not_found'

def route_scan(app):
    targets={
        'products/search':'app/api/pos/products/search/route.ts',
        'products/resolve':'app/api/pos/products/resolve/route.ts',
        'sales/complete':'app/api/pos/sales/complete/route.ts',
    }
    features={'products/search':'pos.product.search','products/resolve':'pos.product.search','sales/complete':'pos.sale.complete'}
    results=[]
    for key, tail in targets.items():
        p=find_route(app, tail)
        res={"key":key,"tail":tail,"path":str(p) if p else None,"exists":bool(p),"feature":features[key],"has_gate":False}
        if p:
            txt=p.read_text(encoding='utf-8',errors='replace')
            feat=features[key]
            res['has_gate'] = f'guardTabletFeatureForApi("{feat}")' in txt or f"guardTabletFeatureForApi('{feat}')" in txt
        results.append(res)
    return results

def fix_api_gates(repo, app):
    route_targets=[
        ('app/api/pos/products/search/route.ts','pos.product.search'),
        ('app/api/pos/products/resolve/route.ts','pos.product.search'),
    ]
    changes=[]
    for tail, feature in route_targets:
        p=find_route(app, tail)
        if not p:
            REPORT['failures'].append(f'ROUTE_NOT_FOUND:{tail}')
            continue
        txt=p.read_text(encoding='utf-8',errors='replace')
        fixed, changed, mode=ensure_api_gate(txt, feature)
        if mode == 'function_not_found':
            REPORT['failures'].append(f'API_GATE_FUNCTION_NOT_FOUND:{rel_to(repo,p)}')
            continue
        if changed and fixed != txt:
            backup_file(repo,p,f'api_gate:{feature}')
            p.write_text(fixed,encoding='utf-8',errors='replace')
            changes.append({"path":rel_to(repo,p),"feature":feature,"mode":mode})
    return changes

def db_sentinel(repo, fix):
    app=app_root(repo)
    real=app/'products/tablet/app/data/tablet-pos.db'
    ghost=app/'products/tablet/data/tablet-pos.db'
    def info(p):
        return {"path":str(p),"exists":p.exists(),"size":p.stat().st_size if p.exists() else None,"sqlite_header_ok":p.exists() and p.is_file() and p.stat().st_size>=16 and p.read_bytes()[:16]==b'SQLite format 3\0'}
    res={"real":info(real),"ghost":info(ghost),"action":None}
    if ghost.exists() and ghost.is_file() and ghost.stat().st_size==0:
        cp=run(['git','ls-files','--error-unmatch',rel_to(repo,ghost)], repo)
        tracked=cp.returncode==0
        res['ghost_tracked']=tracked
        if tracked:
            REPORT['warnings'].append('GHOST_TABLET_DB_0_BYTES_TRACKED_NOT_MOVED')
        elif fix:
            backup_file(repo, ghost, 'ghost_tablet_db_0_bytes')
            trash=TRASH_BASE/'ghost-tablet-db'/safe_rel(rel_to(repo,ghost))
            trash.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(ghost), str(trash))
            res['action']='moved_to_trash_old'
            res['trash_path']=str(trash)
    return res

def install_tool(repo, current_script):
    tool_dir=repo/'tools/prisma-sentinels'
    tool_py=tool_dir/'prisma_tablet_integrity_sentinel.py'
    tool_ps=tool_dir/'RUN_TABLET_SENTINEL.ps1'
    tool_md=tool_dir/'README_TABLET_SENTINEL.md'
    for p in [tool_py,tool_ps,tool_md]:
        backup_file(repo,p,'install_sentinel_tool')
    tool_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(current_script, tool_py)
    ps = "$ErrorActionPreference = 'Stop'\n" \
         "$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)\n" \
         "$Py = Get-Command py -ErrorAction SilentlyContinue\n" \
         "if ($Py) { & py -3 (Join-Path $PSScriptRoot 'prisma_tablet_integrity_sentinel.py') --fix --skip-install --repo $Root } else { & python (Join-Path $PSScriptRoot 'prisma_tablet_integrity_sentinel.py') --fix --skip-install --repo $Root }\n"
    write(tool_ps, ps)
    md = "# PRISMA Tablet Integrity Sentinel\n\nEscáner/autofixer repo-wide para residuos JSX mecánicos, gates de licencia Tablet POS y DB fantasma Tablet.\n\nUso:\n\n```powershell\nF:\\repos\\hitech-os\\tools\\prisma-sentinels\\RUN_TABLET_SENTINEL.ps1\n```\n\nLa herramienta es reversible: cada corrida deja ZIP con backups y ROLLBACK.ps1 en F:\\descargasf.\n"
    write(tool_md, md)
    return [rel_to(repo,tool_py),rel_to(repo,tool_ps),rel_to(repo,tool_md)]

def read_context(repo):
    manual=repo/APP_REL/'docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md'
    if not manual.exists(): manual=repo/'docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md'
    if manual.exists():
        REPORT['manual']={"exists":True,"path":rel_to(repo,manual),"first_2000":manual.read_text(encoding='utf-8',errors='replace')[:2000]}
    else:
        REPORT['warnings'].append('FIELD_MANUAL_NOT_FOUND')
    ledger=repo/'PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md'
    if ledger.exists():
        REPORT['ledger_gate']={"exists":True,"path":rel_to(repo,ledger),"classification":"FIX+BUILD_SENTINEL","first_1500":ledger.read_text(encoding='utf-8',errors='replace')[:1500]}
    else:
        REPORT['warnings'].append('FACTORY_LEDGER_AGENT_GATE_NOT_FOUND')

def scan_all(repo):
    findings=[]
    for p in iter_code_files(repo):
        try:
            txt=p.read_text(encoding='utf-8',errors='replace')
        except Exception:
            continue
        rel=rel_to(repo,p)
        if p.suffix.lower() in {'.tsx','.jsx'}:
            findings.extend(scan_jsx_text(rel, txt))
        elif EVENT_BROKEN_SCAN_RE.search(txt):
            findings.extend(scan_jsx_text(rel, txt))
    return findings

def fix_all_jsx(repo):
    changes=[]
    for p in iter_code_files(repo):
        if p.suffix.lower() not in {'.tsx','.jsx'}: continue
        try: txt=p.read_text(encoding='utf-8',errors='replace')
        except Exception: continue
        fixed, changed=fix_jsx_text(txt)
        if changed and fixed != txt:
            backup_file(repo,p,'jsx_safe_autofix')
            p.write_text(fixed,encoding='utf-8',errors='replace')
            changes.append(rel_to(repo,p))
    return changes

def git_diff_check(repo):
    cp=run(['git','diff','--check'], repo)
    write(STAGE/'validation/git_diff_check.txt', cp.stdout+'\n'+cp.stderr)
    return cp.returncode==0

def try_ts_parse(repo):
    node=shutil.which('node')
    if not node:
        return {"available":False,"reason":"node_not_found","diagnostics":[]}
    js=STAGE/'validation/parse_tsx.js'
    write(js, """
const fs = require('fs');
let ts;
try { ts = require('typescript'); } catch (e) { console.log(JSON.stringify({available:false,reason:'typescript_not_requireable',diagnostics:[]})); process.exit(0); }
const root = process.argv[2];
const skip = new Set(['.git','node_modules','.next','dist','build','coverage','.turbo','.cache']);
const files=[];
function walk(d){ for(const n of fs.readdirSync(d)){ if(skip.has(n)) continue; const p=d+'/'+n; const st=fs.statSync(p); if(st.isDirectory()) walk(p); else if(/\.(tsx|jsx)$/.test(n)) files.push(p); } }
walk(root);
const diagnostics=[];
for(const file of files){ const source=fs.readFileSync(file,'utf8'); const kind=file.endsWith('.tsx')?ts.ScriptKind.TSX:ts.ScriptKind.JSX; const sf=ts.createSourceFile(file,source,ts.ScriptTarget.Latest,true,kind); for(const d of sf.parseDiagnostics||[]){ const pos=sf.getLineAndCharacterOfPosition(d.start||0); diagnostics.push({file,line:pos.line+1,column:pos.character+1,code:d.code,message:ts.flattenDiagnosticMessageText(d.messageText,'\\n')}); } }
console.log(JSON.stringify({available:true,reason:'ok',diagnostics},null,2));
""")
    cp=run([node,str(js),str(repo)], repo)
    try:
        return json.loads(cp.stdout or '{}')
    except Exception:
        return {"available":False,"reason":"parse_script_bad_output","stdout":cp.stdout,"stderr":cp.stderr,"diagnostics":[]}

def make_rollback(repo):
    manifest=STAGE/'rollback_manifest.json'
    write(manifest, json.dumps(REPORT.get('changes',[]), indent=2, ensure_ascii=False))
    ps = f"""$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Repo = '{str(repo).replace("'","''")}'
$Root = $PSScriptRoot
$Manifest = Get-Content -LiteralPath (Join-Path $Root 'rollback_manifest.json') -Raw | ConvertFrom-Json
$Trash = 'F:\\Trash-old\\{RUN_NAME} rollback'
New-Item -ItemType Directory -Force -Path $Trash | Out-Null
[array]::Reverse($Manifest)
foreach ($item in $Manifest) {{
  $Target = Join-Path $Repo $item.rel
  if ($item.existed -and $item.backup_rel) {{
    $Backup = Join-Path $Root $item.backup_rel
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
    Copy-Item -LiteralPath $Backup -Destination $Target -Force
    Write-Host "RESTORED $($item.rel)"
  }} else {{
    if (Test-Path -LiteralPath $Target) {{
      $Safe = ($item.rel -replace '[:<>"/\\|?*]', '_')
      $Dest = Join-Path $Trash $Safe
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Dest) | Out-Null
      Move-Item -LiteralPath $Target -Destination $Dest -Force
      Write-Host "MOVED_NEW_FILE_TO_TRASH $($item.rel)"
    }}
  }}
}}
Write-Host 'ROLLBACK_DONE'
"""
    write(STAGE/'ROLLBACK.ps1', ps)

def zip_stage():
    if ZIP_PATH.exists(): ZIP_PATH.unlink()
    files=[p for p in STAGE.rglob('*') if p.is_file()]
    with zipfile.ZipFile(ZIP_PATH,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,p in enumerate(files,1):
            z.write(p,p.relative_to(STAGE.parent))
            if i%100==0 or i==len(files): pct(i,len(files),f'comprimiendo {i}/{len(files)}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo')
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('--skip-install', action='store_true')
    args=ap.parse_args()
    STAGE.mkdir(parents=True,exist_ok=True)
    repo=Path(args.repo) if args.repo else detect_repo()
    repo=repo.resolve()
    app=app_root(repo)
    REPORT['repo']=str(repo); REPORT['app_root']=str(app); REPORT['fix_mode']=args.fix
    pct(1,10,'leyendo manual operativo y Factory Ledger')
    read_context(repo)
    pct(2,10,'estado git inicial')
    st=run(['git','status','--short','--branch'], repo); write(STAGE/'git/status_before.txt', st.stdout+'\n'+st.stderr)
    pct(3,10,'scan inicial repo-wide')
    before=scan_all(repo); REPORT['findings_before']=before
    pct(4,10,'instalando sentinel permanente')
    if not args.skip_install:
        REPORT['installed_files']=install_tool(repo, Path(__file__).resolve())
    pct(5,10,'aplicando autofixes seguros')
    if args.fix:
        REPORT['jsx_autofixed_files']=fix_all_jsx(repo)
        REPORT['api_gate_changes']=fix_api_gates(repo, app)
        REPORT['db_sentinel']=db_sentinel(repo, True)
    else:
        REPORT['db_sentinel']=db_sentinel(repo, False)
    pct(6,10,'scan posterior')
    after=scan_all(repo); REPORT['findings_after']=after
    routes=route_scan(app); REPORT['api_routes_after']=routes
    missing_gates=[r for r in routes if r['key'] in ('products/search','products/resolve','sales/complete') and r['exists'] and not r['has_gate']]
    missing_routes=[r for r in routes if not r['exists']]
    if after: REPORT['failures'].append(f'JSX_SENTINEL_FINDINGS_AFTER={len(after)}')
    if missing_gates: REPORT['failures'].append(f'API_GATES_STILL_MISSING={len(missing_gates)}')
    if missing_routes: REPORT['warnings'].append(f'API_ROUTES_NOT_FOUND={len(missing_routes)}')
    pct(7,10,'validando git diff --check')
    if not git_diff_check(repo): REPORT['failures'].append('GIT_DIFF_CHECK_FAILED')
    pct(8,10,'intentando TSX parse local')
    ts=try_ts_parse(repo); REPORT['typescript_parse']=ts
    if ts.get('available') and ts.get('diagnostics'):
        REPORT['failures'].append(f'TYPESCRIPT_PARSE_DIAGNOSTICS={len(ts.get("diagnostics") or [])}')
    elif not ts.get('available'):
        REPORT['warnings'].append('TYPESCRIPT_PARSE_SKIPPED:'+str(ts.get('reason')))
    pct(9,10,'generando reportes y rollback')
    if args.fix and REPORT['failures']:
        REPORT['status']='FAIL_SENTINEL_ROLLED_BACK'
        rollback_now(repo)
        st2=run(['git','status','--short','--branch'], repo); write(STAGE/'git/status_after_rollback.txt', st2.stdout+'\n'+st2.stderr)
    else:
        REPORT['status']='PASS_SENTINEL_FIXED' if args.fix else ('PASS_SENTINEL_SCAN' if not REPORT['failures'] else 'FAIL_SENTINEL_SCAN')
    st_after=run(['git','status','--short','--branch'], repo); write(STAGE/'git/status_after.txt', st_after.stdout+'\n'+st_after.stderr)
    make_rollback(repo)
    write(STAGE/'REPORT.json', json.dumps(REPORT, indent=2, ensure_ascii=False))
    md=[]
    md.append('# '+REPORT['status']+'\n')
    md.append(f"- Repo: `{repo}`")
    md.append(f"- Fix mode: `{args.fix}`")
    md.append(f"- Findings before: `{len(before)}`")
    md.append(f"- Findings after: `{len(after)}`")
    md.append(f"- Failures: `{len(REPORT['failures'])}`")
    md.append(f"- Warnings: `{len(REPORT['warnings'])}`")
    md.append('\n## Failures')
    md += [f"- `{x}`" for x in REPORT['failures']] or ['- Ninguna']
    md.append('\n## Warnings')
    md += [f"- `{x}`" for x in REPORT['warnings']] or ['- Ninguna']
    md.append('\n## API routes')
    for r in routes: md.append(f"- `{r['key']}` exists=`{r['exists']}` gate=`{r['has_gate']}` path=`{r.get('path')}`")
    md.append('\n## JSX findings after')
    if after:
        for f in after[:80]:
            md.append(f"\n### `{f['path']}` line {f['line']} `{f['type']}`\n```tsx\n{f['context']}\n```")
    else: md.append('- Ninguno')
    write(STAGE/'REPORT.md','\n'.join(md)+'\n')
    pct(10,10,'creando ZIP único')
    zip_stage()
    if REPORT['status'].startswith('PASS'):
        shutil.rmtree(STAGE, ignore_errors=True)
    print('STATUS='+REPORT['status'])
    print('ZIP_FINAL='+str(ZIP_PATH))
    print('ROLLBACK=Extrae el ZIP y ejecuta ROLLBACK.ps1 si necesitas revertir')
    if REPORT['failures']:
        sys.exit(2)

if __name__=='__main__':
    try:
        main()
    except Exception:
        STAGE.mkdir(parents=True,exist_ok=True)
        REPORT['status']='FAIL_SENTINEL_SCRIPT_ERROR'
        REPORT['failures'].append('SCRIPT_ERROR')
        write(STAGE/'ERROR.txt', traceback.format_exc())
        write(STAGE/'REPORT.json', json.dumps(REPORT, indent=2, ensure_ascii=False))
        try: make_rollback(detect_repo())
        except Exception: pass
        try: zip_stage()
        except Exception: pass
        print('STATUS=FAIL_SENTINEL_SCRIPT_ERROR')
        print('ZIP_FINAL='+str(ZIP_PATH))
        sys.exit(1)
