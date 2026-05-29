from __future__ import annotations
from .base import Recipe,RecipeResult
class DirtyWorktreeRecipe(Recipe):
    name="dirty_worktree"; patterns=('working tree dirty', 'dirty_worktree')
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"note":'blocked before push'})
