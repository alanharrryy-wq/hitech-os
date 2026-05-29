from __future__ import annotations
import json
def validate(repo,paths):
    rows=[]
    for rel in paths:
        full=repo/rel.replace("/","\\")
        if full.suffix.lower()==".json" and full.exists():
            json.loads(full.read_text(encoding="utf-8-sig",errors="replace")); rows.append({"path":rel,"ok":True})
    return rows
