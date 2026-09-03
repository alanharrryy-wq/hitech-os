from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from typing import Any
from .errors import TamperedBackup, RollbackWouldOverwriteNewerWork
from .hashing import pretty_json_bytes, sha256_bytes, sha256_file


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
    try:
        with os.fdopen(fd,"wb") as fh: fh.write(data); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def create_transaction(repo_root: Path, tx_root: Path, tx_id: str, paths: list[Path], authority_commit: str|None) -> dict[str,Any]:
    tx_dir=tx_root/tx_id; backup=tx_dir/"backup"; backup.mkdir(parents=True,exist_ok=False)
    records=[]
    for path in sorted(set(paths)):
        rel=path.relative_to(repo_root).as_posix(); exists=path.exists(); data=path.read_bytes() if exists else b""
        bpath=backup/rel; bpath.parent.mkdir(parents=True,exist_ok=True)
        if exists: bpath.write_bytes(data)
        records.append({"path":rel,"existedBefore":exists,"beforeSha256":sha256_bytes(data) if exists else None,"backupPath":bpath.relative_to(tx_dir).as_posix() if exists else None,"backupSha256":sha256_file(bpath) if exists else None,"afterSha256":None})
    tx={"schema":"prisma.visual.application.transaction.v1","transactionId":tx_id,"authorityCommit":authority_commit,"state":"OPEN","files":records}
    (tx_dir/"transaction.json").write_bytes(pretty_json_bytes(tx)); return tx
def save_transaction(tx_root: Path, tx: dict[str,Any]) -> None:
    (tx_root/tx["transactionId"]/"transaction.json").write_bytes(pretty_json_bytes(tx))
def load_transaction(tx_root: Path, tx_id: str) -> dict[str,Any]:
    return json.loads((tx_root/tx_id/"transaction.json").read_text(encoding="utf-8"))
def mark_after(repo_root:Path,tx_root:Path,tx:dict[str,Any]) -> None:
    for row in tx["files"]:
        p=repo_root/row["path"]; row["afterSha256"]=sha256_file(p) if p.exists() else None
    tx["state"]="APPLIED"; save_transaction(tx_root,tx)
def rollback(repo_root:Path,tx_root:Path,tx:dict[str,Any]) -> dict[str,Any]:
    if tx.get("state")=="ROLLED_BACK": return {"schema":"prisma.visual.application.rollback-result.v1","transactionId":tx["transactionId"],"status":"ALREADY_ROLLED_BACK","restored":[]}
    tx_dir=tx_root/tx["transactionId"]
    restored=[]
    for row in tx["files"]:
        p=repo_root/row["path"]; current=sha256_file(p) if p.exists() else None
        if row.get("afterSha256") is not None and current!=row.get("afterSha256"): raise RollbackWouldOverwriteNewerWork(row["path"])
        if row["existedBefore"]:
            b=tx_dir/row["backupPath"]
            if not b.is_file() or sha256_file(b)!=row["backupSha256"]: raise TamperedBackup(row["path"])
            atomic_write(p,b.read_bytes())
        elif p.exists(): p.unlink()
        restored.append(row["path"])
    tx["state"]="ROLLED_BACK"; save_transaction(tx_root,tx)
    return {"schema":"prisma.visual.application.rollback-result.v1","transactionId":tx["transactionId"],"status":"ROLLED_BACK","restored":restored}
