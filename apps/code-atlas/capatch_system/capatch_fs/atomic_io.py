from __future__ import annotations

import os
import tempfile
from pathlib import Path


def read_file_utf8(path_value: Path) -> str:
    return path_value.read_text(encoding="utf-8")


def write_file_utf8_no_bom(path_value: Path, content: str) -> None:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", newline="", dir=str(path_value.parent)) as handle:
        handle.write(content)
        temp_name = handle.name
    os.replace(temp_name, path_value)


def write_file_if_changed(path_value: Path, original_content: str, final_text: str) -> bool:
    if original_content == final_text:
        return False
    write_file_utf8_no_bom(path_value, final_text)
    return True
