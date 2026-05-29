from __future__ import annotations
import re
def summarize_checks(text):
    rows=[]
    for line in text.splitlines():
        parts=re.split(r"\s{2,}|\t+",line.strip())
        if len(parts)>=2: rows.append({"name":parts[0],"state":parts[1],"raw":line})
    return {"rows":rows,"failures":[r for r in rows if r.get("state","").lower() in {"fail","failure","cancelled"}]}
