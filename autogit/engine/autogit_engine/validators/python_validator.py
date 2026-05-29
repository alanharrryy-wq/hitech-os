from __future__ import annotations
import py_compile
def validate(repo,paths):
    rows=[]
    for rel in paths:
        full=repo/rel.replace("/","\\")
        if full.suffix.lower()==".py" and full.exists():
            py_compile.compile(str(full),doraise=True); rows.append({"path":rel,"ok":True})
    return rows
