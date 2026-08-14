from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "2.0.0"
FINALIZER_ID = "CODE_ATLAS_SUPPORT_FINALIZER"
EXPECTED_CANONICAL_PATHS = [
    "catalogs/support-error-codes.json",
    "catalogs/resolver-actions.json",
    "catalogs/feature-gates.json",
    "catalogs/surface-status-catalog.json",
]
ALLOWED_STATUS = {
    "PASS_SUPPORT_RESOLVER_CONTRACT_OBSERVED",
    "BLOCKED_SUPPORT_RESOLVER_CONTRACT",
    "BLOCKED_NO_SUPPORT_CANON",
    "NOT_CONFIGURED",
}
ALLOWED_ACTION = {"VERIFY_RUNTIME_WHEN_REQUIRED", "FIX_OR_VERIFY", "VERIFY_SOURCE_LOCATION", "OPTIONAL_ADAPTER_NOT_ENABLED"}
GAP_CLASSIFICATIONS = {"OBSERVED", "MISSING", "BLOCKED", "NOT_CONFIGURED"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_support_finalizer(repo_root: str | Path, atlas_output: str | Path, authority: dict[str, Any] | None = None) -> dict[str, Any]:
    """Finalize observed support evidence without modifying the analyzed repository."""

    repo = Path(repo_root).expanduser().resolve()
    atlas_root = Path(atlas_output).expanduser().resolve()
    support_out = atlas_root / "support_resolver"
    summary_rows = _read_json(support_out / "supportResolverSummary.json", [])
    summary = summary_rows[0] if isinstance(summary_rows, list) and summary_rows and isinstance(summary_rows[0], dict) else {}
    status = str(summary.get("status") or "NOT_CONFIGURED")
    decision = str(summary.get("decision") or "OPTIONAL_ADAPTER_NOT_ENABLED")
    blockers = list(summary.get("blockers") or [])

    source_manifest = _read_json(support_out / "SUPPORT_ATLAS_MANIFEST.json", {})
    final = {
        "schemaVersion": "code_atlas_support_finalizer.v2",
        "generator": {"id": FINALIZER_ID, "version": VERSION},
        "generatedAt": _now(),
        "repoRootName": repo.name,
        "status": status if status in ALLOWED_STATUS else "BLOCKED_SUPPORT_RESOLVER_CONTRACT",
        "decision": decision if decision in ALLOWED_ACTION else "FIX_OR_VERIFY",
        "blockers": blockers,
        "sourceManifestObserved": bool(source_manifest),
        "sourceManifestStatus": source_manifest.get("status") if isinstance(source_manifest, dict) else None,
        "readOnlyRepository": True,
        "productionCertified": False,
        "authority": authority or {"status": "NOT_REQUIRED_BY_NEUTRAL_DEFAULT"},
        "doesNotProve": [
            "runtime support behavior",
            "production readiness",
            "customer environment correctness",
            "legal or compliance status",
        ],
    }
    _write_json(atlas_root / "SUPPORT_FINALIZATION.json", final)
    return final


__all__ = [
    "ALLOWED_ACTION",
    "ALLOWED_STATUS",
    "EXPECTED_CANONICAL_PATHS",
    "FINALIZER_ID",
    "GAP_CLASSIFICATIONS",
    "VERSION",
    "run_support_finalizer",
]
