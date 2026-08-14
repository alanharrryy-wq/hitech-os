from __future__ import annotations

import json
from pathlib import Path

from code_atlas.operational import hardened_runner
from code_atlas.operational.capability_contracts import (
    FORMER_PLACEHOLDERS,
    build_capability_specs,
    observe_runtime_bindings,
    validate_capability_specs,
)
from code_atlas.operational.features50 import FEATURE_SPECS, FEATURE_REGISTRY_VERSION


def test_registry_preserves_50_legacy_entries_but_adds_hardening_contract() -> None:
    assert FEATURE_REGISTRY_VERSION == "2.0.0"
    assert len(FEATURE_SPECS) == 50
    assert sum(row["status"] == "implemented_v1" for row in FEATURE_SPECS) == 35
    assert sum(row["status"] == "placeholder_v1" for row in FEATURE_SPECS) == 14
    assert sum(row["status"] == "placeholder_blocked" for row in FEATURE_SPECS) == 1

    hardened = build_capability_specs(FEATURE_SPECS)
    result = validate_capability_specs(hardened)
    assert result["status"] == "PASS_CAPABILITY_CONTRACTS_VALID"
    assert result["formerPlaceholderCount"] == 15
    assert all(row["certifiable"] is False for row in hardened)
    assert all(row["productionCertified"] is False for row in hardened)
    assert all(row["doesNotProve"] for row in hardened)


def test_historical_trend_is_not_promoted_without_runtime_output() -> None:
    specs = build_capability_specs(FEATURE_SPECS)
    observed = observe_runtime_bindings(specs, payload={})
    trend = next(row for row in observed if row["capabilityId"] == "historical_trend_mini_atlas")
    assert trend["implementationState"] == "registry_only_no_runtime_output"
    assert trend["runtimeOutputObserved"] is False
    assert trend["certifiable"] is False


def test_multi_tenant_contract_requires_negative_isolation_tests() -> None:
    spec = next(
        row
        for row in build_capability_specs(FEATURE_SPECS)
        if row["capabilityId"] == "multi_tenant_leakage_guard"
    )
    assert {
        "cross_tenant_read",
        "cross_tenant_join",
        "cross_business_projection",
        "wrong_scope_runtime_evidence",
    }.issubset(set(spec["requiredNegativeTests"]))
    assert "negative_cross_tenant_tests_missing" in spec["hardBlockers"]
    assert spec["certifiable"] is False


def test_wrapper_blocks_scope_presence_from_becoming_leakage_green(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "out"
    out.mkdir()

    base_manifest = {
        "tool": "code_atlas_operational_v3",
        "status": "SOURCE_READY_NOT_PRODUCTION_CERTIFIED",
        "productionGate": "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED",
        "featureCount": 50,
        "detectorsConverted": 15,
        "placeholdersRemaining": 0,
    }
    base_payload = {
        "manifest": dict(base_manifest),
        "multiTenantLeakageGuard": [
            {
                "status": "PASS_SCOPE_AUTHORITY_FOUND",
                "rule": "certify only if real tenant/scope contract exists",
            }
        ],
        "snapshotDiffEngine": [{"status": "BASELINE"}],
        "surfaceRoleMatrix": [{"status": "PASS"}],
        "operationalTimeline": [{"status": "EMPTY"}],
        "clientRiskScore": [{"status": "PASS"}],
        "orphans": [{"status": "PASS_NO_ORPHANS_IN_SAMPLE"}],
        "stalenessMonitor": [{"status": "PASS_TIMESTAMPS_PRESENT_IN_SAMPLE"}],
        "auditCompleteness": [{"status": "PASS"}],
        "dataLineageGraph": [{"status": "EMPTY_NO_EDGES"}],
        "runtimeEvidenceLinks": [{"status": "BLOCKED_NO_RESULT_ZIPS"}],
        "clientSetupJourneyMap": [{"status": "PASS"}],
        "goldenPathComparator": [{"status": "SOURCE_READY_NOT_PRODUCTION_CERTIFIED"}],
    }

    def fake_base(repo_root: str, output_dir: str, result_root=None):
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "ATLAS_MANIFEST_PLUS.json").write_text(
            json.dumps(base_manifest), encoding="utf-8"
        )
        (destination / "operational_evidence_atlas.json").write_text(
            json.dumps(base_payload), encoding="utf-8"
        )
        (destination / "SMOKE.json").write_text(
            json.dumps({"status": "PASS", "requiredFiles": []}), encoding="utf-8"
        )
        for name in (
            "WHY_THIS_IS_RED.md",
            "HUMAN_OPERATOR_SUMMARY.md",
            "CONTINUATION_SUPREME.md",
            "CAN_PATCH_DECISION.md",
        ):
            (destination / name).write_text(name, encoding="utf-8")
        return dict(base_manifest)

    monkeypatch.setattr(hardened_runner, "_run_base_operational_atlas", fake_base)
    manifest = hardened_runner.run_operational_atlas(str(tmp_path), str(out), None)

    payload = json.loads((out / "operational_evidence_atlas.json").read_text(encoding="utf-8"))
    guard = payload["multiTenantLeakageGuard"][0]
    assert guard["scopeAuthorityObserved"] is True
    assert guard["status"] == "BLOCKED_NEGATIVE_ISOLATION_TESTS_REQUIRED"
    assert guard["certifiable"] is False
    assert guard["productionCertified"] is False

    assert manifest["productionCertified"] is False
    assert manifest["hardeningCertifiableCount"] == 0
    assert manifest["legacyRegistryPlaceholderCount"] == len(FORMER_PLACEHOLDERS)
    assert (out / "CAPABILITY_HARDENING_LEDGER.json").exists()
    assert (out / "CAPABILITY_MATURITY_SUMMARY.json").exists()
    assert (out / "HARDENING_SUMMARY.md").exists()

    legacy = json.loads((out / "placeholder_ledger.json").read_text(encoding="utf-8"))
    assert len(legacy) == 15
    assert all(row["legacyPlaceholder"] is True for row in legacy)
    assert all(row["certifiable"] is False for row in legacy)
