from __future__ import annotations
import json,re
from ..text_io import trim_whitespace
WHITESPACE_LINE=re.compile(r"^([^:]+):\d+:\s+(trailing whitespace\.|new blank line at EOF\.)$")
def fix_cached_whitespace(repo,git,paths,backup,manifest_path):
    r=git.sh.run(["git","diff","--cached","--check"],name="git_diff_cached_check_before")
    if r.code==0:
        manifest_path.write_text("[]\n",encoding="utf-8"); return []
    hits=set(); unexpected=[]
    for raw in ((r.stdout or "")+"\n"+(r.stderr or "")).splitlines():
        line=raw.strip()
        if not line: continue
        m=WHITESPACE_LINE.match(line)
        if m: hits.add(m.group(1).replace("\\","/"))
        elif line.startswith("+"): continue
        else: unexpected.append(line)
    if unexpected or not hits or not hits.issubset(set(paths)):
        manifest_path.write_text(json.dumps({"hits":sorted(hits),"unexpected":unexpected},indent=2),encoding="utf-8")
        raise RuntimeError("diff --check failed with non-whitespace errors")
    rows=[]
    for rel in sorted(hits):
        backup.backup(rel,"whitespace"); changed=trim_whitespace(repo/rel.replace("/","\\")); rows.append({"path":rel,"changed":changed})
    git.add_exact(sorted(hits)); git.diff_check(cached=True); manifest_path.write_text(json.dumps(rows,indent=2),encoding="utf-8"); return rows
