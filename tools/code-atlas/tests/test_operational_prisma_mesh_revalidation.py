from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from code_atlas.motors import prisma_mesh_revalidation as m


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def repo(base: Path) -> Path:
    r = base / "repo"
    r.mkdir()
    git(r, "init")
    git(r, "config", "user.email", "x@example.invalid")
    git(r, "config", "user.name", "T")
    (r / "authority").mkdir()
    (r / "authority/core.txt").write_text("authority-v1\n")
    (r / "scope").mkdir()
    (r / "scope/target.txt").write_text("scope-v1\n")
    (r / "notes").mkdir()
    (r / "notes/unrelated.md").write_text("u1\n")
    (r / "candidate").mkdir()
    (r / "candidate/retrieved.txt").write_text("candidate-v1\n")
    (r / ".github/workflows").mkdir(parents=True)
    (r / ".github/workflows/prisma-remote-automesh.yml").write_text("name: mesh\n")
    commit(r, "base")
    return r


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def composed_bytes(r: Path) -> bytes:
    head = git(r, "rev-parse", "HEAD")
    tree = git(r, "rev-parse", "HEAD^{tree}")
    request = {
        "schemaVersion": "prisma_remote_authority_gateway.v2",
        "expectedHead": head,
        "profile": "test",
        "tasks": [{
            "id": "lane",
            "surface": "governance",
            "task": "test bounded drift",
            "intent": "VERIFY",
            "domain": "testing",
            "requiredAuthorities": ["authority/core.txt"],
            "requiredDirectories": ["scope"],
            "requiredCapabilities": [],
            "excludedAuthorities": [],
            "minimumCoverage": 100.0,
            "failOnMissingAuthority": True,
        }],
    }
    request["requestDigest"] = hashlib.sha256(
        json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    lane = {
        "repoHead": head,
        "requiredAuthorities": ["authority/core.txt"],
        "requiredDirectories": ["scope"],
        "selected_files": [
            {"path": "authority/core.txt", "state": "SUPPORTED", "sha256": sha(r / "authority/core.txt"), "whySelected": ["required-by-task"]},
            {"path": "candidate/retrieved.txt", "state": "CANDIDATE", "sha256": sha(r / "candidate/retrieved.txt"), "whySelected": ["semantic-retrieval"]},
        ],
    }
    report = {
        "schemaVersion": "prisma_remote_authority_gateway.v2",
        "status": "PASS_COMPOSED_AUTHORITY_MESH",
        "repoHead": head,
        "repoTree": tree,
        "requestDigest": request["requestDigest"],
        "readOnly": True,
        "productionCertified": False,
    }
    files = {
        "PRISMA_MESH_GATEWAY_REPORT.json": json.dumps(report, sort_keys=True).encode(),
        "authority/normalized_request.json": json.dumps(request, sort_keys=True).encode(),
        "authority/lanes/lane/AUTHORITY_READSET.lock.json": json.dumps(lane, sort_keys=True).encode(),
    }
    rows = [{"path": n, "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)} for n, b in sorted(files.items())]
    files["MANIFEST.json"] = json.dumps({"report": report, "files": rows}, sort_keys=True).encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    return out.getvalue()


def outer_artifact(path: Path, composed: bytes) -> str:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("prisma-automesh-composed-result.zip", composed)
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RevalidationTests(unittest.TestCase):
    def test_same_head_emits_current_attestation(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_ALREADY_CURRENT)
            final = Path(result["artifact"])
            self.assertTrue(final.is_file())
            with zipfile.ZipFile(final) as z:
                report = json.loads(z.read("PRISMA_MESH_GATEWAY_REPORT.json"))
            self.assertEqual(report["repoHead"], git(r, "rev-parse", "HEAD"))
            self.assertEqual(report["revalidationStatus"], m.PASS_ALREADY_CURRENT)

    def test_unrelated_and_candidate_drift_do_not_destroy_authority(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            (r / "notes/unrelated.md").write_text("u2\n")
            (r / "candidate/retrieved.txt").write_text("candidate-v2\n")
            commit(r, "unrelated")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_NO_RELEVANT_DRIFT)
            self.assertEqual(result["relevantChangedPaths"], [])
            self.assertIn("candidate/retrieved.txt", result["changedPaths"])
            self.assertFalse(result["candidateRetrievalIsAuthority"])

    def test_revalidated_artifact_can_chain_across_more_unrelated_drift(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            (r / "notes/unrelated.md").write_text("u2\n")
            head_one = commit(r, "unrelated one")
            first = m.revalidate(r, art, b / "out-one", digest)
            self.assertEqual(first["status"], m.PASS_NO_RELEVANT_DRIFT)
            first_artifact = Path(first["artifact"])
            self.assertTrue(first_artifact.is_file())

            (r / "notes/unrelated.md").write_text("u3\n")
            head_two = commit(r, "unrelated two")
            second = m.revalidate(r, first_artifact, b / "out-two", first["artifactSha256"])
            self.assertEqual(second["status"], m.PASS_NO_RELEVANT_DRIFT)
            self.assertEqual(second["baseHead"], head_one)
            self.assertEqual(second["currentHead"], head_two)
            self.assertEqual(second["relevantChangedPaths"], [])
            self.assertTrue(Path(second["artifact"]).is_file())

    def test_required_authority_drift_blocks_and_prepares_full_refresh(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            (r / "authority/core.txt").write_text("authority-v2\n")
            commit(r, "authority change")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_RELEVANT_DRIFT)
            self.assertIn("authority/core.txt", result["relevantChangedPaths"])
            fallback = json.loads((b / "out/fallback_request.json").read_text())
            self.assertEqual(fallback["expectedHead"], git(r, "rev-parse", "HEAD"))
            self.assertNotIn("requestDigest", fallback)

    def test_required_directory_drift_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            (r / "scope/new.txt").write_text("new\n")
            commit(r, "scope change")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_RELEVANT_DRIFT)
            self.assertIn("scope/new.txt", result["relevantChangedPaths"])

    def test_trust_anchor_drift_blocks_even_if_task_did_not_select_it(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            p = r / ".github/workflows/prisma-remote-automesh.yml"
            p.write_text("name: changed\n")
            commit(r, "trust change")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_RELEVANT_DRIFT)
            self.assertIn(".github/workflows/prisma-remote-automesh.yml", result["relevantChangedPaths"])

    def test_non_ancestor_requires_full_refresh(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); root = git(r, "rev-parse", "HEAD")
            (r / "notes/unrelated.md").write_text("branch-a\n")
            commit(r, "a")
            art = b / "a.zip"; digest = outer_artifact(art, composed_bytes(r))
            git(r, "checkout", "--detach", root)
            (r / "notes/unrelated.md").write_text("branch-b\n")
            commit(r, "b")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_NON_ANCESTOR)
            self.assertTrue(result["canFallbackFullMesh"])

    def test_digest_mismatch_is_invalid_evidence_without_trusted_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); art = b / "a.zip"; outer_artifact(art, composed_bytes(r))
            result = m.revalidate(r, art, b / "out", "0" * 64)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertFalse(result["canFallbackFullMesh"])

    def test_manifest_tamper_is_invalid_even_with_matching_outer_digest(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td); r = repo(b); raw = composed_bytes(r)
            zin = zipfile.ZipFile(io.BytesIO(raw)); out = io.BytesIO()
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
                for n in zin.namelist():
                    data = zin.read(n)
                    if n == "authority/normalized_request.json":
                        data += b" \n"
                    zout.writestr(n, data)
            art = b / "a.zip"; digest = outer_artifact(art, out.getvalue())
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn("COMPOSED_MANIFEST_", result["error"])


if __name__ == "__main__":
    unittest.main()
