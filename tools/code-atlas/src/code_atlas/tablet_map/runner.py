
from __future__ import annotations
import csv
import json
import os
import re
import zipfile
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

EXCLUDES={'.git','node_modules','.next','dist','build','coverage','.turbo','out','__pycache__','.prisma_installer_backups','.prisma_backups'}
TEXT_SUFFIXES={'.ts','.tsx','.js','.jsx','.css','.scss','.sass','.json','.md','.mjs','.mts','.html'}
STATE_WORDS=['base','hover','focus-visible','focus','active','pressed','selected','disabled','loading','error','success','empty','dragging','locked','muted','warning']
KIND_HINTS={
  'button':['button','btn','cta','charge','add','pay','save','cancel'],
  'panel':['panel','card','surface','shell','drawer','modal','sheet','container'],
  'text':['text','title','label','caption','copy','price','amount','total'],
  'icon':['icon','glyph'],
  'background':['background','bg','backdrop','wallpaper','hero'],
}


def rel(root:Path,p:Path)->str:
    try: return p.relative_to(root).as_posix()
    except Exception: return str(p)

def write_text(p:Path,s:str):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')

def write_json(p:Path,o:Any): write_text(p,json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True))

def cell(v:Any)->str:
    if v is None: return ''
    if isinstance(v,(list,dict)): return json.dumps(v,ensure_ascii=False,sort_keys=True)[:30000]
    return str(v)[:30000]

def write_csv(p:Path,rows:list[dict[str,Any]]):
    p.parent.mkdir(parents=True,exist_ok=True); fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    if not fields: fields=['status']; rows=[{'status':'EMPTY'}]
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
        for r in rows: w.writerow({k:cell(r.get(k)) for k in fields})

def skip(path:Path)->bool: return bool(set(path.parts)&EXCLUDES)

def walk(root:Path,suffixes:set[str]|None=None):
    if not root.exists(): return
    for d,dirs,files in os.walk(root):
        dirs[:]=[x for x in dirs if x not in EXCLUDES and not x.startswith('.git')]
        for n in files:
            p=Path(d)/n
            if skip(p): continue
            if suffixes and p.suffix.lower() not in suffixes: continue
            yield p

def read(p:Path)->str:
    try: return p.read_bytes()[:900000].decode('utf-8','ignore')
    except Exception: return ''

def classify_surface(repo:Path,p:Path)->dict[str,Any]:
    r=rel(repo,p)
    route=''
    surface='tablet.unknown'
    is_lab=False; is_runtime=True; protected=False; eligible=False; risk='medium'
    if 'tablet-lab' in r or 'TabletLab' in p.name:
        surface='tablet.lab'; route='/tablet-lab'; is_lab=True; is_runtime=False; eligible=True; risk='low'
    elif '/pos/' in r or r.endswith('/pos/page.tsx') or 'pos-' in r.lower() or '/api/pos/' in r:
        surface='tablet.pos.real'; route='/pos'; protected=True; eligible=False; risk='critical'
    elif '/app/api/' in r:
        surface='tablet.api'; route='/api'; protected=True; eligible=False; risk='high'
    elif '/components/' in r:
        surface='tablet.components'; route='component-library'; eligible=False; risk='medium'
    return {'surfaceId':surface,'route':route,'sourceFile':r,'surfaceType':'visual-lab' if is_lab else ('operational-pos' if protected else 'tablet-code'), 'isLab':is_lab, 'isRuntime':is_runtime, 'isProtected':protected, 'canReceivePreset':eligible, 'riskLevel':risk}

def css_defs(text:str)->list[dict[str,Any]]:
    rows=[]
    for m in re.finditer(r'(^|[\s,{])\.([A-Za-z_][\w-]*)([^,{]*)\{',text,re.M):
        tail=m.group(3) or ''
        selector='.'+m.group(2)+tail.strip()
        states=[]
        for st in STATE_WORDS:
            if ':'+st in selector or st in selector.lower(): states.append(st)
        rows.append({'className':m.group(2),'selector':selector,'states':sorted(set(states)),'isGlobal':':global' in selector or 'global(' in selector})
    return rows

def css_vars(text:str)->tuple[list[str],list[str]]:
    defs=sorted(set(re.findall(r'(--[A-Za-z0-9_-]+)\s*:',text)))
    uses=sorted(set(re.findall(r'var\(\s*(--[A-Za-z0-9_-]+)',text)))
    return defs,uses

def class_uses(text:str)->list[str]:
    vals=[]
    for m in re.finditer(r'className\s*=\s*[{]([^}]+)[}]|className\s*=\s*["\']([^"\']+)',text,re.S):
        blob=(m.group(1) or m.group(2) or '')
        vals += re.findall(r'(?:styles\.|style\.)([A-Za-z_][\w-]*)',blob)
        vals += [x for x in re.findall(r'["\']([A-Za-z_][\w-]{2,})["\']',blob) if x not in {'className'}]
    return sorted(set(vals))

def infer_kind(name:str, selector:str='')->str:
    s=(name+' '+selector).lower()
    for kind,hints in KIND_HINTS.items():
        if any(h in s for h in hints): return kind
    return 'unknown'

def run_tablet_map(repo_root:str,out_root:str|None=None)->dict[str,Any]:
    repo=Path(repo_root).resolve()
    if out_root is None: out_root=str(repo/'tools/code-atlas/tablet_map/current')
    out=Path(out_root).resolve(); out.mkdir(parents=True,exist_ok=True)
    tablet=repo/'apps/terminal-de-venta-system/products/tablet'
    app=repo/'apps/terminal-de-venta-system/products/tablet/app'
    files=list(walk(tablet,TEXT_SUFFIXES))
    text_cache={p:read(p) for p in files}
    surfaces=[]; ownership=[]; selector_rows=[]; token_rows=[]; use_index={}; pos_protection=[]
    for p,t in text_cache.items():
        s=classify_surface(repo,p); surfaces.append(s)
        if p.suffix.lower() in {'.tsx','.ts','.jsx','.js'}:
            css_imports=re.findall(r'import\s+(\w+)\s+from\s+["\']([^"\']+\.module\.(?:css|scss|sass))["\']',t)
            uses=class_uses(t)
            for u in uses: use_index.setdefault(u,[]).append(rel(repo,p))
            ownership.append({'componentId':p.stem,'tsxOwner':rel(repo,p),'styleImports':[x[1] for x in css_imports],'surface':s['surfaceId'],'sharedWith':[],'risk':'safe-lab-only' if s['surfaceId']=='tablet.lab' else ('protected-operational-surface' if s['isProtected'] else 'needs-review'),'classUses':uses})
        if p.suffix.lower() in {'.css','.scss','.sass'}:
            defs,uses=css_vars(t)
            for d in defs:
                token_rows.append({'token':d,'type':infer_token_type(d),'definedIn':rel(repo,p),'usedBy':[],'legacyAlias':'','surfaceScope':s['surfaceId'],'canBePreset':s['canReceivePreset'],'zeroBehavior':infer_zero_behavior(d,t)})
            for u in uses:
                token_rows.append({'token':u,'type':infer_token_type(u),'definedIn':'','usedIn':rel(repo,p),'legacyAlias':'','surfaceScope':s['surfaceId'],'canBePreset':s['canReceivePreset'],'zeroBehavior':infer_zero_behavior(u,t)})
            for row in css_defs(t):
                cls=row['className']; kind=infer_kind(cls,row['selector']); used=use_index.get(cls,[])
                selector_rows.append({'selector':row['selector'],'className':cls,'definedIn':rel(repo,p),'usedIn':used,'surface':s['surfaceId'],'states':row['states'],'kind':kind,'isGlobal':row['isGlobal'],'isShared':len(set(used))>1,'importantCount':t.count('!important'),'classification':classify_selector(s,used,t,row)})
        if s['surfaceId']=='tablet.pos.real':
            pos_protection.append({'path':rel(repo,p),'surface':'tablet.pos.real','protected':True,'presetEligible':False,'reason':'protected-operational-surface'})
    layer_rows=[]
    for o in ownership:
        for cls in o.get('classUses',[])[:80]:
            kind=infer_kind(cls)
            layer_rows.append({'surface':o['surface'],'route':surface_route(o['surface']),'component':o['componentId'],'layer':infer_layer(cls),'role':infer_role(cls),'kind':kind,'state':'base','selector':'.'+cls,'cssVariables':tokens_for_selector(cls,selector_rows,token_rows),'sourceFile':o['tsxOwner'],'presetEligible':o['risk']=='safe-lab-only'})
    token_canonical=canonicalize_tokens(token_rows)
    state_matrix=build_state_matrix(selector_rows)
    control_matrix=build_control_matrix()
    preset_registry=build_preset_registry(layer_rows,pos_protection)
    zero_audit=build_zero_audit(token_canonical,selector_rows)
    surface_registry=dedupe_surfaces(surfaces)
    route_map=build_route_map(surface_registry,ownership)
    important_audit=[r for r in selector_rows if r.get('importantCount',0)>0]
    orphan_duplicate=[r for r in selector_rows if not r.get('usedIn') or r.get('isShared') or r.get('classification') in {'ORPHAN','RISK_SHARED','BLOCKED_POS_REAL'}]
    outputs={
      '01_SURFACE_REGISTRY.json':surface_registry,
      '02_ROUTE_COMPONENT_MAP.json':route_map,
      '03_COMPONENT_OWNERSHIP_MAP.json':ownership,
      '04_LAYER_ROLE_KIND_MAP.json':layer_rows,
      '05_SELECTOR_GRAPH.json':selector_rows,
      '07_TOKEN_GRAPH.json':token_canonical,
      '08_LEGACY_TOKEN_ALIAS_MAP.json':legacy_alias_map(token_canonical),
      '09_STATE_MATRIX.json':state_matrix,
      '10_CONTROL_APPLICABILITY_MATRIX.json':control_matrix,
      '11_PRESET_ELIGIBILITY_REGISTRY.json':preset_registry,
      '12_POS_PROTECTION_MAP.json':pos_protection,
      '13_ZERO_MEANS_ZERO_AUDIT.json':zero_audit,
    }
    for name,data in outputs.items(): write_json(out/name,data)
    write_csv(out/'06_SELECTOR_USAGE.csv',selector_rows)
    write_text(out/'14_IMPORTANT_AUDIT_FILTERED.md',md_table('Important selector audit',important_audit[:500]))
    write_text(out/'15_ORPHAN_DUPLICATE_SHARED_SELECTORS.md',md_table('Orphan/duplicate/shared selector audit',orphan_duplicate[:500]))
    write_text(out/'16_PRESET_PROMOTION_CONTRACT.md',promotion_contract())
    write_text(out/'17_CONTINUATION.md',continuation(len(files),surface_registry,selector_rows,token_canonical))
    write_text(out/'tablet_map_viewer.html',viewer(surface_registry,ownership,selector_rows,token_canonical,preset_registry,zero_audit))
    manifest={'status':'PASS_TABLET_MAP_READONLY_ATLAS_GENERATED','mode':'tablet_map','label':'Tablet Map','repo':str(repo),'filesScanned':len(files),'surfaceCount':len(surface_registry),'componentCount':len(ownership),'selectorCount':len(selector_rows),'tokenCount':len(token_canonical),'posProtectedCount':len(pos_protection),'outputs':sorted(outputs.keys())+['06_SELECTOR_USAGE.csv','14_IMPORTANT_AUDIT_FILTERED.md','15_ORPHAN_DUPLICATE_SHARED_SELECTORS.md','16_PRESET_PROMOTION_CONTRACT.md','17_CONTINUATION.md','tablet_map_viewer.html']}
    write_json(out/'TABLET_MAP_MANIFEST.json',manifest)
    result_zip=out.parent/(f'tabmap {dt.datetime.now().strftime("%d%m %H%M")} result.zip')
    with zipfile.ZipFile(result_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for p in out.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(out.parent).as_posix())
    manifest['resultZip']=str(result_zip)
    write_json(out/'TABLET_MAP_MANIFEST.json',manifest)
    return manifest

def infer_token_type(tok:str)->str:
    s=tok.lower()
    if any(x in s for x in ['color','bg','background','ink','border']): return 'color'
    if any(x in s for x in ['space','gap','pad','margin','offset']): return 'dimension.spacing'
    if any(x in s for x in ['radius','round']): return 'dimension.radius'
    if any(x in s for x in ['shadow','glow','blur','opacity','glass']): return 'effect'
    if any(x in s for x in ['font','text','line','weight']): return 'typography'
    return 'unknown'

def infer_zero_behavior(tok:str,text:str)->str:
    s=(tok+' '+text[max(0,text.find(tok)-200):text.find(tok)+400]).lower() if tok in text else tok.lower()
    if 'blur' in s or 'backdrop' in s: return 'backdrop-filter:none'
    if 'shadow' in s or 'glow' in s: return 'box-shadow:none'
    if 'border' in s: return 'border-width:0;border-color:transparent'
    if 'opacity' in s or 'alpha' in s: return 'transparent/no residual veil'
    return 'not-detected'

def classify_selector(surface,used,text,row):
    if surface['isProtected']: return 'BLOCKED_POS_REAL'
    if row.get('isGlobal'): return 'RISK_SHARED'
    if not used: return 'ORPHAN'
    if len(set(used))>1: return 'RISK_SHARED'
    if 'tabctl3' in text: return 'MERGE_TO_TOKEN'
    if surface['isLab']: return 'KEEP_LAB_ONLY'
    return 'KEEP_CANONICAL'

def infer_layer(cls:str)->str:
    s=cls.lower()
    if 'action' in s or 'button' in s or 'btn' in s: return 'Action area'
    if 'header' in s or 'title' in s: return 'Header'
    if 'price' in s or 'total' in s: return 'Numeric content'
    if 'card' in s or 'panel' in s: return 'Container'
    return 'Unclassified layer'

def infer_role(cls:str)->str:
    s=cls.lower()
    if 'add' in s: return 'Add button'
    if 'charge' in s or 'pay' in s: return 'Charge action'
    if 'price' in s or 'total' in s: return 'Price text'
    if 'card' in s: return 'Card surface'
    if 'title' in s: return 'Title text'
    return cls

def tokens_for_selector(cls,selector_rows,token_rows):
    return sorted({t['token'] for t in token_rows if t.get('surfaceScope') in {'tablet.lab','tablet.components','tablet.unknown'}})[:20]

def surface_route(surface):
    return {'tablet.lab':'/tablet-lab','tablet.pos.real':'/pos','tablet.api':'/api'}.get(surface,'')

def dedupe_surfaces(rows):
    seen={}
    for r in rows:
        sid=r['surfaceId']
        if sid not in seen: seen[sid]={k:r[k] for k in ['surfaceId','route','surfaceType','isLab','isRuntime','isProtected','canReceivePreset','riskLevel']}; seen[sid]['evidenceFiles']=[]
        if len(seen[sid]['evidenceFiles'])<80: seen[sid]['evidenceFiles'].append(r['sourceFile'])
    return list(seen.values())

def build_route_map(surfaces,ownership):
    rows=[]
    for s in surfaces:
        comps=[o['componentId'] for o in ownership if o['surface']==s['surfaceId']]
        rows.append({'surfaceId':s['surfaceId'],'route':s['route'],'componentCount':len(comps),'components':comps[:200],'protected':s['isProtected'],'presetEligible':s['canReceivePreset']})
    return rows

def canonicalize_tokens(rows):
    by={}
    for r in rows:
        tok=r.get('token')
        if not tok: continue
        item=by.setdefault(tok,{'token':tok,'type':r.get('type','unknown'),'definedIn':[],'usedIn':[],'surfaceScope':set(),'canBePreset':False,'zeroBehavior':r.get('zeroBehavior','not-detected'),'legacyAlias':''})
        if r.get('definedIn'): item['definedIn'].append(r['definedIn'])
        if r.get('usedIn'): item['usedIn'].append(r['usedIn'])
        if r.get('surfaceScope'): item['surfaceScope'].add(r['surfaceScope'])
        item['canBePreset']=item['canBePreset'] or bool(r.get('canBePreset'))
        if 'tabctl3' in tok: item['legacyAlias']=tok.replace('tabctl3','tabctl7')
    out=[]
    for item in by.values():
        item['definedIn']=sorted(set(item['definedIn']))
        item['usedIn']=sorted(set(item['usedIn']))
        item['surfaceScope']='|'.join(sorted(item['surfaceScope']))
        out.append(item)
    return sorted(out,key=lambda x:x['token'])

def legacy_alias_map(tokens):
    rows=[]
    for t in tokens:
        tok=t['token']
        if 'tabctl3' in tok:
            rows.append({'legacyToken':tok,'canonicalToken':tok.replace('tabctl3','tabctl7'),'compatBehavior':'preserve alias until saved presets migrate'})
        elif 'tabctl7' in tok:
            rows.append({'legacyToken':tok.replace('tabctl7','tabctl3'),'canonicalToken':tok,'compatBehavior':'canonical preferred'})
    return rows or [{'status':'NO_TABCTL3_TABCTL7_ALIAS_DETECTED','action':'safe to add explicit aliases when presets appear'}]

def build_state_matrix(selectors):
    by_kind={}
    for r in selectors:
        kind=r.get('kind','unknown')
        item=by_kind.setdefault(kind,set())
        for st in r.get('states') or []: item.add(st)
    req={'button':['base','hover','focus-visible','pressed','disabled'],'text':['base','muted','selected','warning','error','disabled'],'panel':['base','hover','selected','dragging','empty','locked'],'background':['base']}
    return [{'kind':k,'detectedStates':sorted(v),'requiredStates':req.get(k,['base']),'missingRecommendedStates':sorted(set(req.get(k,['base']))-set(v)),'requiredTokensByState':{'focus-visible':['outlineColor','outlineWidth','outlineOffset'],'disabled':['opacity','cursor','background']}} for k,v in sorted(by_kind.items())]

def build_control_matrix():
    return [
      {'control':'backdropBlur','label':'Blur de fondo','appliesTo':['panel','modal','background'],'blockedFor':['text','numericText','buttonText','icon'],'allowedStates':['base','hover','selected'],'zeroMeans':'remove-backdrop-filter','cssOutput':{'property':'backdrop-filter','zero':'none'}},
      {'control':'glow','label':'Glow','appliesTo':['button','panel','card'],'blockedFor':['text','numericText'],'allowedStates':['base','hover','pressed','selected'],'zeroMeans':'remove-box-shadow','cssOutput':{'property':'box-shadow','zero':'none'}},
      {'control':'radius','label':'Radio','appliesTo':['button','panel','card','input'],'blockedFor':['text','icon'],'allowedStates':['base'],'zeroMeans':'border-radius:0','cssOutput':{'property':'border-radius','zero':'0'}},
      {'control':'textColor','label':'Color de texto','appliesTo':['text','buttonText','numericText'],'blockedFor':['panel','background'],'allowedStates':['base','hover','selected','disabled'],'zeroMeans':'inherit canonical text color','cssOutput':{'property':'color','zero':'inherit'}},
      {'control':'surfaceAlpha','label':'Alpha superficie','appliesTo':['panel','card','background'],'blockedFor':['text','icon','numericText'],'allowedStates':['base','hover','selected'],'zeroMeans':'transparent with no residual veil','cssOutput':{'property':'background-color','zero':'transparent'}},
    ]

def build_preset_registry(layers,pos):
    rows=[]
    for row in layers:
        target='.'.join([row.get('surface','tablet'), row.get('component','component'), re.sub(r'[^A-Za-z0-9]+','_',row.get('role','role')).strip('_')])
        eligible=bool(row.get('presetEligible')) and row.get('surface')=='tablet.lab'
        rows.append({'targetId':target,'eligible':eligible,'allowedScopes':['this-role','same-kind-in-surface','this-layer'] if eligible else [],'blockedScopes':['global','all-tablet','pos-real'],'promotion':{'allowed':'candidate-only' if eligible else 'blocked','requires':['scope-gate','token-gate','state-gate','contrast-gate','zero-gate','rollback-gate']}})
    for p in pos[:200]: rows.append({'targetId':'tablet.pos.'+Path(p['path']).stem,'eligible':False,'reason':'protected-operational-surface','promotionRequiresExplicitUserAuthorization':True})
    return rows

def build_zero_audit(tokens,selectors):
    rows=[]
    for t in tokens:
        zb=t.get('zeroBehavior','not-detected')
        rows.append({'token':t['token'],'type':t['type'],'surfaceScope':t['surfaceScope'],'zeroBehavior':zb,'status':'PASS_ZERO_BEHAVIOR_DECLARED' if zb!='not-detected' else 'NEEDS_ZERO_BEHAVIOR_DECLARATION'})
    return rows or [{'status':'NO_TOKENS_DETECTED'}]

def md_table(title,rows):
    lines=['# '+title,'']
    if not rows: return '\n'.join(lines+['No findings.',''])
    keys=list(rows[0].keys())[:8]
    lines.append('| '+' | '.join(keys)+' |'); lines.append('| '+' | '.join(['---']*len(keys))+' |')
    for r in rows[:300]: lines.append('| '+' | '.join(str(r.get(k,''))[:120].replace('|','\\|') for k in keys)+' |')
    return '\n'.join(lines)+'\n'

def promotion_contract():
    return '''# Tablet Map Preset Promotion Contract\n\nRead-only atlas only. Presets may be promoted only after scope-gate, token-gate, state-gate, contrast-gate, zero-gate and rollback-gate. POS real is blocked by default and requires explicit user authorization.\n'''

def continuation(nfiles,surfaces,selectors,tokens):
    return f'''# Tablet Map Continuation\n\nStatus: PASS_TABLET_MAP_READONLY_ATLAS_GENERATED\nFiles scanned: {nfiles}\nSurfaces: {len(surfaces)}\nSelectors: {len(selectors)}\nTokens: {len(tokens)}\n\nNext safe step: review `11_PRESET_ELIGIBILITY_REGISTRY.json` before creating any preset sandbox.\n'''

def viewer(surfaces,ownership,selectors,tokens,presets,zero):
    data=json.dumps({'surfaces':surfaces,'components':ownership[:500],'selectors':selectors[:1000],'tokens':tokens[:1000],'presets':presets[:1000],'zero':zero[:1000]},ensure_ascii=False)
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Tablet Map</title><style>body{{font-family:system-ui;margin:24px;background:#f7f8fb;color:#121826}}.card{{background:white;border:1px solid #d8deea;border-radius:18px;padding:16px;margin:12px 0;box-shadow:0 10px 30px rgba(20,30,50,.08)}}code{{background:#eef2ff;padding:2px 6px;border-radius:8px}}pre{{white-space:pre-wrap;max-height:420px;overflow:auto}}</style></head><body><h1>Tablet Map</h1><p>Read-only Code Atlas visual/preset readiness atlas.</p><div class="card"><h2>Summary</h2><p>Surfaces: {len(surfaces)} Â· Components: {len(ownership)} Â· Selectors: {len(selectors)} Â· Tokens: {len(tokens)}</p></div><div class="card"><h2>Data</h2><pre id="data"></pre></div><script>const DATA={data};document.getElementById('data').textContent=JSON.stringify(DATA,null,2);</script></body></html>'''

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',default='.')
    ap.add_argument('--out',required=True)
    ns=ap.parse_args()
    print(json.dumps(run_tablet_map(ns.repo,ns.out),ensure_ascii=False,indent=2))
