from __future__ import annotations

import unittest

from code_atlas.change_intelligence import compare_observed_states
from code_atlas.change_intelligence.contracts import ContractError

_BASE_DIGEST = "a" * 64
_HEAD_DIGEST = "b" * 64


def _snapshot(*, repo: str = "repo:r", commit: str = "commit:a", tree: str = "tree:a", digest: str = _BASE_DIGEST) -> dict[str, str]:
    return {
        "repositoryIdentity": repo,
        "commitIdentity": commit,
        "treeIdentity": tree,
        "snapshotDigest": digest,
    }


def _observation(
    oid: str,
    payload: dict[str, object],
    *,
    support: str = "SUPPORTED",
    evidence: list[object] | None = None,
) -> dict[str, object]:
    return {
        "id": oid,
        "payload": payload,
        "supportLevel": support,
        "evidenceReferences": evidence if evidence is not None else [f"evidence:{oid}"],
    }


def _state(observations: dict[str, list[dict[str, object]]], *, status: str = "COMPLETE") -> dict[str, object]:
    return {"stateStatus": status, "observations": observations}


def _provenance() -> list[dict[str, str]]:
    return [{"source": "snapshot-compare", "digest": "evidence-digest"}]


class ObservedChangeComparisonTests(unittest.TestCase):
    def test_compares_added_removed_changed_and_unchanged_deterministically(self) -> None:
        base = _state(
            {
                "dependencyEdges": [
                    _observation("same", {"from": "a", "to": "b"}),
                    _observation("changed", {"from": "b", "to": "c"}),
                    _observation("removed", {"from": "c", "to": "d"}),
                ]
            }
        )
        head = _state(
            {
                "dependencyEdges": [
                    _observation("added", {"from": "d", "to": "e"}),
                    _observation("changed", {"from": "b", "to": "z"}),
                    _observation("same", {"from": "a", "to": "b"}),
                ]
            }
        )
        kwargs = {
            "base_snapshot": _snapshot(),
            "head_snapshot": _snapshot(commit="commit:b", tree="tree:b", digest=_HEAD_DIGEST),
            "base_state": base,
            "head_state": head,
            "provenance": _provenance(),
        }
        first = compare_observed_states(**kwargs)
        second = compare_observed_states(
            base_snapshot=kwargs["base_snapshot"],
            head_snapshot=kwargs["head_snapshot"],
            base_state=_state({"dependencyEdges": list(reversed(base["observations"]["dependencyEdges"]))}),
            head_state=_state({"dependencyEdges": list(reversed(head["observations"]["dependencyEdges"]))}),
            provenance=list(reversed(_provenance())),
        )

        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "PASS")
        rows = first["architectureDelta"]["categories"]["dependencyEdges"]
        self.assertEqual(
            [(row["id"], row["status"]) for row in rows],
            [("added", "added"), ("changed", "changed"), ("removed", "removed"), ("same", "unchanged")],
        )
        self.assertEqual(first["architectureDelta"]["materialChangeCount"], 3)
        self.assertTrue(first["comparisonDigest"].startswith("sha256:"))
        self.assertFalse(first["authorizesMutation"])

    def test_category_change_is_explicit_remove_and_add(self) -> None:
        result = compare_observed_states(
            base_snapshot=_snapshot(),
            head_snapshot=_snapshot(commit="commit:b", tree="tree:b", digest=_HEAD_DIGEST),
            base_state=_state({"dependencyEdges": [_observation("edge-1", {"value": 1})]}),
            head_state=_state({"architectureLayers": [_observation("edge-1", {"value": 1})]}),
            provenance=_provenance(),
        )
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["architectureDelta"]["categories"]["dependencyEdges"][0]["status"], "removed")
        self.assertEqual(result["architectureDelta"]["categories"]["architectureLayers"][0]["status"], "added")

    def test_rejects_cross_repository_comparison(self) -> None:
        with self.assertRaises(ContractError):
            compare_observed_states(
                base_snapshot=_snapshot(repo="repo:a"),
                head_snapshot=_snapshot(repo="repo:b", digest=_HEAD_DIGEST),
                base_state=_state({}),
                head_state=_state({}),
                provenance=_provenance(),
            )

    def test_rejects_missing_snapshot_lineage(self) -> None:
        base = _snapshot()
        base.pop("snapshotDigest")
        with self.assertRaises(ContractError):
            compare_observed_states(
                base_snapshot=base,
                head_snapshot=_snapshot(digest=_HEAD_DIGEST),
                base_state=_state({}),
                head_state=_state({}),
                provenance=_provenance(),
            )

    def test_rejects_missing_provenance(self) -> None:
        with self.assertRaises(ContractError):
            compare_observed_states(
                base_snapshot=_snapshot(),
                head_snapshot=_snapshot(digest=_HEAD_DIGEST),
                base_state=_state({}),
                head_state=_state({}),
                provenance=[],
            )

    def test_partial_state_is_unknown_and_does_not_invent_removal(self) -> None:
        result = compare_observed_states(
            base_snapshot=_snapshot(),
            head_snapshot=_snapshot(digest=_HEAD_DIGEST),
            base_state=_state({"dependencyEdges": [_observation("edge-1", {"value": 1})]}),
            head_state=_state({}, status="PARTIAL"),
            provenance=_provenance(),
        )
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertIn("PARTIAL_STATE:head", result["reasonCodes"])
        self.assertEqual(result["architectureDelta"]["categories"]["dependencyEdges"], [])

    def test_stale_state_is_blocked(self) -> None:
        result = compare_observed_states(
            base_snapshot=_snapshot(),
            head_snapshot=_snapshot(digest=_HEAD_DIGEST),
            base_state=_state({}, status="STALE"),
            head_state=_state({}),
            provenance=_provenance(),
        )
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertIn("STALE_STATE:base", result["reasonCodes"])

    def test_conflicted_observation_is_blocked(self) -> None:
        result = compare_observed_states(
            base_snapshot=_snapshot(),
            head_snapshot=_snapshot(digest=_HEAD_DIGEST),
            base_state=_state({"authorityOwnership": [_observation("owner-1", {"owner": "a"}, support="CONFLICTED")]}),
            head_state=_state({"authorityOwnership": [_observation("owner-1", {"owner": "b"})]}),
            provenance=_provenance(),
        )
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertIn("CONFLICTED_EVIDENCE:base:owner-1", result["reasonCodes"])

    def test_inferred_observation_is_unknown_not_proof(self) -> None:
        result = compare_observed_states(
            base_snapshot=_snapshot(),
            head_snapshot=_snapshot(digest=_HEAD_DIGEST),
            base_state=_state({"dependencyEdges": [_observation("edge-1", {"value": 1}, support="INFERRED")]}),
            head_state=_state({"dependencyEdges": [_observation("edge-1", {"value": 1})]}),
            provenance=_provenance(),
        )
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertIn("INFERRED_NOT_PROOF:base:edge-1", result["reasonCodes"])
        self.assertFalse(result["retrievalIsProof"])

    def test_supported_observation_without_critical_evidence_is_unknown(self) -> None:
        result = compare_observed_states(
            base_snapshot=_snapshot(),
            head_snapshot=_snapshot(digest=_HEAD_DIGEST),
            base_state=_state({"dependencyEdges": [_observation("edge-1", {"value": 1}, evidence=[])]}),
            head_state=_state({"dependencyEdges": [_observation("edge-1", {"value": 1})]}),
            provenance=_provenance(),
        )
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertIn("MISSING_CRITICAL_EVIDENCE:base:edge-1", result["reasonCodes"])

    def test_duplicate_observation_identity_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            compare_observed_states(
                base_snapshot=_snapshot(),
                head_snapshot=_snapshot(digest=_HEAD_DIGEST),
                base_state=_state(
                    {
                        "dependencyEdges": [
                            _observation("edge-1", {"value": 1}),
                            _observation("edge-1", {"value": 2}),
                        ]
                    }
                ),
                head_state=_state({}),
                provenance=_provenance(),
            )

    def test_raw_secret_payload_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            compare_observed_states(
                base_snapshot=_snapshot(),
                head_snapshot=_snapshot(digest=_HEAD_DIGEST),
                base_state=_state({"protectedSensitiveScope": [_observation("secret-1", {"token": "raw-secret"})]}),
                head_state=_state({}),
                provenance=_provenance(),
            )


if __name__ == "__main__":
    unittest.main()
