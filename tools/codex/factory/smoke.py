from __future__ import annotations

from typing import Any

from .common import RUNS_DIR, WORKERS, iso_utc, stable_sha256_text, write_json, write_text
from .contracts import bundle_dir, scaffold_all_bundles, validate_run
from .integrator import integrate_run
from .run_id import next_run_identity

SAMPLE_PATHS = {
    "A_worker": ["apps/demo/src/a_feature.ts", "apps/demo/src/a_service.ts"],
    "B_worker": ["apps/demo/src/b_feature.ts", "apps/demo/src/b_ui.ts"],
    "C_worker": ["tools/demo/c_tool.py", "tools/demo/c_manifest.json"],
    "D_worker": ["docs/demo/d_validation.md", "docs/demo/d_matrix.md"],
}


def _emit_worker_content(run_id: str, worker: str) -> None:
    root = bundle_dir(run_id, worker)
    status = {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "status": "PASS",
        "noop": True,
        "noop_reason": "factory smoke fixture is declarative only",
        "noop_ack": worker,
        "started_at": iso_utc(),
        "ended_at": iso_utc(),
        "required_checks": [{"name": "smoke_worker", "status": "PASS"}],
        "optional_checks": [],
        "errors": [],
        "warnings": [],
        "artifacts": ["SUMMARY.md", "FILES_CHANGED.json", "DIFF.patch"],
    }
    write_json(root / "STATUS.json", status)

    write_json(
        root / "FILES_CHANGED.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "owner": worker,
            "changes": [],
            "noop": True,
            "noop_reason": "factory smoke fixture is declarative only",
            "noop_ack": worker,
        },
    )

    write_json(
        root / "SCOPE_LOCK.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "worker_id": worker,
            "allowed_globs": ["apps/demo/**", "tools/demo/**", "docs/demo/**"],
            "blocked_globs": ["services/**"],
            "allow_shared_paths": [],
        },
    )

    write_json(
        root / "HANDOFF_NOTE.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "worker_id": worker,
            "summary": f"{worker} smoke summary",
            "decisions": [f"{worker} chose deterministic fixture"],
            "risks": [],
            "next_actions": ["Run integration"],
        },
    )

    write_text(root / "SUMMARY.md", f"# {worker} summary\n\nSmoke fixture for {worker}.\n")
    write_text(root / "SUGGESTIONS.md", f"# {worker} suggestions\n\n- No suggestions.\n")

    write_text(root / "DIFF.patch", "")

    write_json(
        root / "LOGS" / "INDEX.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "owner": worker,
            "logs": [
                {
                    "name": "smoke_generation",
                    "path": "LOGS/smoke_generation.log.txt",
                    "rc": 0,
                }
            ],
        },
    )
    write_text(root / "LOGS" / "smoke_generation.log.txt", f"generated fixture for {worker}\n")


def run_smoke(run_id: str | None = None) -> dict[str, Any]:
    chosen_run_id = run_id or next_run_identity("factory_smoke").run_id
    scaffold_all_bundles(chosen_run_id, workers=list(WORKERS))
    for worker in WORKERS:
        _emit_worker_content(chosen_run_id, worker)

    validation_before = validate_run(chosen_run_id, workers=list(WORKERS))
    integration_first = integrate_run(chosen_run_id, workers=list(WORKERS))
    first_report = (bundle_dir(chosen_run_id, "Z_integrator") / "FINAL_REPORT.txt").read_text(encoding="utf-8")
    first_digest = stable_sha256_text(first_report)

    integration_second = integrate_run(chosen_run_id, workers=list(WORKERS))
    second_report = (bundle_dir(chosen_run_id, "Z_integrator") / "FINAL_REPORT.txt").read_text(encoding="utf-8")
    second_digest = stable_sha256_text(second_report)

    deterministic = first_digest == second_digest
    final_status = "PASS" if integration_first["status"] == "PASS" and deterministic else "BLOCKED"

    payload = {
        "schema_version": 1,
        "run_id": chosen_run_id,
        "status": final_status,
        "validation_before": validation_before,
        "integration_first": integration_first,
        "integration_second": integration_second,
        "deterministic": deterministic,
        "digests": {
            "first": first_digest,
            "second": second_digest,
        },
    }

    smoke_dir = RUNS_DIR / chosen_run_id / "Z_integrator" / "LOGS"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    write_json(smoke_dir / "factory_smoke_STATUS.json", payload)
    return payload
