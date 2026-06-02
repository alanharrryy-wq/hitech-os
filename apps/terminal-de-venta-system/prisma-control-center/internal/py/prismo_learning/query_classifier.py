# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Query classifier for PRISMO Learning."""
from __future__ import annotations
import re

INTENT_PATTERNS = {
    "diagnostic": r"\b(falla|fail|error|diagn[oó]stico|no funciona|broken)\b",
    "evidence": r"\b(evidencia|proof|reporte|manifest|log|zip|archivo)\b",
    "next_step": r"\b(qué sigue|siguiente|recomienda|next|paso)\b",
    "summary": r"\b(resumen|brief|cliente|demo|ejecutivo)\b",
    "graph": r"\b(grafo|graph|patr[oó]n|pattern|relaci[oó]n)\b",
}


def classify_query(text: str) -> dict[str, object]:
    low = (text or "").lower()
    intents = [name for name, pat in INTENT_PATTERNS.items() if re.search(pat, low)]
    risk_words = [w for w in ["delete", "borrar", "deploy", "push", "migrar", "drop", "truncate"] if w in low]
    return {"intents": intents or ["general"], "risk_words": risk_words, "input_chars": len(text or "")}
