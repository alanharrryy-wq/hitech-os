from __future__ import annotations
def validate(repo,paths,shell):
    node=shell.which("node") or shell.which("node.exe"); rows=[]
    if not node: return [{"skipped":"node not found"}]
    for rel in paths:
        full=repo/rel.replace("/","\\")
        if full.suffix.lower() in {".js",".mjs",".cjs"} and full.exists():
            if rel.lower().endswith(".min.js"): rows.append({"path":rel,"skipped":"minified"}); continue
            r=shell.run([node,"--check",str(full)],timeout=120,name="node_check_"+full.name)
            if r.code!=0: raise RuntimeError(f"node --check failed for {rel}")
            rows.append({"path":rel,"ok":True})
    return rows
