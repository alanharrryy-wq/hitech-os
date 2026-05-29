from __future__ import annotations
KNOWN={"spawnSync git ENOBUFS":"increase git ls-files maxBuffer","new blank line at EOF":"trim final whitespace","base branch policy prohibits":"enable auto merge","LOCAL_PATH_REMAINS":"sanitize local paths"}
def recognize(text):
    low=text.lower(); return [{"pattern":k,"recommendation":v} for k,v in KNOWN.items() if k.lower() in low]
