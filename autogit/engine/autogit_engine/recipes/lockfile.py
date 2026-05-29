from __future__ import annotations
from .base import Recipe,RecipeResult
class LockfileRecipe(Recipe):
    name="lockfile"; patterns=('package-lock', 'pnpm-lock', 'yarn.lock')
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"note":'grouped under deps'})
