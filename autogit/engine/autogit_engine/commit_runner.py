from __future__ import annotations
import json
from .validators.diff_validator import fix_cached_whitespace
from .errors import StageMismatchError
from .progress import bar,line
def commit_plans(repo,git,plans,backup,report_dir):
    rows=[]; total=max(len(plans),1)
    for i,plan in enumerate(plans,1):
        bar("COMMIT",i,total,plan.group,force=True); git.reset_index(); git.add_exact(plan.paths); actual=git.staged_paths()
        unexpected=sorted(set(actual)-set(plan.paths)); missing=sorted(set(plan.paths)-set(actual))
        (report_dir/f"staged_{plan.group}.txt").write_text("\n".join(actual)+"\n",encoding="utf-8")
        if unexpected or missing: raise StageMismatchError("Stage mismatch",detail={"group":plan.group,"unexpected":unexpected,"missing":missing})
        fix_cached_whitespace(repo,git,plan.paths,backup,report_dir/f"whitespace_{plan.group}.json")
        commit=git.commit(plan.message,plan.body); rows.append({"group":plan.group,"commit":commit,"message":plan.message,"files":len(plan.paths)})
    bar("COMMIT",total,total,"ready",force=True); line(); (report_dir/"created_commits.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8"); return rows
