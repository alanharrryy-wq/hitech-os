from __future__ import annotations
import re
from .base import Recipe,RecipeResult
class CodeownersCoverageRecipe(Recipe):
    name="codeowners-coverage"; patterns=("CODEOWNERS","unowned_file_count","apps/code-atlas")
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        target="apps/code-atlas/code-atlas.py"
        if not (ctx.repo/target).exists(): return RecipeResult(self.name,False,{"reason":"target missing"})
        codeowners=None
        for rel in [".github/CODEOWNERS","CODEOWNERS","docs/CODEOWNERS"]:
            if (ctx.repo/rel).exists(): codeowners=ctx.repo/rel; break
        if codeowners is None:
            codeowners=ctx.repo/".github/CODEOWNERS"; codeowners.parent.mkdir(parents=True,exist_ok=True); old=""
        else: old=codeowners.read_text(encoding="utf-8",errors="replace")
        if re.search(r"(?m)^\s*/?apps/code-atlas(?:/\*\*|/.*|\s)",old.replace("\\","/")): return RecipeResult(self.name,False,{"reason":"already covered"})
        owner="@alanharrryy-wq"; codeowners.write_text(old.rstrip()+f"\n# AutoGit: Code Atlas ownership\n/apps/code-atlas/** {owner}\n",encoding="utf-8")
        return RecipeResult(self.name,True,{"path":str(codeowners),"owner":owner})
