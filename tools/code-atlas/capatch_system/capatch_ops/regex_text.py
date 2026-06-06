from __future__ import annotations

import re
from pathlib import Path

from .base import compile_regex_flags, fail, regex_pattern_is_likely_complex, regex_replacement_uses_backrefs


def render_replace_regex_once(target: Path, content: str, pattern: str, new_text: str, label: str, raw_flags: object) -> str:
    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")
    matches = list(regex.finditer(content))
    if not matches:
        fail(f"No encontre regex para: {label} en {target}")
    if len(matches) > 1:
        fail(f"El regex para {label} aparece mas de una vez en {target}")
    return regex.sub(new_text, content, count=1)


def render_replace_regex_many(target: Path, content: str, pattern: str, new_text: str, label: str, raw_flags: object, expected_count: object) -> tuple[str, int]:
    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")
    matches = list(regex.finditer(content))
    actual_count = len(matches)
    if actual_count == 0:
        fail(f"No encontre regex para: {label} en {target}")
    if expected_count is not None:
        expected = int(expected_count)
        if expected < 1:
            fail(f"expected_count invalido para {label} en {target}: {expected}")
        if actual_count != expected:
            fail(f"El regex para {label} esperaba {expected} coincidencia(s) y encontro {actual_count} en {target}")
    return regex.sub(new_text, content), actual_count


def render_delete_regex_many(target: Path, content: str, pattern: str, label: str, raw_flags: object, expected_count: object) -> tuple[str, int]:
    return render_replace_regex_many(target, content, pattern, "", label, raw_flags, expected_count)


def render_delete_regex_once(target: Path, content: str, pattern: str, label: str, raw_flags: object) -> str:
    final_text, _ = render_delete_regex_many(target, content, pattern, label, raw_flags, 1)
    return final_text


def render_replace_regex_count(target: Path, content: str, pattern: str, new_text: str, label: str, raw_flags: object, expected_count: object) -> tuple[str, int]:
    if expected_count is None:
        fail(f"expected_count es requerido para {label} en {target}")
    return render_replace_regex_many(target, content, pattern, new_text, label, raw_flags, expected_count)


def render_assert_regex_count(target: Path, content: str, pattern: str, label: str, raw_flags: object, expected_count: object) -> tuple[str, int]:
    if expected_count is None:
        fail(f"expected_count es requerido para {label} en {target}")
    try:
        expected = int(expected_count)
    except (TypeError, ValueError):
        fail(f"expected_count invalido para {label} en {target}: {expected_count}")
    if expected < 0:
        fail(f"expected_count invalido para {label} en {target}: {expected}")
    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")
    actual_count = len(list(regex.finditer(content)))
    if actual_count != expected:
        fail(f"El regex para {label} esperaba {expected} coincidencia(s) y encontro {actual_count} en {target}")
    return content, actual_count


def render_ensure_replace_regex_once(target: Path, content: str, pattern: str, new_text: str, label: str, raw_flags: object, already_applied_text: str | None = None, already_applied_regex: str | None = None) -> tuple[str, str]:
    if new_text == "":
        fail(f"new_text no puede venir vacio para {label} en {target}. Usa DeleteRegexOnce si quieres borrar.")
    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")
    matches = list(regex.finditer(content))
    literal_new_count = content.count(new_text)
    applied_text = (already_applied_text or "").strip()
    applied_regex = (already_applied_regex or "").strip()
    if not matches:
        if applied_text:
            applied_text_count = content.count(applied_text)
            if applied_text_count == 1:
                return content, "ya estaba aplicado"
            if applied_text_count > 1:
                fail(f"already_applied_text para {label} aparece mas de una vez en {target}")
        if applied_regex:
            try:
                applied_regex_compiled = re.compile(applied_regex, compile_regex_flags(raw_flags))
            except re.error as exc:
                fail(f"already_applied_regex invalido para {label} en {target}: {exc}")
            applied_matches = list(applied_regex_compiled.finditer(content))
            if len(applied_matches) == 1:
                return content, "ya estaba aplicado"
            if len(applied_matches) > 1:
                fail(f"already_applied_regex para {label} aparece mas de una vez en {target}")
        if literal_new_count > 1:
            fail(f"El texto nuevo para {label} aparece mas de una vez en {target}")
        if literal_new_count == 1:
            if regex_replacement_uses_backrefs(new_text) or regex_pattern_is_likely_complex(pattern):
                fail(f"No encontre regex para: {label} en {target}, pero el texto nuevo ya existe una vez. No puedo confirmar idempotencia de forma segura con este patron. Usa already_applied_text o already_applied_regex.")
            return content, "ya estaba aplicado"
        fail(f"No encontre regex para: {label} en {target}")
    if len(matches) > 1:
        fail(f"El regex para {label} aparece mas de una vez en {target}")
    prospective_text = regex.sub(new_text, content, count=1)
    if prospective_text == content:
        return content, "ya estaba aplicado"
    if literal_new_count > 1:
        fail(f"El texto nuevo para {label} aparece mas de una vez en {target}")
    if literal_new_count == 1:
        fail(f"El regex viejo y el texto nuevo ya conviven para {label} en {target}")
    return prospective_text, "reemplazo aplicado"
