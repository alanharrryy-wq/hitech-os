from __future__ import annotations
from pathlib import Path
import json,os,traceback,zipfile
from .progress import bar,line
def write_failure(ctx,exc):
    ctx.write_state("failed",{"error":repr(exc)}); ctx.artifact("FAILED_TRACEBACK.txt").write_text("".join(traceback.format_exception(exc)),encoding="utf-8")
    write_continuation(ctx,ctx.artifact("CONTINUATION.md"),exc); return zip_report(ctx,"fail")
def write_success(ctx,summary):
    ctx.artifact("summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    write_continuation(ctx,ctx.artifact("CONTINUATION.md"),None); return zip_report(ctx,"result")
def write_continuation(ctx,path,exc):
    lines=["# AutoGit Continuation","",f"Repo: `{ctx.repo}`",f"Run: `{ctx.run_id}`",f"Start HEAD: `{ctx.start_head}`",f"Final HEAD: `{ctx.final_head}`",""]
    if exc: lines+=["## Failure","","```text",repr(exc),"```",""]
    lines+=["## Evidence","","- `logs/` command outputs","- `validation.json`","- `created_commits.json`","- `autogit latest state.json`",""]
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")
def zip_report(ctx,suffix):
    zip_path=ctx.out/f"autogit {ctx.run_id} {suffix}.zip"; files=[]
    for r,_,names in os.walk(ctx.report_dir):
        for name in names:
            full=Path(r)/name; files.append((full,full.relative_to(ctx.report_dir).as_posix()))
    total=max(len(files),1)
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for i,(full,arc) in enumerate(sorted(files,key=lambda x:x[1]),1):
            z.write(full,arc); bar("ZIP",i,total,arc)
    bar("ZIP",total,total,"ready",force=True); line(); return zip_path
