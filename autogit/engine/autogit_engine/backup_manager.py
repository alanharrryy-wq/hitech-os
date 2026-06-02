from __future__ import annotations
from pathlib import Path
import hashlib,json,os,shutil
from .paths import repo_path
class BackupManager:
    def __init__(self,repo:Path,backup_root:Path): self.repo=repo; self.root=backup_root; self.root.mkdir(parents=True,exist_ok=True); self.rows=[]
    def sha(self,path:Path)->str:
        h=hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
        return h.hexdigest()
    def backup(self,rel_path:str,reason:str)->None:
        src=repo_path(self.repo, rel_path)
        if not src.exists(): return
        dst=repo_path(self.root, rel_path)
        if not dst.exists():
            dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
            self.rows.append({"rel":rel_path,"src":str(src),"backup":str(dst),"sha256":self.sha(src) if src.is_file() else "","reason":reason})
    def write_manifest(self)->None: (self.root/"manifest.json").write_text(json.dumps(self.rows,indent=2,ensure_ascii=False),encoding="utf-8")
