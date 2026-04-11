from __future__ import annotations

from pathlib import Path

from .base import fail


def render_normalize_file(target: Path, content: str, label: str, line_ending: object, ensure_final_newline: object, strip_trailing_spaces: object) -> str:
    normalized_line_ending = str(line_ending or "LF").upper()
    if normalized_line_ending == "LF":
        separator = "\n"
    elif normalized_line_ending == "CRLF":
        separator = "\r\n"
    else:
        fail(f"line_ending invalido para {label} en {target}: {line_ending}. Soportados: LF, CRLF")
    final_newline = True if ensure_final_newline is None else bool(ensure_final_newline)
    trim_spaces = False if strip_trailing_spaces is None else bool(strip_trailing_spaces)
    if content == "":
        return ""
    lines = content.splitlines()
    if trim_spaces:
        lines = [line.rstrip(" \t") for line in lines]
    final_text = separator.join(lines)
    if final_newline:
        final_text += separator
    return final_text
