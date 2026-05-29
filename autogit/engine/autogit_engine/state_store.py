from __future__ import annotations
import json,datetime as dt
class StateStore:
    def __init__(self,path): self.path=path; self.data={}
    def update(self,**kwargs):
        self.data.update(kwargs); self.data["updated_at"]=dt.datetime.now().isoformat(timespec="seconds"); self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(self.data,indent=2,ensure_ascii=False),encoding="utf-8")
