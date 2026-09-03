from __future__ import annotations
import re
from .errors import AmbiguousTarget, TargetNotFound, PriorityOverrideForbidden, BlockedUnsupportedCss

_DECL = re.compile(r"(?m)([ \t\r\n]*)([-\w]+)([ \t]*:[ \t]*)([^;{}]+)(;)")


def _contains_priority_override(text: str) -> bool:
    return ("!" + "important").lower() in text.lower()


def _top_level_blocks(text: str) -> list[tuple[str, int, int]]:
    blocks: list[tuple[str, int, int]] = []
    start = 0
    depth = 0
    quote: str | None = None
    comment = False
    escape = False
    block_start = -1
    selector_start = 0
    i = 0
    while i < len(text):
        c = text[i]
        n = text[i + 1] if i + 1 < len(text) else ""
        if comment:
            if c == "*" and n == "/": comment = False; i += 2; continue
            i += 1; continue
        if quote:
            if escape: escape = False
            elif c == "\\": escape = True
            elif c == quote: quote = None
            i += 1; continue
        if c == "/" and n == "*": comment = True; i += 2; continue
        if c in ("'", '"'): quote = c; i += 1; continue
        if c == "{":
            if depth == 0:
                selector = text[selector_start:i].strip()
                selector_clean = re.sub(r"/\*.*?\*/", "", selector, flags=re.S).strip()
                if selector_clean.startswith("@"):
                    raise BlockedUnsupportedCss("top-level at-rule blocks are unsupported in V1")
                block_start = i + 1
                start = selector_start
            else:
                raise BlockedUnsupportedCss("nested CSS is unsupported in V1")
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0: raise BlockedUnsupportedCss("unbalanced CSS braces")
            if depth == 0 and block_start >= 0:
                selector = text[start:text.rfind("{", start, block_start)].strip()
                selector = re.sub(r"/\*.*?\*/", "", selector, flags=re.S).strip()
                blocks.append((selector, block_start, i))
                selector_start = i + 1
                block_start = -1
        i += 1
    if depth != 0 or quote or comment:
        raise BlockedUnsupportedCss("malformed CSS")
    return blocks


def patch_css(text: str, selector: str, declarations: dict[str, str]) -> str:
    if _contains_priority_override(text) or any(_contains_priority_override(str(v)) for v in declarations.values()):
        raise PriorityOverrideForbidden("priority override syntax is forbidden")
    matches = [row for row in _top_level_blocks(text) if row[0] == selector]
    if not matches: raise TargetNotFound(f"selector not found: {selector}")
    if len(matches) != 1: raise AmbiguousTarget(f"selector is not unique: {selector}")
    _, body_start, body_end = matches[0]
    body = text[body_start:body_end]
    out = body
    for prop, desired in declarations.items():
        hits = [m for m in _DECL.finditer(out) if m.group(2) == prop]
        if not hits: raise TargetNotFound(f"declaration not found: {selector}:{prop}")
        if len(hits) != 1: raise AmbiguousTarget(f"declaration is not unique: {selector}:{prop}")
        m = hits[0]
        replacement = f"{m.group(1)}{prop}{m.group(3)}{desired}{m.group(5)}"
        out = out[:m.start()] + replacement + out[m.end():]
    return text[:body_start] + out + text[body_end:]
