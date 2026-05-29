from __future__ import annotations
from dataclasses import dataclass
@dataclass
class RecipeResult:
    name:str; applied:bool; details:dict
class Recipe:
    name="base"; patterns:tuple[str,...]=()
    def matches(self,text:str)->bool:
        low=(text or "").lower(); return any(p.lower() in low for p in self.patterns)
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        return RecipeResult(self.name,False,{"reason":"not implemented"})
