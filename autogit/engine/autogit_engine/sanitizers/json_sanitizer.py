from __future__ import annotations
import json
from ..paths import redact_local_paths
def sanitize_value(obj):
    if isinstance(obj,dict):
        out={}
        for k,v in obj.items():
            lk=str(k).lower()
            if any(s in lk for s in ["api_key","apikey","token","secret","password","client_secret","access_token","refresh_token"]): out[k]=""
            elif lk in {"owner_email","email","owner"} and isinstance(v,str) and "@" in v: out[k]="owner@example.invalid"
            elif lk=="pin_default": out[k]="000000"
            else: out[k]=sanitize_value(v)
        return out
    if isinstance(obj,list): return [sanitize_value(x) for x in obj]
    if isinstance(obj,str): return redact_local_paths(obj)
    return obj
def sanitize_json_text(text:str)->str: return json.dumps(sanitize_value(json.loads(text)),ensure_ascii=False,indent=2)+"\n"
