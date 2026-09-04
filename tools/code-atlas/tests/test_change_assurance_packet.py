from __future__ import annotations

import unittest

from code_atlas.change_intelligence import (
    build_change_assurance_packet,
    render_change_assurance_packet_markdown,
)
from code_atlas.change_intelligence.contracts import ContractError


SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40
TREE_A = "d" * 40
TREE_B = "e" * 40
DIGEST = "sha256:" + "f" * 64


class ChangeAssurancePacketTests(unittest.TestCase):
    def base_kwargs(self):
        chain = [
            ("Code Atlas", "PRISMA Change Assurance"),
            ("PRISMA Change Assurance", "Authority Mesh"),
            ("Authority Mesh", "gates"),
            ("gates", "Evidence Bundle"),
            ("Evidence Bundle", "Factory Ledger"),
        ]
        return {
            "analyzed_change": {
                "summary": "Normalize one bounded assurance surface",
                "repositoryIdentity": "repo",
                "changedPaths": ["src/a.py"],
            },
            "impact_radius": {
                "summary": "One bounded source path plus its governed evidence",
                "affectedPaths": ["src/a.py", "tests/test_a.py"],
            },
            "authorized_snapshot": {
                "repositoryIdentity": "repo",
                "commitIdentity": SHA_A,
                "treeIdentity": TREE_A,
            },
            "current_snapshot": {
                "repositoryIdentity": "repo",
                "commitIdentity": SHA_A,
                "treeIdentity": TREE_A,
            },
            "drift_classification": "PASS_ALREADY_CURRENT",
            "affected_authority": [],
            "protected_scope": ["src/protected"],
            "provenance": {"authorityRun": "run:1", "authorityArtifact": "artifact:2"},
            "evidence": [
                {"id": "verify", "kind": "workflow", "reference": "run:3", "digest": DIGEST},
            ],
            "unknowns": [],
            "verification": {
                "decision": "PASS",
                "reportDigest": DIGEST,
                "evidenceReferences": ["verify"],
            },
            "integration_chain": [
                {
                    "producer": producer,
                    "consumer": consumer,
                    "contract": f"contract:{index}",
                    "binding": f"sha:{index}",
                    "evidenceReferences": ["verify"],
                }
                for index, (producer, consumer) in enumerate(chain, start=1)
            ],
            "claim_evidence": [
                {
                    "claim": "Preserves UNKNOWN instead of promoting it",
                    "status": "SUPPORTED",
                    "evidenceReferences": ["verify"],
                }
            ],
            "external_validation": {
                "G": {"status": "PARTIAL", "evidenceReferences": []},
                "J": {"status": "BLOCKED", "evidenceReferences": []},
            },
            "exact_pr_sha": SHA_B,
            "generated_at": "2026-09-04T12:00:00Z",
        }

    def test_premerge_pass_is_only_candidate(self):
        packet = build_change_assurance_packet(**self.base_kwargs())
        self.assertEqual(packet["decision"], "PASS")
        self.assertEqual(packet["readiness"], "TECHNICAL_COMMERCIALIZATION_CANDIDATE")
        self.assertFalse(packet["productionCertified"])
        self.assertEqual(packet["externalValidationPending"], ["G", "J"])
        self.assertIn("PRISMA Change Assurance Packet V1", render_change_assurance_packet_markdown(packet))

    def test_blocked_relevant_drift_blocks_packet(self):
        kwargs = self.base_kwargs()
        kwargs["drift_classification"] = "BLOCKED_RELEVANT_DRIFT"
        packet = build_change_assurance_packet(**kwargs)
        self.assertEqual(packet["decision"], "BLOCKED")
        self.assertEqual(packet["readiness"], "BLOCKED")

    def test_unknowns_force_unknown(self):
        kwargs = self.base_kwargs()
        kwargs["unknowns"] = ["runtime owner not evidenced"]
        packet = build_change_assurance_packet(**kwargs)
        self.assertEqual(packet["decision"], "UNKNOWN")
        self.assertEqual(packet["readiness"], "UNKNOWN")

    def test_supported_claim_requires_evidence(self):
        kwargs = self.base_kwargs()
        kwargs["claim_evidence"] = [{
            "claim": "Detects relevant authority drift",
            "status": "SUPPORTED",
            "evidenceReferences": [],
        }]
        with self.assertRaises(ContractError):
            build_change_assurance_packet(**kwargs)

    def test_integration_chain_must_be_exact(self):
        kwargs = self.base_kwargs()
        kwargs["integration_chain"][1]["consumer"] = "Something Else"
        with self.assertRaises(ContractError):
            build_change_assurance_packet(**kwargs)

    def test_postmerge_pass_with_external_pending_is_technical_ready(self):
        kwargs = self.base_kwargs()
        kwargs["merge_sha"] = SHA_C
        kwargs["post_merge_proof"] = {
            "mergeSha": SHA_C,
            "decision": "PASS",
            "evidenceReferences": ["verify"],
            "digest": DIGEST,
        }
        packet = build_change_assurance_packet(**kwargs)
        self.assertEqual(packet["readiness"], "TECHNICAL_COMMERCIALIZATION_READY")

    def test_full_commercial_ready_requires_g_and_j_done(self):
        kwargs = self.base_kwargs()
        kwargs["merge_sha"] = SHA_C
        kwargs["post_merge_proof"] = {
            "mergeSha": SHA_C,
            "decision": "PASS",
            "evidenceReferences": ["verify"],
        }
        kwargs["external_validation"] = {
            "G": {"status": "DONE", "evidenceReferences": ["independent-run"]},
            "J": {"status": "DONE", "evidenceReferences": ["human-study"]},
        }
        packet = build_change_assurance_packet(**kwargs)
        self.assertEqual(packet["readiness"], "COMMERCIALIZATION_READY")
        self.assertEqual(packet["externalValidationPending"], [])

    def test_postmerge_proof_must_match_merge_sha(self):
        kwargs = self.base_kwargs()
        kwargs["merge_sha"] = SHA_C
        kwargs["post_merge_proof"] = {
            "mergeSha": SHA_A,
            "decision": "PASS",
            "evidenceReferences": ["verify"],
        }
        with self.assertRaises(ContractError):
            build_change_assurance_packet(**kwargs)

    def test_pass_already_current_requires_same_snapshot(self):
        kwargs = self.base_kwargs()
        kwargs["current_snapshot"] = {
            "repositoryIdentity": "repo",
            "commitIdentity": SHA_B,
            "treeIdentity": TREE_B,
        }
        with self.assertRaises(ContractError):
            build_change_assurance_packet(**kwargs)


if __name__ == "__main__":
    unittest.main()
