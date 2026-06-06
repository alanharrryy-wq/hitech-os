from __future__ import annotations

from pathlib import Path

from .base import fail, fail_not_found_with_suggestion


def render_assert_contains(target: Path, content: str, text: str, label: str) -> str:
    if text not in content:
        fail_not_found_with_suggestion(target, content, text, label, "el texto requerido")
    return content


def render_assert_not_contains(target: Path, content: str, text: str, label: str) -> str:
    if text in content:
        fail(f"Se encontro texto prohibido para: {label} en {target}")
    return content


def render_assert_file_exists(target: Path, label: str) -> None:
    if not target.exists():
        fail(f"No existe el archivo requerido para: {label} en {target}")
    if not target.is_file():
        fail(f"Se esperaba archivo para: {label}, no carpeta: {target}")


def render_assert_file_not_exists(target: Path, label: str) -> None:
    if target.exists():
        fail(f"El archivo no deberia existir para: {label} en {target}")
