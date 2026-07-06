from __future__ import annotations

import json
from pathlib import Path
from .ag98_policy import classify_preflight_path

def filter_changed_paths(repo: Path, runner, changed_paths: list[str], report: Path | None = None) -> dict:
    kept = []
    excluded = []
    blockers = []
    warnings = []
    decisions = []

    for rel in changed_paths:
        d = classify_preflight_path(repo, rel)
        decisions.append(d)
        decision = d.get("decision")
        if decision == "COMMITTABLE":
            kept.append(rel)
        elif decision == "EXCLUDE_SAFE":
            excluded.append(d)
            warnings.append({"severity": "INFO", "kind": d.get("kind"), "path": rel, "detail": d.get("detail")})
        elif decision == "BLOCK":
            kept.append(rel)
            blockers.append({"severity": "BLOCKER", "kind": d.get("kind"), "path": rel, "detail": d.get("detail")})
        else:
            kept.append(rel)
            warnings.append({"severity": "WARNING", "kind": d.get("kind", "review_required"), "path": rel, "detail": d.get("detail", "review required")})

    summary = {
        "schema": "autogit.ag98_runtime_filter.v1",
        "total_input": len(changed_paths),
        "total_committable": len(kept),
        "total_excluded": len(excluded),
        "committable_paths": kept,
        "excluded": excluded,
        "blockers": blockers,
        "warnings": warnings,
        "decisions": decisions,
    }
    if report:
        try:
            (report / "AG98_RUNTIME_NOISE.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    return summary
