from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .versions import PATCH_OPERATION_SCHEMA_VERSION

PATCH_OPERATION_TYPES = (
    "ReplaceLineRange",
    "DeleteLineRange",
    "InsertAtLine",
    "ReplaceExactOnce",
    "ReplaceExactMany",
    "EnsureReplaceExactOnce",
    "ReplaceNearestExact",
    "MoveBlockExactOnce",
    "ReplaceBetweenExactAnchors",
    "DeleteBetweenExactAnchors",
    "NormalizeFile",
    "DeleteExactOnce",
    "DeleteRegexMany",
    "DeleteRegexOnce",
    "EnsureInsertAfterExact",
    "EnsureInsertBeforeExact",
    "InsertAfterExact",
    "InsertBeforeExact",
    "ReplaceRegexOnce",
    "ReplaceRegexMany",
    "ReplaceRegexCount",
    "EnsureReplaceRegexOnce",
    "AssertContains",
    "AssertNotContains",
    "AssertRegexCount",
    "AssertFileExists",
    "AssertFileNotExists",
    "ApplySet",
)

SEMANTIC_OPERATION_TYPES = (
    "SetJsonValue",
    "DeleteJsonKey",
    "MergeJsonObject",
    "SetYamlValue",
    "DeleteYamlKey",
    "SetTomlValue",
    "EnsurePythonImport",
    "DeletePythonImport",
    "SetPythonConstant",
    "InsertPythonFunctionArg",
)

READ_ONLY_OPERATION_TYPES = (
    "AssertContains",
    "AssertNotContains",
    "AssertRegexCount",
    "AssertFileExists",
    "AssertFileNotExists",
)

MUTATING_OPERATION_TYPES = tuple(
    operation_type
    for operation_type in PATCH_OPERATION_TYPES + SEMANTIC_OPERATION_TYPES
    if operation_type not in READ_ONLY_OPERATION_TYPES
)

REGEX_FLAG_NAMES = (
    "ASCII",
    "DOTALL",
    "IGNORECASE",
    "MULTILINE",
    "VERBOSE",
)

TEXT_FIELD_NAMES = (
    "file",
    "old_text",
    "new_text",
    "pattern",
    "anchor",
    "near_anchor",
    "start_anchor",
    "end_anchor",
    "text",
    "insert_text",
    "line_ending",
    "insert_position",
    "already_applied_text",
    "already_applied_regex",
)

INT_FIELD_NAMES = (
    "start_line",
    "end_line",
    "line_number",
    "expected_count",
)

IDEMPOTENCY_CLASSES = (
    "strict",
    "best-effort",
    "non-idempotent",
)

REVERSIBILITY_CLASSES = (
    "full",
    "partial",
    "manual",
)

REQUIRED_FIELDS_BY_OPERATION = {
    "ReplaceLineRange": ("start_line", "end_line"),
    "DeleteLineRange": ("start_line", "end_line"),
    "InsertAtLine": ("line_number",),
    "ReplaceExactOnce": ("old_text",),
    "ReplaceExactMany": ("old_text",),
    "EnsureReplaceExactOnce": ("old_text", "new_text"),
    "ReplaceNearestExact": ("old_text", "near_anchor"),
    "MoveBlockExactOnce": ("old_text", "anchor", "insert_position"),
    "ReplaceBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteExactOnce": ("old_text",),
    "DeleteRegexMany": ("pattern",),
    "DeleteRegexOnce": ("pattern",),
    "AssertContains": ("text",),
    "AssertNotContains": ("text",),
    "AssertRegexCount": ("pattern", "expected_count"),
    "EnsureInsertAfterExact": ("anchor", "insert_text"),
    "EnsureInsertBeforeExact": ("anchor", "insert_text"),
    "InsertAfterExact": ("anchor", "insert_text"),
    "InsertBeforeExact": ("anchor", "insert_text"),
    "ReplaceRegexOnce": ("pattern",),
    "ReplaceRegexMany": ("pattern",),
    "ReplaceRegexCount": ("pattern", "expected_count"),
    "EnsureReplaceRegexOnce": ("pattern", "new_text"),
    "AssertFileExists": (),
    "AssertFileNotExists": (),
    "NormalizeFile": (),
    "ApplySet": ("operations",),
    "SetJsonValue": ("json_pointer", "value"),
    "DeleteJsonKey": ("json_pointer",),
    "MergeJsonObject": ("json_pointer", "object_value"),
    "SetYamlValue": ("yaml_path", "value"),
    "DeleteYamlKey": ("yaml_path",),
    "SetTomlValue": ("toml_path", "value"),
    "EnsurePythonImport": ("module", "symbol"),
    "DeletePythonImport": ("module", "symbol"),
    "SetPythonConstant": ("name", "value"),
    "InsertPythonFunctionArg": ("function_name", "arg_name"),
}

SUPPORT_FIELDS_BY_OPERATION = {
    "ReplaceExactOnce": ("old_text",),
    "ReplaceExactMany": ("old_text",),
    "EnsureReplaceExactOnce": ("old_text",),
    "ReplaceNearestExact": ("old_text", "near_anchor"),
    "MoveBlockExactOnce": ("old_text", "anchor"),
    "ReplaceBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteExactOnce": ("old_text",),
    "InsertAfterExact": ("anchor",),
    "EnsureInsertAfterExact": ("anchor",),
    "InsertBeforeExact": ("anchor",),
    "EnsureInsertBeforeExact": ("anchor",),
    "AssertContains": ("text",),
}


@dataclass(slots=True, frozen=True)
class OperationSpec:
    type: str
    label: str
    file: str
    payload: dict[str, Any]
    schema_version: str
    idempotency_class: str
    reversibility: str


def operation_default_idempotency(operation_type: str) -> str:
    if operation_type in READ_ONLY_OPERATION_TYPES:
        return "strict"
    if operation_type in {"ApplySet", "MoveBlockExactOnce"}:
        return "best-effort"
    return "strict"


def operation_default_reversibility(operation_type: str) -> str:
    if operation_type in READ_ONLY_OPERATION_TYPES:
        return "full"
    if operation_type in {"DeleteRegexMany", "DeleteRegexOnce", "DeleteJsonKey", "DeleteYamlKey"}:
        return "partial"
    return "full"


def is_valid_operation_type(operation_type: str) -> bool:
    return operation_type in PATCH_OPERATION_TYPES or operation_type in SEMANTIC_OPERATION_TYPES


def is_mutating_operation(operation_type: str) -> bool:
    return operation_type in MUTATING_OPERATION_TYPES


def required_fields_for(operation_type: str) -> tuple[str, ...]:
    return tuple(REQUIRED_FIELDS_BY_OPERATION.get(operation_type, ()))


def normalize_operation_payload(raw_payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(raw_payload)
    operation_type = str(payload.get("type") or "").strip()
    if not operation_type:
        raise ValueError("Operation payload missing 'type'.")
    if not is_valid_operation_type(operation_type):
        raise ValueError(f"Unsupported operation type: {operation_type}")

    if "payload" in payload and isinstance(payload["payload"], Mapping):
        body = dict(payload["payload"])
    else:
        body = {
            key: value
            for key, value in payload.items()
            if key not in {
                "type",
                "label",
                "file",
                "payload",
                "schema_version",
                "idempotency_class",
                "reversibility",
            }
        }

    normalized = {
        "type": operation_type,
        "label": str(payload.get("label") or operation_type),
        "file": str(payload.get("file") or ""),
        "payload": body,
        "schema_version": str(payload.get("schema_version") or PATCH_OPERATION_SCHEMA_VERSION),
        "idempotency_class": str(payload.get("idempotency_class") or operation_default_idempotency(operation_type)),
        "reversibility": str(payload.get("reversibility") or operation_default_reversibility(operation_type)),
    }

    missing = [field_name for field_name in required_fields_for(operation_type) if field_name not in body]
    if missing:
        raise ValueError(f"Operation {operation_type} missing required payload fields: {', '.join(missing)}")
    return normalized


def build_operation_spec(raw_payload: Mapping[str, Any]) -> OperationSpec:
    normalized = normalize_operation_payload(raw_payload)
    return OperationSpec(
        type=normalized["type"],
        label=normalized["label"],
        file=normalized["file"],
        payload=normalized["payload"],
        schema_version=normalized["schema_version"],
        idempotency_class=normalized["idempotency_class"],
        reversibility=normalized["reversibility"],
    )


# Compatibility aliases for B-engine consumers
REQUIRED_FIELDS = REQUIRED_FIELDS_BY_OPERATION


_ORIGINAL_BUILD_OPERATION_SPEC = build_operation_spec

def build_operation_spec(*args, **kwargs) -> OperationSpec:
    if len(args) == 1 and not kwargs:
        return _ORIGINAL_BUILD_OPERATION_SPEC(args[0])
    if len(args) == 4 and not kwargs:
        op_type, label, file, payload = args
        raw_payload = {
            "type": op_type,
            "label": label,
            "file": file,
            "payload": payload,
        }
        return _ORIGINAL_BUILD_OPERATION_SPEC(raw_payload)
    if not args and kwargs:
        return _ORIGINAL_BUILD_OPERATION_SPEC(kwargs)
    raise TypeError("build_operation_spec expects either (mapping) or (type, label, file, payload)")
