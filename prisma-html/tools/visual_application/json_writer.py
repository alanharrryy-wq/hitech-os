from __future__ import annotations
import json, math, re
from typing import Any
from .errors import ContractError, TargetNotFound
from .hashing import pretty_json_bytes

_ARRAY_INDEX = re.compile(r"^(?:0|[1-9][0-9]*)$")

def _decode(token: str) -> str:
    out=[]; i=0
    while i<len(token):
        if token[i]=="~":
            if i+1>=len(token) or token[i+1] not in "01":
                raise ContractError("invalid JSON Pointer escape")
            out.append("/" if token[i+1]=="1" else "~"); i+=2
        else:
            out.append(token[i]); i+=1
    return "".join(out)

def _scalar(value: Any) -> bool:
    return value is None or isinstance(value,(str,int,float,bool))

def _finite(value: Any) -> bool:
    return not isinstance(value,float) or math.isfinite(value)

def _loads_strict(data: bytes) -> Any:
    def bad(token: str):
        raise ContractError(f"non-finite JSON constant forbidden: {token}")
    try:
        return json.loads(data.decode("utf-8-sig"), parse_constant=bad)
    except UnicodeDecodeError as exc:
        raise ContractError("JSON must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON: {exc}") from exc

def _index(token: str, pointer: str) -> int:
    if not _ARRAY_INDEX.fullmatch(token):
        raise TargetNotFound(pointer)
    return int(token)

def _under_root(pointer: str, root: str) -> bool:
    return pointer == root or pointer.startswith(root + "/")

def patch_json_bytes(data: bytes, pointers: dict[str, Any], expected: dict[str, Any] | None = None, *, root: str | None = None) -> bytes:
    doc=_loads_strict(data)
    for pointer,desired in pointers.items():
        if not isinstance(pointer,str) or not pointer.startswith("/") or pointer=="/":
            raise ContractError("V1 requires non-root JSON Pointer")
        if root is not None and not _under_root(pointer,root):
            raise ContractError(f"JSON pointer escapes governed root: {pointer}")
        tokens=[_decode(t) for t in pointer[1:].split("/")]
        parent=doc
        for token in tokens[:-1]:
            if isinstance(parent,list):
                idx=_index(token,pointer)
                if idx>=len(parent): raise TargetNotFound(pointer)
                parent=parent[idx]
            elif isinstance(parent,dict) and token in parent:
                parent=parent[token]
            else:
                raise TargetNotFound(pointer)
        key=tokens[-1]
        try:
            if isinstance(parent,list):
                idx=_index(key,pointer)
                if idx>=len(parent): raise TargetNotFound(pointer)
                current=parent[idx]
            else:
                current=parent[key]
        except (KeyError,TypeError):
            raise TargetNotFound(pointer)
        if not _scalar(current) or not _scalar(desired) or not _finite(current) or not _finite(desired):
            raise ContractError("V1 JSON mutation is finite scalar-only")
        if type(current) is not type(desired):
            raise ContractError("V1 JSON mutation cannot change scalar type")
        if expected is not None:
            if pointer not in expected:
                raise ContractError(f"expectedCurrent must cover every mutated pointer: {pointer}")
            if current != expected[pointer]:
                raise ContractError(f"expected current value mismatch at {pointer}")
        if isinstance(parent,list): parent[idx]=desired
        else: parent[key]=desired
    if expected is not None and set(expected) != set(pointers):
        raise ContractError("expectedCurrent contains pointers not being mutated")
    return pretty_json_bytes(doc)
