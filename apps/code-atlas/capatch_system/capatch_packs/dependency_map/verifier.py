#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from typing import Any
from capatch_packs.dependency_map.planner import INSTALL_RELATIVE_PATH
from capatch_project.detectors import detect_project
def verify_project(target_root:Path|str,*,timeout_seconds:int=45)->dict[str,Any]:
    root=Path(target_root).expanduser().resolve(); profile=detect_project(root); analyzer=root/INSTALL_RELATIVE_PATH
    checks=[{'id':'profile-detect','ok':profile.exists,'detail':profile.to_dict()},{'id':'analyzer-file-exists','ok':analyzer.exists(),'detail':str(analyzer)}]
    if analyzer.exists():
        proc=subprocess.run([sys.executable,str(analyzer),'--root',str(root),'--format','json','--max-files','1000'],cwd=str(root),text=True,capture_output=True,timeout=timeout_seconds)
        parsed=False; summary={}
        if proc.returncode==0:
            try:
                payload=json.loads(proc.stdout); parsed=isinstance(payload,dict); summary=dict(payload.get('summary') or {})
            except Exception: parsed=False
        checks.append({'id':'analyzer-json-smoke','ok':proc.returncode==0 and parsed,'exit_code':proc.returncode,'summary':summary,'stderr_tail':proc.stderr[-2000:]})
    return {'ok': all(bool(c.get('ok')) for c in checks), 'target_root':str(root), 'checks':checks}
