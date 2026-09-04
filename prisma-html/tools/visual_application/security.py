from __future__ import annotations
import re
from pathlib import Path, PurePosixPath
from .errors import ContractError, PathSecurityError

TX_ID_RE = re.compile(r"^gvae-[a-z0-9][a-z0-9_-]{0,63}$")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
TASK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")

def validate_tx_id(value: str) -> str:
    if not isinstance(value, str) or not TX_ID_RE.fullmatch(value):
        raise ContractError("invalid transactionId")
    return value

def validate_hex(value: str, width: int, field: str) -> str:
    rx = HEX40_RE if width == 40 else HEX64_RE
    if not isinstance(value, str) or not rx.fullmatch(value):
        raise ContractError(f"{field} must be lowercase hex length {width}")
    return value

def normalize_rel(raw: str, *, field: str = "path") -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise PathSecurityError(f"{field} invalid")
    normalized = raw.replace("\\", "/")
    p = PurePosixPath(normalized)
    if p.is_absolute() or ":" in p.parts[0] or any(part in ("", ".", "..") for part in p.parts):
        raise PathSecurityError(f"{field} must be a contained relative path")
    return p.as_posix()

def contained_path(root: Path, raw: str, *, must_exist: bool = False, field: str = "path") -> Path:
    rel = normalize_rel(raw, field=field)
    root = root.resolve()
    candidate = root.joinpath(*PurePosixPath(rel).parts)
    cur = root
    for part in PurePosixPath(rel).parts:
        cur = cur / part
        if cur.exists() and cur.is_symlink():
            raise PathSecurityError(f"{field} crosses symlink: {rel}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise PathSecurityError(f"{field} escapes root: {rel}")
    if must_exist and not candidate.exists():
        raise PathSecurityError(f"{field} missing: {rel}")
    return candidate

def ensure_path_object_contained(root: Path, path: Path, *, must_exist: bool = False, field: str = "path") -> Path:
    root = root.resolve()
    try:
        rel = path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        raise PathSecurityError(f"{field} escapes root")
    return contained_path(root, rel, must_exist=must_exist, field=field)
