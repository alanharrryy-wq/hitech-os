from __future__ import annotations

from pathlib import Path

from .base import fail, fail_not_found_with_suggestion, find_closest_match, normalize_match_candidate


def render_replace_exact_once(target: Path, content: str, old_text: str, new_text: str, label: str) -> str:
    first = content.find(old_text)
    if first < 0:
        if old_text != new_text and new_text != "":
            new_first = content.find(new_text)
            new_second = content.find(new_text, new_first + len(new_text)) if new_first >= 0 else -1
            if new_first >= 0 and new_second < 0:
                suggestion = find_closest_match(content, old_text)
                if suggestion is None or normalize_match_candidate(suggestion) == normalize_match_candidate(new_text):
                    return content
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")
    second = content.find(old_text, first + len(old_text))
    if second >= 0:
        fail(f"El bloque exacto para {label} aparece mas de una vez en {target}")
    return content.replace(old_text, new_text)


def render_delete_exact_once(target: Path, content: str, old_text: str, label: str) -> str:
    return render_replace_exact_once(target, content, old_text, "", label)


def render_insert_after_exact(target: Path, content: str, anchor: str, insert_text: str, label: str) -> str:
    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")
    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")
    pos = first + len(anchor)
    return content[:pos] + insert_text + content[pos:]


def render_insert_before_exact(target: Path, content: str, anchor: str, insert_text: str, label: str) -> str:
    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")
    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")
    return content[:first] + insert_text + content[first:]


def render_ensure_insert_after_exact(target: Path, content: str, anchor: str, insert_text: str, label: str) -> str:
    if insert_text == "":
        return content
    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")
    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")
    pos = first + len(anchor)
    if content[pos:pos + len(insert_text)] == insert_text:
        return content
    if insert_text in content:
        fail(f"El bloque para {label} ya existe en {target}, pero no esta inmediatamente despues del ancla. Estado ambiguo.")
    return content[:pos] + insert_text + content[pos:]


def render_ensure_insert_before_exact(target: Path, content: str, anchor: str, insert_text: str, label: str) -> str:
    if insert_text == "":
        return content
    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")
    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")
    start = max(0, first - len(insert_text))
    if content[start:first] == insert_text:
        return content
    if insert_text in content:
        fail(f"El bloque para {label} ya existe en {target}, pero no esta inmediatamente antes del ancla. Estado ambiguo.")
    return content[:first] + insert_text + content[first:]


def render_replace_exact_many(target: Path, content: str, old_text: str, new_text: str, label: str, expected_count: object) -> tuple[str, int]:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")
    actual_count = content.count(old_text)
    if actual_count == 0:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")
    if expected_count is not None:
        expected = int(expected_count)
        if expected < 1:
            fail(f"expected_count invalido para {label} en {target}: {expected}")
        if actual_count != expected:
            fail(f"El bloque exacto para {label} esperaba {expected} coincidencia(s) y encontro {actual_count} en {target}")
    return content.replace(old_text, new_text), actual_count


def render_replace_between_exact_anchors(target: Path, content: str, start_anchor: str, end_anchor: str, new_text: str, label: str) -> str:
    start_first = content.find(start_anchor)
    if start_first < 0:
        fail_not_found_with_suggestion(target, content, start_anchor, label, "start_anchor")
    start_second = content.find(start_anchor, start_first + len(start_anchor))
    if start_second >= 0:
        fail(f"start_anchor para {label} aparece mas de una vez en {target}")
    end_first = content.find(end_anchor)
    if end_first < 0:
        fail_not_found_with_suggestion(target, content, end_anchor, label, "end_anchor")
    end_second = content.find(end_anchor, end_first + len(end_anchor))
    if end_second >= 0:
        fail(f"end_anchor para {label} aparece mas de una vez en {target}")
    start_pos = start_first + len(start_anchor)
    end_pos = end_first
    if end_pos < start_pos:
        fail(f"Las anclas para {label} estan fuera de orden o se traslapan en {target}")
    return content[:start_pos] + new_text + content[end_pos:]


def render_delete_between_exact_anchors(target: Path, content: str, start_anchor: str, end_anchor: str, label: str) -> str:
    return render_replace_between_exact_anchors(target, content, start_anchor, end_anchor, "", label)


def render_replace_nearest_exact(target: Path, content: str, old_text: str, new_text: str, near_anchor: str, label: str) -> str:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")
    anchor_first = content.find(near_anchor)
    if anchor_first < 0:
        fail_not_found_with_suggestion(target, content, near_anchor, label, "near_anchor")
    anchor_second = content.find(near_anchor, anchor_first + len(near_anchor))
    if anchor_second >= 0:
        fail(f"near_anchor para {label} aparece mas de una vez en {target}")
    positions = []
    search_from = 0
    step = max(len(old_text), 1)
    while True:
        position = content.find(old_text, search_from)
        if position < 0:
            break
        positions.append(position)
        search_from = position + step
    if not positions:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")
    best_position = min(positions, key=lambda pos: (abs(pos - anchor_first), pos))
    return content[:best_position] + new_text + content[best_position + len(old_text):]


def render_ensure_replace_exact_once(target: Path, content: str, old_text: str, new_text: str, label: str) -> tuple[str, str]:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")
    if new_text == "":
        fail(f"new_text no puede venir vacio para {label} en {target}. Usa DeleteExactOnce si quieres borrar.")
    if old_text == new_text:
        return content, "ya estaba aplicado"
    old_count = content.count(old_text)
    new_count = content.count(new_text)
    if old_count == 0:
        if new_count == 1:
            suggestion = find_closest_match(content, old_text)
            if suggestion is None or normalize_match_candidate(suggestion) == normalize_match_candidate(new_text):
                return content, "ya estaba aplicado"
            fail(f"No encontre el bloque viejo para {label} en {target}, pero el bloque nuevo ya existe y hay un candidato parecido al bloque viejo. Estado ambiguo.")
        if new_count > 1:
            fail(f"El bloque nuevo para {label} aparece mas de una vez en {target}")
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")
    if old_count > 1:
        fail(f"El bloque exacto para {label} aparece mas de una vez en {target}")
    if new_count > 1:
        fail(f"El bloque nuevo para {label} aparece mas de una vez en {target}")
    if new_count == 1:
        fail(f"El bloque viejo y el bloque nuevo ya conviven para {label} en {target}")
    return content.replace(old_text, new_text), "reemplazo aplicado"


def render_move_block_exact_once(target: Path, content: str, old_text: str, anchor: str, insert_position: object, label: str) -> str:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")
    normalized_position = str(insert_position or "").strip().lower()
    if normalized_position not in {"before", "after"}:
        fail(f"insert_position invalido para {label} en {target}: {insert_position}. Soportados: before, after")
    first = content.find(old_text)
    if first < 0:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")
    second = content.find(old_text, first + len(old_text))
    if second >= 0:
        fail(f"El bloque exacto para {label} aparece mas de una vez en {target}")
    without_block = content[:first] + content[first + len(old_text):]
    if normalized_position == "before":
        return render_insert_before_exact(target, without_block, anchor, old_text, label)
    return render_insert_after_exact(target, without_block, anchor, old_text, label)
