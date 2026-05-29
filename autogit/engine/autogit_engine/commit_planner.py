from __future__ import annotations
from dataclasses import dataclass
ORDER=["docs","control-center","app-surfaces","tooling","deps","assets","cleanup","misc"]
MESSAGES={"docs":"docs(prisma): update curated documentation","control-center":"feat(control-center): add curated runtime updates","app-surfaces":"feat(prisma): add curated app surface updates","tooling":"chore(prisma): add curated tooling updates","deps":"chore(deps): update curated package metadata","assets":"chore(assets): add curated visual assets","cleanup":"chore(prisma): remove superseded files","misc":"chore(prisma): add remaining curated files"}
@dataclass
class CommitPlan:
    group:str; paths:list[str]; message:str; body:str
def build_plans(groups):
    plans=[]
    for group in ORDER+sorted(set(groups)-set(ORDER)):
        paths=sorted(set(groups.get(group,[])))
        if not paths: continue
        body=f"Automated AutoGit curated commit for group {group}.\n\nFiles: {len(paths)}.\nFail-fast validations passed before commit.\nNo force push and no merge inside commit phase.\n"
        plans.append(CommitPlan(group,paths,MESSAGES.get(group,f"chore(prisma): add curated {group} files"),body))
    return plans
