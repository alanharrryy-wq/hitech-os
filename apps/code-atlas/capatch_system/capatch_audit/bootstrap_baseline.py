from __future__ import annotations
from pathlib import Path
from typing import Any
from capatch_audit.baseline_registry import write_baseline
DEFAULT_BASELINE_TARGETS=['capatch.py','capatch_cli/main.py','capatch_cli/commands_patch.py','capatch_runtime/readiness_gate.py','capatch_verify/registry.py','capatch_policy/verification_requirements.py']
def bootstrap_readiness_baseline(root_dir:Path,*,label:str='readiness-bootstrap',notes:str='',blessed_by:str|None='capatch-ready-pack')->dict[str,Any]:
    root_dir=Path(root_dir).resolve(); targets=[x for x in DEFAULT_BASELINE_TARGETS if (root_dir/x).exists()]
    snap=[{'verifier_id':'readiness-baseline-bootstrap','ok':True,'title':'Bootstrap baseline created','detail':'Manual formalization baseline.','metrics':{'target_count':len(targets)}}]
    rec=write_baseline(root_dir,label=label,target_files=targets,verification_snapshot=snap,notes=notes or 'Bootstrap baseline generated after readiness pack installation.',blessed_by=blessed_by,baseline_kind='readiness-bootstrap')
    return {'status':'ok','baseline_id':rec.baseline_id,'target_files':targets,'baseline_kind':rec.baseline_kind}
