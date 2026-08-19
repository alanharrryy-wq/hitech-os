# -*- coding: utf-8 -*-
"""Read-only Change Intelligence repository runtime adapter for Prisma Cloud Center.

This adapter projects a deliberately small, sanitized envelope from the canonical
Code Atlas intelligence API. It does not own repository discovery, registration,
private-repository rental, licensing, source browsing, or mutation.
"""
from __future__ import annotations

import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCHEMA_VERSION = "prisma.change_intelligence.repository_runtime.v1"
ROUTE = "/api/command-center/change-intelligence/repository"
CACHE_TTL_SECONDS = 15.0
_CACHE_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {"identityKey": None, "expiresAt": 0.0, "payload": None}

DOES_NOT_PROVE = [
    "future provider permission persistence",
    "authorization for any other repository",
    "hosted multi-tenant execution",
    "private-repository production readiness",
    "paid-pilot readiness",
    "human usefulness",
    "independent-agent usefulness",
    "production certification",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _find_repo_root(lab_root: Path) -> Path:
    start = Path(lab_root).resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() and (candidate / "tools" / "code-atlas" / "src").is_dir():
            return candidate
    raise RuntimeError("REPOSITORY_ROOT_UNAVAILABLE")


def _load_code_atlas(repo_root: Path):
    src = repo_root / "tools" / "code-atlas" / "src"
    src_text = str(src)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)
    from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context
    from code_atlas.intelligence.common import git_identity
    return IntelligenceRequest, resolve_intelligence_context, git_identity


def _safe_repository_identity(remote: Any, fallback_name: str) -> str:
    text = str(remote or "").strip()
    if not text:
        return fallback_name or "UNKNOWN"

    path = ""
    if re.match(r"^[^/@\s]+@[^:\s]+:.+$", text):
        path = text.split(":", 1)[1]
    elif "://" in text:
        try:
            path = urlparse(text).path
        except Exception:
            path = ""
    else:
        path = text.replace("\\", "/")

    path = path.strip().replace("\\", "/").strip("/")
    if path.lower().endswith(".git"):
        path = path[:-4]
    parts = [part for part in path.split("/") if part and part not in {".", ".."}]
    candidate = "/".join(parts[-2:]) if len(parts) >= 2 else (parts[-1] if parts else fallback_name)
    candidate = re.sub(r"[^A-Za-z0-9._/-]", "", str(candidate or ""))
    return candidate or fallback_name or "UNKNOWN"


def _number(value: Any) -> int | float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _coverage(context: dict[str, Any]) -> dict[str, Any]:
    inventory = context.get("inventory") if isinstance(context.get("inventory"), dict) else {}
    physical = inventory.get("physicalCoverage") if isinstance(inventory.get("physicalCoverage"), dict) else {}
    semantic = inventory.get("semanticCoverage") if isinstance(inventory.get("semanticCoverage"), dict) else {}
    return {
        "status": "MEASURED",
        "physical": {
            "enumerated": _number(physical.get("enumerated")),
            "expected": _number(physical.get("expected")),
            "percent": _number(physical.get("percent")),
        },
        "semantic": {
            "eligibleText": _number(semantic.get("eligibleText")),
            "contentRead": _number(semantic.get("contentRead")),
            "percent": _number(semantic.get("percent")),
            "recognizedSourceFiles": _number(semantic.get("recognizedSourceFiles")),
            "recognizedSourceRead": _number(semantic.get("recognizedSourceRead")),
            "recognizedSourceCoveragePercent": _number(semantic.get("recognizedSourceCoveragePercent")),
        },
    }


def _blocked(error_code: str) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "ok": False,
        "status": "BLOCKED",
        "errorCode": error_code,
        "repository": {
            "identity": "UNKNOWN",
            "head": "UNKNOWN",
            "tree": "UNKNOWN",
            "branch": "UNKNOWN",
            "dirty": "UNKNOWN",
        },
        "freshness": {"status": "UNKNOWN", "observedAt": _utc_now()},
        "coverage": {"status": "UNKNOWN"},
        "readiness": {"status": "BLOCKED"},
        "provenance": {
            "source": "code_atlas.intelligence.resolve_intelligence_context",
            "runtimeEnvelope": True,
            "rawContextExposed": False,
        },
        "readOnly": True,
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": list(DOES_NOT_PROVE),
        "_httpStatus": 503,
    }


def _project(repo_root: Path, context: dict[str, Any]) -> dict[str, Any]:
    if context.get("readOnly") is not True or context.get("productionCertified") is not False:
        return _blocked("CODE_ATLAS_CONTRACT_CEILING_VIOLATION")

    inventory = context.get("inventory") if isinstance(context.get("inventory"), dict) else {}
    identity = inventory.get("identity") if isinstance(inventory.get("identity"), dict) else {}
    snapshot = context.get("snapshot") if isinstance(context.get("snapshot"), dict) else {}
    snapshot_repo = snapshot.get("repository") if isinstance(snapshot.get("repository"), dict) else {}

    head = snapshot_repo.get("head") or identity.get("head")
    tree = snapshot_repo.get("tree") or identity.get("tree")
    branch = snapshot_repo.get("branch") or identity.get("branch")
    dirty = snapshot_repo.get("dirty")
    if dirty is None:
        dirty = identity.get("dirty")

    if not isinstance(head, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", head):
        return _blocked("CODE_ATLAS_HEAD_UNAVAILABLE")
    if not isinstance(tree, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", tree):
        return _blocked("CODE_ATLAS_TREE_UNAVAILABLE")

    repository_identity = _safe_repository_identity(identity.get("remote"), repo_root.name)
    if repository_identity == "UNKNOWN":
        return _blocked("CODE_ATLAS_REPOSITORY_IDENTITY_UNAVAILABLE")

    generated_at = snapshot.get("generatedAt")
    profile = context.get("profile") if isinstance(context.get("profile"), dict) else {}
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "ok": True,
        "status": "RUNTIME_SOURCE_READ_ONLY",
        "repository": {
            "identity": repository_identity,
            "head": head.lower(),
            "tree": tree.lower(),
            "branch": str(branch or "UNKNOWN"),
            "dirty": bool(dirty),
        },
        "freshness": {
            "status": "LIVE_SCAN",
            "observedAt": str(generated_at or _utc_now()),
            "snapshotDigest": snapshot.get("snapshotDigest"),
        },
        "coverage": _coverage(context),
        "readiness": {
            "status": "RUNTIME_FACTS_AVAILABLE" if dirty is False else "BLOCKED_WORKTREE_DIRTY",
            "worktreeClean": dirty is False,
            "sourceFactsAvailable": True,
        },
        "provenance": {
            "source": "code_atlas.intelligence.resolve_intelligence_context",
            "contextSchemaVersion": context.get("schemaVersion"),
            "snapshotSchemaVersion": snapshot.get("schemaVersion"),
            "scannerVersion": snapshot.get("scannerVersion"),
            "profileId": profile.get("id"),
            "runtimeEnvelope": True,
            "rawContextExposed": False,
        },
        "readOnly": True,
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": list(DOES_NOT_PROVE),
    }
    if dirty is not False:
        payload["ok"] = False
        payload["status"] = "BLOCKED"
        payload["errorCode"] = "CODE_ATLAS_WORKTREE_DIRTY"
        payload["_httpStatus"] = 409
    return payload


def repository_projection(lab_root: Path) -> dict[str, Any]:
    try:
        repo_root = _find_repo_root(lab_root)
        IntelligenceRequest, resolve_intelligence_context, git_identity = _load_code_atlas(repo_root)
        cheap_identity = git_identity(repo_root)
        identity_key = "|".join(
            str(cheap_identity.get(key) or "UNKNOWN")
            for key in ("head", "tree", "branch", "dirty")
        )
        now = time.monotonic()
        with _CACHE_LOCK:
            cached = _CACHE.get("payload")
            if cached is not None and _CACHE.get("identityKey") == identity_key and now < float(_CACHE.get("expiresAt") or 0):
                return dict(cached)

        request = IntelligenceRequest(
            intent="VERIFY",
            domain="runtime",
            semantic_query="",
            fail_on_missing_authority=False,
            workers=18,
        )
        context = resolve_intelligence_context(repo_root, request=request)
        payload = _project(repo_root, context)
        with _CACHE_LOCK:
            _CACHE["identityKey"] = identity_key
            _CACHE["expiresAt"] = now + CACHE_TTL_SECONDS
            _CACHE["payload"] = dict(payload)
        return payload
    except Exception:
        return _blocked("CODE_ATLAS_RUNTIME_UNAVAILABLE")


def install_runtime(ns: dict[str, Any]) -> None:
    """Install only the Change Intelligence repository GET projection."""
    if ns.get("_CHANGE_INTELLIGENCE_RUNTIME_INSTALLED"):
        return
    ns["_CHANGE_INTELLIGENCE_RUNTIME_INSTALLED"] = True
    previous = ns["command_center_payload"]
    lab_root = Path(ns["LAB_ROOT"])

    def command_center_payload(raw_path: str, method: str = "GET", body: dict[str, Any] | None = None):
        path = urlparse(raw_path).path.rstrip("/")
        if path == ROUTE:
            if method != "GET":
                payload = _blocked("READ_ONLY_ROUTE")
                payload["_httpStatus"] = 405
                return payload
            return repository_projection(lab_root)
        return previous(raw_path, method=method, body=body)

    ns["command_center_payload"] = command_center_payload
