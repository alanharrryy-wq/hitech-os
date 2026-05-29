from __future__ import annotations
from .base import Recipe,RecipeResult
class WhitespaceRecipe(Recipe):
    name="whitespace"; patterns=('new blank line at EOF', 'trailing whitespace')
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"note":'handled by diff validator'})
