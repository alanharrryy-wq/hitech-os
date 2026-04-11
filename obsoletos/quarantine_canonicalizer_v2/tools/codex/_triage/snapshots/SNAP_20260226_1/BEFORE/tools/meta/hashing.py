from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_text(text: str) -> str:
    digest = hashlib.sha256()
    digest.update(text.encode("utf-8"))
    return digest.hexdigest()


def sha256_bytes(blob: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(blob)
    return digest.hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def stable_line(value: str) -> str:
    collapsed = " ".join(value.strip().split())
    return collapsed.lower()


def deterministic_debt_id(repo_name: str, line: str) -> str:
    normalized = f"{repo_name}|{stable_line(line)}"
    return sha256_text(normalized)


def combine_hashes(parts: list[str]) -> str:
    joined = "\n".join(parts)
    return sha256_text(joined)
