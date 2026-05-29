from __future__ import annotations
from dataclasses import asdict
import json
from .file_metadata import build_meta
from .file_classifier import classify
from .progress import bar,line
def build_index(repo,git,out_json):
    entries=git.status_porcelain(); groups={}; included=[]; rejected=[]; trash=[]; total=max(len(entries),1)
    for i,e in enumerate(entries,1):
        bar("INDEX",i,total,e.path); meta=build_meta(repo,e.path,e.status); dec=classify(meta)
        row={"path":e.path,"status":e.status,"meta":asdict(meta),"decision":asdict(dec)}
        if dec.action=="include": groups.setdefault(dec.group,[]).append(e.path); included.append(row)
        elif dec.action=="trash": trash.append(row)
        else: rejected.append(row)
    bar("INDEX",total,total,"ready",force=True); line()
    out_json.write_text(json.dumps({"groups":groups,"included":included,"rejected":rejected,"trash":trash},indent=2,ensure_ascii=False),encoding="utf-8")
    return groups,included,rejected,trash
