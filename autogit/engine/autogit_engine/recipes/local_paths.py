from __future__ import annotations
from .base import Recipe,RecipeResult
class LocalPathRecipe(Recipe):
    name="local_paths"; patterns=('LOCAL_PATH_REMAINS', 'F:\\', 'C:\\Users', '/mnt/data')
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"note":'handled by sanitizer'})
