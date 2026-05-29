from __future__ import annotations
from .base import Recipe,RecipeResult
class AutoMergePolicyRecipe(Recipe):
    name="pr_branch_policy"; patterns=('base branch policy prohibits', '--auto flag')
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"note":'handled by PR gate'})
