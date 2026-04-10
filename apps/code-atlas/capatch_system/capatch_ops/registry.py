from __future__ import annotations

from pathlib import Path

from capatch_contracts.operations import OperationSpec

from .assert_ops import render_assert_contains, render_assert_file_exists, render_assert_file_not_exists, render_assert_not_contains
from .base import OperationExecution, fail
from .exact_text import (
    render_delete_between_exact_anchors,
    render_delete_exact_once,
    render_ensure_insert_after_exact,
    render_ensure_insert_before_exact,
    render_ensure_replace_exact_once,
    render_insert_after_exact,
    render_insert_before_exact,
    render_move_block_exact_once,
    render_replace_between_exact_anchors,
    render_replace_exact_many,
    render_replace_exact_once,
    render_replace_nearest_exact,
)
from .line_text import render_delete_line_range, render_insert_at_line, render_replace_line_range
from .normalize_ops import render_normalize_file
from .regex_text import (
    render_assert_regex_count,
    render_delete_regex_many,
    render_delete_regex_once,
    render_ensure_replace_regex_once,
    render_replace_regex_count,
    render_replace_regex_many,
    render_replace_regex_once,
)
from .semantic_json import render_delete_json_key, render_merge_json_object, render_set_json_value
from .semantic_python import render_delete_python_import, render_ensure_python_import, render_insert_python_function_arg, render_set_python_constant
from .semantic_toml import render_set_toml_value
from .semantic_yaml import render_delete_yaml_key, render_set_yaml_value


def _content_required(target: Path, content: str | None, label: str) -> str:
    if content is None:
        fail(f"No hay contenido cargado para {label} en {target}")
    return content


def execute_operation(target: Path, content: str | None, operation: OperationSpec) -> OperationExecution:
    op_type = operation.type
    payload = operation.payload
    label = operation.label
    if op_type == "AssertFileExists":
        render_assert_file_exists(target, label)
        return OperationExecution(target, None, None, f"{target.name}: assert file exists OK", False)
    if op_type == "AssertFileNotExists":
        render_assert_file_not_exists(target, label)
        return OperationExecution(target, None, None, f"{target.name}: assert file not exists OK", False)
    text = _content_required(target, content, label)
    if op_type == "ReplaceLineRange":
        final_text = render_replace_line_range(target, text, int(payload["start_line"]), int(payload["end_line"]), str(payload.get("new_text", "")))
        return OperationExecution(target, text, final_text, f"{target.name}: rango reemplazado", True)
    if op_type == "DeleteLineRange":
        final_text = render_delete_line_range(target, text, int(payload["start_line"]), int(payload["end_line"]))
        return OperationExecution(target, text, final_text, f"{target.name}: rango eliminado", True)
    if op_type == "InsertAtLine":
        final_text = render_insert_at_line(target, text, int(payload["line_number"]), str(payload.get("insert_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: insercion aplicada en linea", True)
    if op_type == "ReplaceExactOnce":
        final_text = render_replace_exact_once(target, text, str(payload["old_text"]), str(payload.get("new_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo exacto aplicado", True)
    if op_type == "ReplaceExactMany":
        final_text, actual_count = render_replace_exact_many(target, text, str(payload["old_text"]), str(payload.get("new_text", "")), label, payload.get("expected_count"))
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo exacto multiple aplicado ({actual_count} coincidencia(s))", True)
    if op_type == "EnsureReplaceExactOnce":
        final_text, state = render_ensure_replace_exact_once(target, text, str(payload["old_text"]), str(payload["new_text"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: ensure replace exact once OK ({state})", True)
    if op_type == "ReplaceNearestExact":
        final_text = render_replace_nearest_exact(target, text, str(payload["old_text"]), str(payload.get("new_text", "")), str(payload["near_anchor"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo nearest aplicado", True)
    if op_type == "MoveBlockExactOnce":
        final_text = render_move_block_exact_once(target, text, str(payload["old_text"]), str(payload["anchor"]), payload.get("insert_position"), label)
        return OperationExecution(target, text, final_text, f"{target.name}: bloque movido", True)
    if op_type == "ReplaceBetweenExactAnchors":
        final_text = render_replace_between_exact_anchors(target, text, str(payload["start_anchor"]), str(payload["end_anchor"]), str(payload.get("new_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo entre anclas aplicado", True)
    if op_type == "DeleteBetweenExactAnchors":
        final_text = render_delete_between_exact_anchors(target, text, str(payload["start_anchor"]), str(payload["end_anchor"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: bloque entre anclas eliminado", True)
    if op_type == "NormalizeFile":
        final_text = render_normalize_file(target, text, label, payload.get("line_ending"), payload.get("ensure_final_newline"), payload.get("strip_trailing_spaces"))
        return OperationExecution(target, text, final_text, f"{target.name}: normalizacion aplicada", True)
    if op_type == "DeleteExactOnce":
        final_text = render_delete_exact_once(target, text, str(payload["old_text"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: bloque eliminado", True)
    if op_type == "DeleteRegexMany":
        final_text, actual_count = render_delete_regex_many(target, text, str(payload["pattern"]), label, payload.get("flags"), payload.get("expected_count"))
        return OperationExecution(target, text, final_text, f"{target.name}: delete regex aplicado ({actual_count} coincidencia(s))", True)
    if op_type == "DeleteRegexOnce":
        final_text = render_delete_regex_once(target, text, str(payload["pattern"]), label, payload.get("flags"))
        return OperationExecution(target, text, final_text, f"{target.name}: delete regex aplicado", True)
    if op_type == "EnsureInsertAfterExact":
        final_text = render_ensure_insert_after_exact(target, text, str(payload["anchor"]), str(payload.get("insert_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: insercion ensure-after aplicada", True)
    if op_type == "EnsureInsertBeforeExact":
        final_text = render_ensure_insert_before_exact(target, text, str(payload["anchor"]), str(payload.get("insert_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: insercion ensure-before aplicada", True)
    if op_type == "InsertAfterExact":
        final_text = render_insert_after_exact(target, text, str(payload["anchor"]), str(payload.get("insert_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: insercion aplicada despues del ancla", True)
    if op_type == "InsertBeforeExact":
        final_text = render_insert_before_exact(target, text, str(payload["anchor"]), str(payload.get("insert_text", "")), label)
        return OperationExecution(target, text, final_text, f"{target.name}: insercion aplicada antes del ancla", True)
    if op_type == "ReplaceRegexOnce":
        final_text = render_replace_regex_once(target, text, str(payload["pattern"]), str(payload.get("new_text", "")), label, payload.get("flags"))
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo regex aplicado", True)
    if op_type == "ReplaceRegexMany":
        final_text, actual_count = render_replace_regex_many(target, text, str(payload["pattern"]), str(payload.get("new_text", "")), label, payload.get("flags"), payload.get("expected_count"))
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo regex multiple aplicado ({actual_count} coincidencia(s))", True)
    if op_type == "ReplaceRegexCount":
        final_text, actual_count = render_replace_regex_count(target, text, str(payload["pattern"]), str(payload.get("new_text", "")), label, payload.get("flags"), payload.get("expected_count"))
        return OperationExecution(target, text, final_text, f"{target.name}: reemplazo regex count aplicado ({actual_count} coincidencia(s))", True)
    if op_type == "EnsureReplaceRegexOnce":
        final_text, state = render_ensure_replace_regex_once(target, text, str(payload["pattern"]), str(payload["new_text"]), label, payload.get("flags"), payload.get("already_applied_text"), payload.get("already_applied_regex"))
        return OperationExecution(target, text, final_text, f"{target.name}: ensure replace regex once OK ({state})", True)
    if op_type == "AssertContains":
        final_text = render_assert_contains(target, text, str(payload["text"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: assert contains OK", False)
    if op_type == "AssertNotContains":
        final_text = render_assert_not_contains(target, text, str(payload["text"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: assert not contains OK", False)
    if op_type == "AssertRegexCount":
        final_text, actual_count = render_assert_regex_count(target, text, str(payload["pattern"]), label, payload.get("flags"), payload.get("expected_count"))
        return OperationExecution(target, text, final_text, f"{target.name}: assert regex count OK ({actual_count})", False)
    if op_type == "SetJsonValue":
        final_text = render_set_json_value(target, text, str(payload["json_pointer"]), payload.get("value"), label)
        return OperationExecution(target, text, final_text, f"{target.name}: json value seteado", True)
    if op_type == "DeleteJsonKey":
        final_text = render_delete_json_key(target, text, str(payload["json_pointer"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: json key eliminado", True)
    if op_type == "MergeJsonObject":
        final_text = render_merge_json_object(target, text, str(payload["json_pointer"]), payload.get("object_value"), label)
        return OperationExecution(target, text, final_text, f"{target.name}: json object merge aplicado", True)
    if op_type == "SetYamlValue":
        final_text = render_set_yaml_value(target, text, str(payload["yaml_path"]), payload.get("value"), label)
        return OperationExecution(target, text, final_text, f"{target.name}: yaml value seteado", True)
    if op_type == "DeleteYamlKey":
        final_text = render_delete_yaml_key(target, text, str(payload["yaml_path"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: yaml key eliminado", True)
    if op_type == "SetTomlValue":
        final_text = render_set_toml_value(target, text, str(payload["toml_path"]), payload.get("value"), label)
        return OperationExecution(target, text, final_text, f"{target.name}: toml value seteado", True)
    if op_type == "EnsurePythonImport":
        final_text = render_ensure_python_import(target, text, str(payload["module"]), str(payload["symbol"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: python import asegurado", True)
    if op_type == "DeletePythonImport":
        final_text = render_delete_python_import(target, text, str(payload["module"]), str(payload["symbol"]), label)
        return OperationExecution(target, text, final_text, f"{target.name}: python import eliminado", True)
    if op_type == "SetPythonConstant":
        final_text = render_set_python_constant(target, text, str(payload["name"]), payload.get("value"), label)
        return OperationExecution(target, text, final_text, f"{target.name}: python constant seteada", True)
    if op_type == "InsertPythonFunctionArg":
        final_text = render_insert_python_function_arg(target, text, str(payload["function_name"]), str(payload["arg_name"]), label, payload.get("default_value"))
        return OperationExecution(target, text, final_text, f"{target.name}: python function arg insertado", True)
    fail(f"No se puede ejecutar la operacion: {op_type}")
