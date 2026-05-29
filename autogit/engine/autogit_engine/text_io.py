from __future__ import annotations
from pathlib import Path
def read_text_lossless(path:Path,limit:int|None=None)->tuple[str,str]:
    data=path.read_bytes() if limit is None else path.read_bytes()[:limit]
    if b"\x00" in data: raise ValueError("binary/null byte file")
    for enc in ("utf-8-sig","utf-8","cp1252","latin-1"):
        try: return data.decode(enc),enc
        except Exception: pass
    return data.decode("utf-8","replace"),"utf-8-replace"
def write_utf8(path:Path,text:str)->None:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8",errors="replace",newline="")
def trim_whitespace(path:Path)->bool:
    before=path.read_bytes(); newline=b"\r\n" if b"\r\n" in before else b"\n"
    after=newline.join(line.rstrip(b" \t") for line in before.splitlines()).rstrip(b"\r\n")+newline
    if before!=after: path.write_bytes(after); return True
    return False
