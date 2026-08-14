from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from code_atlas.intelligence.authority import (
    AuthorityRequest, AuthorityRequirementError, discover_authorities, semantic_retrieve,
)
from code_atlas.intelligence.engine import IntelligenceRequest, run_intelligence
from code_atlas.intelligence.graphs import build_system_graphs
from code_atlas.intelligence.index import build_derived_index, query_derived_index
from code_atlas.intelligence.repository import discover_repository
from code_atlas.intelligence.snapshot import assess_snapshot_freshness, build_snapshot


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


def _init_repo(root: Path) -> Path:
    repo = root / "foreign repo ü"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    (repo / ".github/workflows").mkdir(parents=True)
    (repo / "src/domain").mkdir(parents=True)
    (repo / "src/db").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "docs/architecture").mkdir(parents=True)
    (repo / "config space").mkdir()
    (repo / ".code-atlas").mkdir()
    (repo / "archive").mkdir()
    (repo / "generated").mkdir()
    (repo / ".env.secret").write_text("DO_NOT_READ=supersecret\n", encoding="utf-8")
    (repo / "README.md").write_text("# Foreign Service\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("Repository instructions.\n", encoding="utf-8")
    (repo / "CODEOWNERS").write_text("/src/db/* @data-team\n/src/domain/* @domain-team\n", encoding="utf-8")
    (repo / "package.json").write_text(json.dumps({
        "name":"foreign-service",
        "scripts":{"test":"pytest"},
        "dependencies":{"react":"1.0.0"}
    }), encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='foreign-service'\n", encoding="utf-8")
    (repo / ".github/workflows/ci.yml").write_text("name: CI\n", encoding="utf-8")
    (repo / "src/domain/service.py").write_text("from src.db.store import load\n\ndef run():\n return load()\n", encoding="utf-8")
    (repo / "src/db/store.py").write_text("def load():\n return 1\n", encoding="utf-8")
    (repo / "src/db/schema.prisma").write_text("model Item { id Int @id }\n", encoding="utf-8")
    (repo / "tests/test_service.py").write_text("from src.domain.service import run\n\ndef test_run(): assert run()==1\n", encoding="utf-8")
    (repo / "docs/architecture/system.md").write_text("# Architecture\nCurrent design.\n", encoding="utf-8")
    (repo / "config space/authority ü.md").write_text("# Special authority\n", encoding="utf-8")
    (repo / "archive/architecture-old.md").write_text("# Old architecture\n", encoding="utf-8")
    (repo / "generated/client.py").write_text("# generated\n", encoding="utf-8")
    (repo / ".code-atlas/authority.json").write_text(json.dumps({
        "authorities":[
            {"path":"config space/authority ü.md","scope":"configuration","priority":50},
            {"path":"src/db/schema.prisma","scope":"data-schema","priority":80},
        ]
    }), encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return repo


class UniversalIntelligenceTests(unittest.TestCase):
    def test_unknown_repository_discovery_is_neutral_and_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            head_before = _git(repo, "rev-parse", "HEAD")
            inv = discover_repository(repo, workers=4)
            head_after = _git(repo, "rev-parse", "HEAD")
            self.assertEqual(head_before, head_after)
            self.assertEqual(inv["physicalCoverage"]["percent"], 100.0)
            self.assertGreater(inv["semanticCoverage"]["percent"], 0)
            self.assertTrue(any(row["id"] == "react" for row in inv["frameworks"]))
            self.assertIn(".github/workflows/ci.yml", inv["ciFiles"])
            self.assertIn("src/db/schema.prisma", inv["databaseFiles"])
            secret = next(row for row in inv["files"] if row["path"] == ".env.secret")
            self.assertTrue(secret["sensitiveName"])
            self.assertFalse(secret["contentRead"])
            self.assertIsNone(secret["contentSha256"])

    def test_profile_hint_cannot_invent_authority(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            result = discover_authorities(
                repo, inv,
                request=AuthorityRequest(fail_on_missing=False),
                profile_metadata={"authorityHints":["does/not/exist.md"]},
            )
            hint = next(row for row in result["candidates"] if row["path"] == "does/not/exist.md")
            self.assertEqual(hint["state"], "MISSING")
            self.assertNotEqual(hint["state"], "AUTHORITATIVE")
            self.assertEqual(result["profileRule"], "EXPECTATIONS_ONLY_NOT_FACTS")

    def test_candidate_is_not_authority_without_repo_declaration(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            result = discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=False))
            readme = next(row for row in result["candidates"] if row["path"] == "README.md")
            declared = next(row for row in result["candidates"] if row["path"] == "src/db/schema.prisma")
            self.assertEqual(readme["state"], "CANDIDATE")
            self.assertEqual(declared["state"], "AUTHORITATIVE")

    def test_required_paths_with_spaces_unicode_and_directory_expand(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            result = discover_authorities(
                repo, inv,
                request=AuthorityRequest(
                    required_authorities=("config space/authority ü.md",),
                    required_directories=("src/db",),
                    fail_on_missing=True,
                ),
            )
            self.assertEqual(result["coverage"]["requiredAuthoritiesMissing"], 0)
            self.assertEqual(result["coverage"]["requiredDirectoriesMissing"], 0)
            paths = {row["path"] for row in result["candidates"]}
            self.assertIn("config space/authority ü.md", paths)
            self.assertIn("src/db/schema.prisma", paths)
            self.assertIn("src/db/store.py", paths)

    def test_required_authority_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            with self.assertRaises(AuthorityRequirementError):
                discover_authorities(
                    repo, inv,
                    request=AuthorityRequest(required_authorities=("missing authority.md",), fail_on_missing=True),
                )

    def test_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            with self.assertRaises(ValueError):
                discover_authorities(
                    repo, inv,
                    request=AuthorityRequest(required_authorities=("../outside.md",), fail_on_missing=False),
                )

    def test_semantic_retrieval_returns_evidence_not_truth(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            auth = discover_authorities(repo, inv, request=AuthorityRequest(domain="data", fail_on_missing=False))
            result = semantic_retrieve("schema data", auth)
            self.assertEqual(result["retrievalRule"], "SEMANTIC_RETRIEVAL_DISCOVERS_EVIDENCE_NOT_TRUTH")
            self.assertTrue(result["results"])
            self.assertTrue(all("evidenceSha256" in row for row in result["results"]))

    def test_system_graphs_keep_architecture_distinct_from_visual(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            auth = discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=False))
            graphs = build_system_graphs(repo, inv, auth, changed_paths=["src/db/store.py"])
            self.assertIsNone(graphs["visualLayerMap"])
            self.assertEqual(graphs["architectureLayerGraph"]["name"], "Architecture Layer Graph")
            self.assertTrue(graphs["dependencyGraph"]["edges"])
            self.assertIn("@data-team", graphs["changeImpact"]["owners"])

    def test_sqlite_is_derived_not_authority(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = _init_repo(base)
            inv = discover_repository(repo)
            auth = discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=False))
            graphs = build_system_graphs(repo, inv, auth)
            snapshot = build_snapshot(repo, inv, auth, profile_id="generic", profile_version="1", request_digest=auth["requestDigest"])
            index = base/"index.sqlite"
            build_derived_index(index, inv, auth, graphs, snapshot)
            con = sqlite3.connect(index)
            try:
                meta = dict(con.execute("SELECT key,value FROM meta").fetchall())
            finally:
                con.close()
            self.assertEqual(meta["authoritative"], "false")
            self.assertEqual(meta["rebuildable"], "true")
            result = query_derived_index(index, "schema")
            self.assertEqual(result["indexAuthority"], "DERIVED_NON_AUTHORITATIVE")

    def test_snapshot_freshness_same_head_then_material_drift(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            auth = discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=False))
            snap = build_snapshot(repo, inv, auth, profile_id="generic", profile_version="1", request_digest=auth["requestDigest"])
            same = assess_snapshot_freshness(snap, repo)
            self.assertEqual(same["status"], "REUSABLE_SAME_HEAD")
            (repo/"README.md").write_text("# changed non-material\n", encoding="utf-8")
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-m", "non material")
            refresh = assess_snapshot_freshness(snap, repo)
            self.assertEqual(refresh["status"], "INCREMENTAL_REFRESH_ELIGIBLE")
            (repo/"src/db/schema.prisma").write_text("model Item { id String @id }\n", encoding="utf-8")
            _git(repo, "add", "src/db/schema.prisma")
            _git(repo, "commit", "-m", "schema drift")
            stale = assess_snapshot_freshness(snap, repo)
            self.assertEqual(stale["status"], "STALE_RESCAN_REQUIRED")
            self.assertTrue(stale["rescanRequired"])

    def test_engine_builds_portable_bundle_without_repo_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = _init_repo(base)
            out = base/"atlas output"
            profile = base/"profile.json"
            profile.write_text(json.dumps({
                "profileId":"external-client",
                "projectName":"External Client",
                "projectRoot":str(repo),
                "outputRoot":str(out),
                "metadata":{
                    "profileVersion":"7",
                    "authorityHints":["README.md","not-real.md"],
                }
            }), encoding="utf-8")
            before = _git(repo, "rev-parse", "HEAD")
            result = run_intelligence(
                repo, out, profile_path=profile,
                request=IntelligenceRequest(
                    intent="AUDIT",
                    domain="data",
                    required_authorities=("src/db/schema.prisma",),
                    required_directories=("config space",),
                    semantic_query="schema",
                    workers=4,
                ),
            )
            after = _git(repo, "rev-parse", "HEAD")
            self.assertEqual(before, after)
            self.assertEqual(result["status"], "PASS_UNIVERSAL_INTELLIGENCE_SOURCE_READY")
            self.assertTrue(Path(result["artifact"]).is_file())
            self.assertFalse(result["derivedIndexAuthoritative"])
            self.assertFalse(result["semanticRetrievalIsProof"])
            self.assertFalse(result["profileMayInventTruth"])
            self.assertFalse(result["productionCertified"])

    def test_dirty_worktree_invalidates_snapshot_even_same_head(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            auth = discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=False))
            snap = build_snapshot(repo, inv, auth, profile_id="generic", profile_version="1", request_digest=auth["requestDigest"])
            (repo/"README.md").write_text("# dirty\n", encoding="utf-8")
            status = assess_snapshot_freshness(snap, repo)
            self.assertEqual(status["status"], "STALE_WORKTREE_DIRTY_RESCAN_REQUIRED")
            self.assertTrue(status["rescanRequired"])

    def test_repo_declared_missing_authority_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            declaration = repo/".code-atlas/authority.json"
            raw = json.loads(declaration.read_text(encoding="utf-8"))
            raw["authorities"].append({"path":"deleted/policy.md","scope":"policy"})
            declaration.write_text(json.dumps(raw), encoding="utf-8")
            _git(repo, "add", ".code-atlas/authority.json")
            _git(repo, "commit", "-m", "broken declaration")
            inv = discover_repository(repo)
            with self.assertRaises(AuthorityRequirementError):
                discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=True))

    def test_historical_generated_are_not_promoted_by_path_name_alone(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _init_repo(Path(td))
            inv = discover_repository(repo)
            auth = discover_authorities(repo, inv, request=AuthorityRequest(fail_on_missing=False))
            old = next((row for row in auth["candidates"] if row["path"] == "archive/architecture-old.md"), None)
            if old is not None:
                self.assertNotEqual(old["state"], "AUTHORITATIVE")
                self.assertTrue(old["historical"])
            inv_row = next(row for row in inv["files"] if row["path"] == "archive/architecture-old.md")
            self.assertTrue(inv_row["historical"])


if __name__ == "__main__":
    unittest.main()
