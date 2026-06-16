from __future__ import annotations
import json
from pathlib import Path
from typing import Any
try:
    from capatch_cartridges.loader import recommend_cartridges
except Exception:
    def recommend_cartridges(paths:list[str])->list[str]: return ['generic-code']
try:
    from capatch_intent.risk import score_patch_risk
except Exception:
    def score_patch_risk(*,files:list[str],operations:list[dict[str,Any]]|None=None,visual:bool=False)->dict[str,Any]: return {'score':0,'level':'unknown','reasons':[]}
def _op(op): return dict(op) if isinstance(op,dict) else {'type':getattr(op,'type',None),'label':getattr(op,'label',None),'file':getattr(op,'file',None),'payload':dict(getattr(op,'payload',{}) or {})}
def build_patch_plan(*,root_dir:Path,target_files:list[str],operations:list[Any],pipeline:Any|None=None,intent:str|None=None)->dict[str,Any]:
    ops=[_op(o) for o in list(operations or [])]; files=list(dict.fromkeys(str(x) for x in list(target_files or []) if str(x))); visual=any(x.lower().endswith(('.css','.module.css','.tsx','.jsx')) for x in files)
    return {'schema_version':'1.0.0','root_dir':str(Path(root_dir).resolve()),'intent':str(intent or ''),'outcome':str(getattr(pipeline,'outcome','preview') if pipeline is not None else 'preview'),'target_files':files,'operation_count':len(ops),'operations':ops,'recommended_cartridges':recommend_cartridges(files),'risk':score_patch_risk(files=files,operations=ops,visual=visual),'required_verifiers':list(getattr(pipeline,'required_verifiers',[]) or []) if pipeline is not None else []}
def render_patch_plan_md(plan:dict[str,Any])->str:
    lines=['# PATCH_PLAN','',f"- outcome: `{plan.get('outcome')}`",f"- operation_count: `{plan.get('operation_count')}`",f"- cartridges: `{', '.join(plan.get('recommended_cartridges') or []) or 'none'}`",'', '## Target files']
    lines += [f'- `{x}`' for x in plan.get('target_files') or []] or ['- none']
    lines += ['', '## Raw JSON', '```json', json.dumps(plan,indent=2,ensure_ascii=False), '```']
    return '\n'.join(lines)+'\n'
