from __future__ import annotations

import re


_NEWLINE_PATTERN = re.compile(r"\r\n|\r|\n")


def detect_dominant_line_ending(text: str) -> str | None:
    if not text:
        return None
    crlf = text.count("\r\n")
    shadow = text.replace("\r\n", "")
    cr = shadow.count("\r")
    lf = shadow.count("\n")
    if crlf and crlf >= max(cr, lf):
        return "\r\n"
    if lf:
        return "\n"
    if cr:
        return "\r"
    return None


def normalize_line_endings(text: str, line_ending: str) -> str:
    if not text:
        return text
    if line_ending not in {"\n", "\r\n", "\r"}:
        return text
    return _NEWLINE_PATTERN.sub(line_ending, text)


def preserve_file_style(original_content: str, final_text: str, operation_type: str) -> str:
    if final_text is None:
        return final_text
    if operation_type == "NormalizeFile":
        return final_text
    dominant = detect_dominant_line_ending(original_content)
    if not dominant:
        return final_text
    return normalize_line_endings(final_text, dominant)
