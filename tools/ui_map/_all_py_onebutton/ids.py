from __future__ import annotations

from hashlib import sha256

DEFAULT_HASH_LENGTH = 10


def _normalize_seed(seed: str) -> str:
    normalized = seed.replace("\\", "/").strip()
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized


def stable_short_hash(seed: str, length: int = DEFAULT_HASH_LENGTH) -> str:
    if length < 6:
        raise ValueError("length must be >= 6")
    normalized = _normalize_seed(seed)
    return sha256(normalized.encode("utf-8")).hexdigest()[:length]


def component_id(file_path: str, export_name: str) -> str:
    return f"cmp_{stable_short_hash(f'{_normalize_seed(file_path)}::{export_name}')}"


def route_id(route_path: str) -> str:
    return f"rte_{stable_short_hash(_normalize_seed(route_path))}"


def state_id(file_path: str) -> str:
    return f"stt_{stable_short_hash(_normalize_seed(file_path))}"


def style_id(file_path: str) -> str:
    return f"sty_{stable_short_hash(_normalize_seed(file_path))}"


def asset_id(file_path: str) -> str:
    return f"ast_{stable_short_hash(_normalize_seed(file_path))}"


def hotspot_id(screen_or_global: str, title: str) -> str:
    return f"hsp_{stable_short_hash(f'{screen_or_global}::{title}')}"
