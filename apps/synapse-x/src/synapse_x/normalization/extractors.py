from typing import Any

from synapse_x.utils import keyword_tokens, semantic_text_fingerprint


def extract_keywords(text: Any, *, max_tokens: int = 12) -> list[str]:
    return keyword_tokens(text, max_tokens=max_tokens)


def extract_fingerprint(text: Any, *, max_tokens: int = 16) -> str:
    return semantic_text_fingerprint(text, max_tokens=max_tokens)
