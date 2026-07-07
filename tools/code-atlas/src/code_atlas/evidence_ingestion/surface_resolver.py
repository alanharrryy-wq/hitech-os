# -*- coding: utf-8 -*-
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any, Dict, List
ROLE_RULES=[('PC',[r'products[\\/]pc[\\/]',r'apps[\\/]terminal-de-venta-system[\\/]products[\\/]pc']),('Tablet',[r'products[\\/]tablet[\\/]',r'apps[\\/]terminal-de-venta-system[\\/]products[\\/]tablet']),('Mobile',[r'products[\\/]mobile[\\/]',r'apps[\\/]terminal-de-venta-system[\\/]products[\\/]mobile']),('Cloud Center',[r'cloud',r'worker',r'wrangler',r'd1',r'cloudflare',r'cloud-center',r'control-center']),('Licensing',[r'licens',r'licctx',r'licflow',r'lickey',r'license']),('Shared UI',[r'products[\\/]shared-ui',r'shared-ui']),('Shared Core',[r'shared[\\/](contracts|licensing|twin-kernel)',r'shared[\\/]']),('Visual',[r'prisma-visual-os',r'visual',r'styles[\\/]prisma',r'glass',r'liquid']),('Governor/Authority',[r'authority',r'govern',r'factory ledger',r'Factory Ledger',r'ledger',r'mesh']),('DB',[r'prisma',r'migration',r'seed',r'sqlite',r'database',r'schema']),('Docs',[r'docs[\\/]',r'\\.md$',r'manual',r'runbook',r'atlas[\\/]_incoming']),('Tests/Verifiers',[r'test',r'verify',r'smoke',r'spec',r'e2e']),('Productization',[r'productization',r'release',r'bundle',r'distribut']),('Tooling',[r'tools[\\/]',r'scripts[\\/]',r'bin[\\/]'])]
def load_json(path:Path,default=None):
    try: return json.loads(path.read_text(encoding='utf-8', errors='replace'))
    except Exception: return {} if default is None else default
def classify_path(path:str)->str:
    p=str(path).replace('\\\\','/')
    for role,patterns in ROLE_RULES:
        for pat in patterns:
            if re.search(pat,p,re.I): return role
    return 'Unknown'
def collect_path_strings(obj:Any,out:List[str],limit:int=20000):
    if len(out)>=limit: return
    if isinstance(obj,dict):
        for k,v in obj.items():
            if isinstance(v,str) and ('/' in v or '\\\\' in v or '.' in v): out.append(v)
            elif isinstance(v,(dict,list)): collect_path_strings(v,out,limit)
    elif isinstance(obj,list):
        for v in obj: collect_path_strings(v,out,limit)
    elif isinstance(obj,str) and ('/' in obj or '\\\\' in obj): out.append(obj)
def build_surface_aware_index(repo_root:Path,registers_dir:Path)->Dict[str,Any]:
    sources=[load_json(registers_dir/n,{}) for n in ['PATH_ROLE_INDEX.json','ATLAS_COVERAGE_GAP_REGISTER.json','IMPORTANT_ENTRYPOINTS_REGISTER.json','TREE_INVENTORY.json']]
    strings=[]
    for s in sources: collect_path_strings(s,strings)
    skip={'.git','node_modules','.next','dist','build','.cache','.turbo','__pycache__'}
    for root in ['tools','products','shared','config','styles','docs/atlas','templates','prisma','apps/terminal-de-venta-system']:
        base=repo_root/root
        if not base.exists(): continue
        for p in base.rglob('*'):
            if len(strings)>=35000: break
            if any(part in skip for part in p.parts): continue
            if p.is_file():
                try: strings.append(str(p.resolve().relative_to(repo_root.resolve())).replace('\\\\','/'))
                except Exception: strings.append(str(p).replace('\\\\','/'))
    seen=set(); unique=[]
    for s in strings:
        s=str(s).strip().replace('\\\\','/')
        if not s or len(s)>400 or s in seen: continue
        seen.add(s); unique.append(s)
    role_counts={}; entries=[]
    for p in unique:
        role=classify_path(p); role_counts[role]=role_counts.get(role,0)+1
        entries.append({'path':p,'surfaceRole':role,'exists':(repo_root/p).exists() if not p.startswith('F:') else Path(p).exists()})
    coverage=sources[1]; semantic_missing=0
    if isinstance(coverage,dict):
        for k in ['missing_atlas_nodes','missingAtlasNodes','missing_nodes']:
            if isinstance(coverage.get(k),int): semantic_missing=int(coverage[k]); break
    return {'status':'PASS_SURFACE_AWARE_ATLAS_NODE_RESOLVER_BUILT','resolverVersion':'atlastriad.surface.v1','totalResolvedCandidates':len(entries),'roleCounts':role_counts,'coverageComplete':False if semantic_missing else None,'semanticMissingCountFromPriorRegister':semantic_missing,'unknownCount':role_counts.get('Unknown',0),'unknownSample':[e for e in entries if e['surfaceRole']=='Unknown'][:500],'resolverRules':[{'role':r,'patterns':pats} for r,pats in ROLE_RULES],'doesProve':['paths are classified by surface/workspace/tooling role','coverage gaps are no longer ownerless strings','semantic completeness remains separately tracked'],'doesNotProve':['complete semantic Atlas coverage','runtime/live certification','that every docs mention is a live node'],'nextGate':'USE_RESOLVER_TO_REDUCE_MISSING_ATLAS_NODES_BY_OWNER'}
