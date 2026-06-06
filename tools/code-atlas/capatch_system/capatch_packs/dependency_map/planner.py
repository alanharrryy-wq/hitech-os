#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from importlib import resources
from pathlib import Path
from typing import Any
from capatch_project.planner_contracts import CapabilityPlan
from capatch_project.profile import ProjectProfile
CAPABILITY_ID='dependency-map'; INSTALL_RELATIVE_PATH='tools/dependency_map/analyze_project.py'
def analyzer_template_text()->str:
    return resources.files('capatch_packs.dependency_map.templates').joinpath('analyze_project.py').read_text(encoding='utf-8')
def build_plan(profile:ProjectProfile,*,mode:str='plan')->CapabilityPlan:
    return CapabilityPlan(CAPABILITY_ID, profile.root, mode, actions=[{'type':'install-file','label':'install-universal-dependency-analyzer','target':INSTALL_RELATIVE_PATH,'source':'capatch_packs/dependency_map/templates/analyze_project.py','idempotent':True},{'type':'run-verifier','label':'analyzer-json-smoke','command':f'python {INSTALL_RELATIVE_PATH} --root . --format json','idempotent':True}], writes=[INSTALL_RELATIVE_PATH,'reports/dependency_map/'], verifiers=['profile-detect','analyzer-json-smoke'], notes=['Capability universal; no depende de Code Atlas.'])
def plan_to_json(profile:ProjectProfile,*,mode:str='plan')->str:
    return json.dumps({'profile':profile.to_dict(),'plan':build_plan(profile,mode=mode).to_dict()},indent=2,ensure_ascii=False)
def install_analyzer(target_root:Path,*,dry_run:bool=False)->dict[str,Any]:
    root=target_root.expanduser().resolve(); target=root/INSTALL_RELATIVE_PATH; content=analyzer_template_text(); result={'target':str(target),'dry_run':dry_run,'changed':False,'backup':None}
    if dry_run: result['would_write']=True; return result
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        old=target.read_text(encoding='utf-8',errors='replace')
        if old==content: return result
        backup=target.with_suffix(target.suffix+'.capatch_bak'); backup.write_text(old,encoding='utf-8'); result['backup']=str(backup)
    target.write_text(content,encoding='utf-8',newline=''); result['changed']=True; return result
