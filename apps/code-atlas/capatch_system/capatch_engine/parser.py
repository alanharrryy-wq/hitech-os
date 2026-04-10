from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from capatch_contracts.operations import INT_FIELD_NAMES, REQUIRED_FIELDS, TEXT_FIELD_NAMES, build_operation_spec
from capatch_ops.base import fail, validate_flag_value, validate_positive_intish


def validate_optional_already_applied_markers(label: str, payload: dict[str, Any]) -> None:
    has_text = bool(str(payload.get("already_applied_text") or ""))
    has_regex = bool(str(payload.get("already_applied_regex") or ""))
    if has_text and has_regex:
        fail(f"La operacion {label} no debe traer already_applied_text y already_applied_regex al mismo tiempo.")


def validate_operation_payload(op_type: str, label: str, file_value: str, payload: dict[str, Any]) -> None:
    if op_type != "ApplySet" and not file_value:
        fail(f"La operacion {label or op_type} no trae file.")
    required = REQUIRED_FIELDS.get(op_type)
    if required is None:
        supported = ", ".join(sorted(REQUIRED_FIELDS))
        fail(f"Tipo de operacion no soportado: {op_type}. Soportados: {supported}")
    for field_name in required:
        if field_name not in payload:
            fail(f"La operacion {label or op_type} requiere {field_name}.")
    for key, value in payload.items():
        if key in TEXT_FIELD_NAMES and value is not None and not isinstance(value, str):
            fail(f"{key} invalido para {label or op_type}: debe ser string o null.")
        if key in INT_FIELD_NAMES and value is not None:
            try:
                int(value)
            except (TypeError, ValueError):
                fail(f"{key} invalido para {label or op_type}: {value}")
    if "start_line" in payload:
        validate_positive_intish("start_line", payload["start_line"], label or op_type)
    if "end_line" in payload:
        validate_positive_intish("end_line", payload["end_line"], label or op_type)
        if "start_line" in payload and int(payload["end_line"]) < int(payload["start_line"]):
            fail(f"Rango invalido para {label or op_type}: end_line < start_line")
    if "line_number" in payload:
        validate_positive_intish("line_number", payload["line_number"], label or op_type)
    if "expected_count" in payload and payload["expected_count"] is not None:
        validate_positive_intish("expected_count", payload["expected_count"], label or op_type, allow_zero=(op_type == "AssertRegexCount"))
    if "flags" in payload:
        validate_flag_value(payload.get("flags"), label or op_type)
    if op_type == "EnsureReplaceRegexOnce":
        validate_optional_already_applied_markers(label or op_type, payload)
    if op_type == "ApplySet":
        raw_operations = payload.get("operations")
        if not isinstance(raw_operations, list) or not raw_operations:
            fail(f"La operacion {label or op_type} debe traer operations como lista no vacia.")
    if op_type == "MoveBlockExactOnce":
        insert_position = str(payload.get("insert_position", "")).strip().lower()
        if insert_position not in {"before", "after"}:
            fail(f"insert_position invalido para {label or op_type}: {payload.get('insert_position')}. Soportados: before, after")
    if op_type == "NormalizeFile" and payload.get("line_ending") is not None:
        line_ending = str(payload.get("line_ending", "")).upper()
        if line_ending not in {"LF", "CRLF"}:
            fail(f"line_ending invalido para {label or op_type}: {payload.get('line_ending')}. Soportados: LF, CRLF")
    non_empty_fields = {"old_text", "pattern", "anchor", "near_anchor", "start_anchor", "end_anchor", "text", "json_pointer", "yaml_path", "toml_path", "module", "symbol", "name", "function_name", "arg_name"}
    for field_name in non_empty_fields:
        if field_name in payload and str(payload[field_name]) == "":
            fail(f"{field_name} no puede venir vacio para {label or op_type}.")


def _extract_inline_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload = dict(item.get("payload") or {}) if isinstance(item.get("payload"), dict) else {}
    for key, value in item.items():
        if key not in {"type", "label", "file", "payload", "schema_version", "idempotency_class", "reversibility"}:
            payload[key] = value
    return payload


def parse_operation(item: dict[str, Any]):
    op_type = str(item.get("type", "")).strip()
    label = str(item.get("label", op_type)).strip()
    file_value = str(item.get("file", "")).strip()
    if not op_type:
        fail("Una operacion no trae type.")
    payload = _extract_inline_payload(item)
    validate_operation_payload(op_type, label, file_value, payload)
    if op_type == "ApplySet":
        payload = dict(payload)
        payload["operations"] = [parse_operation(child) for child in payload.get("operations") or []]
    return build_operation_spec(
        {
            "type": op_type,
            "label": label,
            "file": file_value,
            "payload": payload,
            "schema_version": item.get("schema_version"),
            "idempotency_class": item.get("idempotency_class"),
            "reversibility": item.get("reversibility"),
        }
    )


def _unwrap_operations_payload(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
    operations = data.get("operations")
    if isinstance(operations, list):
        return operations
    payload = data.get("payload")
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("operations"), list):
        return payload.get("operations")
    return [data]


def parse_operations(data: Any):
    data = _unwrap_operations_payload(data)
    if not isinstance(data, list):
        fail("El payload de operaciones debe ser una lista JSON o un objeto JSON.")
    if not data:
        fail("No mandaste operaciones.")
    if not all(isinstance(item, dict) for item in data):
        fail("Cada operacion debe ser un objeto JSON.")
    return [parse_operation(item) for item in data]


def load_operations_from_file(path_value: Path):
    raw = path_value.read_text(encoding="utf-8")
    return parse_operations(json.loads(raw))


def load_operations_from_stdin():
    raw = sys.stdin.read()
    if not raw.strip():
        fail("STDIN viene vacio. Pasa JSON por stdin o usa --ops-file.")
    return parse_operations(json.loads(raw))
