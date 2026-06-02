from __future__ import annotations
from pathlib import Path
import re
WINDOWS_DRIVE_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])(?:[A-Z]:[\\/][^\s`)'\"{}<>|]+)")
USER_PATH_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])C:[\\/]Users[\\/][^\s`)'\"{}<>|]+")
UNIX_LOCAL_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])(?:/mnt/data|/home/[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+)(?:/[^\s`)'\"{}<>|]*)?")
def contains_local_path(text:str)->bool: return bool(WINDOWS_DRIVE_RE.search(text) or USER_PATH_RE.search(text) or UNIX_LOCAL_RE.search(text))
def redact_local_paths(text:str)->str:
    def drive(m):
        s=m.group(0); low=s.lower()
        if low.startswith("f:\\repos\\hitech-os") or low.startswith("f:/repos/hitech-os"):
            return s.replace("F:\\repos\\hitech-os","<REPO_ROOT>").replace("f:\\repos\\hitech-os","<REPO_ROOT>").replace("F:/repos/hitech-os","<REPO_ROOT>").replace("f:/repos/hitech-os","<REPO_ROOT>")
        if low.startswith("f:\\descargasf") or low.startswith("f:/descargasf"):
            return s.replace("F:\\descargasf","<OUTPUT_DIR>").replace("f:\\descargasf","<OUTPUT_DIR>").replace("F:/descargasf","<OUTPUT_DIR>").replace("f:/descargasf","<OUTPUT_DIR>")
        if low.startswith("c:\\users") or low.startswith("c:/users"): return "<USER_HOME>"
        return "<LOCAL_PATH>"
    text=USER_PATH_RE.sub("<USER_HOME>",text); text=WINDOWS_DRIVE_RE.sub(drive,text)
    return UNIX_LOCAL_RE.sub(lambda m:"<SANDBOX_FILE>" if m.group(0).lower().startswith("/mnt/data") else "<HOME_PATH>",text)

def repo_path(repo: Path, rel: str | Path) -> Path:
    """Join a Git-style relative path to repo safely on any OS.

    Git reports paths with forward slashes. Building paths by forcing
    backslashes breaks Linux/macOS smoke tests and can hide package bugs.
    This helper keeps Windows compatibility while remaining portable.
    """
    rel_s = str(rel).replace("\\", "/")
    if Path(rel_s).is_absolute():
        raise ValueError(f"Unsafe repository-relative path: {rel_s!r}")
    parts = [part for part in rel_s.split("/") if part not in {"", "."}]
    if any(part == ".." for part in parts):
        raise ValueError(f"Unsafe repository-relative path: {rel_s!r}")
    if parts and ":" in parts[0]:
        raise ValueError(f"Unsafe repository-relative path: {rel_s!r}")
    return Path(repo).joinpath(*parts)
