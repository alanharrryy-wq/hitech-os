from __future__ import annotations
import json
from .validators import json_validator,python_validator,node_validator,powershell_validator
from .secret_scan import severe_hits
from .paths import contains_local_path, repo_path
from .sanitizer_core import CODE_EXTS, NO_SOURCE_REWRITE_NAMES
from .text_io import read_text_lossless
from .progress import bar,line

def should_block_local_paths(full):
    if full.name in NO_SOURCE_REWRITE_NAMES:
        return False
    if full.suffix.lower() in CODE_EXTS:
        return False
    return True

def severe_scan(repo,paths):
    blockers={}; total=max(len(paths),1)
    for i,rel in enumerate(paths,1):
        bar("BLOCKERS",i,total,rel); full=repo_path(repo, rel)
        if not full.exists() or not full.is_file(): continue
        try: text,_=read_text_lossless(full,limit=6*1024*1024)
        except Exception: continue
        hits=severe_hits(text)
        if should_block_local_paths(full) and contains_local_path(text): hits.append("LOCAL_PATH_REMAINS")
        if hits: blockers[rel]=sorted(set(hits))
    bar("BLOCKERS",total,total,"ready",force=True); line(); return blockers
def validate_all(repo,paths,shell,scratch,report_path):
    result={"json":json_validator.validate(repo,paths),"python":python_validator.validate(repo,paths),"node":node_validator.validate(repo,paths,shell),"powershell":powershell_validator.validate(repo,paths,shell,scratch)}
    blockers=severe_scan(repo,paths); result["blockers"]=blockers; report_path.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    if blockers: raise RuntimeError("Blockers remain after sanitize")
    return result
