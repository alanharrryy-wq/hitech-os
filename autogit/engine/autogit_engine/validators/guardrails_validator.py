from __future__ import annotations
from pathlib import Path
def run_local_guardrails(repo,shell,out_dir):
    node=shell.which("node") or shell.which("node.exe")
    if not node: return [{"skipped":"node missing"}]
    rows=[]
    for script,output in [("tools/scripts/report_repo_hygiene.mjs",out_dir/"repo_hygiene.local.json"),("tools/scripts/report_codeowners_coverage.mjs",out_dir/"codeowners_coverage.local.json")]:
        if (repo/script).exists():
            r=shell.run([node,script,"--output",str(output)],timeout=600,name="local_guardrail_"+Path(script).stem)
            if r.code!=0: raise RuntimeError(f"Guardrail script failed: {script}")
            rows.append({"script":script,"output":str(output),"ok":True})
    return rows
