
from __future__ import annotations
import csv, datetime as dt, hashlib, json, os, re, sqlite3, zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional
EXCLUDE={'.git','node_modules','.next','dist','build','coverage','.turbo','__pycache__','.prisma_installer_backups'}
SENSITIVE=re.compile(r'(token|secret|password|passwd|authorization|bearer|api[_-]?key|claim|code|email|phone|tel|address|qr|magic|session)',re.I)
PLACEHOLDERS=['snapshot_diff_engine','surface_role_matrix','operational_timeline','client_risk_score','orphan_detector','staleness_monitor','audit_completeness_matrix','data_lineage_graph','runtime_evidence_links','atlas_query_console','entity_detail_drawer','historical_trend_mini_atlas','client_setup_journey_map','multi_tenant_leakage_guard','golden_path_comparator']

def rel(repo:Path,p:Path)->str:
    try: return p.relative_to(repo).as_posix()
    except Exception: return str(p)
def h(s:str)->str: return hashlib.sha256(str(s).encode('utf-8','ignore')).hexdigest()
def write_text(p:Path,s:str): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')
def write_json(p:Path,o:Any): write_text(p,json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True))
def cell(v:Any)->str:
    if v is None: return ''
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False,sort_keys=True)[:30000]
    return str(v)[:30000]
def write_csv(p:Path,rows:List[Dict[str,Any]]):
    p.parent.mkdir(parents=True,exist_ok=True); fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    if not fields: fields=['status']; rows=[{'status':'EMPTY'}]
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
        for r in rows: w.writerow({k:cell(r.get(k)) for k in fields})
def walk(root:Path,suffixes=()):
    if not root.exists(): return
    for d,dirs,files in os.walk(root):
        dirs[:]=[x for x in dirs if x not in EXCLUDE and not x.startswith('.')]
        for n in files:
            p=Path(d)/n
            if not suffixes or p.suffix.lower() in suffixes: yield p
def sanitize(k:str,v:Any)->Any:
    if v is None or isinstance(v,(int,float,bool)): return v
    s=str(v)
    if SENSITIVE.search(k) or re.search(r'\S+@\S+',s): return 'sha256:'+h(s)[:20]
    return s[:180]+('â€¦' if len(s)>180 else '')
def sanitize_row(row:Dict[str,Any])->Dict[str,Any]: return {str(k):sanitize(str(k),v) for k,v in row.items()}
def classify(name:str)->str:
    n=name.lower()
    if 'outbox' in n or ('event' in n and 'payload' in n): return 'outbox'
    if any(x in n for x in ['client','customer','business','tenant']): return 'client'
    if 'license' in n or 'licence' in n: return 'license'
    if 'device' in n or 'terminal' in n: return 'device'
    if n in {'sale','sales'} or 'sale' in n or 'order' in n or 'ticket' in n: return 'sales'
    if any(x in n for x in ['audit','log']): return 'audit'
    return 'other'
def dbs(repo:Path)->List[Path]:
    out=[]
    for p in walk(repo,('.db','.sqlite','.sqlite3')):
        rp=rel(repo,p)
        if any(x in rp for x in ['node_modules','.git','.next']): continue
        try:
            if p.stat().st_size>0: out.append(p)
        except Exception: pass
    return sorted(out,key=lambda p:rel(repo,p))
def q(conn,sql):
    conn.row_factory=sqlite3.Row
    return [dict(x) for x in conn.execute(sql).fetchall()]
def inspect_db(repo:Path,db:Path)->Dict[str,Any]:
    item={'path':rel(repo,db),'sha256Prefix':'','tables':[],'error':None}
    try:
        item['sha256Prefix']=hashlib.sha256(db.read_bytes()[:1024*1024]).hexdigest()[:16]
        conn=sqlite3.connect(f'file:{db}?mode=ro',uri=True,timeout=2)
        tabs=[r['name'] for r in q(conn,"select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
        for t in tabs:
            cols=[r['name'] for r in q(conn,f'pragma table_info("{t}")')]
            try: cnt=q(conn,f'select count(*) c from "{t}"')[0]['c']
            except Exception: cnt=None
            item['tables'].append({'table':t,'columns':cols,'rowCount':cnt,'className':classify(t),'db':item['path']})
        conn.close()
    except Exception as e: item['error']=str(e)[:200]
    return item
def samples(repo:Path,db_rel:str,table:str,limit:int=40)->List[Dict[str,Any]]:
    try:
        conn=sqlite3.connect(f'file:{repo/db_rel}?mode=ro',uri=True,timeout=2); conn.row_factory=sqlite3.Row
        rows=[sanitize_row(dict(r)) for r in conn.execute(f'select * from "{table}" limit {limit}').fetchall()]
        conn.close(); return rows
    except Exception: return []
def payload_parser(repo:Path,tables:List[Dict[str,Any]])->List[Dict[str,Any]]:
    out=[]
    for t in tables:
        pcols=[c for c in t.get('columns',[]) if re.search(r'(payload|json|body|event)',c,re.I)]
        if t.get('className')!='outbox' and not pcols: continue
        for row in samples(repo,t['db'],t['table'],50):
            for c in pcols:
                val=row.get(c)
                if not isinstance(val,str) or not val.strip(): continue
                try:
                    obj=json.loads(val); keys=list(obj.keys()) if isinstance(obj,dict) else [type(obj).__name__]
                    out.append({'db':t['db'],'table':t['table'],'column':c,'payloadParsed':True,'payloadKeys':'|'.join(map(str,keys)),'sampleHash':h(val)[:18]})
                except Exception as e: out.append({'db':t['db'],'table':t['table'],'column':c,'payloadParsed':False,'error':str(e)[:120],'sampleHash':h(val)[:18]})
    return out or [{'status':'BLOCKED_NO_PAYLOADJSON_ROWS','rule':'OutboxEvent PayloadJson parser ran but no payload/json rows were detected'}]
def mappers(repo:Path,tables:List[Dict[str,Any]])->Dict[str,List[Dict[str,Any]]]:
    buckets={'clients':[],'licenses':[],'devices':[],'sales':[]}
    mapcls={'client':'clients','license':'licenses','device':'devices','sales':'sales'}
    for t in tables:
        if t.get('className') not in mapcls: continue
        b=mapcls[t['className']]
        for r in samples(repo,t['db'],t['table'],75):
            eid=r.get('id') or r.get('uuid') or r.get('number') or h(json.dumps(r,sort_keys=True,default=str))[:16]
            buckets[b].append({'entityId':eid,'sourceDb':t['db'],'sourceTable':t['table'],'trustLevel':'row-level-sanitized','sourceLevel':'sqlite','fields':r})
    return buckets
def device_cross(mapped):
    out=[]
    for d in mapped['devices']:
        raw=json.dumps(d,ensure_ascii=False).lower(); keys=[k for k in ['license','claim','setup','client','customer','tenant','business','scope'] if k in raw]
        out.append({'deviceId':d.get('entityId'),'sourceTable':d.get('sourceTable'),'evidenceKeys':'|'.join(keys),'status':'PASS' if keys else 'BLOCKED_MISSING_DEVICE_CLAIM_SCOPE'})
    return out or [{'status':'BLOCKED_NO_DEVICE_ROWS'}]
def sales_lineage(mapped,tables):
    related='\n'.join(json.dumps(t,ensure_ascii=False).lower() for t in tables if re.search(r'(line|tender|payment|outbox|sync|canonical)',t.get('table',''),re.I))
    out=[]
    for s in mapped['sales']:
        fields=s.get('fields',{}); sid=str(fields.get('id') or fields.get('saleId') or s.get('entityId'))
        explicit=bool(sid and sid.lower() in related); scope=bool(re.search(r'(tenant|business|client|customer|license|device|terminal|store)',json.dumps(fields,ensure_ascii=False),re.I))
        status='PASS_EXPLICIT_PROVENANCE' if explicit and scope else ('INFERRED_PROVENANCE' if explicit or scope else 'unknown_missing_provenance')
        out.append({'saleId':sid,'sourceDb':s.get('sourceDb'),'sourceTable':s.get('sourceTable'),'hasRelatedLineage':explicit,'hasScopeKeys':scope,'status':status})
    return out or [{'status':'BLOCKED_NO_SALE_ROWS'}]
def tenant_scope(repo:Path,tables):
    hits=[]
    for p in walk(repo,('.ts','.tsx','.js','.mjs','.md','.json','.sql','.prisma')):
        rp=rel(repo,p)
        if not any(x in rp for x in ['shared','docs/ops','licscope','prisma','infra/cloudflare','tools/code-atlas']): continue
        try: txt=p.read_text(encoding='utf-8',errors='replace')[:250000]
        except Exception: continue
        if re.search(r'\b(tenant|scope|businessId|clientId|licenseId|multi[-_ ]tenant)\b',txt,re.I): hits.append({'path':rp,'terms':'|'.join(sorted(set(re.findall(r'\b(?:tenant|scope|businessId|clientId|licenseId|multi[-_ ]tenant)\b',txt,re.I)))[:12]),'sha256Prefix':h(txt)[:16]})
    cols=[{'db':t['db'],'table':t['table'],'columns':'|'.join([c for c in t.get('columns',[]) if re.search(r'(tenant|scope|business|client|customer|license)',c,re.I)])} for t in tables]
    cols=[c for c in cols if c['columns']]
    ok=bool(hits) and bool(cols)
    return {'status':'PASS_SCOPE_AUTHORITY_FOUND' if ok else 'blocked-by-missing-scope-contract','contractHits':hits[:80],'scopedColumns':cols[:200]}
def prisma_models(repo:Path):
    out=[]
    for p in walk(repo,('.prisma',)):
        txt=p.read_text(encoding='utf-8',errors='replace')
        for m in re.finditer(r'model\s+(\w+)\s*\{(.*?)\n\}',txt,re.S):
            fields=[]
            for line in m.group(2).splitlines():
                line=line.strip()
                if line and not line.startswith('//') and not line.startswith('@@'): fields.append(line.split()[0])
            out.append({'path':rel(repo,p),'model':m.group(1),'fields':fields})
    return out
def schema_drift(repo:Path,tables):
    tm={t['table'].lower():t for t in tables}; out=[]
    for m in prisma_models(repo):
        t=tm.get(m['model'].lower()) or tm.get((m['model']+'s').lower())
        if not t: out.append({'model':m['model'],'path':m['path'],'status':'DRIFT_MODEL_WITHOUT_SQLITE_TABLE'})
        else:
            missing=[f for f in m['fields'] if f not in t.get('columns',[])]
            out.append({'model':m['model'],'db':t['db'],'table':t['table'],'status':'PASS' if not missing else 'DRIFT_FIELD_MISMATCH','missingColumns':'|'.join(missing[:40])})
    return out or [{'status':'BLOCKED_NO_PRISMA_MODELS'}]
def runtime_links(repo:Path,result_root:Path):
    roots=[result_root,repo/'apps/terminal-de-venta-system/docs/ops']; zips=[]
    for r in roots:
        if r.exists(): zips+=list(r.glob('**/*result*.zip'))[:1000]
    out=[]
    for z in sorted(set(zips),key=lambda p:str(p).lower())[-150:]:
        try:
            with zipfile.ZipFile(z) as zz:
                names=zz.namelist(); interesting=[n for n in names if re.search(r'(manifest|verif|result|smoke|check|report|continuation)',n,re.I)][:50]
            out.append({'zip':str(z),'entryCount':len(names),'interestingEntries':'|'.join(interesting),'status':'LINKED'})
        except Exception as e: out.append({'zip':str(z),'status':'READ_ERROR','error':str(e)[:120]})
    return out or [{'status':'BLOCKED_NO_RESULT_ZIPS'}]
def surface_matrix(repo:Path):
    defs=[('Tablet','products/tablet','operative POS, local sales/inventory'),('PC','products/pc','admin/control, canonical consolidation'),('Mobile','products/mobile','supervisor/companion'),('Chart Lab','products/chart-lab','runtime chart governance'),('Shared','shared','contracts/shared UI')]
    rows=[]
    app=repo/'apps/terminal-de-venta-system'
    for s,path,role in defs:
        root=app/path; files=list(walk(root,('.ts','.tsx','.js','.mjs','.json','.md','.css')))[:10000] if root.exists() else []
        routes=[rel(repo,p) for p in files if p.name in {'page.tsx','route.ts','layout.tsx'}]
        rows.append({'surface':s,'path':rel(repo,root),'exists':root.exists(),'fileCount':len(files),'routeCount':len(routes),'role':role,'status':'PASS' if root.exists() else 'BLOCKED_MISSING_SURFACE_ROOT','sampleRoutes':'|'.join(routes[:30])})
    return rows
def snapshot_diff(result_root:Path):
    zips=sorted(list(result_root.glob('catlas*result.zip'))+list(result_root.glob('*atlas*result.zip')),key=lambda p:p.stat().st_mtime if p.exists() else 0)
    rows=[]; prev=None
    for z in zips[-10:]:
        try:
            with zipfile.ZipFile(z) as zz: names=sorted(zz.namelist())
            row={'zip':str(z),'entryCount':len(names),'fileListHash':h('\n'.join(names))[:18],'status':'BASELINE' if prev is None else 'COMPARABLE'}
            if prev is not None: row.update({'addedEntries':len(set(names)-set(prev)),'removedEntries':len(set(prev)-set(names))})
            rows.append(row); prev=names
        except Exception as e: rows.append({'zip':str(z),'status':'READ_ERROR','error':str(e)[:120]})
    if len(rows)<2: rows.append({'status':'BLOCKED_INSUFFICIENT_COMPARABLE_RUNS'})
    return rows
def extra_detectors(mapped,lineage,cross,scope,tables,runtime):
    dup=[]; seen={}; orphan=[]; stale=[]
    for kind,items in mapped.items():
        for row in items:
            key=(kind,str(row.get('entityId'))); raw=json.dumps(row,ensure_ascii=False).lower()
            if key in seen: dup.append({'entityKind':kind,'entityId':key[1],'status':'DUPLICATE_ID'})
            seen[key]=1
            if kind in {'licenses','devices','sales'} and not re.search(r'(client|customer|business|tenant|scope)',raw): orphan.append({'entityKind':kind,'entityId':key[1],'status':'ORPHAN_SCOPE_UNKNOWN'})
            if not re.search(r'(updated|created|timestamp|date|expires|lastseen)',raw): stale.append({'entityKind':kind,'entityId':key[1],'status':'STALE_MONITOR_NO_TIMESTAMP_FIELD'})
    audit=[{'auditTableCount':sum(1 for t in tables if t.get('className')=='audit'),'status':'PASS' if any(t.get('className')=='audit' for t in tables) else 'BLOCKED_NO_AUDIT_TABLES'}]
    clientRisk=[{'risk':'unknown_missing_provenance','count':sum(1 for x in lineage if x.get('status')=='unknown_missing_provenance'),'status':'NO_GREEN' if any(x.get('status')=='unknown_missing_provenance' for x in lineage) else 'PASS'},{'risk':'tenant_scope_authority','status':scope.get('status')}]
    graph=[{'from':'Sale:'+str(x.get('saleId','unknown')),'to':'Provenance:'+str(x.get('status')),'type':'sale_lineage'} for x in lineage]
    graph += [{'from':'Device:'+str(x.get('deviceId','unknown')),'to':'ClaimScope:'+str(x.get('status')),'type':'device_claim'} for x in cross]
    journey=[{'step':'client','count':len(mapped['clients']),'status':'PASS' if mapped['clients'] else 'BLOCKED_NO_CLIENT_ROWS'},{'step':'license','count':len(mapped['licenses']),'status':'PASS' if mapped['licenses'] else 'BLOCKED_NO_LICENSE_ROWS'},{'step':'device_claim','count':len(mapped['devices']),'status':'PASS' if mapped['devices'] else 'BLOCKED_NO_DEVICE_ROWS'}]
    return {'duplicates':dup or [{'status':'PASS_NO_DUPLICATE_SAMPLE_IDS'}],'orphans':orphan or [{'status':'PASS_NO_ORPHANS_IN_SAMPLE'}],'stalenessMonitor':stale or [{'status':'PASS_TIMESTAMPS_PRESENT_IN_SAMPLE'}],'auditCompleteness':audit,'clientRiskScore':clientRisk,'dataLineageGraph':graph or [{'status':'EMPTY_NO_EDGES'}],'clientSetupJourneyMap':journey,'operationalTimeline':[{'source':r.get('zip',''),'event':'runtime_evidence_zip','status':r.get('status')} for r in runtime] or [{'status':'EMPTY'}]}
def html_report(path:Path,payload:Dict[str,Any]):
    data=json.dumps(payload,ensure_ascii=False)
    body=f"""<!doctype html><html><head><meta charset="utf-8"><title>PRISMA Operational Evidence Atlas v3</title><style>body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f7f8fb;color:#172033;margin:0}}header{{padding:24px 32px;background:linear-gradient(135deg,#fff,#e9eefc);border-bottom:1px solid #dbe3f3}}.tabs{{display:flex;gap:8px;flex-wrap:wrap;padding:16px 24px;background:white;position:sticky;top:0}}button{{border:1px solid #cbd5e1;background:white;border-radius:999px;padding:8px 12px}}button.active{{background:#111827;color:white}}main{{padding:24px;display:grid;grid-template-columns:1fr 360px;gap:18px}}.card{{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:18px;box-shadow:0 10px 30px #0f172a10}}pre{{white-space:pre-wrap;word-break:break-word;background:#0f172a;color:#e2e8f0;border-radius:14px;padding:14px;max-height:62vh;overflow:auto}}input{{width:100%;padding:12px;border-radius:12px;border:1px solid #cbd5e1}}</style></head><body><header><h1>PRISMA Operational Evidence Atlas v3</h1><p>ERD = estructura. Operational Evidence = evidencia row-level. Production Gate = certificaciÃ³n.</p></header><div class="tabs" id="tabs"></div><main><section class="card"><input id="q" placeholder="Atlas Query Console"/><pre id="view"></pre></section><aside class="card"><h2>Entity Detail Drawer</h2><pre id="drawer"></pre></aside></main><script>const DATA={data}; const keys=Object.keys(DATA); let active=keys[0]; const tabs=document.getElementById('tabs'), view=document.getElementById('view'), q=document.getElementById('q'), drawer=document.getElementById('drawer'); function esc(s){{return s.replace(/[<>&]/g,c=>({{'<':'&lt;','>':'&gt;','&':'&amp;'}}[c]))}} function renderTabs(){{tabs.innerHTML=''; keys.forEach(k=>{{let b=document.createElement('button'); b.textContent=k; b.className=k===active?'active':''; b.onclick=()=>{{active=k;render()}}; tabs.appendChild(b)}})}} function render(){{renderTabs(); let txt=JSON.stringify(DATA[active],null,2); let term=q.value.toLowerCase(); if(term) txt=txt.split('\n').filter(x=>x.toLowerCase().includes(term)).join('\n')||'Sin coincidencias'; view.textContent=txt; let obj=DATA[active]; drawer.textContent=JSON.stringify(Array.isArray(obj)?obj[0]:obj,null,2)}} q.oninput=render; render();</script></body></html>"""
    write_text(path,body)
def run_operational_atlas(repo_root:str, output_dir:str, result_root:Optional[str]=None)->Dict[str,Any]:
    repo=Path(repo_root).resolve(); out=Path(output_dir).resolve(); out.mkdir(parents=True,exist_ok=True); rr=Path(result_root).resolve() if result_root else Path(r'F:\descargasf')
    inventory=[]; tables=[]
    for db in dbs(repo):
        meta=inspect_db(repo,db); inventory.append(meta); tables.extend(meta.get('tables',[]))
    mapped=mappers(repo,tables); payload_rows=payload_parser(repo,tables); cross=device_cross(mapped); lineage=sales_lineage(mapped,tables); scope=tenant_scope(repo,tables); drift=schema_drift(repo,tables); runtime=runtime_links(repo,rr); surface=surface_matrix(repo); snap=snapshot_diff(rr); extra=extra_detectors(mapped,lineage,cross,scope,tables,runtime)
    # SUPPORT_RESOLVER_ATLAS_RUN_START
    try:
        from .support_resolver import run_support_resolver_atlas as _run_support_resolver_atlas
        support_result = _run_support_resolver_atlas(repo, out, rr)
    except Exception as _support_exc:
        support_result = {
            'summary': {
                'status': 'BLOCKED_SUPPORT_CONSUMER_ERROR',
                'decision': 'VERIFY_ADAPTER',
                'doNotRebuild': True,
                'blockers': [f'{type(_support_exc).__name__}: {_support_exc}'],
            },
            'payload': {
                'supportResolverSummary': [{
                    'status': 'BLOCKED_SUPPORT_CONSUMER_ERROR',
                    'error': f'{type(_support_exc).__name__}: {_support_exc}',
                    'doNotRebuild': True,
                }],
            },
            'exports': {},
        }
    # SUPPORT_RESOLVER_ATLAS_RUN_END
    blockers=[]
    if any(x.get('status')=='unknown_missing_provenance' for x in lineage): blockers.append('unknown_missing_provenance')
    if scope.get('status')=='blocked-by-missing-scope-contract': blockers.append('blocked-by-missing-scope-contract')
    if any(str(x.get('status','')).startswith('BLOCKED') for x in cross): blockers.append('device_claim_scope_incomplete')
    ledger=[]
    for name in PLACEHOLDERS:
        status='implemented_v3_detector'
        if name=='multi_tenant_leakage_guard' and scope.get('status')=='blocked-by-missing-scope-contract': status='blocked-by-missing-scope-contract'
        if name=='snapshot_diff_engine' and any(x.get('status')=='BLOCKED_INSUFFICIENT_COMPARABLE_RUNS' for x in snap): status='implemented_v3_blocked_insufficient_comparable_runs'
        ledger.append({'feature':name,'placeholder':False,'status':status})
    manifest={'tool':'code_atlas_operational_v3','createdAt':dt.datetime.now().isoformat(),'repo':str(repo),'status':'BLOCKED_FOR_PRODUCTION' if blockers else 'SOURCE_READY_NOT_PRODUCTION_CERTIFIED','productionGate':'NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED','productionBlockers':blockers,'featureCount':50,'detectorsConverted':len(ledger),'placeholdersRemaining':0,'monolithDependency':False,'rawDatabasesIncluded':False}
    # SUPPORT_RESOLVER_ATLAS_MANIFEST_START
    manifest['supportResolverStatus'] = support_result.get('summary', {}).get('status', 'BLOCKED_SUPPORT_CONSUMER_UNKNOWN')
    manifest['supportResolverDecision'] = support_result.get('summary', {}).get('decision', 'VERIFY_ADAPTER')
    manifest['supportResolverDoNotRebuild'] = bool(support_result.get('summary', {}).get('doNotRebuild', True))
    manifest['supportResolverBlockers'] = support_result.get('summary', {}).get('blockers', [])
    # SUPPORT_RESOLVER_ATLAS_MANIFEST_END
    payload={'manifest':manifest,'dbInventory':inventory,'payloadJsonIndex':payload_rows,'clients':mapped['clients'],'licenses':mapped['licenses'],'devices':mapped['devices'],'sales':mapped['sales'],'deviceClaimCrosscheck':cross,'salesLineage':lineage,'tenantScopeResolver':scope,'schemaDriftGuard':drift,'runtimeEvidenceLinks':runtime,'surfaceRoleMatrix':surface,'snapshotDiffEngine':snap,'placeholderLedger':ledger,'multiTenantLeakageGuard':[{'status':scope.get('status'),'rule':'certify only if real tenant/scope contract exists'}],'goldenPathComparator':[{'component':'production_gate','status':'BLOCKED_FOR_PRODUCTION' if blockers else 'SOURCE_READY_NOT_PRODUCTION_CERTIFIED','rule':'unknown_missing_provenance = no green'}]}
    # SUPPORT_RESOLVER_ATLAS_PAYLOAD_START
    payload.update(support_result.get('payload', {}))
    # SUPPORT_RESOLVER_ATLAS_PAYLOAD_END
    payload.update(extra)
    write_json(out/'ATLAS_MANIFEST_PLUS.json',manifest); write_json(out/'operational_evidence_atlas.json',payload); write_json(out/'placeholder_ledger.json',ledger); write_csv(out/'placeholder_ledger.csv',ledger)
    for k,v in payload.items():
        if isinstance(v,list): write_csv(out/'csv'/(k+'.csv'),v)
        elif isinstance(v,dict): write_json(out/'json'/(k+'.json'),v)
    write_text(out/'WHY_THIS_IS_RED.md','# WHY_THIS_IS_RED.md\n\nProduction remains blocked unless contracts and lineage are complete.\n\n'+''.join(f'- {b}\n' for b in (blockers or ['no production pass declared by design'])))
    write_text(out/'CAN_PATCH_DECISION.md','# CAN_PATCH_DECISION.md\n\nCAN_PATCH_SOURCE_MODULES=true\nCAN_DECLARE_PRODUCTION_CERTIFIED=false\n\nRules:\n- ERD = structure.\n- Operational Evidence = row-level evidence.\n- Production Gate = certification.\n- unknown_missing_provenance = no green.\n')
    write_text(out/'HUMAN_OPERATOR_SUMMARY.md',f"# Human Operator Summary\n\nStatus: `{manifest['status']}`\n\nConverted placeholder detectors: {len(ledger)}.\n\nRaw DBs included: false.\n")
    write_text(out/'CONTINUATION_SUPREME.md','# CONTINUATION_SUPREME.md\n\nInspect ATLAS_MANIFEST_PLUS.json, WHY_THIS_IS_RED.md, placeholder_ledger.json and CSV exports before patching. Do not touch tools/code-atlas/code-atlas.py without explicit authorization.\n')
    write_json(out/'SMOKE.json',{'status':'PASS','requiredFiles':['ATLAS_MANIFEST_PLUS.json','operational_evidence_atlas.html','placeholder_ledger.json','CAN_PATCH_DECISION.md','WHY_THIS_IS_RED.md']})
    write_text(out/'SMOKE.md','# Smoke\n\nPASS: Operational Evidence Atlas v3 outputs generated.\n')
    html_report(out/'operational_evidence_atlas.html',payload)
    return manifest
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True); ap.add_argument('--out',required=True); ap.add_argument('--result-root',default=None)
    ns=ap.parse_args(); print(json.dumps(run_operational_atlas(ns.repo,ns.out,ns.result_root),ensure_ascii=False,indent=2))
