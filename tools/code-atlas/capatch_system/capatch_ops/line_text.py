from __future__ import annotations

from pathlib import Path

from .base import fail


def render_replace_line_range(target: Path, content: str, start_line: int, end_line: int, new_text: str) -> str:
    if start_line < 1 or end_line < start_line:
        fail(f"Rango invalido en {target}: {start_line}-{end_line}")
    lines = content.splitlines()
    if end_line > len(lines):
        fail(f"El rango {start_line}-{end_line} se sale del archivo ({len(lines)} lineas): {target}")
    before = lines[: start_line - 1]
    after = lines[end_line:]
    replacement = new_text.splitlines() if new_text else []
    final_lines = before + replacement + after
    final_text = "\n".join(final_lines)
    if content.endswith("\n"):
        final_text += "\n"
    return final_text


def render_delete_line_range(target: Path, content: str, start_line: int, end_line: int) -> str:
    return render_replace_line_range(target, content, start_line, end_line, "")


def render_insert_at_line(target: Path, content: str, line_number: int, insert_text: str, label: str) -> str:
    if line_number < 1:
        fail(f"line_number invalido para {label} en {target}: {line_number}")
    lines = content.splitlines(keepends=True)
    max_allowed = len(lines) + 1
    if line_number > max_allowed:
        fail(f"line_number invalido para {label} en {target}: {line_number}. Maximo permitido: {max_allowed}")
    if insert_text == "":
        return content
    position = sum(len(line) for line in lines[: line_number - 1])
    return content[:position] + insert_text + content[position:]
