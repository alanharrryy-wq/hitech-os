from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .common import (
    CANONICAL_POST_RUN_WORKERS,
    CONTRACTS_DIR,
    INTEGRATOR,
    REPO_ROOT,
    RUNS_DIR,
    WORKERS,
    canonical_worker_id,
    canonicalize_workers,
    ensure_dir,
    iso_utc,
    read_json,
    resolve_bundle_dir,
    write_json,
    write_text,
)
from .config import load_factory_config
from .schemas import validate_payload

WORKER_REQUIRED_FILES: tuple[str, ...] = (
    "STATUS.json",
    "SUMMARY.md",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "SUGGESTIONS.md",
    "SCOPE_LOCK.json",
    "HANDOFF_NOTE.json",
    "LOGS/INDEX.json",
    "CODEX_OUTPUT.txt",
    "SELF_EVAL_REPORT.json",
    "SANCTION_SCORE.json",
    "SELF_CORRECTION_LOG.jsonl",
)

INTEGRATOR_REQUIRED_FILES: tuple[str, ...] = (
    "STATUS.json",
    "FINAL_REPORT.txt",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "MERGE_PLAN.md",
    "LOGS/INDEX.json",
    "GRAVITY_REPORT.json",
    "PROTECTED_NODES.json",
    "IMPACT_CONE_REPORT.json",
    "DEPENDENCY_DIFF.json",
    "DISPATCH_RECOMMENDATIONS.json",
    "GRAVITY_SUMMARY.md",
    "DISPATCH_RECOMMENDATIONS.md",
)

INTEGRATOR_GRAPH_SCHEMA_FILES: tuple[tuple[str, str], ...] = (
    ("GRAVITY_REPORT.json", "gravity_report"),
    ("PROTECTED_NODES.json", "protected_nodes"),
    ("IMPACT_CONE_REPORT.json", "impact_cone_report"),
    ("DEPENDENCY_DIFF.json", "dependency_diff"),
    ("DISPATCH_RECOMMENDATIONS.json", "dispatch_recommendations"),
)

POST_RUN_REQUIRED_FILES: dict[str, tuple[str, ...]] = {
    "R_reviewer": (
        "REVIEW_REPORT.json",
        "REVIEW_FINDINGS.json",
        "REVIEW_RECOMMENDATIONS.json",
        "ARCH_REVIEW_SUMMARY.md",
    ),
    "E_planner": (
        "TASK_BANK_DELTA.json",
        "TASK_BANK_INGEST_REPORT.json",
        "PLANNER_RECOMMENDATIONS.json",
        "PLANNER_SUMMARY.md",
    ),
}

POST_RUN_SCHEMA_FILES: dict[str, tuple[tuple[str, str], ...]] = {
    "R_reviewer": (
        ("REVIEW_REPORT.json", "review_report"),
        ("REVIEW_FINDINGS.json", "review_findings"),
        ("REVIEW_RECOMMENDATIONS.json", "review_recommendations"),
    ),
    "E_planner": (
        ("TASK_BANK_DELTA.json", "task_bank_delta"),
        ("TASK_BANK_INGEST_REPORT.json", "task_bank_ingest_report"),
        ("PLANNER_RECOMMENDATIONS.json", "planner_recommendations"),
    ),
}

EVOLUTIONARY_REQUIRED_FILES: tuple[str, ...] = (
    "SELF_EVAL_REPORT.json",
    "SANCTION_SCORE.json",
    "SELF_CORRECTION_LOG.jsonl",
)
EVOLUTIONARY_MAX_ATTEMPTS = 3
EVOLUTIONARY_RETRY_SECONDS = 0.5
EVOLUTIONARY_ENGINE = REPO_ROOT / "tools" / "hos" / "guardrails" / "evolutionary_sanctions.py"
EVOLUTIONARY_POLICY = REPO_ROOT / "tools" / "hos" / "guardrails" / "policy.json"


def registry_path() -> Path:
    return CONTRACTS_DIR / "contracts_registry.json"


def load_registry() -> dict[str, Any]:
    payload = read_json(registry_path())
    errors = validate_payload("contracts_registry", payload)
    if errors:
        joined = "\n".join(errors)
        raise ValueError(f"contracts registry invalid:\n{joined}")
    return payload


def run_dir(run_id: str) -> Path:
    return RUNS_DIR / run_id


def bundle_dir(run_id: str, worker: str) -> Path:
    return resolve_bundle_dir(run_id, canonical_worker_id(worker), prefer_existing=True)


def _default_worker_status(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "contract_version": 2,
        "run_id": run_id,
        "worker_id": worker,
        "status": "PENDING",
        "noop": False,
        "noop_reason": "",
        "noop_ack": "",
        "started_at": "",
        "ended_at": "",
        "required_checks": [],
        "optional_checks": [],
        "errors": [],
        "warnings": [],
        "artifacts": [],
    }


def _default_files_changed(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "owner": worker,
        "changes": [],
        "noop": True,
        "noop_reason": "scaffold placeholder: worker has not declared changes",
        "noop_ack": worker,
    }


def _default_scope_lock(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "allowed_globs": [f"{worker.lower()}/**"],
        "blocked_globs": [],
        "allow_shared_paths": [],
    }


def _default_handoff(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "summary": "",
        "decisions": [],
        "risks": [],
        "next_actions": [],
    }


def _default_log_index(run_id: str, owner: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "owner": owner,
        "logs": [],
    }


def _default_graph_repository() -> dict[str, Any]:
    return {
        "repo_root": ".",
        "base_ref": "HEAD",
        "head_ref": "HEAD",
        "commit_sha": "0000000",
        "comparison_basis": "working_tree",
    }


def _default_snapshot_lineage() -> dict[str, Any]:
    return {
        "snapshot_id": "SNAP_NONE",
        "previous_snapshot_id": None,
        "baseline_snapshot_id": None,
        "lineage_mode": "NOT_AVAILABLE",
        "graph_build_id": "GRAPH_BUILD_NONE",
    }


def _default_dependency_basis() -> dict[str, Any]:
    return {
        "upstream_nodes": [],
        "downstream_nodes": [],
        "dependency_count": 0,
        "transitive_dependency_count": 0,
        "graph_scope_reference": "repository",
    }


def _default_scope_ref(scope_id: str, owner: str) -> dict[str, Any]:
    return {
        "scope_id": scope_id,
        "scope_type": "workspace",
        "scope_path": ".",
        "owner_worker": owner,
        "parent_scope_id": None,
        "internal_only": True,
    }


def _base_graph_artifact(*, artifact_type: str, run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": "2.0.0",
        "schema_family": "HITECH_GRAPH_ANALYSIS",
        "compatibility_mode": "LEGACY_ALIAS_ACCEPTED",
        "minimum_reader_version": "1.0.0",
        "breaking_change": False,
        "artifact_type": artifact_type,
        "artifact_id": f"{artifact_type}:{run_id}:placeholder",
        "artifact_status": "INCOMPLETE",
        "run_id": run_id,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "generator": {
            "actor": worker,
            "tool_name": "tools.codex.factory",
            "tool_version": "2.0.0",
            "execution_mode": "integration",
            "invocation_context": {
                "run_phase": "scaffold",
                "command": "python -m tools.codex.factory.cli scaffold",
                "working_directory": ".",
                "environment_keys": [],
            },
            "source_inputs": [
                {
                    "input_type": "RUN_BUNDLE",
                    "input_id": "SCAFFOLD_INPUT",
                    "input_path": "tools/codex/runs",
                    "input_sha256": None,
                    "input_role": "placeholder",
                }
            ],
        },
        "repository": _default_graph_repository(),
        "snapshot_lineage": _default_snapshot_lineage(),
        "notes": [],
    }


def _default_gravity_report(run_id: str, worker: str) -> dict[str, Any]:
    base = _base_graph_artifact(artifact_type="GRAVITY_REPORT", run_id=run_id, worker=worker)
    base.update(
        {
            "schema_version": "2.1.0",
            "policy": {
                "policy_name": "default_arch_gravity",
                "policy_version": "2.1.0",
                "threshold_mode": "hybrid",
                "thresholds": {
                    "score_scale": "0_to_100",
                    "level_bands": [
                        {
                            "gravity_level": "LOW",
                            "min_inclusive": 0,
                            "max_exclusive": 25,
                            "rationale": "low coupling and limited blast radius",
                        },
                        {
                            "gravity_level": "MEDIUM",
                            "min_inclusive": 25,
                            "max_exclusive": 50,
                            "rationale": "moderate coupling and impact",
                        },
                        {
                            "gravity_level": "HIGH",
                            "min_inclusive": 50,
                            "max_exclusive": 80,
                            "rationale": "high coupling and validation burden",
                        },
                        {
                            "gravity_level": "PROTECTED",
                            "min_inclusive": 80,
                            "max_exclusive": None,
                            "rationale": "protected-node policy threshold",
                        },
                    ],
                    "protected_conditions": ["PROTECTED_POLICY_RULE"],
                },
                "protected_node_rule": "Protected nodes require explicit protocol before mutation.",
                "scoring_notes": [],
            },
            "source_graph": {
                "graph_scope": "repository",
                "graph_artifact_root": "tools/codex/runs",
                "internal_only": True,
                "total_graph_files": 0,
                "total_nodes_seen": 0,
                "total_edges_seen": 0,
            },
            "summary": {
                "node_count": 0,
                "edge_count": 0,
                "scope_count": 0,
                "protected_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "hotspot_count": 0,
                "cycle_count": 0,
                "orphan_count": 0,
                "external_dependency_count": 0,
                "highest_risk_level": "NONE",
                "refactor_candidate_count": 0,
                "protected_recommendation_count": 0,
                "architecture_risk_flag_count": 0,
                "centrality_metric_count": 0,
                "centrality_computed_node_count": 0,
            },
            "centrality_summary": {
                "computed": False,
                "graph_model": "DIRECTED_GENERAL",
                "normalization": "ALGORITHM_DEFAULT",
                "damping_factor": 0.85,
                "max_iterations": 100,
                "convergence_tolerance": 0.000001,
                "node_coverage": 0,
                "metric_status": [
                    {
                        "metric": "BETWEENNESS_CENTRALITY",
                        "computed": False,
                        "computation_basis": "NOT_COMPUTED",
                        "algorithm": "Brandes",
                        "notes": ["Placeholder scaffold value."],
                    },
                    {
                        "metric": "PAGERANK",
                        "computed": False,
                        "computation_basis": "NOT_COMPUTED",
                        "algorithm": "PageRank",
                        "notes": ["Placeholder scaffold value."],
                    },
                    {
                        "metric": "EIGENVECTOR_CENTRALITY",
                        "computed": False,
                        "computation_basis": "NOT_COMPUTED",
                        "algorithm": "Power iteration",
                        "notes": ["Placeholder scaffold value."],
                    },
                    {
                        "metric": "CLOSENESS_CENTRALITY",
                        "computed": False,
                        "computation_basis": "NOT_COMPUTED",
                        "algorithm": "Shortest-path based",
                        "notes": ["Placeholder scaffold value."],
                    },
                    {
                        "metric": "DEGREE_CENTRALITY",
                        "computed": False,
                        "computation_basis": "NOT_COMPUTED",
                        "algorithm": "Degree-based",
                        "notes": ["Placeholder scaffold value."],
                    },
                    {
                        "metric": "BRIDGING_CENTRALITY",
                        "computed": False,
                        "computation_basis": "NOT_COMPUTED",
                        "algorithm": "Bridge coefficient",
                        "notes": ["Placeholder scaffold value."],
                    },
                ],
                "top_nodes_by_metric": [],
                "computation_notes": [
                    "Centrality metrics are optional but recommended for high-quality gravity scoring.",
                ],
            },
            "nodes": [],
            "hotspots": [],
            "refactor_candidates": [],
            "protected_node_recommendations": [],
            "architecture_risk_flags": [],
            "anomalies": {
                "cycles": [],
                "orphan_nodes": [],
                "unstable_hubs": [],
                "missing_owner_nodes": [],
                "external_drift": [],
                "classification_regressions": [],
                "ownership_mismatches": [],
                "contract_gaps": [],
            },
        }
    )
    return base


def _default_protected_nodes(run_id: str, worker: str) -> dict[str, Any]:
    protocol_steps = [
        "DECLARE_PROTECTED_CHANGE",
        "GENERATE_IMPACT_CONE_REPORT",
        "GENERATE_DEPENDENCY_DIFF",
        "REQUEST_D_VALIDATION_REVIEW",
        "REQUEST_Z_APPROVAL",
        "ATTACH_EVIDENCE_TO_FINAL_REPORT",
    ]
    base = _base_graph_artifact(artifact_type="PROTECTED_NODES", run_id=run_id, worker=worker)
    base.update(
        {
            "policy": {
                "rule_name": "protected_node_protocol",
                "rule_version": "2.0.0",
                "default_block_result": "BLOCKED",
                "required_protocol_steps": protocol_steps,
                "explicit_authorization_required": True,
                "unauthorized_mutation_status": "BLOCKED",
            },
            "summary": {
                "protected_count": 0,
                "watched_count": 0,
                "guarded_count": 0,
                "protected_level_count": 0,
                "locked_count": 0,
                "exemption_count": 0,
                "highest_risk_level": "NONE",
            },
            "protected_nodes": [],
            "exemptions": [],
        }
    )
    return base


def _default_impact_cone_report(run_id: str, worker: str) -> dict[str, Any]:
    base = _base_graph_artifact(artifact_type="IMPACT_CONE_REPORT", run_id=run_id, worker=worker)
    base.update(
        {
            "summary": {
                "changed_entity_count": 0,
                "directly_affected_count": 0,
                "transitively_affected_count": 0,
                "affected_scope_count": 0,
                "affected_contract_count": 0,
                "affected_test_count": 0,
                "protected_entity_count": 0,
                "highest_risk_entities": [],
                "highest_risk_level": "NONE",
            },
            "changed_entities": [],
            "aggregate_risk": {
                "overall_risk_level": "NONE",
                "reason_codes": ["VALIDATION_GAP"],
                "rationale": "No changed entities were detected.",
                "protected_nodes_touched": [],
                "validation_burden": {
                    "command_count": 0,
                    "test_count": 0,
                    "contract_count": 0,
                    "estimated_minutes": 0,
                    "risk_level": "NONE",
                },
                "recommended_owner_sequence": [
                    "A_core",
                    "B_tooling",
                    "C_features",
                    "D_validation",
                    "Z_aggregator",
                    "R_reviewer",
                    "E_planner",
                ],
            },
            "validation_targets": {
                "contracts": [],
                "tests": [],
                "commands": [],
                "smoke_paths": [],
            },
        }
    )
    return base


def _default_dependency_diff(run_id: str, worker: str) -> dict[str, Any]:
    base = _base_graph_artifact(artifact_type="DEPENDENCY_DIFF", run_id=run_id, worker=worker)
    base.update(
        {
            "comparison": {
                "baseline_snapshot_id": "SNAP_NONE",
                "current_snapshot_id": "SNAP_NONE",
                "baseline_run_id": run_id,
                "current_run_id": run_id,
                "baseline_ref": "HEAD",
                "current_ref": "HEAD",
                "comparable": True,
                "incompatibility_reason": "",
            },
            "summary": {
                "node_add_count": 0,
                "node_remove_count": 0,
                "edge_add_count": 0,
                "edge_remove_count": 0,
                "classification_change_count": 0,
                "protected_add_count": 0,
                "protected_remove_count": 0,
                "cycle_add_count": 0,
                "cycle_remove_count": 0,
                "ownership_change_count": 0,
            },
            "nodes_added": [],
            "nodes_removed": [],
            "edges_added": [],
            "edges_removed": [],
            "classification_changes": [],
            "cycle_changes": [],
            "ownership_changes": [],
            "contract_changes": [],
        }
    )
    return base


def _default_dispatch_recommendations(run_id: str, worker: str) -> dict[str, Any]:
    base = _base_graph_artifact(artifact_type="DISPATCH_RECOMMENDATIONS", run_id=run_id, worker=worker)
    base.update(
        {
            "planning_scope": {
                "planning_mode": "next_iteration",
                "based_on_run_id": run_id,
                "based_on_snapshot_id": "SNAP_NONE",
                "respects_current_run_ownership": True,
                "advisory_only": True,
                "policy_version": "2.0.0",
            },
            "summary": {
                "slice_count": 0,
                "protected_slice_count": 0,
                "blocked_slice_count": 0,
                "deferred_slice_count": 0,
                "high_risk_slice_count": 0,
                "recommended_execution_order": [
                    "A_core",
                    "B_tooling",
                    "C_features",
                    "D_validation",
                    "Z_aggregator",
                    "R_reviewer",
                    "E_planner",
                ],
                "highest_risk_level": "NONE",
            },
            "worker_queues": {
                "A_core": [],
                "B_tooling": [],
                "C_features": [],
                "D_validation": [],
                "Z_aggregator": [],
                "R_reviewer": [],
                "E_planner": [],
            },
            "recommended_slices": [],
            "deferred_work": [],
            "blocked_work": [],
        }
    )
    return base


def _default_review_report(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "status": "PASS",
        "summary": {
            "finding_count": 0,
            "recommendation_count": 0,
            "severity_counts": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0,
            },
            "category_counts": {},
        },
        "history": {
            "runs_considered": 0,
            "repeated_risk_patterns": 0,
        },
        "source_artifacts": [
            "Z_aggregator/GRAVITY_REPORT.json",
            "Z_aggregator/IMPACT_CONE_REPORT.json",
            "Z_aggregator/DEPENDENCY_DIFF.json",
            "Z_aggregator/DISPATCH_RECOMMENDATIONS.json",
        ],
        "notes": [],
    }


def _default_review_findings(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "findings": [],
    }


def _default_review_recommendations(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "recommendations": [],
    }


def _default_task_bank_delta(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "status": "PASS",
        "summary": {
            "candidate_count": 0,
            "added_count": 0,
            "updated_count": 0,
            "duplicate_count": 0,
        },
        "added_tasks": [],
        "updated_tasks": [],
        "skipped_duplicates": [],
    }


def _default_task_bank_ingest_report(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "status": "PASS",
        "summary": {
            "source_count": 0,
            "candidate_count": 0,
            "accepted_count": 0,
            "rejected_count": 0,
        },
        "sources": [],
        "accepted": [],
        "rejected": [],
        "notes": [],
    }


def _default_planner_recommendations(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": "1970-01-01T00:00:00Z",
        "recommendations": [],
        "notes": [],
    }


def scaffold_worker_bundle(run_id: str, worker: str) -> dict[str, Any]:
    worker = canonical_worker_id(worker)
    target = bundle_dir(run_id, worker)
    ensure_dir(target)
    ensure_dir(target / "LOGS")

    created: list[str] = []

    files_payload: dict[str, Any] = {
        "STATUS.json": _default_worker_status(run_id, worker),
        "FILES_CHANGED.json": _default_files_changed(run_id, worker),
        "SCOPE_LOCK.json": _default_scope_lock(run_id, worker),
        "HANDOFF_NOTE.json": _default_handoff(run_id, worker),
        "LOGS/INDEX.json": _default_log_index(run_id, worker),
        "SELF_EVAL_REPORT.json": {
            "run_id": run_id,
            "worker_id": worker,
            "sanction_level": "WARN",
            "sanction_score": 1.0,
            "flags": ["PENDING_AUTOCLOSEOUT_EVALUATION"],
        },
        "SANCTION_SCORE.json": {
            "run_id": run_id,
            "worker_id": worker,
            "sanction_score": 1.0,
            "sanction_level": "WARN",
            "vdi": 0.0,
            "loc_delta": 0,
            "notes": ["PENDING_AUTOCLOSEOUT_EVALUATION"],
        },
    }
    if worker == "R_reviewer":
        files_payload.update(
            {
                "REVIEW_REPORT.json": _default_review_report(run_id, worker),
                "REVIEW_FINDINGS.json": _default_review_findings(run_id, worker),
                "REVIEW_RECOMMENDATIONS.json": _default_review_recommendations(run_id, worker),
            }
        )
    elif worker == "E_planner":
        files_payload.update(
            {
                "TASK_BANK_DELTA.json": _default_task_bank_delta(run_id, worker),
                "TASK_BANK_INGEST_REPORT.json": _default_task_bank_ingest_report(run_id, worker),
                "PLANNER_RECOMMENDATIONS.json": _default_planner_recommendations(run_id, worker),
            }
        )

    for name, payload in files_payload.items():
        path = target / name
        if not path.exists():
            write_json(path, payload)
            created.append(path.as_posix())

    text_files = {
        "SUMMARY.md": f"# {worker} Summary\n\n- Run ID: `{run_id}`\n- Worker: `{worker}`\n- Status: pending\n",
        "SUGGESTIONS.md": f"# {worker} Suggestions\n\n- None yet.\n",
        "DIFF.patch": "",
        "CODEX_OUTPUT.txt": (
            f"# CODEX_OUTPUT_{worker}_{run_id}\n\n"
            "## WHAT CHANGED\n- pending\n\n"
            "## FILES CREATED\n- none\n\n"
            "## FILES MODIFIED\n- none\n\n"
            "## DELETION_REQUESTS\n- none\n\n"
            "## COMMAND LOGS\n- pending\n\n"
            "## DIFF / PATCH\n- see DIFF.patch\n\n"
            "## FINAL SUMMARY\n- pending\n"
        ),
        "SELF_CORRECTION_LOG.jsonl": "",
    }
    if worker == "R_reviewer":
        text_files["ARCH_REVIEW_SUMMARY.md"] = "# Architecture Review Summary\n\nPending review synthesis.\n"
    elif worker == "E_planner":
        text_files["PLANNER_SUMMARY.md"] = "# Planner Summary\n\nPending task bank synthesis.\n"
    for name, text in text_files.items():
        path = target / name
        if not path.exists():
            write_text(path, text)
            created.append(path.as_posix())

    return {
        "worker": worker,
        "bundle_dir": target.as_posix(),
        "created": sorted(created),
    }


def scaffold_integrator_bundle(run_id: str) -> dict[str, Any]:
    worker = INTEGRATOR
    target = bundle_dir(run_id, worker)
    ensure_dir(target)
    ensure_dir(target / "LOGS")

    created: list[str] = []
    json_files = {
        "STATUS.json": {
            "schema_version": 1,
            "contract_version": 2,
            "run_id": run_id,
            "worker_id": worker,
            "status": "PENDING",
            "noop": False,
            "noop_reason": "",
            "noop_ack": "",
            "started_at": "",
            "ended_at": "",
            "required_checks": [],
            "optional_checks": [],
            "errors": [],
            "warnings": [],
            "artifacts": [],
        },
        "FILES_CHANGED.json": {
            "schema_version": 1,
            "run_id": run_id,
            "owner": worker,
            "changes": [],
            "noop": True,
            "noop_reason": "scaffold placeholder: integrator has not declared changes",
            "noop_ack": worker,
        },
        "LOGS/INDEX.json": _default_log_index(run_id, worker),
        "GRAVITY_REPORT.json": _default_gravity_report(run_id, worker),
        "PROTECTED_NODES.json": _default_protected_nodes(run_id, worker),
        "IMPACT_CONE_REPORT.json": _default_impact_cone_report(run_id, worker),
        "DEPENDENCY_DIFF.json": _default_dependency_diff(run_id, worker),
        "DISPATCH_RECOMMENDATIONS.json": _default_dispatch_recommendations(run_id, worker),
    }

    for name, payload in json_files.items():
        path = target / name
        if not path.exists():
            write_json(path, payload)
            created.append(path.as_posix())

    text_files = {
        "FINAL_REPORT.txt": "# Final Report\n\nPending integration.\n",
        "MERGE_PLAN.md": "# Merge Plan\n\nPending integration.\n",
        "GRAVITY_SUMMARY.md": "# Gravity Summary\n\nPending graph analysis.\n",
        "DISPATCH_RECOMMENDATIONS.md": "# Dispatch Recommendations\n\nPending slice planning.\n",
        "DIFF.patch": "",
    }
    for name, payload in text_files.items():
        path = target / name
        if not path.exists():
            write_text(path, payload)
            created.append(path.as_posix())

    return {
        "worker": worker,
        "bundle_dir": target.as_posix(),
        "created": sorted(created),
    }


def _read_json_or_default(path: Path, default_payload: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default_payload)
    payload = read_json(path)
    if not isinstance(payload, dict):
        return dict(default_payload)
    return payload


def _safe_changes(files_changed: dict[str, Any]) -> list[dict[str, str]]:
    changes_raw = files_changed.get("changes", [])
    if not isinstance(changes_raw, list):
        return []
    changes: list[dict[str, str]] = []
    for item in changes_raw:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).replace("\\", "/").strip()
        if not path:
            continue
        changes.append(
            {
                "path": path,
                "change_type": str(item.get("change_type", "modified")).strip().lower() or "modified",
                "reason": str(item.get("reason", "")).strip(),
            }
        )
    return sorted(changes, key=lambda row: row["path"])


def _existing_or_generated(path: Path, generated: str) -> str:
    if not path.exists():
        return generated
    current = path.read_text(encoding="utf-8").strip()
    if not current:
        return generated
    if current.lower().endswith("pending") or "status: pending" in current.lower():
        return generated
    return current + "\n"


def _build_summary_md(run_id: str, worker: str, changes: list[dict[str, str]], status: str) -> str:
    created = [item["path"] for item in changes if item["change_type"] in {"added", "created"}]
    modified = [item["path"] for item in changes if item["change_type"] in {"modified", "changed", "updated"}]
    deleted = [item["path"] for item in changes if item["change_type"] in {"deleted", "removed"}]

    lines = [
        f"# {worker} Summary",
        "",
        "## Scope",
        f"- Run ID: `{run_id}`",
        f"- Worker: `{worker}`",
        f"- Status: `{status}`",
        "",
        "## What Changed",
    ]
    if not changes:
        lines.append("- no changes declared")
    else:
        lines.append(f"- total changes: {len(changes)}")
        if created:
            lines.append(f"- created: {len(created)}")
        if modified:
            lines.append(f"- modified: {len(modified)}")
        if deleted:
            lines.append(f"- deletion requests: {len(deleted)}")

    lines.extend(["", "## Validation", "- bundle auto-closeout applied", ""])
    return "\n".join(lines)


def _build_suggestions_md(worker: str, changes: list[dict[str, str]]) -> str:
    lines = [f"# {worker} Suggestions", ""]
    if not changes:
        lines.append("- no follow-up required")
    else:
        lines.append("- run targeted tests for touched paths")
        lines.append("- keep scope lock aligned with future edits")
    lines.append("")
    return "\n".join(lines)


def _build_codex_output(run_id: str, worker: str, changes: list[dict[str, str]], status_payload: dict[str, Any]) -> str:
    created = [item["path"] for item in changes if item["change_type"] in {"added", "created"}]
    modified = [item["path"] for item in changes if item["change_type"] in {"modified", "changed", "updated"}]
    deleted = [item["path"] for item in changes if item["change_type"] in {"deleted", "removed"}]
    blockers = status_payload.get("errors", []) if isinstance(status_payload.get("errors", []), list) else []
    lines = [
        f"# CODEX_OUTPUT_{worker}_{run_id}",
        "",
        "## WHAT CHANGED",
        f"- total changes declared: {len(changes)}",
        "",
        "## FILES CREATED",
    ]
    if created:
        lines.extend([f"- {item}" for item in created])
    else:
        lines.append("- none")

    lines.extend(["", "## FILES MODIFIED"])
    if modified:
        lines.extend([f"- {item}" for item in modified])
    else:
        lines.append("- none")

    lines.extend(["", "## DELETION_REQUESTS"])
    if deleted:
        lines.extend([f"- {item} — request only" for item in deleted])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## COMMAND LOGS",
            "- autogenerated by factory auto-closeout",
            "",
            "## DIFF / PATCH",
            "- see DIFF.patch",
            "",
            "## FINAL SUMMARY",
            f"- worker status: {status_payload.get('status', 'PENDING')}",
            f"- required checks: {len(status_payload.get('required_checks', [])) if isinstance(status_payload.get('required_checks', []), list) else 0}",
            f"- blockers: {len(blockers)}",
        ]
    )
    if blockers:
        lines.extend([f"- blocker: {item}" for item in blockers])
    lines.append("")
    return "\n".join(lines)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _read_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = read_json(path)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _fallback_evolutionary_report(
    *,
    run_id: str,
    worker: str,
    root: Path,
    changes: list[dict[str, str]],
    reason: str,
) -> dict[str, Any]:
    loc_delta = len(changes)
    path_counts: dict[str, int] = {}
    ext_counts: dict[str, int] = {}
    dir_counts: dict[str, int] = {}
    for item in changes:
        path = str(item.get("path", "")).replace("\\", "/")
        if not path:
            continue
        path_counts[path] = path_counts.get(path, 0) + 1
        ext = Path(path).suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        parent = str(Path(path).parent).replace("\\", "/")
        dir_counts[parent] = dir_counts.get(parent, 0) + 1

    unique_paths = len(path_counts)
    unique_dirs = len(dir_counts)
    behavioral_delta = float(unique_dirs + max(0, unique_paths // 2))
    structural_diversity = _clamp01((len(ext_counts) + unique_dirs) / max(1.0, float(loc_delta) * 2.0))
    vdi = _clamp01((behavioral_delta * structural_diversity) / max(1.0, float(loc_delta)) * 0.85)
    duplicate_rows = max(0, loc_delta - unique_paths)
    duplication_ratio = duplicate_rows / max(1.0, float(loc_delta))
    concentration = max(path_counts.values()) / max(1.0, float(loc_delta)) if path_counts else 1.0
    low_entropy_flag = len(ext_counts) <= 1 and loc_delta >= 6
    blinded_flag = behavioral_delta <= 1.0 and loc_delta >= 4
    dup_penalty = duplication_ratio * concentration
    entropy_penalty = 0.75 if low_entropy_flag else 0.0
    blind_penalty = 0.9 if blinded_flag else 0.0
    sanction_score = (1.0 - vdi) + dup_penalty + entropy_penalty + blind_penalty
    sanction_level = "OK" if sanction_score < 0.6 else ("WARN" if sanction_score < 1.2 else "SEVERE")

    report = {
        "run_id": run_id,
        "worker_id": worker,
        "computed_at_utc": iso_utc(),
        "bundle_dir": root.as_posix(),
        "base_ref": "HEAD",
        "loc_delta": int(loc_delta),
        "loc_removed": 0,
        "changed_files_count": int(unique_paths),
        "added_files_count": 0,
        "behavioral_delta": behavioral_delta,
        "behavioral_density": behavioral_delta / max(1.0, float(loc_delta)),
        "structural_diversity": structural_diversity,
        "duplication_ratio_new": duplication_ratio,
        "file_concentration_ratio": concentration,
        "gzip_ratio_min": 1.0,
        "ttr_min": 1.0,
        "flags": [reason],
        "vdi": vdi,
        "sanction_score": sanction_score,
        "sanction_level": sanction_level,
        "duplicate_clusters": [],
        "blinded_suspects": [{"reason": "heuristic_trigger", "details": {}}] if blinded_flag else [],
        "top_offenders": [{"path": path, "score_proxy": float(count)} for path, count in sorted(path_counts.items(), key=lambda row: row[1], reverse=True)[:25]],
        "per_file": [
            {
                "path": path,
                "loc": count,
                "chars": count * 40,
                "gzip_ratio": 1.0,
                "ttr": 1.0,
            }
            for path, count in sorted(path_counts.items())
        ],
        "policy_used": {
            "defaults": {
                "max_file_chars": 120000,
                "max_file_loc": 2000,
                "k_tokens": 25,
                "winnow_window": 6,
                "dup_ratio_new_warn": 0.08,
                "dup_ratio_new_severe": 0.15,
                "min_gzip_ratio": 0.18,
                "min_ttr": 0.12,
                "scaling_constant_K": 1200.0,
                "penalties": {"entropy_severe": 0.75, "blind_severe": 0.9, "caps_severe": 1.1},
            }
        },
    }
    score = {
        "run_id": run_id,
        "worker_id": worker,
        "computed_at_utc": report["computed_at_utc"],
        "sanction_score": sanction_score,
        "sanction_level": sanction_level,
        "vdi": vdi,
        "loc_delta": int(loc_delta),
        "notes": [reason],
    }
    return {"report": report, "score": score}


def _write_evolutionary_fallback_artifacts(
    *,
    run_id: str,
    worker: str,
    root: Path,
    changes: list[dict[str, str]],
    reason: str,
) -> dict[str, Any]:
    payload = _fallback_evolutionary_report(run_id=run_id, worker=worker, root=root, changes=changes, reason=reason)
    report_path = root / "SELF_EVAL_REPORT.json"
    score_path = root / "SANCTION_SCORE.json"
    correction_log_path = root / "SELF_CORRECTION_LOG.jsonl"
    write_json(report_path, payload["report"])
    write_json(score_path, payload["score"])
    _append_jsonl(
        correction_log_path,
        {
            "run_id": run_id,
            "worker_id": worker,
            "computed_at_utc": payload["report"]["computed_at_utc"],
            "sanction_score": payload["score"]["sanction_score"],
            "sanction_level": payload["score"]["sanction_level"],
            "vdi": payload["score"]["vdi"],
            "loc_delta": payload["score"]["loc_delta"],
            "flags": [reason],
        },
    )
    return {
        "score": _to_float(payload["score"].get("sanction_score"), 1.0),
        "level": str(payload["score"].get("sanction_level", "WARN")),
    }


def _artifacts_present(root: Path, rel_paths: tuple[str, ...]) -> bool:
    return all((root / rel).exists() for rel in rel_paths)


def _read_latest_score(root: Path) -> float | None:
    score_payload = _read_json_dict(root / "SANCTION_SCORE.json")
    if "sanction_score" in score_payload:
        return _to_float(score_payload.get("sanction_score"), 1.0)
    return None


def _run_evolutionary_autocloseout(run_id: str, worker: str, root: Path, changes: list[dict[str, str]]) -> dict[str, Any]:
    log_path = root / "LOGS" / "evolutionary_autocloseout.log.jsonl"
    previous_score = _read_latest_score(root)
    best_score = previous_score
    attempts: list[dict[str, Any]] = []
    command = ""
    best_level = "WARN"

    for attempt in range(1, EVOLUTIONARY_MAX_ATTEMPTS + 1):
        engine_used = False
        rc = 0
        stdout_tail = ""
        stderr_tail = ""
        if EVOLUTIONARY_ENGINE.exists():
            engine_used = True
            cmd = [
                sys.executable or "python",
                EVOLUTIONARY_ENGINE.as_posix(),
                "--repo",
                REPO_ROOT.as_posix(),
                "--run-id",
                run_id,
                "--worker-id",
                worker,
                "--bundle-dir",
                root.as_posix(),
            ]
            if EVOLUTIONARY_POLICY.exists():
                cmd.extend(["--policy", EVOLUTIONARY_POLICY.as_posix()])
            command = " ".join(cmd)
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
            )
            rc = int(proc.returncode)
            stdout_tail = (proc.stdout or "").strip()[-300:]
            stderr_tail = (proc.stderr or "").strip()[-300:]

        fallback_reason = "ENGINE_NOT_FOUND"
        if engine_used and rc != 0:
            fallback_reason = "ENGINE_RUNTIME_ERROR"
        if engine_used and rc == 0 and not _artifacts_present(root, EVOLUTIONARY_REQUIRED_FILES):
            fallback_reason = "ENGINE_INCOMPLETE_OUTPUT"

        if not engine_used or rc != 0 or not _artifacts_present(root, EVOLUTIONARY_REQUIRED_FILES):
            fallback = _write_evolutionary_fallback_artifacts(
                run_id=run_id,
                worker=worker,
                root=root,
                changes=changes,
                reason=fallback_reason,
            )
            score = _to_float(fallback.get("score"), 1.0)
            level = str(fallback.get("level", "WARN"))
            source = "fallback"
        else:
            score_payload = _read_json_dict(root / "SANCTION_SCORE.json")
            score = _to_float(score_payload.get("sanction_score"), 1.0)
            level = str(score_payload.get("sanction_level", "WARN")).upper()
            source = "engine"

        improved = True if best_score is None else score < best_score
        if improved:
            best_score = score
            best_level = level
        attempt_row = {
            "attempt": attempt,
            "ts_utc": iso_utc(),
            "run_id": run_id,
            "worker_id": worker,
            "source": source,
            "engine_used": engine_used,
            "rc": rc,
            "sanction_score": score,
            "sanction_level": level,
            "improved": improved,
            "previous_best": best_score if improved else (best_score if best_score is not None else score),
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
        }
        attempts.append(attempt_row)
        _append_jsonl(log_path, attempt_row)
        if improved and _artifacts_present(root, EVOLUTIONARY_REQUIRED_FILES):
            break
        if attempt < EVOLUTIONARY_MAX_ATTEMPTS:
            time.sleep(EVOLUTIONARY_RETRY_SECONDS)

    artifacts_ok = _artifacts_present(root, EVOLUTIONARY_REQUIRED_FILES)
    final_score = _read_latest_score(root)
    if final_score is None:
        fallback = _write_evolutionary_fallback_artifacts(
            run_id=run_id,
            worker=worker,
            root=root,
            changes=changes,
            reason="FINAL_FALLBACK",
        )
        final_score = _to_float(fallback.get("score"), 1.0)
        best_level = str(fallback.get("level", "WARN"))
        artifacts_ok = _artifacts_present(root, EVOLUTIONARY_REQUIRED_FILES)

    trend_down = True
    if previous_score is not None and final_score is not None:
        trend_down = final_score < previous_score

    return {
        "status": "PASS" if artifacts_ok else "WARN",
        "artifacts_present": artifacts_ok,
        "attempts": len(attempts),
        "max_attempts": EVOLUTIONARY_MAX_ATTEMPTS,
        "trend_down": trend_down,
        "previous_score": previous_score,
        "final_score": final_score,
        "sanction_level": best_level,
        "log_path": log_path.as_posix(),
        "command": command,
        "attempt_rows": attempts,
    }


def _resolve_worktree_path(worker: str) -> Path:
    return REPO_ROOT / "tools" / "codex" / "worktrees" / worker


def autocloseout_worker_bundle(run_id: str, worker: str) -> dict[str, Any]:
    worker = canonical_worker_id(worker)
    scaffold_worker_bundle(run_id, worker)
    root = bundle_dir(run_id, worker)
    logs_dir = root / "LOGS"
    ensure_dir(logs_dir)

    status_path = root / "STATUS.json"
    files_changed_path = root / "FILES_CHANGED.json"
    handoff_path = root / "HANDOFF_NOTE.json"
    scope_lock_path = root / "SCOPE_LOCK.json"
    summary_path = root / "SUMMARY.md"
    suggestions_path = root / "SUGGESTIONS.md"
    codex_output_path = root / "CODEX_OUTPUT.txt"
    log_index_path = logs_dir / "INDEX.json"
    closeout_log_path = logs_dir / "autocloseout.log.txt"

    status_payload = _read_json_or_default(status_path, _default_worker_status(run_id, worker))
    files_changed_payload = _read_json_or_default(files_changed_path, _default_files_changed(run_id, worker))
    _ = _read_json_or_default(handoff_path, _default_handoff(run_id, worker))
    _ = _read_json_or_default(scope_lock_path, _default_scope_lock(run_id, worker))
    log_index_payload = _read_json_or_default(log_index_path, _default_log_index(run_id, worker))

    changes = _safe_changes(files_changed_payload)
    evolutionary = _run_evolutionary_autocloseout(run_id, worker, root, changes)
    if not changes:
        files_changed_payload["noop"] = True
        files_changed_payload["noop_reason"] = str(files_changed_payload.get("noop_reason") or "no worker changes declared")
        files_changed_payload["noop_ack"] = str(files_changed_payload.get("noop_ack") or worker)
    else:
        files_changed_payload["noop"] = False
        files_changed_payload["noop_reason"] = ""
        files_changed_payload["noop_ack"] = ""
    files_changed_payload["owner"] = worker
    files_changed_payload["run_id"] = run_id
    files_changed_payload["schema_version"] = int(files_changed_payload.get("schema_version", 1) or 1)
    write_json(files_changed_path, files_changed_payload)

    now = iso_utc()
    status_payload["schema_version"] = int(status_payload.get("schema_version", 1) or 1)
    status_payload["contract_version"] = int(status_payload.get("contract_version", 2) or 2)
    status_payload["run_id"] = run_id
    status_payload["worker_id"] = worker
    status_payload["started_at"] = str(status_payload.get("started_at") or now)
    status_payload["ended_at"] = now
    raw_status = str(status_payload.get("status", "PENDING")).upper()
    if raw_status == "PENDING":
        raw_status = "PASS"
    status_payload["status"] = raw_status if raw_status in {"PASS", "BLOCKED", "WARN", "FAIL"} else "PASS"

    required_checks = status_payload.get("required_checks", [])
    if not isinstance(required_checks, list):
        required_checks = []
    required_checks.extend(
        [
            {"name": "scope_lock_present", "status": "PASS"},
            {"name": "handoff_present", "status": "PASS"},
            {"name": "auto_closeout", "status": "PASS"},
            {"name": "session_hygiene_declared", "status": "PASS"},
            {
                "name": "evolutionary_autocloseout_artifacts",
                "status": "PASS" if evolutionary.get("artifacts_present") else "WARN",
            },
        ]
    )
    dedup_required: dict[str, dict[str, Any]] = {}
    for item in required_checks:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            if name:
                dedup_required[name] = {"name": name, "status": str(item.get("status", "PASS")).upper()}
    status_payload["required_checks"] = [dedup_required[key] for key in sorted(dedup_required)]
    optional_checks = status_payload.get("optional_checks", [])
    if not isinstance(optional_checks, list):
        optional_checks = []
    status_payload["optional_checks"] = optional_checks
    if not isinstance(status_payload.get("errors", []), list):
        status_payload["errors"] = []
    if not isinstance(status_payload.get("warnings", []), list):
        status_payload["warnings"] = []
    if not evolutionary.get("trend_down", True):
        status_payload["warnings"].append(
            {
                "kind": "evolutionary_sanction",
                "detail": "SanctionScore did not improve after retries; auto-sanction logged",
                "log_path": str(evolutionary.get("log_path", "")),
                "final_score": evolutionary.get("final_score"),
            }
        )
    level = str(evolutionary.get("sanction_level", "WARN")).upper()
    if level in {"WARN", "SEVERE"}:
        status_payload["warnings"].append(
            {
                "kind": "evolutionary_sanction",
                "detail": f"sanction level {level}",
                "final_score": evolutionary.get("final_score"),
            }
        )
    status_payload["noop"] = bool(files_changed_payload.get("noop", False))
    status_payload["noop_reason"] = str(files_changed_payload.get("noop_reason", ""))
    status_payload["noop_ack"] = str(files_changed_payload.get("noop_ack", ""))
    post_run_required = list(POST_RUN_REQUIRED_FILES.get(worker, ()))
    status_payload["artifacts"] = sorted(set([*list(WORKER_REQUIRED_FILES), *post_run_required]))
    write_json(status_path, status_payload)

    summary_generated = _build_summary_md(run_id, worker, changes, str(status_payload.get("status", "PASS")))
    write_text(summary_path, _existing_or_generated(summary_path, summary_generated))
    suggestions_generated = _build_suggestions_md(worker, changes)
    write_text(suggestions_path, _existing_or_generated(suggestions_path, suggestions_generated))

    closeout_log = (
        f"run_id={run_id}\n"
        f"worker={worker}\n"
        f"status={status_payload.get('status', 'PASS')}\n"
        f"changes={len(changes)}\n"
        f"evolutionary_status={evolutionary.get('status', 'WARN')}\n"
        f"evolutionary_attempts={evolutionary.get('attempts', 0)}\n"
        f"evolutionary_score={evolutionary.get('final_score')}\n"
    )
    write_text(closeout_log_path, closeout_log)
    logs = log_index_payload.get("logs", [])
    if not isinstance(logs, list):
        logs = []
    logs.append({"name": "autocloseout", "path": "LOGS/autocloseout.log.txt", "rc": 0})
    logs.append({"name": "evolutionary_autocloseout", "path": "LOGS/evolutionary_autocloseout.log.jsonl", "rc": 0})
    dedup_logs: dict[tuple[str, str], dict[str, Any]] = {}
    for item in logs:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        path = str(item.get("path", "")).strip()
        if not name or not path:
            continue
        dedup_logs[(name, path)] = {"name": name, "path": path, "rc": int(item.get("rc", 0) or 0)}
    log_index_payload = {
        "schema_version": int(log_index_payload.get("schema_version", 1) or 1),
        "run_id": run_id,
        "owner": worker,
        "logs": [dedup_logs[key] for key in sorted(dedup_logs)],
    }
    write_json(log_index_path, log_index_payload)

    codex_output_text = _build_codex_output(run_id, worker, changes, status_payload)
    write_text(codex_output_path, codex_output_text)
    worker_worktree = _resolve_worktree_path(worker)
    if worker_worktree.exists() and worker_worktree.is_dir():
        external_output = worker_worktree / f"CODEX_OUTPUT_{worker}_{run_id}.txt"
        write_text(external_output, codex_output_text)

    return {
        "run_id": run_id,
        "worker": worker,
        "status": str(status_payload.get("status", "PASS")),
        "changes": len(changes),
        "evolutionary": {
            "status": evolutionary.get("status", "WARN"),
            "attempts": evolutionary.get("attempts", 0),
            "trend_down": evolutionary.get("trend_down", False),
            "final_score": evolutionary.get("final_score"),
            "sanction_level": evolutionary.get("sanction_level", "WARN"),
        },
        "bundle_dir": root.as_posix(),
    }


def autocloseout_run(run_id: str, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = canonicalize_workers(workers, include_post_run=True)
    results = [autocloseout_worker_bundle(run_id, worker) for worker in chosen if worker != INTEGRATOR]
    return {
        "run_id": run_id,
        "status": "PASS",
        "workers": results,
    }


def scaffold_all_bundles(run_id: str, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = canonicalize_workers(workers, include_post_run=True)
    result = {
        "run_id": run_id,
        "workers": [],
    }
    for worker in chosen:
        result["workers"].append(scaffold_worker_bundle(run_id, worker))
    result["integrator"] = scaffold_integrator_bundle(run_id)
    return result


def validate_bundle_shape(run_id: str, worker: str) -> list[str]:
    worker = canonical_worker_id(worker)
    target = bundle_dir(run_id, worker)
    cfg = load_factory_config(strict=False)
    worker_files = cfg.get("workers", {}).get("required_worker_files", list(WORKER_REQUIRED_FILES))
    integrator_files = cfg.get("workers", {}).get("required_integrator_files", list(INTEGRATOR_REQUIRED_FILES))
    post_run_files_cfg = (
        cfg.get("workers", {}).get("required_post_run_files", {})
        if isinstance(cfg.get("workers", {}).get("required_post_run_files", {}), dict)
        else {}
    )
    post_run_files = post_run_files_cfg.get(worker, POST_RUN_REQUIRED_FILES.get(worker, ()))
    if worker != INTEGRATOR:
        required = tuple(
            sorted(
                set(
                    [
                        *list(worker_files),
                        *list(EVOLUTIONARY_REQUIRED_FILES),
                        *([str(item) for item in post_run_files] if worker in CANONICAL_POST_RUN_WORKERS else []),
                    ]
                )
            )
        )
    else:
        required = tuple(integrator_files)
    errors: list[str] = []
    if not target.exists():
        return [f"missing bundle directory: {target.as_posix()}"]
    for name in required:
        path = target / name
        if not path.exists():
            errors.append(f"missing required artifact: {path.as_posix()}")
    return errors


def validate_bundle_schemas(run_id: str, worker: str) -> list[str]:
    worker = canonical_worker_id(worker)
    target = bundle_dir(run_id, worker)
    errors: list[str] = []

    status_path = target / "STATUS.json"
    if status_path.exists():
        status_payload = read_json(status_path)
        schema_name = "integrator_status" if worker == INTEGRATOR else "worker_bundle_status"
        status_errors = validate_payload(schema_name, status_payload)
        errors.extend([f"STATUS.json: {item}" for item in status_errors])

    files_changed_path = target / "FILES_CHANGED.json"
    if files_changed_path.exists():
        files_changed_payload = read_json(files_changed_path)
        errors.extend([f"FILES_CHANGED.json: {item}" for item in validate_payload("files_changed", files_changed_payload)])

    if worker != INTEGRATOR:
        scope_lock_path = target / "SCOPE_LOCK.json"
        handoff_path = target / "HANDOFF_NOTE.json"
        if scope_lock_path.exists():
            errors.extend([f"SCOPE_LOCK.json: {item}" for item in validate_payload("scope_lock", read_json(scope_lock_path))])
        if handoff_path.exists():
            errors.extend([f"HANDOFF_NOTE.json: {item}" for item in validate_payload("handoff_note", read_json(handoff_path))])
        for filename, schema_name in POST_RUN_SCHEMA_FILES.get(worker, ()):
            payload_path = target / filename
            if payload_path.exists():
                schema_errors = validate_payload(schema_name, read_json(payload_path))
                errors.extend([f"{filename}: {item}" for item in schema_errors])
    else:
        for filename, schema_name in INTEGRATOR_GRAPH_SCHEMA_FILES:
            payload_path = target / filename
            if payload_path.exists():
                schema_errors = validate_payload(schema_name, read_json(payload_path))
                errors.extend([f"{filename}: {item}" for item in schema_errors])

    log_index_path = target / "LOGS" / "INDEX.json"
    if log_index_path.exists():
        errors.extend([f"LOGS/INDEX.json: {item}" for item in validate_payload("log_index", read_json(log_index_path))])

    return errors


def validate_bundle(run_id: str, worker: str) -> dict[str, Any]:
    worker = canonical_worker_id(worker)
    shape_errors = validate_bundle_shape(run_id, worker)
    schema_errors = [] if shape_errors else validate_bundle_schemas(run_id, worker)
    all_errors = [*shape_errors, *schema_errors]
    return {
        "run_id": run_id,
        "worker": worker,
        "status": "PASS" if not all_errors else "BLOCKED",
        "errors": all_errors,
    }


def validate_run(run_id: str, workers: list[str] | None = None, *, auto_closeout: bool = False) -> dict[str, Any]:
    chosen = canonicalize_workers(workers, include_post_run=True)
    closeout_payload: dict[str, Any] | None = None
    if auto_closeout:
        closeout_payload = autocloseout_run(run_id, workers=chosen)
    results = [validate_bundle(run_id, worker) for worker in chosen]
    results.append(validate_bundle(run_id, INTEGRATOR))
    blocked = [entry for entry in results if entry["status"] != "PASS"]
    payload = {
        "run_id": run_id,
        "status": "PASS" if not blocked else "BLOCKED",
        "results": results,
        "blocked": len(blocked),
    }
    if closeout_payload is not None:
        payload["auto_closeout"] = closeout_payload
    return payload
