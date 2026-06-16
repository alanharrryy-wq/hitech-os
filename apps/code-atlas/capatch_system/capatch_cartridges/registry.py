from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Cartridge, CartridgePolicy


def _tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(str(item) for item in value if str(item).strip())
    return ()


def cartridge_from_dict(data: dict[str, Any]) -> Cartridge:
    policy_raw = data.get('policy') if isinstance(data.get('policy'), dict) else {}
    policy = CartridgePolicy(
        allowed_paths=_tuple(policy_raw.get('allowed_paths')),
        excluded_paths=_tuple(policy_raw.get('excluded_paths')),
        required_verifiers=_tuple(policy_raw.get('required_verifiers')),
        evidence_required=_tuple(policy_raw.get('evidence_required')),
        risk_gates=_tuple(policy_raw.get('risk_gates')),
        notes=_tuple(policy_raw.get('notes')),
    )
    return Cartridge(
        cartridge_id=str(data.get('id') or data.get('cartridge_id') or '').strip(),
        title=str(data.get('title') or data.get('id') or '').strip(),
        version=str(data.get('version') or '1.0.0'),
        inherits=_tuple(data.get('inherits')),
        tags=_tuple(data.get('tags')),
        policy=policy,
        raw=dict(data),
    )


def builtin_cartridge_dir(base_dir: Path | None = None) -> Path:
    root = Path(base_dir or Path(__file__).resolve().parent)
    return root / 'packs'


def load_builtin_cartridges(base_dir: Path | None = None) -> dict[str, Cartridge]:
    pack_dir = builtin_cartridge_dir(base_dir)
    registry: dict[str, Cartridge] = {}
    if not pack_dir.exists():
        return registry
    for path_value in sorted(pack_dir.glob('*.json')):
        data = json.loads(path_value.read_text(encoding='utf-8'))
        cartridge = cartridge_from_dict(data)
        if cartridge.cartridge_id:
            registry[cartridge.cartridge_id] = cartridge
    return registry


def resolve_cartridge_stack(requested: list[str], registry: dict[str, Cartridge] | None = None) -> list[Cartridge]:
    registry = registry or load_builtin_cartridges()
    resolved: list[Cartridge] = []
    seen: set[str] = set()

    def add(cartridge_id: str) -> None:
        if cartridge_id in seen:
            return
        cartridge = registry.get(cartridge_id)
        if cartridge is None:
            raise KeyError(f'Unknown cartridge: {cartridge_id}')
        for parent_id in cartridge.inherits:
            add(parent_id)
        seen.add(cartridge_id)
        resolved.append(cartridge)

    for item in requested:
        add(str(item))
    return resolved
