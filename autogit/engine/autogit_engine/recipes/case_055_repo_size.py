from __future__ import annotations
from dataclasses import dataclass
from .base import Recipe,RecipeResult
@dataclass(frozen=True)
class EvidenceItem:
    signature:str
    explanation:str
    risk:str
    remediation:str
    commands_to_capture:tuple[str,...]
class Case055RepoSizeRecipe(Recipe):
    name="case_055_repo_size"
    patterns=('spawnSync git ENOBUFS','repo_size',"autogit-case-055")
    evidence=EvidenceItem(
        signature='spawnSync git ENOBUFS',
        explanation='Detected failure family repo_size during automated Git/CI flow.',
        risk='Ignoring this can produce fake green, regressions, or dirty PR state.',
        remediation='Stop immediately, capture logs, apply one narrow recipe, validate exact staged paths, then retry.',
        commands_to_capture=("git status --short --branch --untracked-files=all","git diff --check","git diff --cached --check","git log --oneline -n 20"),
    )
    def classify(self,text:str)->dict:
        low=(text or "").lower(); score=0
        for pattern in self.patterns:
            if pattern.lower() in low: score+=10
        if 'repo_size'.lower() in low: score+=3
        return {"recipe":self.name,"score":score,"signature":self.evidence.signature}
    def suggested_plan(self)->list[str]:
        return ["freeze HEAD and porcelain status","collect command logs","apply targeted remediation","run syntax/static checks","stage exact paths","stop if unrelated dirty state appears"]
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"advisory":True,"match":self.classify(text or ""),"evidence":self.evidence.__dict__,"plan":self.suggested_plan()})
