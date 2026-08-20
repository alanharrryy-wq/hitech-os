from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context
from code_atlas.intelligence.edge_provenance import normalize_system_graph_edge_provenance


class EdgeProvenanceTests(unittest.TestCase):
    def test_existing_evidence_becomes_structured_provenance_without_mutating_raw_graph(self) -> None:
        raw = {
            "dependencyGraph": {
                "edges": [
                    {
                        "from": "src/a.py",
                        "to": "src/b.py",
                        "type": "imports",
                        "evidence": "parsed-python-import",
                        "confidence": "supported",
                    }
                ],
                "edgeCount": 1,
            }
        }
        before = copy.deepcopy(raw)
        first = normalize_system_graph_edge_provenance(raw, {})
        second = normalize_system_graph_edge_provenance(raw, {})
        edge = first["dependencyGraph"]["edges"][0]

        self.assertEqual(raw, before)
        self.assertEqual(first, second)
        self.assertEqual(edge["confidence"], "supported")
        self.assertEqual(edge["provenance"]["kind"], "edge-evidence")
        self.assertEqual(edge["provenance"]["evidence"], "parsed-python-import")
        self.assertFalse(first["edgeProvenance"]["rawGraphMutated"])

    def test_authority_declaration_and_conflict_use_repository_declaration_provenance(self) -> None:
        authorities = {
            "declarations": [
                {
                    "declarationFile": ".code-atlas/authority.json",
                    "path": "AUTH_A.md",
                    "scope": "security",
                    "kind": "repo-declared",
                    "priority": 0,
                },
                {
                    "declarationFile": ".code-atlas/authority.json",
                    "path": "AUTH_B.md",
                    "scope": "security",
                    "kind": "repo-declared",
                    "priority": 0,
                },
            ],
            "conflicts": {"security": ["AUTH_A.md", "AUTH_B.md"]},
            "candidates": [],
        }
        raw = {
            "authorityGraph": {
                "edges": [
                    {
                        "from": ".code-atlas/authority.json",
                        "to": "AUTH_A.md",
                        "type": "authority-declaration",
                        "scope": "security",
                    },
                    {
                        "from": "conflict:security",
                        "to": "AUTH_A.md",
                        "type": "authority-conflict",
                    },
                ]
            }
        }
        normalized = normalize_system_graph_edge_provenance(raw, authorities)
        declaration, conflict = normalized["authorityGraph"]["edges"]

        self.assertEqual(declaration["confidence"], "supported")
        self.assertEqual(declaration["provenance"]["kind"], "repository-authority-declaration")
        self.assertEqual(declaration["provenance"]["records"][0]["path"], "AUTH_A.md")

        self.assertEqual(conflict["confidence"], "supported")
        self.assertEqual(conflict["provenance"]["kind"], "repository-authority-conflict")
        self.assertEqual(conflict["provenance"]["scope"], "security")
        self.assertEqual(conflict["provenance"]["conflictingPaths"], ["AUTH_A.md", "AUTH_B.md"])
        self.assertEqual(len(conflict["provenance"]["records"]), 2)

    def test_unproven_supported_edge_is_downgraded_to_unknown(self) -> None:
        raw = {
            "opaqueGraph": {
                "edges": [
                    {
                        "from": "a",
                        "to": "b",
                        "type": "opaque-material-edge",
                        "confidence": "supported",
                    }
                ]
            }
        }
        normalized = normalize_system_graph_edge_provenance(raw, {})
        edge = normalized["opaqueGraph"]["edges"][0]

        self.assertEqual(edge["confidence"], "unknown")
        self.assertEqual(edge["provenance"]["kind"], "unresolved-edge-provenance")
        self.assertEqual(
            edge["provenance"]["reason"],
            "EDGE_LEVEL_PROVENANCE_NOT_PROVEN_FROM_CANONICAL_REPOSITORY_FACTS",
        )

    def test_engine_exposes_normalized_edges_from_repository_facts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="code-atlas-edge-provenance-") as td:
            repo = Path(td) / "neutral-repo"
            repo.mkdir()
            (repo / "src").mkdir()
            (repo / ".code-atlas").mkdir()
            (repo / "src" / "__init__.py").write_text("", encoding="utf-8")
            (repo / "src" / "b.py").write_text("VALUE = 1\n", encoding="utf-8")
            (repo / "src" / "a.py").write_text("from src.b import VALUE\n", encoding="utf-8")
            (repo / "CODEOWNERS").write_text("/src/*.py @team\n", encoding="utf-8")
            (repo / "AUTH_A.md").write_text("A\n", encoding="utf-8")
            (repo / "AUTH_B.md").write_text("B\n", encoding="utf-8")
            (repo / ".code-atlas" / "authority.json").write_text(
                json.dumps(
                    {
                        "authorities": [
                            {"path": "AUTH_A.md", "scope": "security"},
                            {"path": "AUTH_B.md", "scope": "security"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self._git(repo, "init")
            self._git(repo, "config", "user.email", "edge@example.invalid")
            self._git(repo, "config", "user.name", "Edge Fixture")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-m", "fixture")

            context = resolve_intelligence_context(
                repo,
                request=IntelligenceRequest(
                    intent="VERIFY",
                    domain="security",
                    changed_paths=("src/b.py",),
                    fail_on_missing_authority=False,
                ),
            )

            self.assertEqual(context["graphs"]["edgeProvenance"]["schemaVersion"], "code_atlas_edge_provenance.v1")
            self.assertFalse(context["graphs"]["edgeProvenance"]["productionCertified"])
            for graph in context["graphs"].values():
                if not isinstance(graph, dict) or not isinstance(graph.get("edges"), list):
                    continue
                for edge in graph["edges"]:
                    self.assertIn(edge["confidence"], {"supported", "inferred", "unknown"})
                    self.assertTrue(edge.get("provenance"))

            conflicts = [
                edge
                for edge in context["graphs"]["authorityGraph"]["edges"]
                if edge.get("type") == "authority-conflict"
            ]
            self.assertEqual(len(conflicts), 2)
            self.assertTrue(all(edge["confidence"] == "supported" for edge in conflicts))
            self.assertTrue(all(edge["provenance"]["kind"] == "repository-authority-conflict" for edge in conflicts))

            dependency_edges = context["graphs"]["dependencyGraph"]["edges"]
            self.assertTrue(any(
                edge.get("from") == "src/a.py"
                and edge.get("to") == "src/b.py"
                and edge.get("confidence") == "supported"
                and edge.get("provenance", {}).get("kind") == "edge-evidence"
                for edge in dependency_edges
            ))

    @staticmethod
    def _git(repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout.strip()


if __name__ == "__main__":
    unittest.main()
