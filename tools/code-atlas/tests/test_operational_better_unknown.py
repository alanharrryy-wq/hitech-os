from __future__ import annotations

import unittest

from code_atlas.change_intelligence.authority_pack import build_authority_pack
from code_atlas.change_intelligence.change_studio import compose_change_model
from code_atlas.change_intelligence.unknown_obligations import build_unknown_obligation, normalize_unknown_obligations
from code_atlas.change_intelligence.verification import verify_change


class BetterUnknownOperationalTests(unittest.TestCase):
    def _snapshot(self) -> dict[str, str]:
        return {
            "repositoryIdentity": "repo-d",
            "commitIdentity": "commit-d",
            "treeIdentity": "tree-d",
        }

    def _pack(self, *, unknowns: list[str] | None = None) -> dict:
        return build_authority_pack(
            repository_identity="repo-d",
            commit_identity="commit-d",
            tree_identity="tree-d",
            request_digest="request-d",
            normalized_task="verify bounded unknown guidance",
            allowed_scope=["src/auth"],
            required_checks=["focused-tests"],
            required_evidence=["scope-proof"],
            unknowns=unknowns,
            tool_version="1.0.0",
            profile_version="neutral-v1",
            authority_resolution={"missing": [], "conflicted": []},
            generated_at="2026-08-25T03:40:00Z",
        )

    def test_change_model_unknown_conditions_are_actionable_and_stay_unknown(self) -> None:
        model = compose_change_model(
            normalized_intent="change auth safely",
            repository_snapshot=self._snapshot(),
            primary_targets=[{
                "path": "src/auth/login.py",
                "reason": "target support not yet proven",
                "supportLevel": "UNKNOWN",
                "evidenceReferences": [],
            }],
            unknowns=["runtime owner is not proven"],
            contradictions=["two ownership sources disagree"],
            required_evidence=[{
                "id": "runtime-proof",
                "status": "UNKNOWN",
                "nextEvidence": "Capture bounded runtime ownership evidence for src/auth/login.py.",
            }],
            provenance=[{"source": "test-fixture"}],
        )
        self.assertEqual(model["decision"], "UNKNOWN")
        codes = {row["code"] for row in model["unknownObligations"]}
        self.assertEqual(
            codes,
            {"UNSUPPORTED_PRIMARY_TARGET", "DECLARED_UNKNOWN", "CONTRADICTORY_EVIDENCE", "REQUIRED_EVIDENCE_UNKNOWN"},
        )
        self.assertTrue(all(row["reason"] and row["source"] and row["nextEvidence"] for row in model["unknownObligations"]))
        required = next(row for row in model["unknownObligations"] if row["code"] == "REQUIRED_EVIDENCE_UNKNOWN")
        self.assertEqual(required["subject"], "runtime-proof")
        self.assertIn("Capture bounded runtime ownership evidence", required["nextEvidence"])

    def test_supported_change_model_has_no_unknown_obligations(self) -> None:
        model = compose_change_model(
            normalized_intent="change auth safely",
            repository_snapshot=self._snapshot(),
            primary_targets=[{
                "path": "src/auth/login.py",
                "reason": "repository evidence supports this target",
                "supportLevel": "SUPPORTED",
                "evidenceReferences": [{"path": "src/auth/login.py"}],
            }],
            provenance=[{"source": "test-fixture"}],
        )
        self.assertEqual(model["decision"], "PASS")
        self.assertEqual(model["unknownObligations"], [])

    def test_verify_contradiction_exposes_next_evidence_without_promoting_unknown(self) -> None:
        report = verify_change(
            authority_pack=self._pack(),
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot=self._snapshot(),
            produced_evidence=["focused-tests", "scope-proof"],
            contradictions=["CODEOWNERS and repository authority declaration disagree"],
        )
        self.assertEqual(report["decision"], "UNKNOWN")
        self.assertEqual(len(report["unknownObligations"]), 1)
        obligation = report["unknownObligations"][0]
        self.assertEqual(obligation["code"], "CONTRADICTORY_EVIDENCE")
        self.assertTrue(obligation["nextEvidence"])
        finding = next(row for row in report["findings"] if row["code"] == "CONTRADICTORY_EVIDENCE")
        self.assertEqual(finding["unknownObligations"], report["unknownObligations"])

    def test_pack_and_new_unknowns_remain_unknown_with_actionable_obligations(self) -> None:
        report = verify_change(
            authority_pack=self._pack(unknowns=["deployment owner not proven"]),
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot=self._snapshot(),
            produced_evidence=["focused-tests", "scope-proof"],
            new_unknowns=["new generated companion file may exist"],
        )
        self.assertEqual(report["decision"], "UNKNOWN")
        self.assertEqual({row["code"] for row in report["unknownObligations"]}, {"PACK_UNKNOWN", "NEW_UNKNOWN"})
        self.assertTrue(all(row["nextEvidence"] for row in report["unknownObligations"]))

    def test_unknown_obligation_normalization_is_deterministic_and_deduplicated(self) -> None:
        row = build_unknown_obligation(
            code="DECLARED_UNKNOWN",
            source="change_model.unknowns",
            reason="owner is unknown",
        )
        normalized = normalize_unknown_obligations([row, dict(row)])
        self.assertEqual(normalized, [row])


if __name__ == "__main__":
    unittest.main()
