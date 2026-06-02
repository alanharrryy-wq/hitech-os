from __future__ import annotations
import json
from .text_io import read_text_lossless,write_utf8
from .sanitizers.json_sanitizer import sanitize_json_text
from .sanitizers.code_sanitizer import sanitize_code_text
from .sanitizers.doc_sanitizer import sanitize_doc_text
from .progress import bar,line
from .paths import repo_path
CODE_EXTS={".py",".js",".jsx",".ts",".tsx",".mjs",".cjs",".ps1",".psm1",".sh",".bat",".cmd",".html",".css",".scss"}
NO_SOURCE_REWRITE_NAMES={"package.json","pnpm-lock.yaml","package-lock.json","yarn.lock",".gitignore"}
def sanitize_paths(repo,paths,backup,manifest_path):
    rows=[]; total=max(len(paths),1)
    for i,rel in enumerate(paths,1):
        bar("SANITIZE",i,total,rel); full=repo_path(repo, rel)
        if not full.exists() or not full.is_file(): continue
        try: text,enc=read_text_lossless(full)
        except Exception as exc: rows.append({"path":rel,"changed":False,"error":repr(exc)}); continue
        old=text; ext=full.suffix.lower()
        try:
            if full.name in NO_SOURCE_REWRITE_NAMES: new=text
            elif ext==".json": new=sanitize_json_text(text)
            elif ext in CODE_EXTS: new=sanitize_code_text(text)
            else: new=sanitize_doc_text(text)
        except Exception: new=sanitize_doc_text(text)
        if new!=old:
            backup.backup(rel,"sanitize"); write_utf8(full,new); rows.append({"path":rel,"changed":True,"encoding":enc})
        else: rows.append({"path":rel,"changed":False,"encoding":enc})
    bar("SANITIZE",total,total,"ready",force=True); line(); manifest_path.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8"); return rows
