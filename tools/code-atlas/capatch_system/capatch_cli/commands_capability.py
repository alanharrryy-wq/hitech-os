#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from capatch_project.capability_registry import get_capability, list_capabilities
from capatch_project.detectors import detect_project
from capatch_packs.dependency_map.planner import build_plan, install_analyzer, plan_to_json
from capatch_packs.dependency_map.verifier import verify_project
def _print_json(payload:Any)->None: print(json.dumps(payload,indent=2,ensure_ascii=False))
def handle(args:Any,*,base_dir:Path)->int|None:
    capability_id=getattr(args,'capability',None)
    if not capability_id: return None
    if str(capability_id).strip().lower()=='list': _print_json({'capabilities':list_capabilities()}); return 0
    cap=get_capability(str(capability_id)); root=Path(str(getattr(args,'root_dir','.'))).expanduser().resolve(); action=str(getattr(args,'capability_action','profile') or 'profile'); output=getattr(args,'capability_output',None); dry_run=bool(getattr(args,'dry_run',False)); profile=detect_project(root)
    if action=='profile': payload={'capability':cap.to_dict(),'profile':profile.to_dict()}
    elif action=='plan': payload=json.loads(plan_to_json(profile,mode='plan'))
    elif action=='install': payload={'capability':cap.to_dict(),'profile':profile.to_dict(),'plan':build_plan(profile,mode='install').to_dict(),'install':install_analyzer(root,dry_run=dry_run)}
    elif action=='verify': payload={'capability':cap.to_dict(),'profile':profile.to_dict(),'verification':verify_project(root)}
    else: raise ValueError(f'Accion de capability no soportada: {action}')
    if output:
        out=Path(str(output)).expanduser().resolve(); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8'); print(f'[INFO] capability output: {out}')
    else: _print_json(payload)
    return 0 if action!='verify' or bool(payload.get('verification',{}).get('ok')) else 2
