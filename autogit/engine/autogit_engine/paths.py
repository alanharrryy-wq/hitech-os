from __future__ import annotations
from pathlib import Path
import re
WINDOWS_DRIVE_RE=re.compile(r"(?i)(?<![A-Za-z0-9_])(?:[A-Z]:\\[^\s`)'\"{}<>|]+)")
USER_PATH_RE=re.compile(r"(?i)(?<![A-Za-z0-9_])C:\\Users\\[^\s`)'\"{}<>|]+")
UNIX_LOCAL_RE=re.compile(r"(?i)(?:/mnt/data|/home)/[^\s`)'\"{}<>|]+")
def contains_local_path(text:str)->bool: return bool(WINDOWS_DRIVE_RE.search(text) or USER_PATH_RE.search(text) or UNIX_LOCAL_RE.search(text))
def redact_local_paths(text:str)->str:
    def drive(m):
        s=m.group(0); low=s.lower()
        if low.startswith("f:\\repos\\hitech-os"): return s.replace("F:\\repos\\hitech-os","<REPO_ROOT>").replace("f:\\repos\\hitech-os","<REPO_ROOT>")
        if low.startswith("f:\\descargasf"): return s.replace("F:\\descargasf","<OUTPUT_DIR>").replace("f:\\descargasf","<OUTPUT_DIR>")
        if low.startswith("c:\\users"): return "<USER_HOME>"
        return "<LOCAL_PATH>"
    text=USER_PATH_RE.sub("<USER_HOME>",text); text=WINDOWS_DRIVE_RE.sub(drive,text)
    return UNIX_LOCAL_RE.sub(lambda m:"<SANDBOX_FILE>" if m.group(0).lower().startswith("/mnt/data") else "<HOME_PATH>",text)
