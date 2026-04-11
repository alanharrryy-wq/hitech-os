from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .base import ast_parse_with_message, fail, python_literal


def _line_offsets(content: str) -> list[int]:
    offsets = [0]
    running = 0
    for line in content.splitlines(keepends=True):
        running += len(line)
        offsets.append(running)
    return offsets


def _line_range_to_slice(content: str, start_line: int, end_line: int) -> tuple[int, int]:
    offsets = _line_offsets(content)
    return offsets[start_line - 1], offsets[end_line]


def render_ensure_python_import(target: Path, content: str, module: str, symbol: str, label: str) -> str:
    tree = ast_parse_with_message(content, target)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == module:
            if any(alias.name == symbol for alias in node.names):
                return content
            start, end = _line_range_to_slice(content, node.lineno, node.end_lineno or node.lineno)
            line = content[start:end].rstrip("\n")
            replacement = line + f", {symbol}" + ("\n" if content[end - 1 : end] == "\n" else "")
            return content[:start] + replacement + content[end:]
    insert_at = 0
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
        insert_at = tree.body[0].end_lineno or tree.body[0].lineno
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            insert_at = max(insert_at, node.end_lineno or node.lineno)
    offsets = _line_offsets(content)
    pos = offsets[insert_at] if insert_at < len(offsets) else len(content)
    import_line = f"from {module} import {symbol}\n"
    return content[:pos] + import_line + content[pos:]


def render_delete_python_import(target: Path, content: str, module: str, symbol: str, label: str) -> str:
    tree = ast_parse_with_message(content, target)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == module:
            aliases = [alias.name for alias in node.names]
            if symbol not in aliases:
                continue
            start, end = _line_range_to_slice(content, node.lineno, node.end_lineno or node.lineno)
            if len(aliases) == 1:
                return content[:start] + content[end:]
            remaining = [name for name in aliases if name != symbol]
            replacement = f"from {module} import {', '.join(remaining)}\n"
            return content[:start] + replacement + content[end:]
    fail(f"No encontre import para {label} en {target}: from {module} import {symbol}")


def render_set_python_constant(target: Path, content: str, name: str, value: Any, label: str) -> str:
    tree = ast_parse_with_message(content, target)
    literal = python_literal(value)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for assign_target in node.targets:
                if isinstance(assign_target, ast.Name) and assign_target.id == name:
                    start, end = _line_range_to_slice(content, node.lineno, node.end_lineno or node.lineno)
                    return content[:start] + f"{name} = {literal}\n" + content[end:]
    suffix = "" if content.endswith("\n") or content == "" else "\n"
    return content + suffix + f"{name} = {literal}\n"


def render_insert_python_function_arg(target: Path, content: str, function_name: str, arg_name: str, label: str, default_value: Any | None = None) -> str:
    tree = ast_parse_with_message(content, target)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            args = [arg.arg for arg in node.args.args]
            if arg_name in args:
                return content
            segment = ast.get_source_segment(content, node)
            if not segment:
                fail(f"No pude reconstruir la funcion para {label} en {target}")
            header_end = segment.find(":")
            if header_end < 0:
                fail(f"Cabecera de funcion invalida para {label} en {target}")
            header = segment[:header_end]
            insert = arg_name if default_value is None else f"{arg_name}={python_literal(default_value)}"
            close = header.rfind(")")
            if close < 0:
                fail(f"Cabecera de funcion invalida para {label} en {target}")
            if header[header.find("(") + 1 : close].strip():
                new_header = header[:close] + ", " + insert + header[close:]
            else:
                new_header = header[:close] + insert + header[close:]
            new_segment = new_header + segment[header_end:]
            start, end = _line_range_to_slice(content, node.lineno, node.end_lineno or node.lineno)
            return content[:start] + new_segment + content[end:]
    fail(f"No encontre function_name para {label} en {target}: {function_name}")
