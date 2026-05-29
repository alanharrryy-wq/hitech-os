from __future__ import annotations
from .patterns import SEVERE,SECRET_ASSIGN_RE
def severe_hits(text:str)->list[str]:
    hits=[]
    for name,rgx in SEVERE:
        if rgx.search(text): hits.append(name)
    return sorted(set(hits))
def redact_literal_keys(text:str)->str:
    for _,rgx in SEVERE: text=rgx.sub("<REDACTED_SECRET>",text)
    return SECRET_ASSIGN_RE.sub(lambda m:m.group(1)+"=<REDACTED>",text)
