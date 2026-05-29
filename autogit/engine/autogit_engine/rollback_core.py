from __future__ import annotations
from pathlib import Path
import json
from .shell import Shell
def rollback_latest(repo:Path,out:Path):
    state_path=out/"autogit latest state.json"
    if not state_path.exists(): raise RuntimeError("No autogit latest state.json found")
    state=json.loads(state_path.read_text(encoding="utf-8")); start=state.get("start_head")
    shell=Shell(repo,out/"rollback_logs"); current=shell.run(["git","rev-parse","HEAD"],check=True,name="rollback_current_head").stdout.strip()
    if start: shell.run(["git","reset","--mixed",start],check=True,name="rollback_reset_start")
    return {"current_before":current,"reset_to":start,"note":"Remote PR merges are not reverted automatically. Use a revert PR."}
