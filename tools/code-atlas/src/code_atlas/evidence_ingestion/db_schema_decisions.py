# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List
def load_json(path:Path,default=None):
    try: return json.loads(path.read_text(encoding='utf-8', errors='replace'))
    except Exception: return {} if default is None else default
def find_ghosts(obj:Any,out:List[Dict[str,Any]],breadcrumb:str=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            key=str(k).lower()
            if 'ghost' in key and isinstance(v,list):
                for i,item in enumerate(v): out.append({'sourceKey':k,'index':i,'value':item,'breadcrumb':breadcrumb})
            elif 'ghost' in key and isinstance(v,(str,int,float,bool)): out.append({'sourceKey':k,'value':v,'breadcrumb':breadcrumb})
            elif isinstance(v,(dict,list)): find_ghosts(v,out,f'{breadcrumb}.{k}' if breadcrumb else str(k))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            if isinstance(v,dict) and any('ghost' in str(x).lower() for x in list(v.keys())+[v.get('status',''),v.get('type',''),v.get('name','')]): out.append({'sourceKey':'listItem','index':i,'value':v,'breadcrumb':breadcrumb})
            find_ghosts(v,out,f'{breadcrumb}[{i}]')
def classify_relation(item:Dict[str,Any])->str:
    txt=json.dumps(item,ensure_ascii=False).lower()
    if any(x in txt for x in ['outbox','sync','terminal','canonical','projection']): return 'SYNC_OUTBOX_TERMINAL_SCHEMA_CONTRACT_DECISION'
    return 'DB_SCHEMA_CONTRACT_DECISION'
def build_db_ghost_decisions(registers_dir:Path)->Dict[str,Any]:
    db=load_json(registers_dir/'DB_REALITY_INDEX.json',{})
    ghosts=[]; find_ghosts(db,ghosts); aggregate=None
    for k in ['ghost_relations','ghostRelations','ghost_relations_count']:
        if isinstance(db,dict) and isinstance(db.get(k),int): aggregate=int(db[k])
    if not ghosts and aggregate: ghosts=[{'sourceKey':'ghost_relations','index':i,'value':'AGGREGATE_ONLY','breadcrumb':'DB_REALITY_INDEX'} for i in range(aggregate)]
    decisions=[]; counts={}
    for i,g in enumerate(ghosts):
        decision=classify_relation(g); counts[decision]=counts.get(decision,0)+1
        decisions.append({'id':f'ghost_relation_{i+1:03d}','status':'CLASSIFIED_DECISION_REQUIRED_NOT_PATCHED','decisionClass':decision,'source':g,'nextGate':decision,'doesProve':['ghost relation is classified and no longer unowned'],'doesNotProve':['schema/migration corrected','runtime DB relation validated']})
    return {'status':'PASS_DB_GHOST_RELATIONS_CLASSIFIED_DECISION_REQUIRED','totalGhostRelationsClassified':len(decisions),'classificationCounts':counts,'decisions':decisions,'schemaModified':False,'migrationsModified':False,'productionGreenAllowed':False,'nextGate':'HUMAN_DB_SCHEMA_CONTRACT_DECISION_THEN_MIGRATION_PATCH_IF_APPROVED','doesProve':['DB ghost relation ambiguity is registered and routed'],'doesNotProve':['DB schema fixed','migrations updated','production certified']}
