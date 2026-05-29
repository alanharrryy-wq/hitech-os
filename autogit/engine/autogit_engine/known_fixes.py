from __future__ import annotations
import json
from .recipes.registry import matching
def apply_known_fixes(ctx,text,report_path):
    rows=[]
    for recipe in matching(text):
        result=recipe.apply(ctx,text); rows.append({"name":result.name,"applied":result.applied,"details":result.details})
    report_path.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8"); return rows
