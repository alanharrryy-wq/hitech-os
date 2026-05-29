from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import datetime as dt, json
from .config import Policy
from .shell import Shell
@dataclass
class Context:
    repo:Path; out:Path; package_root:Path; policy:Policy
    run_id:str=field(default_factory=lambda: dt.datetime.now().strftime("%d%m %H%M%S"))
    report_dir:Path|None=None; logs_dir:Path|None=None; state_path:Path|None=None; shell:Shell|None=None
    start_head:str=""; final_head:str=""; created_commits:list[dict]=field(default_factory=list); moved_to_trash:list[dict]=field(default_factory=list); opened_pr:dict|None=None
    def initialize(self)->"Context":
        self.out.mkdir(parents=True,exist_ok=True); self.report_dir=self.out/f"autogit run {self.run_id}"; self.report_dir.mkdir(parents=True,exist_ok=True)
        self.logs_dir=self.report_dir/"logs"; self.logs_dir.mkdir(parents=True,exist_ok=True); self.state_path=self.out/"autogit latest state.json"; self.shell=Shell(self.repo,self.logs_dir)
        self.write_state("initialized"); return self
    def artifact(self,name:str)->Path:
        assert self.report_dir is not None
        p=self.report_dir/name; p.parent.mkdir(parents=True,exist_ok=True); return p
    def write_state(self,phase:str,extra:dict|None=None)->None:
        if not self.state_path: return
        payload={"phase":phase,"repo":str(self.repo),"out":str(self.out),"run_id":self.run_id,"start_head":self.start_head,"final_head":self.final_head,"created_commits":self.created_commits,"moved_to_trash":self.moved_to_trash,"opened_pr":self.opened_pr,"extra":extra or {}}
        self.state_path.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding="utf-8")
