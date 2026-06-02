# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Evidence classifier by name, path, text signals and ZIP inventories."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .constants import *
from .pass_fail_detector import detect_status_from_text
from .scoring import authority_weight, evidence_confidence
from .surface_detector import detect_surfaces

CLASS_HINTS = [
    (EVIDENCE_PLAYWRIGHT, ["playwright", "trace.zip", "screenshot", "visual-qa", "browser"]),
    (EVIDENCE_GOVERNANCE_CANON, ["governance", "canon", "authority", "policy"]),
    (EVIDENCE_QUERY_TYPE_GUARD, ["query_type_guard", "certainty_normalized", "null_guard"]),
    (EVIDENCE_PRISMO_VERIFY_REPORT, ["prismo", "verify", "verification", "learning"]),
    (EVIDENCE_SKILLOPS_CLEAN, ["skillops", "clean", "cleanup"]),
    (EVIDENCE_RELEASE_TRAIN, ["release", "train", "pilot"]),
    (EVIDENCE_DEPENDENCY_ATLAS, ["dependency", "atlas", "tree"]),
    (EVIDENCE_DB_GLASS_ERD, ["db_glass", "erd", "schema"]),
    (EVIDENCE_CODEX_REPORT, ["codex", "agents", "continuation"]),
    (EVIDENCE_RUNTIME_SCREENSHOT, ["screenshot", "png", "jpg", "browser"]),
    (EVIDENCE_REPO_INVENTORY, ["files/repo", "repo_inventory", "worktree"]),
    (EVIDENCE_DOWNLOADS_INVENTORY, ["descargasf", "downloads", "file_inventory"]),
]


def classify_text_blob(name: str, text: str) -> str:
    low = f"{name}\n{text}".lower()
    for etype, hints in CLASS_HINTS:
        if any(h in low for h in hints):
            return etype
    return EVIDENCE_UNKNOWN_PRISMO_RELATED


def detect_status(record: dict[str, Any]) -> str:
    if record.get("status"):
        return str(record["status"]).upper()
    pieces = [str(record.get("name") or ""), str(record.get("safe_source_label") or ""), str(record.get("preview") or "")]
    for sample in record.get("small_text_samples") or []:
        if isinstance(sample, dict):
            pieces.append(str(sample.get("preview") or ""))
    return detect_status_from_text("\n".join(pieces))


def detect_scope(record: dict[str, Any]) -> list[str]:
    chunks = [str(record.get("name") or ""), str(record.get("safe_source_label") or ""), str(record.get("preview") or "")]
    return detect_surfaces(*chunks)


def classify_zip_inventory(zip_report: dict[str, Any]) -> dict[str, Any]:
    entries = "\n".join(zip_report.get("entries_preview") or [])
    samples = "\n".join(str(s.get("preview", "")) for s in zip_report.get("small_text_samples") or [] if isinstance(s, dict))
    etype = classify_text_blob(str(zip_report.get("source_path") or "zip"), entries + "\n" + samples)
    record = dict(zip_report)
    record["type"] = etype
    record["status"] = detect_status(record)
    record["surface"] = detect_scope(record)
    record["confidence"] = evidence_confidence(record)
    record["authority_weight"] = authority_weight(record)
    return record


def classify_record(record: dict[str, Any]) -> dict[str, Any]:
    name = str(record.get("name") or Path(str(record.get("source_path") or "")).name)
    preview = str(record.get("preview") or "")
    enriched = dict(record)
    enriched["type"] = classify_text_blob(name, preview + "\n" + str(record.get("safe_source_label") or ""))
    enriched["status"] = detect_status(enriched)
    enriched["surface"] = detect_scope(enriched)
    enriched["confidence"] = evidence_confidence(enriched)
    enriched["authority_weight"] = authority_weight(enriched)
    return enriched
