from __future__ import annotations
from .base import Recipe,RecipeResult
class GitHubChecksRecipe(Recipe):
    name="github_checks"; patterns=('checks failed', 'workflow failed', 'guardrails fail', 'deps fail')
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"note":'handled by diagnostics'})
