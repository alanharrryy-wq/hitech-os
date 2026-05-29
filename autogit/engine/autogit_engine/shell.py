from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os, subprocess
from .errors import AutoGitError
from .no_delete_guard import forbid_delete_command
@dataclass
class CommandResult:
    cmd:list[str]; cwd:str; code:int; stdout:str; stderr:str
    def as_text(self)->str:
        return "$ "+" ".join(self.cmd)+f"\ncwd={self.cwd}\nexit_code={self.code}\n\n--- STDOUT ---\n{self.stdout or ''}\n--- STDERR ---\n{self.stderr or ''}\n"
class Shell:
    def __init__(self,cwd:Path,log_dir:Path):
        self.cwd=Path(cwd); self.log_dir=Path(log_dir); self.log_dir.mkdir(parents=True,exist_ok=True); self.counter=0
    def run(self,cmd:list[str],*,cwd:Path|None=None,timeout:int=300,check:bool=False,name:str|None=None)->CommandResult:
        forbid_delete_command(cmd); wd=Path(cwd or self.cwd); self.counter+=1
        safe=(name or f"cmd_{self.counter:04d}_"+"_".join(cmd[:3])).replace(":","_").replace("/","_").replace("\\","_")[:120]
        try:
            p=subprocess.run(cmd,cwd=str(wd),capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
            res=CommandResult(cmd,str(wd),p.returncode,p.stdout,p.stderr)
        except Exception as exc:
            res=CommandResult(cmd,str(wd),999,"",repr(exc))
        (self.log_dir/f"{safe}.txt").write_text(res.as_text(),encoding="utf-8",errors="replace")
        if check and res.code!=0: raise AutoGitError(f"Command failed: {' '.join(cmd)}", detail={"code":res.code,"log":str(self.log_dir/f'{safe}.txt')})
        return res
    def which(self,name:str)->str|None:
        from shutil import which
        return which(name)
