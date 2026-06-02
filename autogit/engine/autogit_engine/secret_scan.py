from __future__ import annotations
import re
from .patterns import SEVERE, SECRET_ASSIGN_RE

_CALL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_\.]*\s*\(")
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_\.]*$")
_PLACEHOLDER_RE = re.compile(r"^<[^>]+>$")
_CODE_SYNTAX_RE = re.compile(r"[\[\]\(\)\{\}]|(?:\.[A-Za-z_$])")
_HIGH_ENTROPY_PREFIX_RE = re.compile(
    r"(?i)^(sk-|xox[baprs]-|gh[pousr]_|github_pat_|AKIA|ASIA|AIza|ya29\.|eyJ[A-Za-z0-9_\-]{8,}\.)"
)

def severe_hits(text: str) -> list[str]:
    hits = []
    for name, rgx in SEVERE:
        if rgx.search(text):
            hits.append(name)
    return sorted(set(hits))

def _looks_like_code_value(value: str) -> bool:
    value = value.strip()
    if not value:
        return True
    if _CALL_RE.match(value):
        return True
    if _NAME_RE.match(value) and not re.search(r"\d", value):
        return True
    if _PLACEHOLDER_RE.match(value):
        return True
    # Member expressions and indexed expressions are code, not literal secrets:
    # token:v[O].token, secret:ctx.policy.secret, apiKey:opts.apiKey.
    if _CODE_SYNTAX_RE.search(value):
        return True
    if value.lower() in {"true", "false", "none", "null", "undefined"}:
        return True
    return False

def _looks_secretish(value: str) -> bool:
    value = value.strip().rstrip(";)")
    if len(value) < 8:
        return False
    if _HIGH_ENTROPY_PREFIX_RE.search(value):
        return True
    if _looks_like_code_value(value):
        return False
    has_letter = bool(re.search(r"[A-Za-z]", value))
    has_entropy_marker = bool(re.search(r"[0-9_\-+/=:.]", value))
    return has_letter and has_entropy_marker

def _redact_assignment(match: re.Match[str], *, code_mode: bool) -> str:
    prefix = match.group("prefix")
    quote = match.group("quote") or ""
    value = match.group("value") or ""
    suffix = match.group("suffix") or ""

    # In code, an unquoted colon form is commonly an object literal/property
    # mapping, not a secret declaration. Rewriting it can turn valid JS such as
    # {token:v[O].token} into invalid JS. Only redact quoted values or obvious
    # high-entropy raw assignments in code.
    if code_mode and not quote and prefix.rstrip().endswith(":"):
        return match.group(0)

    if quote:
        return f"{prefix}{quote}<REDACTED>{quote}{suffix}"

    if not _looks_secretish(value):
        return match.group(0)
    return f'{prefix}"<REDACTED>"{suffix}'

def redact_literal_keys(text: str, *, code: bool = False) -> str:
    for _, rgx in SEVERE:
        text = rgx.sub("<REDACTED_SECRET>", text)
    return SECRET_ASSIGN_RE.sub(lambda m: _redact_assignment(m, code_mode=code), text)
