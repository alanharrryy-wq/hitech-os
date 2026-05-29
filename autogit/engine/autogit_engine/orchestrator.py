from __future__ import annotations
import json
from pathlib import Path
from .backup_manager import BackupManager
from .commit_planner import build_plans
from .commit_runner import commit_plans
from .diagnostics import write_success
from .file_index import build_index
from .known_fixes import apply_known_fixes
from .preflight import run_preflight
from .pr_gate import run_pr_gate
from .progress import line,phase
from .sanitizer_core import sanitize_paths
from .trash_manager import TrashManager
from .validator_pipeline import validate_all
from .validators.guardrails_validator import run_local_guardrails
class Orchestrator:
    def __init__(self,ctx):
        self.ctx=ctx; self.backup=BackupManager(ctx.repo,ctx.artifact("backups_before_changes")); self.trash=TrashManager(ctx.repo,Path(ctx.policy.trash_root),ctx.run_id)
    def run(self):
        ctx=self.ctx; phase("PREFLIGHT"); git,gh=run_preflight(ctx)
        phase("SCAN DIRTY TREE"); groups,included,rejected,trash=build_index(ctx.repo,git,ctx.artifact("index.json"))
        for row in trash: ctx.moved_to_trash.append(self.trash.move(row["path"],row["decision"]["reason"]))
        self.trash.write_manifest(); ctx.artifact("rejected.json").write_text(json.dumps(rejected,indent=2,ensure_ascii=False),encoding="utf-8")
        all_paths=[p for paths in groups.values() for p in paths]
        phase("SANITIZE"); sanitize_paths(ctx.repo,all_paths,self.backup,ctx.artifact("sanitize_manifest.json")); self.backup.write_manifest()
        phase("VALIDATE"); validate_all(ctx.repo,all_paths,ctx.shell,ctx.artifact("scratch"),ctx.artifact("validation.json"))
        phase("KNOWN FIXES"); recipe_rows=apply_known_fixes(ctx,"spawnSync git ENOBUFS CODEOWNERS apps/code-atlas",ctx.artifact("known_fix_results.json"))
        phase("RESCAN AFTER FIXES"); groups2,_,rejected2,trash2=build_index(ctx.repo,git,ctx.artifact("index_after_recipes.json"))
        all_paths2=[p for paths in groups2.values() for p in paths]; validate_all(ctx.repo,all_paths2,ctx.shell,ctx.artifact("scratch2"),ctx.artifact("validation_after_recipes.json"))
        phase("LOCAL GUARDRAILS"); guardrail_rows=run_local_guardrails(ctx.repo,ctx.shell,ctx.artifact("local_guardrails")); ctx.artifact("local_guardrails.json").write_text(json.dumps(guardrail_rows,indent=2,ensure_ascii=False),encoding="utf-8")
        phase("COMMIT"); plans=build_plans(groups2); ctx.created_commits=commit_plans(ctx.repo,git,plans,self.backup,ctx.report_dir); ctx.write_state("committed")
        phase("PR GATE"); pr_result={"result":"skipped","reason":"mode"}
        if ctx.policy.mode in {"full","pr-only"} and gh: pr_result=run_pr_gate(ctx,git,gh)
        summary={"result":"ok","commits":ctx.created_commits,"moved_to_trash":ctx.moved_to_trash,"pr":pr_result,"recipes":recipe_rows}
        zip_path=write_success(ctx,summary); line(f"RESULT_ZIP: {zip_path}"); return summary
