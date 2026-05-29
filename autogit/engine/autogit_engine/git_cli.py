from __future__ import annotations
from dataclasses import dataclass
from .errors import DirtyTreeError
@dataclass
class GitStatusEntry:
    status:str; path:str
class Git:
    def __init__(self,shell): self.sh=shell
    def rev_parse(self,ref:str="HEAD")->str: return self.sh.run(["git","rev-parse",ref],check=True,name="git_rev_parse").stdout.strip()
    def branch(self)->str: return self.sh.run(["git","branch","--show-current"],check=True,name="git_branch").stdout.strip()
    def fetch(self,remote="origin",branch="main")->None: self.sh.run(["git","fetch",remote,branch,"--prune"],check=True,timeout=600,name="git_fetch")
    def is_ancestor(self,ancestor:str,descendant:str)->bool: return self.sh.run(["git","merge-base","--is-ancestor",ancestor,descendant],name="git_merge_base").code==0
    def ahead_count(self,base:str,head:str="HEAD")->int:
        out=self.sh.run(["git","rev-list","--count",f"{base}..{head}"],check=True,name="git_ahead").stdout
        return int((out or "0").strip() or "0")
    def status_porcelain(self)->list[GitStatusEntry]:
        r=self.sh.run(["git","status","--porcelain","--untracked-files=all"],check=True,name="git_status_porcelain")
        rows=[]
        for line in r.stdout.splitlines():
            if not line.strip(): continue
            status=line[:2]; path=line[3:].strip().replace("\\","/")
            if " -> " in path: path=path.split(" -> ",1)[-1].strip().replace("\\","/")
            rows.append(GitStatusEntry(status,path))
        return rows
    def assert_clean(self)->None:
        rows=self.status_porcelain()
        if rows: raise DirtyTreeError("Working tree dirty", detail={"entries":[r.__dict__ for r in rows]})
    def staged_paths(self)->list[str]:
        out=self.sh.run(["git","diff","--cached","--name-only","--no-renames"],check=True,name="git_staged_paths").stdout
        return [x.strip().replace("\\","/") for x in out.splitlines() if x.strip()]
    def add_exact(self,paths:list[str])->None:
        chunk=[]; size=0
        for p in sorted(paths):
            n=len(p)+4
            if chunk and size+n>6500:
                self.sh.run(["git","add","--"]+chunk,check=True,name="git_add"); chunk=[]; size=0
            chunk.append(p); size+=n
        if chunk: self.sh.run(["git","add","--"]+chunk,check=True,name="git_add")
    def reset_index(self)->None: self.sh.run(["git","reset"],check=True,name="git_reset_index")
    def commit(self,message:str,body:str)->str:
        self.sh.run(["git","commit","-m",message,"-m",body],check=True,timeout=600,name="git_commit")
        return self.rev_parse("HEAD")
    def push_head(self,remote_branch:str,remote:str="origin")->None: self.sh.run(["git","push",remote,f"HEAD:refs/heads/{remote_branch}"],check=True,timeout=900,name="git_push_head")
    def ff_only(self,ref:str)->None: self.sh.run(["git","merge","--ff-only",ref],check=True,timeout=600,name="git_ff_only")
    def diff_check(self,range_spec:str|None=None,cached:bool=False)->None:
        cmd=["git","diff"]
        if cached: cmd.append("--cached")
        cmd.append("--check")
        if range_spec: cmd.append(range_spec)
        self.sh.run(cmd,check=True,timeout=300,name="git_diff_check")
