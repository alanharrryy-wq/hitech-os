from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "caext_external_gate_v2.py"
SPEC = importlib.util.spec_from_file_location("caext_external_gate_v2", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class BoundaryAwareLeakScanTests(unittest.TestCase):
    def test_ndc_does_not_match_tailwindcss_substring(self) -> None:
        self.assertEqual(mod.boundary_occurrences("node_modules/tailwindcss/plugin.js", "NDC"), [])

    def test_real_ndc_token_is_detected(self) -> None:
        spans = mod.boundary_occurrences("architecture token: NDC; next", "NDC")
        self.assertEqual(len(spans), 1)

    def test_source_derived_provenance_wins_for_neutral_profile(self) -> None:
        value = mod.classify_occurrence(
            term="NDC", json_path="$.files[0].path", artifact_name="repository_inventory.json",
            source_derived=True, profile_name="neutral/default", profile_terms=(),
        )
        self.assertEqual(value, "SOURCE_DERIVED")

    def test_explicit_profile_provenance_is_not_core_leak(self) -> None:
        value = mod.classify_occurrence(
            term="PRISMA", json_path="$.profile.name", artifact_name="prep.json",
            source_derived=False, profile_name="prisma", profile_terms=("PRISMA",),
        )
        self.assertEqual(value, "PROFILE_DERIVED")

    def test_historical_tool_evidence_is_distinct(self) -> None:
        value = mod.classify_occurrence(
            term="PRISMA", json_path="$.historical.note", artifact_name="historical_validation.json",
            source_derived=False, profile_name="neutral/default", profile_terms=(),
        )
        self.assertEqual(value, "HISTORICAL_TOOL_EVIDENCE")

    def test_unexplained_neutral_token_is_core_leak(self) -> None:
        value = mod.classify_occurrence(
            term="PRISMA", json_path="$.engine.label", artifact_name="system_graphs.json",
            source_derived=False, profile_name="neutral/default", profile_terms=(),
        )
        self.assertEqual(value, "CORE_LEAK")


class PrepareImpactMetricTests(unittest.TestCase):
    def test_prepare_radius_overrides_empty_discover_change_impact(self) -> None:
        prepared = {
            "changeModel": {
                "impactRadius": {
                    "changed": ["src/a.py"],
                    "impacted": ["src/a.py", "src/b.py", "tests/test_a.py"],
                },
                "protectedScope": ["src/payments.py"],
                "requiredEvidence": [{"id": "test:a"}, {"id": "evidence:a"}],
            }
        }
        discovery = {
            "changeImpact": {"changed": [], "impacted": []},
            "dependencyGraph": {
                "nodes": ["src/a.py", "src/b.py", "tests/test_a.py"],
                "edgeCount": 2,
                "edges": [
                    {"from": "src/b.py", "to": "src/a.py"},
                    {"from": "tests/test_a.py", "to": "src/b.py"},
                ],
            },
        }
        metrics = mod.prepare_metrics(prepared, discovery)
        self.assertEqual(metrics["discoveryChangeImpactSize"], 0)
        self.assertEqual(metrics["prepareImpactRadiusSize"], 3)
        self.assertEqual(metrics["prepareDirectImpactCount"], 1)
        self.assertEqual(metrics["prepareTransitiveImpactCount"], 1)
        self.assertEqual(metrics["protectedScopeCount"], 1)
        self.assertEqual(metrics["requiredEvidenceCount"], 2)
        self.assertEqual(metrics["legacyDiscoveryChangeImpactSize"], "DEPRECATED_DO_NOT_USE")


if __name__ == "__main__":
    unittest.main()
