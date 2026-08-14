from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Optional

from .capability_contracts import (
    FORMER_PLACEHOLDERS,
    build_capability_specs,
    harden_multi_tenant_guard,
    legacy_placeholder_ledger,
    observe_runtime_bindings,
    summarize_capabilities,
)
from .features50 import FEATURE_SPECS
from .foundation_integration import apply_operational_foundations
from .runner import run_operational_atlas as _run_base_operational_atlas


FOUNDATION_CAPABILITY_BINDINGS = {
    "snapshot_diff_engine": "snapshotDiffEngine",
    "operational_timeline": "operationalTimeline",
    "orphan_detector": "orphans",
    "staleness_monitor": "stalenessMonitor",
    "audit_completeness_matrix": "auditCompleteness",
    "data_lineage_graph": "dataLineageGraph",
    "runtime_evidence_links": "runtimeEvidenceLinks",
    "historical_trend_mini_atlas": "historicalTrendMiniAtlas",
}

FOUNDATION_BLOCKERS_BY_CAPABILITY = {
    "snapshot_diff_engine": {"snapshot_baseline_missing"},
    "historical_trend_mini_atlas": {"historical_trend_insufficient_history"},
    "staleness_monitor": {"freshness_policy_or_evidence_missing"},
    "audit_completeness_matrix": {"audit_catalog_or_events_incomplete"},
    "data_lineage_graph": {"lineage"},
    "orphan_detector": {"lineage"},
    "runtime_evidence_links": {"runtime_evidence_links_incomplete"},
}


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["status"]
        rows = [{"status": "EMPTY"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _cell(row.get(key)) for key in fields})


def _write_hardening_summary(
    path: Path,
    summary: dict[str, Any],
    legacy_rows: list[dict[str, Any]],
    foundation_summary: dict[str, Any],
) -> None:
    lines = [
        "# Code Atlas Operational Hardening Summary",
        "",
        f"Status: `{summary['status']}`",
        f"Capabilities: `{summary['featureCount']}`",
        f"Observed primary runtime outputs: `{summary['runtimeOutputObservedCount']}`",
        f"Hard-blocked capabilities: `{summary['hardBlockedCapabilityCount']}`",
        f"Foundations: `{foundation_summary['status']}`",
        f"Foundation blockers: `{len(foundation_summary.get('blockers', []))}`",
        "Production certified by this hardening: `false`",
        "",
        "## Governing rule",
        "",
        "`detector existence != contract maturity != runtime evidence != certification`",
        "",
        "## Former placeholder reconciliation",
        "",
        "| Capability | State | Runtime output | Maturity | Certifiable |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in legacy_rows:
        lines.append(
            "| {feature} | {state} | {observed} | {maturity} | false |".format(
                feature=row["feature"],
                state=row["detectorOrViewerState"],
                observed=str(row["runtimeOutputObserved"]).lower(),
                maturity=row["maturity"],
            )
        )
    lines.extend([
        "",
        "## Foundation blockers",
        "",
    ])
    blockers = foundation_summary.get("blockers") or []
    lines.extend(f"- `{item}`" for item in blockers)
    if not blockers:
        lines.append("- None at source-foundation level. This still does not certify production.")
    lines.extend([
        "",
        "## Non-claims",
        "",
        "- This hardening does not certify production.",
        "- Scope-field presence does not certify tenant isolation.",
        "- A viewer text filter is not a typed query engine.",
        "- A generated detector row is not automatically contract-backed evidence.",
        "- A contract-backed foundation output may still be blocked by missing runtime evidence or policy.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _foundation_blockers_for(capability_id: str, foundation_summary: dict[str, Any]) -> list[str]:
    blockers = [str(item) for item in foundation_summary.get("blockers") or []]
    selectors = FOUNDATION_BLOCKERS_BY_CAPABILITY.get(capability_id, set())
    matched: list[str] = []
    for blocker in blockers:
        if blocker in selectors or ("lineage" in selectors and blocker.startswith("lineage:")):
            matched.append(f"foundation:{blocker}")
    return matched


def _reconcile_foundation_capabilities(
    specs: list[dict[str, Any]],
    payload: dict[str, Any],
    foundation_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    reconciled: list[dict[str, Any]] = []
    for spec in specs:
        row = dict(spec)
        capability_id = str(row.get("capabilityId") or "")
        binding = FOUNDATION_CAPABILITY_BINDINGS.get(capability_id)
        if not binding:
            reconciled.append(row)
            continue

        observed = binding in payload and payload.get(binding) is not None
        row["runtimeBinding"] = binding
        row["runtimeOutputObserved"] = observed
        row["runtimeObservation"] = f"payload:{binding}" if observed else f"missing-payload:{binding}"
        if observed:
            row["implementationState"] = "foundation_v1_present"
            if row.get("maturity") in {"HEURISTIC", "SOURCE_BACKED"}:
                row["maturity"] = "CONTRACT_BACKED"
        else:
            row["implementationState"] = "foundation_v1_output_not_observed"

        hard_blockers = list(row.get("hardBlockers") or [])
        hard_blockers.extend(_foundation_blockers_for(capability_id, foundation_summary))
        if not observed:
            hard_blockers.append("foundation_runtime_output_not_observed")
        row["hardBlockers"] = list(dict.fromkeys(hard_blockers))
        row["certifiable"] = False
        row["productionCertified"] = False
        reconciled.append(row)
    return reconciled


def run_operational_atlas(
    repo_root: str,
    output_dir: str,
    result_root: Optional[str] = None,
) -> dict[str, Any]:
    """Run the existing collector, foundations, then no-fake-green hardening.

    The base runner remains the data collector for backward compatibility.
    Foundations replace selected heuristic outputs with deterministic,
    contract-backed and fail-closed evidence/temporal/lineage outputs. The
    capability layer then reconciles runtime observation and maturity without
    granting certification.
    """

    manifest = dict(_run_base_operational_atlas(repo_root, output_dir, result_root))
    out = Path(output_dir).resolve()
    payload_path = out / "operational_evidence_atlas.json"
    manifest_path = out / "ATLAS_MANIFEST_PLUS.json"
    payload = _read_json(payload_path, {})
    if not isinstance(payload, dict):
        payload = {}

    foundation_result = apply_operational_foundations(
        payload,
        manifest,
        result_root=result_root,
    )
    payload = foundation_result["payload"]
    foundation_summary = dict(foundation_result["summary"])
    for name, value in foundation_result["outputs"].items():
        _write_json(out / name, value)

    # Hard rule: a scope detector is not a leakage certification.
    payload["multiTenantLeakageGuard"] = harden_multi_tenant_guard(
        payload.get("multiTenantLeakageGuard")
    )

    capability_specs = build_capability_specs(FEATURE_SPECS)
    observed_specs = observe_runtime_bindings(
        capability_specs,
        payload,
        (path.name for path in out.iterdir() if path.is_file()),
    )
    observed_specs = _reconcile_foundation_capabilities(
        observed_specs,
        payload,
        foundation_summary,
    )
    summary = summarize_capabilities(observed_specs)
    legacy_rows = legacy_placeholder_ledger(observed_specs)

    payload["capabilityHardeningLedger"] = observed_specs
    payload["capabilityMaturitySummary"] = summary
    payload["placeholderLedger"] = legacy_rows
    payload["foundationHardeningSummary"] = foundation_summary

    manifest["capabilityRegistryVersion"] = "2.0.0"
    manifest["capabilityHardeningStatus"] = summary["status"]
    manifest["capabilityMaturitySummary"] = summary
    manifest["foundationHardeningStatus"] = foundation_summary["status"]
    manifest["foundationHardeningSummary"] = foundation_summary
    manifest["legacyRegistryPlaceholderCount"] = len(FORMER_PLACEHOLDERS)
    manifest["registryDriftDetected"] = any(
        "placeholder" in str(row.get("legacyRegistryStatus", ""))
        for row in observed_specs
    )
    manifest["registryDriftReason"] = (
        "Legacy feature status fields are historical compatibility metadata; "
        "runtime detector presence, foundation maturity and certification are tracked separately."
    )
    manifest["productionCertified"] = False
    manifest["hardeningCertifiableCount"] = 0
    manifest["hardeningRule"] = (
        "detector existence != contract maturity != runtime evidence != certification"
    )

    payload["manifest"] = manifest

    _write_json(out / "CAPABILITY_HARDENING_LEDGER.json", observed_specs)
    _write_csv(out / "CAPABILITY_HARDENING_LEDGER.csv", observed_specs)
    _write_json(out / "CAPABILITY_MATURITY_SUMMARY.json", summary)
    _write_json(out / "placeholder_ledger.json", legacy_rows)
    _write_csv(out / "placeholder_ledger.csv", legacy_rows)
    _write_json(payload_path, payload)
    _write_json(manifest_path, manifest)
    _write_hardening_summary(out / "HARDENING_SUMMARY.md", summary, legacy_rows, foundation_summary)

    smoke_path = out / "SMOKE.json"
    smoke = _read_json(smoke_path, {})
    if isinstance(smoke, dict):
        required = smoke.setdefault("requiredFiles", [])
        for name in (
            "CAPABILITY_HARDENING_LEDGER.json",
            "CAPABILITY_MATURITY_SUMMARY.json",
            "HARDENING_SUMMARY.md",
            "FOUNDATION_HARDENING_SUMMARY.json",
            "EVIDENCE_RECORDS.json",
            "SEMANTIC_SNAPSHOT.json",
            "SNAPSHOT_DIFF_ENGINE.json",
            "HISTORICAL_TREND_MINI_ATLAS.json",
            "DATA_LINEAGE_GRAPH.json",
        ):
            if name not in required:
                required.append(name)
        smoke["hardeningStatus"] = "PASS_SOURCE_HARDENING_OUTPUTS_GENERATED"
        smoke["foundationStatus"] = foundation_summary["status"]
        smoke["productionCertified"] = False
        _write_json(smoke_path, smoke)

    return manifest


__all__ = ["run_operational_atlas"]
