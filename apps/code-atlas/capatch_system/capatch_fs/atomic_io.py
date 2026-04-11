from __future__ import annotations

import codecs
import os
import tempfile
from pathlib import Path


def _read_raw_bytes(path_value: Path) -> bytes:
    return path_value.read_bytes()


def file_has_utf8_bom(path_value: Path) -> bool:
    try:
        return _read_raw_bytes(path_value).startswith(codecs.BOM_UTF8)
    except Exception:
        return False


def read_file_utf8(path_value: Path) -> str:
    data = _read_raw_bytes(path_value)
    if data.startswith(codecs.BOM_UTF8):
        data = data[len(codecs.BOM_UTF8):]
    return data.decode("utf-8")


def write_file_utf8_no_bom(path_value: Path, content: str) -> None:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(path_value.parent)) as handle:
        handle.write(data)
        temp_name = handle.name
    os.replace(temp_name, path_value)


def write_file_if_changed(path_value: Path, original_content: str, final_text: str) -> bool:
    if original_content == final_text:
        return False
    path_value.parent.mkdir(parents=True, exist_ok=True)
    has_bom = file_has_utf8_bom(path_value) if path_value.exists() else False
    data = final_text.encode("utf-8")
    if has_bom:
        data = codecs.BOM_UTF8 + data
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(path_value.parent)) as handle:
        handle.write(data)
        temp_name = handle.name
    os.replace(temp_name, path_value)
    return True
