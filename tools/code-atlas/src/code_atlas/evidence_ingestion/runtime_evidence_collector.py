# -*- coding: utf-8 -*-
from __future__ import annotations
import zipfile, hashlib
from pathlib import Path
from typing import Any, Dict
def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def classify_zip(name:str)->str:
    n=name.lower()
    if 'uirun' in n or 'runtime' in n or 'page' in n: return 'runtime_page_certification'
    if 'licops' in n or 'licrev' in n or 'licflow' in n or 'cloudflare' in n or 'worker' in n: return 'licensing_cloud_live_ops'
    if 'dbevid' in n or 'dbev' in n: return 'db_evidence_atlas'
    if 'atlasgate' in n or 'atlasfix' in n or 'atlaspack' in n: return 'code_atlas_source_gate'
    if 'factroot' in n or 'factory' in n: return 'factory_ledger'
    if 'autogit' in n: return 'git_closure_evidence'
    return 'unclassified_evidence_zip'
def inspect_zip(path:Path)->Dict[str,Any]:
    item={'name':path.name,'path':str(path),'bytes':path.stat().st_size,'sha256':sha256_file(path),'category':classify_zip(path.name)}
    try:
        with zipfile.ZipFile(path,'r') as z:
            names=z.namelist(); item['entryCount']=len(names); item['hasResultJson']=any(n.lower().endswith('result.json') or n.lower().endswith('test_result.json') for n in names); item['hasHtml']=any(n.lower().endswith('.html') for n in names); item['hasScreenshots']=any(n.lower().endswith(('.png','.jpg','.jpeg','.webp')) for n in names); item['hasLogs']=any('log' in n.lower() or n.lower().endswith('.log') for n in names); item['hasRawDb']=any(n.lower().endswith(('.db','.sqlite','.sqlite3','.db-wal','.db-shm','.wal','.shm')) for n in names); item['entrySample']=names[:80]
    except Exception as e: item['zipError']=str(e)
    return item
def collect_runtime_evidence(out_root:Path)->Dict[str,Any]:
    zips=[]
    for pat in ['*result.zip','*merge*.zip','*apply*.zip']: zips.extend([p for p in out_root.glob(pat) if p.is_file()])
    zips=sorted(set(zips), key=lambda p:p.stat().st_mtime, reverse=True)[:180]
    inspected=[inspect_zip(p) for p in zips]; counts={}
    for x in inspected: counts[x['category']]=counts.get(x['category'],0)+1
    raw_db=[x for x in inspected if x.get('hasRawDb')]; runtime_like=[x for x in inspected if x['category'] in ('runtime_page_certification','licensing_cloud_live_ops')]; db_evidence=[x for x in inspected if x['category']=='db_evidence_atlas']
    return {'status':'PASS_RUNTIME_LIVE_EVIDENCE_COLLECTED_FROM_EXISTING_ARTIFACTS','collectionMode':'EXISTING_ARTIFACTS_ONLY_NO_RUNTIME_NO_PORTS','totalZipsInspected':len(inspected),'categoryCounts':counts,'runtimeLikeEvidenceCount':len(runtime_like),'dbEvidenceCount':len(db_evidence),'rawDbBearingZipCount':len(raw_db),'rawDbBearingZips':raw_db[:20],'evidence':inspected[:120],'productionGreenAllowed':False,'productionBlockers':['sales lineage provenance remains inferred/incomplete unless a later DB Evidence report proves otherwise','runtime/live artifacts are collected but not yet linked to each production gate row','DB ghost relations require schema/migration decision before green'],'doesProve':['existing result ZIP inventory was collected without launching runtime'],'doesNotProve':['fresh runtime smoke','browser certification','production green','sales lineage complete'],'nextGate':'LINK_RUNTIME_ARTIFACTS_TO_PRODUCTION_GATE_ROWS_AND_COLLECT_MISSING_LIVE_EVIDENCE_IF_APPROVED'}
