from __future__ import annotations
import json
from typing import Any
from .errors import ContractError, TargetNotFound
from .hashing import pretty_json_bytes


def _decode(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def patch_json_bytes(data: bytes, pointers: dict[str, Any], expected: dict[str, Any] | None = None) -> bytes:
    doc = json.loads(data.decode("utf-8-sig"))
    for pointer, desired in pointers.items():
        if not pointer.startswith("/") or pointer == "/": raise ContractError("V1 requires non-root JSON Pointer")
        tokens = [_decode(t) for t in pointer[1:].split("/")]
        parent = doc
        for token in tokens[:-1]:
            if isinstance(parent, list):
                try: parent = parent[int(token)]
                except (ValueError, IndexError): raise TargetNotFound(pointer)
            elif isinstance(parent, dict) and token in parent: parent = parent[token]
            else: raise TargetNotFound(pointer)
        key = tokens[-1]
        try:
            current = parent[int(key)] if isinstance(parent, list) else parent[key]
        except (ValueError, IndexError, KeyError, TypeError):
            raise TargetNotFound(pointer)
        if not _scalar(current) or not _scalar(desired): raise ContractError("V1 JSON mutation is scalar-only")
        if type(current) is not type(desired): raise ContractError("V1 JSON mutation cannot change scalar type")
        if expected is not None and pointer in expected and current != expected[pointer]:
            raise ContractError(f"expected current value mismatch at {pointer}")
        if isinstance(parent, list): parent[int(key)] = desired
        else: parent[key] = desired
    return pretty_json_bytes(doc)
