from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config_loader import CONFIG_ROOT, CONTROL_ROOT, INTERNAL_ROOT, LATEST_ROOT, LOG_ROOT, TERMINAL_ROOT
from prismo_safety import sanitize_text


AUTHORITY_PRECEDENCE = [
    "PRISMA_CURRENT_STATE",
    "current code/runtime/verifiers",
    "current governance docs",
    "fresh temporary evidence",
    "planned docs",
    "legacy docs",
    "model inference without evidence",
]

LOCAL_CONTEXT_FILES = [
    CONFIG_ROOT / "services.json",
    CONFIG_ROOT / "safety_policy.json",
    CONFIG_ROOT / "health_profiles.json",
    INTERNAL_ROOT / "docs" / "README_OPERADOR.md",
    INTERNAL_ROOT / "docs" / "README_OPERADOR_CRYSTAL.md",
    INTERNAL_ROOT / "docs" / "data-lifecycle" / "README.md",
    TERMINAL_ROOT / "docs" / "PRISMA_CURRENT_STATE.md",
    TERMINAL_ROOT / "docs" / "PRISMA_CURRENT_STATE.json",
    TERMINAL_ROOT / "docs" / "PRISMA_DOCUMENT_PRECEDENCE_RULES.md",
    TERMINAL_ROOT / "docs" / "PRISMA_DOCS_STATUS_TAGS.md",
    TERMINAL_ROOT / "docs" / "PRISMA_MASTER_DOC_INDEX.md",
]

FORBIDDEN_PARTS = {".env", "node_modules", ".next", "out", "dist", "build"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3"}


def _safe_read_text(path: Path, limit: int = 9000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    lowered = str(path).lower()
    if any(part in lowered for part in FORBIDDEN_PARTS) or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def _load_json(path: Path) -> Any:
    text = _safe_read_text(path, limit=12000)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _summarize_file(path: Path) -> dict[str, Any] | None:
    text = _safe_read_text(path)
    if not text:
        return None
    sanitized, events = sanitize_text(text, max_chars=9000)
    return {
        "path": str(path),
        "exists": True,
        "kind": "json" if path.suffix.lower() == ".json" else "text",
        "preview": sanitized[:1400],
        "char_count": len(sanitized),
        "safety_events": events,
    }


def build_context_packet(user_evidence: str = "") -> dict[str, Any]:
    authority_docs = [item for item in (_summarize_file(path) for path in LOCAL_CONTEXT_FILES) if item]
    health = _load_json(LATEST_ROOT / "health.json")
    public_health = _load_json(LATEST_ROOT / "public-health.json")
    evidence, evidence_events = sanitize_text(user_evidence, max_chars=250000)
    current_state = next((item for item in authority_docs if "PRISMA_CURRENT_STATE" in item["path"]), None)
    control_center_doc = next((item for item in authority_docs if "README_OPERADOR" in item["path"]), None)
    return {
        "authorityRules": AUTHORITY_PRECEDENCE,
        "currentStateExtract": current_state or {"status": "MISSING", "message": "No PRISMA_CURRENT_STATE file found in current repo docs."},
        "controlCenterStatus": {
            "root": str(CONTROL_ROOT),
            "logsRoot": str(LOG_ROOT),
            "docsLoaded": len(authority_docs),
            "operatorDoc": control_center_doc,
        },
        "healthSummary": health or public_health or {"status": "NO_RUNTIME_HEALTH_AVAILABLE"},
        "authorityDocs": authority_docs[:10],
        "userEvidence": evidence[:250000],
        "safetyEvents": evidence_events,
    }


def evidence_cards_from_context(context: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, doc in enumerate(context.get("authorityDocs", [])[:5], start=1):
        source_type = "current_state" if "PRISMA_CURRENT_STATE" in doc.get("path", "") else "doc_current"
        cards.append(
            {
                "id": f"ev_ctx_{index:02d}",
                "title": Path(doc.get("path", "")).name or "Contexto",
                "source_type": source_type,
                "path": doc.get("path", ""),
                "quote": str(doc.get("preview", ""))[:220],
                "summary": f"Contexto local leído desde {Path(doc.get('path', '')).name}.",
                "confidence": "medium",
                "freshness": "current" if source_type == "current_state" else "unknown",
            }
        )
    if not cards:
        cards.append(
            {
                "id": "ev_no_context",
                "title": "Contexto local no confirmado",
                "source_type": "unknown",
                "summary": "No se encontró evidencia local suficiente para confirmar la respuesta.",
                "confidence": "low",
                "freshness": "unknown",
            }
        )
    return cards
