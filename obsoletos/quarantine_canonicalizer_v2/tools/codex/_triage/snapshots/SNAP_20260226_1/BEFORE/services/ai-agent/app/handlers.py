from __future__ import annotations

import re
from collections import Counter
from typing import Dict

from .models import JsonValue, JobRequestModel

WHITESPACE_RE = re.compile(r"\s+")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]+")
TOKEN_RE = re.compile(r"[a-z0-9']+")

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


def _extract_text(payload: Dict[str, JsonValue]) -> str:
    raw = payload.get("text")
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    return str(raw)


def _normalize_text(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.strip())


def handle_echo(request: JobRequestModel) -> Dict[str, JsonValue]:
    return {
        "kind": "echo",
        "echo": request.input,
        "receivedAtUtc": request.requestedAtUtc,
    }


def handle_summarize_text(request: JobRequestModel) -> Dict[str, JsonValue]:
    text = _normalize_text(_extract_text(request.input))
    sentence_candidates = [segment.strip() for segment in SENTENCE_SPLIT_RE.split(text) if segment.strip()]
    first_sentence = sentence_candidates[0] if sentence_candidates else ""
    summary = first_sentence
    if len(summary) > 160:
        summary = f"{summary[:157]}..."

    words = [token for token in text.split(" ") if token]

    return {
        "kind": "summarize_text",
        "summary": summary,
        "sentenceCount": len(sentence_candidates),
        "wordCount": len(words),
        "sourceChars": len(text),
    }


def handle_extract_keywords(request: JobRequestModel) -> Dict[str, JsonValue]:
    text = _normalize_text(_extract_text(request.input)).lower()
    tokens = TOKEN_RE.findall(text)
    filtered = [token for token in tokens if token not in STOP_WORDS and len(token) >= 3]

    counts = Counter(filtered)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top_keywords = ordered[:10]

    return {
        "kind": "extract_keywords",
        "keywords": [word for word, _ in top_keywords],
        "frequencies": [{"keyword": word, "count": count} for word, count in top_keywords],
        "tokenCount": len(tokens),
        "filteredTokenCount": len(filtered),
    }


HANDLERS = {
    "echo": handle_echo,
    "summarize_text": handle_summarize_text,
    "extract_keywords": handle_extract_keywords,
}


def execute_handler(request: JobRequestModel) -> Dict[str, JsonValue]:
    handler = HANDLERS[request.kind]
    return handler(request)
