from __future__ import annotations

import json
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Iterable, Mapping, Sequence, Type


ISO_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ContractValidationError(ValueError):
    """Raised when a payload violates a canonical contract."""


def utc_now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_iso_timestamp(value: str) -> bool:
    return bool(ISO_PATTERN.match(value))


def stable_json(payload: Any) -> str:
    if is_dataclass(payload):
        payload = asdict(payload)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(payload: Any) -> str:
    return sha256(stable_json(payload).encode("utf-8")).hexdigest()


def deterministic_id(prefix: str, *parts: Any) -> str:
    material = "::".join(str(part) for part in parts)
    digest = sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def ensure_mapping(contract_name: str, payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise ContractValidationError(f"{contract_name} must be a mapping, got {type(payload).__name__}")
    return payload


def ensure_required(contract_name: str, payload: Mapping[str, Any], fields: Sequence[str]) -> None:
    missing = [field for field in fields if field not in payload]
    if missing:
        raise ContractValidationError(f"{contract_name} missing required fields: {', '.join(missing)}")


def ensure_type(contract_name: str, payload: Mapping[str, Any], field: str, expected: Type[Any] | tuple[Type[Any], ...]) -> None:
    if field in payload and not isinstance(payload[field], expected):
        expected_name = (
            ", ".join(t.__name__ for t in expected)
            if isinstance(expected, tuple)
            else expected.__name__
        )
        raise ContractValidationError(
            f"{contract_name}.{field} must be {expected_name}, got {type(payload[field]).__name__}"
        )


def ensure_string(contract_name: str, payload: Mapping[str, Any], field: str, allow_empty: bool = False) -> None:
    ensure_type(contract_name, payload, field, str)
    if not allow_empty and not payload[field].strip():
        raise ContractValidationError(f"{contract_name}.{field} must be a non-empty string")


def ensure_list(contract_name: str, payload: Mapping[str, Any], field: str) -> None:
    ensure_type(contract_name, payload, field, list)


def ensure_mapping_field(contract_name: str, payload: Mapping[str, Any], field: str) -> None:
    ensure_type(contract_name, payload, field, Mapping)


def ensure_iso_timestamp(contract_name: str, payload: Mapping[str, Any], field: str) -> None:
    ensure_string(contract_name, payload, field)
    if not is_iso_timestamp(payload[field]):
        raise ContractValidationError(f"{contract_name}.{field} must be an ISO-8601 UTC timestamp ending in Z")


def ensure_enum_value(contract_name: str, payload: Mapping[str, Any], field: str, enum_type: Type[Any]) -> None:
    ensure_string(contract_name, payload, field)
    allowed = {item.value for item in enum_type}
    if payload[field] not in allowed:
        raise ContractValidationError(
            f"{contract_name}.{field} must be one of {sorted(allowed)}, got {payload[field]!r}"
        )


def ensure_optional_enum_value(contract_name: str, payload: Mapping[str, Any], field: str, enum_type: Type[Any]) -> None:
    if field in payload and payload[field] is not None:
        ensure_enum_value(contract_name, payload, field, enum_type)


def ensure_list_of_strings(contract_name: str, payload: Mapping[str, Any], field: str) -> None:
    ensure_list(contract_name, payload, field)
    bad = [item for item in payload[field] if not isinstance(item, str)]
    if bad:
        raise ContractValidationError(f"{contract_name}.{field} must contain only strings")


def ensure_list_of_mappings(contract_name: str, payload: Mapping[str, Any], field: str) -> None:
    ensure_list(contract_name, payload, field)
    bad = [item for item in payload[field] if not isinstance(item, Mapping)]
    if bad:
        raise ContractValidationError(f"{contract_name}.{field} must contain only mappings")
