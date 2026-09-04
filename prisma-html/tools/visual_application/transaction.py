from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from typing import Any
from .errors import TamperedBackup, TamperedTransaction, RollbackWouldOverwriteNewerWork, RollbackFailure
from .hashing import canonical_json_bytes, pretty_json_bytes, sha256_bytes, sha256_file
from .security import validate_tx_id, contained_path, ensure_path_object_contained

_TX_KEYS={"schema","transactionId","targetId","authorityCommit","state","files","transactionDigest"}
_ROW_KEYS={"path","existedBefore","beforeSha256","backupPath","backupSha256","afterSha256"}

def atomic_write(path:Path,data:bytes)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.is_symlink():
        raise TamperedTransaction(f"refusing atomic write through symlink: {path}")
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
    try:
        with os.fdopen(fd,"wb") as fh:
            fh.write(data); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def _payload(tx:dict[str,Any])->dict[str,Any]:
    return {k:v for k,v in tx.items() if k!="transactionDigest"}

def _digest(tx:dict[str,Any])->str:
    return sha256_bytes(canonical_json_bytes(_payload(tx)))

def _validate_structure(tx:Any, tx_id:str|None=None)->dict[str,Any]:
    if not isinstance(tx,dict) or set(tx)!=_TX_KEYS:
        raise TamperedTransaction("transaction structure invalid")
    if tx.get("schema")!="prisma.visual.application.transaction.v1":
        raise TamperedTransaction("transaction schema invalid")
    validate_tx_id(tx.get("transactionId"))
    if tx_id is not None and tx["transactionId"]!=tx_id:
        raise TamperedTransaction("transactionId mismatch")
    if not isinstance(tx.get("targetId"),str) or not tx["targetId"]:
        raise TamperedTransaction("targetId missing")
    if tx.get("state") not in {"OPEN","APPLIED","ROLLED_BACK"}:
        raise TamperedTransaction("transaction state invalid")
    rows=tx.get("files")
    if not isinstance(rows,list) or not rows:
        raise TamperedTransaction("transaction files invalid")
    seen=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!=_ROW_KEYS:
            raise TamperedTransaction("transaction file row invalid")
        if not isinstance(row["path"],str) or not row["path"] or row["path"] in seen:
            raise TamperedTransaction("duplicate/invalid transaction path")
        seen.add(row["path"])
        if not isinstance(row["existedBefore"],bool):
            raise TamperedTransaction("existedBefore invalid")
        for key in ("beforeSha256","backupSha256","afterSha256"):
            val=row[key]
            if val is not None and (not isinstance(val,str) or len(val)!=64 or any(c not in "0123456789abcdef" for c in val)):
                raise TamperedTransaction(f"{key} invalid")
        if row["existedBefore"]:
            if not isinstance(row["backupPath"],str) or not row["backupPath"] or row["beforeSha256"] is None or row["backupSha256"] is None:
                raise TamperedTransaction("backup metadata missing")
        elif any(row[k] is not None for k in ("beforeSha256","backupPath","backupSha256")):
            raise TamperedTransaction("nonexistent-before row has backup metadata")
    if tx.get("transactionDigest")!=_digest(tx):
        raise TamperedTransaction("transaction digest mismatch")
    return tx

def save_transaction(tx_root:Path, tx:dict[str,Any])->None:
    validate_tx_id(tx["transactionId"])
    tx["transactionDigest"]=_digest(tx)
    tx_dir=tx_root/tx["transactionId"]
    atomic_write(tx_dir/"transaction.json",pretty_json_bytes(tx))

def create_transaction(repo_root:Path,tx_root:Path,tx_id:str,target_id:str,paths:list[Path],authority_commit:str|None)->dict[str,Any]:
    validate_tx_id(tx_id)
    repo_root=repo_root.resolve()
    tx_root=ensure_path_object_contained(repo_root,tx_root,field="transactions root")
    tx_root.mkdir(parents=True,exist_ok=True)
    tx_dir=tx_root/tx_id
    backup=tx_dir/"backup"
    backup.mkdir(parents=True,exist_ok=False)
    records=[]
    unique={}
    for path in paths:
        safe=ensure_path_object_contained(repo_root,path,field="transaction file")
        unique[safe.resolve(strict=False).as_posix()]=safe
    for path in sorted(unique.values(), key=lambda p:p.as_posix()):
        rel=path.resolve(strict=False).relative_to(repo_root).as_posix()
        exists=path.exists()
        if exists and path.is_symlink():
            raise TamperedTransaction(f"transaction path is symlink: {rel}")
        data=path.read_bytes() if exists else b""
        bpath=backup/rel
        if exists:
            atomic_write(bpath,data)
        records.append({
            "path":rel,"existedBefore":exists,
            "beforeSha256":sha256_bytes(data) if exists else None,
            "backupPath":bpath.relative_to(tx_dir).as_posix() if exists else None,
            "backupSha256":sha256_file(bpath) if exists else None,
            "afterSha256":None
        })
    tx={"schema":"prisma.visual.application.transaction.v1","transactionId":tx_id,"targetId":target_id,
        "authorityCommit":authority_commit,"state":"OPEN","files":records,"transactionDigest":""}
    save_transaction(tx_root,tx)
    return tx

def load_transaction(tx_root:Path,tx_id:str)->dict[str,Any]:
    validate_tx_id(tx_id)
    path=tx_root/tx_id/"transaction.json"
    try:
        tx=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise TamperedTransaction(f"cannot load transaction: {exc}") from exc
    return _validate_structure(tx,tx_id)

def mark_after(repo_root:Path,tx_root:Path,tx:dict[str,Any])->None:
    _validate_structure(tx)
    for row in tx["files"]:
        p=contained_path(repo_root,row["path"],field="transaction file")
        row["afterSha256"]=sha256_file(p) if p.exists() else None
    tx["state"]="APPLIED"
    save_transaction(tx_root,tx)

def _prevalidate_rollback(repo_root:Path,tx_root:Path,tx:dict[str,Any])->list[dict[str,Any]]:
    tx=_validate_structure(tx)
    tx_dir=tx_root/tx["transactionId"]
    staged=[]
    for row in tx["files"]:
        p=contained_path(repo_root,row["path"],field="transaction file")
        current=sha256_file(p) if p.exists() else None
        if current!=row.get("afterSha256"):
            raise RollbackWouldOverwriteNewerWork(row["path"])
        backup_bytes=None
        if row["existedBefore"]:
            b=contained_path(tx_dir,row["backupPath"],must_exist=True,field="backupPath")
            if not b.is_file() or b.is_symlink() or sha256_file(b)!=row["backupSha256"]:
                raise TamperedBackup(row["path"])
            backup_bytes=b.read_bytes()
            if sha256_bytes(backup_bytes)!=row["beforeSha256"]:
                raise TamperedBackup(row["path"])
        staged.append({"row":row,"path":p,"restoreBytes":backup_bytes,
                       "postExists":p.exists(),"postBytes":p.read_bytes() if p.exists() else None})
    return staged

def rollback(repo_root:Path,tx_root:Path,tx:dict[str,Any])->dict[str,Any]:
    tx=_validate_structure(tx)
    if tx.get("state")=="ROLLED_BACK":
        return {"schema":"prisma.visual.application.rollback-result.v1","transactionId":tx["transactionId"],"status":"ALREADY_ROLLED_BACK","restored":[]}
    if tx.get("state")!="APPLIED":
        raise TamperedTransaction("only APPLIED transactions can be rolled back")
    staged=_prevalidate_rollback(repo_root,tx_root,tx)
    restored=[]
    try:
        for item in staged:
            p=item["path"]
            if item["row"]["existedBefore"]:
                atomic_write(p,item["restoreBytes"])
            elif p.exists():
                if p.is_symlink(): raise TamperedTransaction(f"rollback target became symlink: {item['row']['path']}")
                p.unlink()
            restored.append(item["row"]["path"])
    except Exception as exc:
        recovery_errors=[]
        for item in reversed(staged):
            p=item["path"]
            try:
                if item["postExists"]:
                    atomic_write(p,item["postBytes"])
                elif p.exists():
                    p.unlink()
            except Exception as rec:
                recovery_errors.append(f"{item['row']['path']}:{rec}")
        raise RollbackFailure("rollback execution failed; post-apply state restoration attempted",
                              details={"cause":repr(exc),"recoveryErrors":recovery_errors}) from exc
    tx["state"]="ROLLED_BACK"
    save_transaction(tx_root,tx)
    return {"schema":"prisma.visual.application.rollback-result.v1","transactionId":tx["transactionId"],"status":"ROLLED_BACK","restored":restored}
