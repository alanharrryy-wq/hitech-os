from __future__ import annotations
import csv, html, json, os, re, sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from .features50 import FEATURE_SPECS
from .contracts import CONTRACTS, contracts_as_dicts

def iso_now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def rel(p: Path, root: Path):
    try: return str(p.resolve().relative_to(root.resolve())).replace('\\','/')
    except Exception: return str(p)
def write_json(p: Path, data: Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); return p
def write_csv(p: Path, rows: list[dict[str,Any]]):
    p.parent.mkdir(parents=True,exist_ok=True); keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys or ['empty']); w.writeheader(); w.writerows(rows)
    return p
def write_md(p: Path, title: str, rows: Any, note: str=''):
    p.parent.mkdir(parents=True,exist_ok=True); lines=[f'# {title}','',f'Generated: {iso_now()}','']
    if note: lines += [note,'']
    if isinstance(rows,dict):
        for k,v in rows.items(): lines.append(f'- **{k}**: `{v}`')
    elif isinstance(rows,list) and rows and isinstance(rows[0],dict):
        keys=[]
        for r in rows:
            for k in r:
                if k not in keys: keys.append(k)
        lines.append('| '+' | '.join(keys)+' |'); lines.append('| '+' | '.join(['---']*len(keys))+' |')
        for r in rows: lines.append('| '+' | '.join(str(r.get(k,''))[:500].replace('\n',' ') for k in keys)+' |')
    elif isinstance(rows,list):
        lines += [f'- {x}' for x in rows]
    else: lines.append(str(rows))
    p.write_text('\n'.join(lines)+'\n',encoding='utf-8'); return p
def export(out: Path, stem: str, rows: list[dict[str,Any]], title: str, note: str=''):
    return {'csv':str(write_csv(out/f'{stem}.csv',rows)),'json':str(write_json(out/f'{stem}.json',rows)),'md':str(write_md(out/f'{stem}.md',title,rows,note))}
def export_doc(out: Path, stem: str, data: Any, title: str, note: str=''):
    return {'json':str(write_json(out/f'{stem}.json',data)),'md':str(write_md(out/f'{stem}.md',title,data,note))}
def redact(v: Any):
    if v is None or isinstance(v,(int,float,bool)): return v
    s=str(v)
    if len(s)>160: s=s[:157]+'...'
    if re.search(r'(?i)(token|secret|password|bearer|api[_-]?key)',s): return '<REDACTED_SECRET_LIKE_VALUE>'
    if re.search(r'[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}',s,re.I): return '<REDACTED_EMAIL>'
    return s
def find_dbs(root: Path):
    bad={'node_modules','.git','.next','dist','build','coverage','__pycache__','.prisma_installer_backups'}; out=[]
    for cur,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in bad]
        for n in files:
            p=Path(cur)/n
            if p.suffix.lower() in {'.db','.sqlite','.sqlite3'}: out.append(p)
            if len(out)>=40: return out
    return out
def inspect_db(path: Path, root: Path, max_rows:int):
    info={'path':str(path),'relative_path':rel(path,root),'ok':False,'tables':{},'error':''}
    try:
        con=sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True,timeout=2); con.row_factory=sqlite3.Row
        for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            t=str(r[0]); cols=[]
            for c in con.execute(f'PRAGMA table_info("{t}")'): cols.append({'name':c[1],'type':c[2],'notnull':bool(c[3]),'pk':bool(c[5])})
            try: cnt=int(con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0])
            except Exception: cnt=None
            samples=[]
            if max_rows>0:
                try: samples=[{k:redact(v) for k,v in dict(x).items()} for x in con.execute(f'SELECT * FROM "{t}" LIMIT ?',(max_rows,)).fetchall()]
                except Exception: samples=[]
            info['tables'][t]={'columns':cols,'row_count':cnt,'sample_rows':samples,'database':info['relative_path']}
        con.close(); info['ok']=True
    except Exception as e: info['error']=f'{type(e).__name__}: {e}'
    return info
def flatten(dbs):
    tables={}
    for db in dbs:
        for t,m in db.get('tables',{}).items(): tables.setdefault(t.lower(),dict(m,table_name=t))
    return tables
def cols(meta): return {str(c.get('name','')).lower() for c in meta.get('columns',[])}
def find_table(contract,tables):
    aliases=[x.lower() for x in contract.tables]+[contract.entity.lower()]
    for k,m in tables.items():
        compact=k.replace('_','')
        if k in aliases or any(a.replace('_','') in compact or compact in a.replace('_','') for a in aliases): return m.get('table_name',k),m
    return '',None
def has_field(name, columns):
    compact={c.replace('_',''):c for c in columns}; n=name.lower(); return (n in columns) or (n.replace('_','') in compact)
def contract_coverage(tables):
    rows=[]; blockers=[]
    for c in CONTRACTS:
        tn,meta=find_table(c,tables); columns=cols(meta or {}) if meta else set()
        if not meta and c.production_blocking: blockers.append(f'{c.entity}::table MISSING_TABLE')
        for f in c.required_fields:
            ok=bool(meta) and has_field(f,columns); st='PRESENT' if ok else 'MISSING_FIELD'
            if not ok and c.production_blocking: blockers.append(f'{c.entity}::{f} MISSING_FIELD')
            rows.append({'entity':c.entity,'table':tn,'field':f,'required':True,'status':st,'sourceLevel':'db_schema' if meta else 'placeholder'})
        for f in c.optional_fields:
            ok=bool(meta) and has_field(f,columns); rows.append({'entity':c.entity,'table':tn,'field':f,'required':False,'status':'PRESENT' if ok else 'OPTIONAL_MISSING','sourceLevel':'db_schema' if meta else 'placeholder'})
    return rows, list(dict.fromkeys(blockers))
def sample_rows(tables):
    out=[]
    for c in CONTRACTS:
        tn,meta=find_table(c,tables)
        if not meta: out.append({'entity':c.entity,'table':'','rowId':'','status':'PLACEHOLDER_PENDING_TABLE','sourceLevel':'placeholder','sample':''}); continue
        sm=meta.get('sample_rows') or []
        if not sm: out.append({'entity':c.entity,'table':tn,'rowId':'<aggregate>','status':'NO_SAMPLE_ROWS','sourceLevel':'db_schema','sample':''}); continue
        for i,r in enumerate(sm,1): out.append({'entity':c.entity,'table':tn,'rowId':r.get('id') or r.get('deviceId') or r.get('saleId') or f'sample_{i}','status':'SAMPLED_SANITIZED','sourceLevel':'db_sample','sample':json.dumps(r,ensure_ascii=False)})
    return out
def scan_files(root: Path, needles: tuple[str,...], exts: set[str], limit=1200):
    bad={'node_modules','.git','.next','dist','build','coverage','__pycache__'}; rows=[]
    for cur,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in bad]
        for n in files:
            p=Path(cur)/n; low=str(p).lower()
            if p.suffix.lower() in exts and any(x in low for x in needles): rows.append({'file':rel(p,root),'status':'DETECTED','sourceLevel':'file_path'})
            if len(rows)>=limit: return rows
    return rows
def build_html(out, manifest, feature_rows):
    cards=''.join(f"<article class='card'><h3>{html.escape(r['title'])}</h3><b>{html.escape(r['status'])}</b><p>{html.escape(r['note'])}</p></article>" for r in feature_rows)
    doc=f"""<!doctype html><meta charset='utf-8'><title>Operational Evidence Atlas 50</title><style>body{{margin:0;background:#07090d;color:#eef;font-family:Segoe UI,system-ui,sans-serif}}main{{padding:24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}.card,pre{{border:1px solid rgba(255,255,255,.16);border-radius:16px;padding:16px;background:rgba(255,255,255,.06)}}input{{width:100%;padding:12px;margin:12px 0;background:#111827;color:#fff;border:1px solid #334;border-radius:12px}}</style><main><h1>Operational Evidence Atlas 50</h1><p>Production: <b>{html.escape(str(manifest.get('production_readiness')))}</b>. Certified: <b>{manifest.get('production_certified')}</b>.</p><p>Placeholders are explicit. No fake green.</p><input id='q' placeholder='buscar'><section class='grid'>{cards}</section><h2>Manifest</h2><pre>{html.escape(json.dumps(manifest,ensure_ascii=False,indent=2))}</pre><script>q.oninput=()=>{{s=q.value.toLowerCase();document.querySelectorAll('.card').forEach(c=>c.style.display=c.textContent.toLowerCase().includes(s)?'':'none')}}</script></main>"""
    p=out/'operational_evidence_atlas.html'; p.write_text(doc,encoding='utf-8'); return p
def run_operational_evidence(project_root: str|Path, output_dir: str|Path, *, max_sample_rows:int=5, strict_production:bool=False, include_placeholders:bool=True):
    root=Path(project_root).resolve(); out=Path(output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    dbs=[inspect_db(p,root,max_sample_rows) for p in find_dbs(root)]; tables=flatten(dbs)
    cov, blockers=contract_coverage(tables)
    if any('sale::originDeviceId' in b for b in blockers): blockers.append('sales_lineage unknown_missing_provenance = no production green')
    if any(b.startswith('tenant::') or b.startswith('business::tenantId') for b in blockers): blockers.append('multi_tenant_leakage_guard blocked-by-missing-scope-contract')
    placeholders=[f['id'] for f in FEATURE_SPECS if 'placeholder' in f['status']] if include_placeholders else []
    production_certified=False; status='BLOCKED_FOR_PRODUCTION' if blockers or placeholders else 'PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED'
    production_certified=status.startswith('PASS_PRODUCTION')
    rows=sample_rows(tables)
    fixture_words=('demo','dummy','seed','test','mock','prueba','pilot','piloto','fixture')
    fixture=[{'entity':r['entity'],'table':r['table'],'rowId':r['rowId'],'status':'POSSIBLE_FIXTURE_WORD','word':w,'sourceLevel':r['sourceLevel']} for r in rows for w in fixture_words if w in str(r.get('sample','')).lower()] or [{'entity':'all','status':'NO_FIXTURE_WORDS_IN_SAMPLES','sourceLevel':'db_sample'}]
    verifiers=scan_files(root,('verify','test','spec','playwright','mamastrophic'),{'.mjs','.js','.ts','.tsx','.py'}) or [{'file':'','status':'PLACEHOLDER_NO_VERIFIER_FILES_DETECTED','sourceLevel':'placeholder'}]
    apis=scan_files(root,('/api/','route.ts','route.js'),{'.js','.jsx','.ts','.tsx'}) or [{'file':'','status':'PLACEHOLDER_NO_API_ROUTES_DETECTED','sourceLevel':'placeholder'}]
    feature_rows=[dict(f,sourceLevel='feature_registry') for f in FEATURE_SPECS]
    exports={}
    exports['FEATURE_REGISTRY_50']=export(out,'FEATURE_REGISTRY_50',feature_rows,'Feature Registry 50')
    exports['PLACEHOLDER_LEDGER']=export(out,'PLACEHOLDER_LEDGER',[r for r in feature_rows if 'placeholder' in r['status']],'Placeholder Ledger','Every placeholder is marked for replacement.')
    exports['OPERATIONAL_CONTRACTS']=export_doc(out,'OPERATIONAL_CONTRACTS',contracts_as_dicts(),'Operational Contracts')
    exports['SQLITE_DISCOVERY']=export_doc(out,'SQLITE_DISCOVERY',dbs,'SQLite Discovery')
    data={
      'OPERATIONAL_EVIDENCE_ATLAS_ROW_LEVEL':rows,'CLIENT_OPERATIONS_MATRIX':[r for r in rows if r['entity'] in {'client','business','license','device','store'}],'DEVICE_CLAIM_CROSSCHECK':[r for r in rows if r['entity'] in {'device','license','sync_checkpoint','sale','outbox'}],
      'SALES_LINEAGE_MATRIX':[r for r in rows if r['entity'] in {'sale','sale_line','tender','outbox','canonical_projection'}],'FLOW_HEALTH_MAP':[{'area':'sqlite','status':'PASS' if dbs else 'WARN_NO_SQLITE','count':len(dbs)},{'area':'contracts','status':'BLOCKED' if blockers else 'PASS','count':len(cov)},{'area':'placeholders','status':'PLACEHOLDER' if placeholders else 'PASS','count':len(placeholders)}],
      'BREAKAGE_RADAR':[{'severity':'BLOCKER','code':b,'status':'BLOCKED'} for b in blockers] or [{'severity':'INFO','code':'no_breakage_detected','status':'PASS'}], 'CONTRACT_COVERAGE_MATRIX':cov,
      'CUSTOMER_VISIBLE_SCAN':fixture,'FIXTURE_CONTAMINATION_SCAN':fixture,'VERIFIER_COVERAGE_MAP':verifiers,'API_DATA_MAP':apis,
      'PRODUCTION_GATE_READINESS':[{'status':status,'productionCertified':production_certified,'blockers':len(blockers),'placeholders':len(placeholders)}],
      'WHY_THIS_IS_RED':[{'rule':'No PASS with unknown_missing_provenance, missing tenant/scope, or placeholders.','status':status,'blockers':'; '.join(blockers[:20])}],
      'CAN_PATCH_DECISION':[{'decision':'YES_SAFE_TO_PATCH_SRC_ONLY','blocked':'tools/code-atlas/code-atlas.py, apps/**, ports, Prisma hot'}],
      'CONTINUATION_SUPREME':[{'next':'Replace PLACEHOLDER_LEDGER items with real mappers in src/code_atlas/operational only.'}],
      'DO_NOT_TOUCH_MAP':[{'path':'tools/code-atlas/code-atlas.py','status':'DO_NOT_TOUCH'},{'path':'apps/**','status':'OUT_OF_SCOPE'}],
      'SAFE_SCOPE_GUARD':[{'path':'tools/code-atlas/src/code_atlas/operational/**','status':'PATCHABLE'}],
      'DATA_QUALITY_RULESET':[{'rule':'unknown_missing_provenance=no_green','status':'ACTIVE'},{'rule':'tenant_scope_required_for_leakage_green','status':'ACTIVE'}],
      'RECONCILIATION_RECIPES':[{'problem':b,'recipe':'Implement contract/mapper in src-only; rerun operational smoke.'} for b in blockers[:50]] or [{'problem':'none','recipe':'no blocker recipe'}],
      'ALERT_RULES_EXPORT':[{'alert':'production_gate_blocked','severity':'P0'},{'alert':'secret_like_output','severity':'P0'}],
      'PII_PRIVACY_CLASSIFIER':[{'field':'email/name/phone/token','policy':'redact sampled values'}],
      'RELEASE_READINESS_MATRIX':[{'gate':'production','status':status,'certified':production_certified}],
      'SUPPORT_TICKET_DRAFTS':[{'title':'Code Atlas production gate blocked','body':b} for b in blockers[:25]],
    }
    # Fill all missing feature outputs as marked placeholders or small docs.
    stems={fid: fid.upper() for fid,_,_ in []}
    mapping={
      'snapshot_diff_engine':'SNAPSHOT_DIFF_ENGINE','surface_role_matrix':'SURFACE_ROLE_MATRIX','operational_timeline':'OPERATIONAL_TIMELINE','client_risk_score':'CLIENT_RISK_SCORE','next_best_action_engine':'NEXT_BEST_ACTIONS','orphan_detector':'ORPHAN_ENTITY_MATRIX','duplicate_detector':'DUPLICATE_RISK_MATRIX','staleness_monitor':'STALE_DATA_MATRIX','schema_drift_guard':'SCHEMA_DRIFT_GUARD','audit_completeness_matrix':'AUDIT_COMPLETENESS_MATRIX','data_lineage_graph':'DATA_LINEAGE_GRAPH','impact_radius_calculator':'IMPACT_RADIUS_CALCULATOR','safe_fix_recommendation_map':'SAFE_FIX_RECOMMENDATION_MAP','runtime_evidence_links':'RUNTIME_EVIDENCE_LINKS','secret_exposure_guard':'SECRET_EXPOSURE_GUARD','human_operator_summary':'OPERATOR_SUMMARY','machine_continuation_pack':'CONTINUATION_SUPREME','atlas_query_console':'ATLAS_QUERY_CONSOLE','entity_detail_drawer':'ENTITY_DETAIL_DRAWER','evidence_confidence_score':'EVIDENCE_CONFIDENCE_SCORE','ownership_map':'OWNERSHIP_MAP','evidence_bundle_index':'EVIDENCE_BUNDLE_INDEX','historical_trend_mini_atlas':'HISTORICAL_TREND_MINI_ATLAS','trust_source_level_per_datum':'TRUST_SOURCE_LEVEL_PER_DATUM','atlas_manifest_plus':'ATLAS_MANIFEST_PLUS','client_setup_journey_map':'CLIENT_SETUP_JOURNEY_MAP','multi_tenant_leakage_guard':'MULTI_TENANT_LEAKAGE_GUARD','golden_path_comparator':'GOLDEN_PATH_COMPARATOR'}
    for fid,stem in mapping.items():
        data.setdefault(stem,[{'featureId':fid,'status':'PLACEHOLDER_MARKED' if fid in placeholders else 'REGISTERED','note':'placeholder marked; replace with real evidence when available','sourceLevel':'placeholder'}])
    for stem,rs in data.items(): exports[stem]=export(out,stem,rs,stem.replace('_',' ').title())
    manifest={'kind':'operational_evidence_atlas_50_v1','created_at':iso_now(),'project_root':str(root),'output_dir':str(out),'src_only':True,'monolith_touched':False,'feature_count':len(FEATURE_SPECS),'placeholder_count':len(placeholders),'production_readiness':status,'production_certified':production_certified,'blockers':blockers,'sqlite_database_count':len(dbs),'sqlite_table_count':len(tables),'features':FEATURE_SPECS,'exports':exports}
    write_json(out/'ATLAS_MANIFEST_PLUS.json',manifest); html_path=build_html(out,manifest,feature_rows); manifest['exports']['operational_evidence_atlas_html']=str(html_path); write_json(out/'ATLAS_MANIFEST_PLUS.json',manifest)
    # final evidence index after manifest/html exists
    idx=[]
    for p in sorted(out.glob('*')):
        if p.is_file(): idx.append({'file':p.name,'sizeBytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'EXPORTED'})
    exports['EVIDENCE_BUNDLE_INDEX']=export(out,'EVIDENCE_BUNDLE_INDEX',idx,'Evidence Bundle Index'); write_json(out/'ATLAS_MANIFEST_PLUS.json',manifest)
    return manifest
run_operational_evidence_atlas=run_operational_evidence
run=run_operational_evidence
