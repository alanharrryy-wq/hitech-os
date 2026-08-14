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
        f"Foundation status: `{foundation_summary['status']}`",
        f"Capabilities: `{summary['featureCount']}`",
        f"Observed primary runtime outputs: `{summary['runtimeOutputObservedCount']}`",
        f"Hard-blocked capabilities: `{summary['hardBlockedCapabilityCount']}`",
        "Production certified by this hardening: `false`",
        "",
        "## Governing rule",
        "",
        "`detector existence != contract maturity != certification`",
        "",
        "## Foundation blockers",
        "",
    ]
    blockers = foundation_summary.get("blockers") or []
    lines.extend([f"- `{item}`" for item in blockers] or ["- None reported by the source foundation layer."])
    lines.extend([
        "",
        "## Former placeholder reconciliation",
        "",
        "| Capability | State | Runtime output | Maturity | Certifiable |",
        "| --- | --- | --- | --- | --- |",
    ])
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
        "## Non-claims",
        "",
        "- This hardening does not certify production.",
        "- Scope-field presence does not certify tenant isolation.",
        "- A viewer text filter is not a typed query engine.",
        "- A generated detector row is not automatically contract-backed evidence.",
        "- Source snapshots and graph contracts do not prove runtime behavior.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run_operational_atlas(
    repo_root: str,
    output_dir: str,
    result_root: Optional[str] = None,
) -> dict[str, Any]:
    """Run the existing collector, then apply governed no-fake-green hardening.

    The v3 runner remains the collector for backward compatibility. Foundations
    add evidence identity, semantic time/diff, explicit lineage and assurance
    contracts. No source-only result from this wrapper is production-certified.
    """

    manifest = dict(_run_base_operational_atlas(repo_root, output_dir, result_root))
    out = Path(output_dir).resolve()
    payload_path = out / "operational_evidence_atlas.json"
    manifest_path = out / "ATLAS_MANIFEST_PLUS.json"
    payload = _read_json(payload_path, {})
    if not isinstance(payload, dict):
        payload = {}

    foundation = apply_operational_foundations(
        payload,
        manifest,
        result_root=result_root,
    )
    payload = foundation["payload"]
    foundation_summary = dict(foundation["summary"])

    for filename, value in foundation["outputs"].items():
        _write_json(out / filename, value)

    capability_specs = build_capability_specs(FEATURE_SPECS)
    observed_specs = observe_runtime_bindings(
        capability_specs,
        payload,
        (path.name for path in out.iterdir() if path.is_file()),
    )
    summary = summarize_capabilities(observed_specs)
    legacy_rows = legacy_placeholder_ledger(observed_specs)

    payload["multiTenantLeakageGuard"] = harden_multi_tenant_guard(
        payload.get("multiTenantLeakageGuard")
    )

    payload["capabilityHardeningLedger"] = observed_specs
    payload["capabilityMaturitySummary"] = summary
    payload["placeholderLedger"] = legacy_rows
    payload["foundationHardeningSummary"] = foundation_summary

    manifest["capabilityRegistryVersion"] = "2.0.0"
    manifest["capabilityHardeningStatus"] = summary["status"]
    manifest["capabilityMaturitySummary"] = summary
    manifest["foundationHardeningVersion"] = foundation_summary["foundationVersion"]
    manifest["foundationHardeningStatus"] = foundation_summary["status"]
    manifest["foundationHardeningSummary"] = foundation_summary
    manifest["legacyRegistryPlaceholderCount"] = len(FORMER_PLACEHOLDERS)
    manifest["registryDriftDetected"] = any(
        "placeholder" in str(row.get("legacyRegistryStatus", ""))
        for row in observed_specs
    )
    manifest["registryDriftReason"] = (
        "Legacy feature status fields are historical compatibility metadata; "
        "runtime detector presence and contract maturity are tracked separately."
    )
    manifest["productionCertified"] = False
    manifest["hardeningCertifiableCount"] = 0
    manifest["hardeningRule"] = "detector existence != contract maturity != certification"

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
            "FOUNDATION_HARDENING_SUMMARY.json",
            "EVIDENCE_RECORDS.json",
            "SEMANTIC_SNAPSHOT.json",
            "SNAPSHOT_DIFF_ENGINE.json",
            "HISTORICAL_TREND_MINI_ATLAS.json",
            "DATA_LINEAGE_GRAPH.json",
            "HARDENING_SUMMARY.md",
        ):
            if name not in required:
                required.append(name)
        smoke["hardeningStatus"] = "PASS_SOURCE_HARDENING_OUTPUTS_GENERATED"
        smoke["foundationHardeningStatus"] = foundation_summary["status"]
        smoke["productionCertified"] = False
        _write_json(smoke_path, smoke)

    return manifest


__all__ = ["run_operational_atlas"]
