from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib,os
TEXT_EXTS={".ts",".tsx",".js",".jsx",".mjs",".cjs",".json",".jsonc",".css",".scss",".html",".md",".mdx",".txt",".yml",".yaml",".toml",".ini",".env",".example",".prisma",".sql",".py",".ps1",".psm1",".bat",".cmd",".sh",".xml",".svg",".csv",".tsv",".lock"}
BINARY_OK_EXTS={".png",".jpg",".jpeg",".webp",".gif",".ico",".bmp",".mp3",".wav",".mp4",".mov",".pdf"}
@dataclass
class FileMeta:
    rel:str; status:str; exists:bool; size:int; ext:str; sha256:str|None; is_text:bool; is_binary_ok:bool
def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def probably_text(path:Path,rel:str)->bool:
    if Path(rel).suffix.lower() in TEXT_EXTS: return True
    try: return b"\x00" not in path.read_bytes()[:4096]
    except Exception: return False
def build_meta(repo:Path,rel:str,status:str)->FileMeta:
    full=repo/rel.replace("/",os.sep); exists=full.exists(); ext=Path(rel).suffix.lower()
    if not exists: return FileMeta(rel,status,False,0,ext,None,False,False)
    return FileMeta(rel,status,True,full.stat().st_size,ext,sha256(full) if full.is_file() else None,probably_text(full,rel),ext in BINARY_OK_EXTS)
