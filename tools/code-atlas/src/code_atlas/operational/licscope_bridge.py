from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEPRECATION_STATUS = "BLOCKED_PROJECT_SCOPE_ADAPTER_REQUIRED"


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build_bridge_register(repo_root: Path, source: str = "explicit-adapter-required") -> dict[str, Any]:
    return {
        "schemaVersion": "code_atlas_project_scope_adapter.v2",
        "status": DEPRECATION_STATUS,
        "source": source,
        "productionGreenAllowed": False,
        "productionCertified": False,
        "remainingBlockers": ["Project-specific scope evidence must be supplied through an explicit profile or adapter."],
        "proves": [],
        "doesNotProve": [
            "tenant isolation",
            "runtime scope correctness",
            "production readiness",
            "cross-system provenance",
        ],
    }


def verify_bridge(repo_root: Path, evidence_zip: Path | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "status": DEPRECATION_STATUS,
        "repoRootName": Path(repo_root).name,
        "evidenceProvided": bool(evidence_zip),
        "productionCertified": False,
        "message": "The historical implicit scope adapter is disabled in neutral core. Configure an explicit project adapter instead.",
    }


def apply_bridge_to_output_dir(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    raise RuntimeError(DEPRECATION_STATUS)


def apply_bridge_to_dbevid_zip(repo_root: Path, evidence_zip: Path, output_zip: Path, work_dir: Path | None = None) -> dict[str, Any]:
    raise RuntimeError(DEPRECATION_STATUS)


__all__ = [
    "DEPRECATION_STATUS",
    "apply_bridge_to_dbevid_zip",
    "apply_bridge_to_output_dir",
    "build_bridge_register",
    "json_dumps",
    "verify_bridge",
]
