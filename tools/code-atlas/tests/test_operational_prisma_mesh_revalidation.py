from __future__ import annotations

import hashlib
import io
import json
import stat
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from code_atlas.motors import prisma_mesh_revalidation as m


def git(repo: Path, *args: str, allow: set[int] | None = None) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    allowed = allow if allow is not None else {0}
    if p.returncode not in allowed:
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
    (r / ".github/workflows/prisma-remote-automesh-revalidate.yml").write_text(
        "name: revalidate\n"
    )
    commit(r, "base")
    return r


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_oid(r: Path, rel: str) -> str:
    row = git(r, "ls-tree", "HEAD", "--", rel)
    parts = row.split()
    if len(parts) < 3:
        raise AssertionError(row)
    return parts[2]


def legacy_visual_bytes() -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        readset = {
            "layer_map_required": True,
            "surface_argument": "tablet",
            "explicit_existing_paths": [],
            "missing_expected_authority_files": [],
        }
        z.writestr(
            "x/authority_mesh/.governance/current/AUTHORITY_READSET.lock.json",
            json.dumps(readset),
        )
        z.writestr(
            "x/authority_mesh/reports/LAYERS_MAP.json",
            json.dumps({"path": "scope/target.txt"}),
        )
    return out.getvalue()


def composed_bytes(
    r: Path,
    *,
    visual: bool = False,
    include_legacy: bool = False,
    include_inventory: bool = True,
) -> bytes:
    head = git(r, "rev-parse", "HEAD")
    tree = git(r, "rev-parse", "HEAD^{tree}")
    request = {
        "schemaVersion": "prisma_remote_authority_gateway.v2",
        "expectedHead": head,
        "profile": "test",
        "tasks": [{
            "id": "lane",
            "surface": "tablet" if visual else "governance",
            "task": "test bounded drift",
            "intent": "VERIFY",
            "domain": "visual" if visual else "testing",
            "requiredAuthorities": ["authority/core.txt"],
            "requiredDirectories": ["scope"],
            "requiredCapabilities": [],
            "excludedAuthorities": [],
            "minimumCoverage": 100.0,
            "failOnMissingAuthority": True,
        }],
    }
    request["requestDigest"] = hashlib.sha256(
        json.dumps(
            request,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    lane = {
        "repoHead": head,
        "requiredAuthorities": ["authority/core.txt"],
        "requiredDirectories": ["scope"],
        "selected_files": [
            {
                "path": "authority/core.txt",
                "state": "SUPPORTED",
                "sha256": sha(r / "authority/core.txt"),
                "whySelected": ["required-by-task"],
            },
            {
                "path": "candidate/retrieved.txt",
                "state": "CANDIDATE",
                "sha256": sha(r / "candidate/retrieved.txt"),
                "whySelected": ["semantic-retrieval"],
            },
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
    files: dict[str, bytes] = {
        "PRISMA_MESH_GATEWAY_REPORT.json": json.dumps(
            report, sort_keys=True
        ).encode(),
        "authority/normalized_request.json": json.dumps(
            request, sort_keys=True
        ).encode(),
        "authority/lanes/lane/AUTHORITY_READSET.lock.json": json.dumps(
            lane, sort_keys=True
        ).encode(),
    }
    if include_inventory:
        inventory_rows = []
        for rel in ("authority/core.txt", "candidate/retrieved.txt"):
            inventory_rows.append({
                "path": rel,
                "fileSha256": sha(r / rel),
                "contentSha256": sha(r / rel),
                "gitBlobSha": blob_oid(r, rel),
                "gitMode": "100644",
                "gitStage": 0,
                "exists": True,
                "isSymlink": False,
                "isText": True,
            })
        inventory = {
            "schemaVersion": "code_atlas_repository_discovery.v1",
            "identity": {
                "head": head,
                "tree": tree,
                "dirty": False,
                "isGit": True,
            },
            "inventorySource": "git-index",
            "files": inventory_rows,
            "readOnly": True,
            "productionCertified": False,
        }
        files["authority/repository_inventory.json"] = json.dumps(
            inventory, sort_keys=True
        ).encode()
    if include_legacy:
        files["legacy_surface_mesh.zip"] = legacy_visual_bytes()
    rows = [
        {
            "path": n,
            "sha256": hashlib.sha256(b).hexdigest(),
            "bytes": len(b),
        }
        for n, b in sorted(files.items())
    ]
    files["MANIFEST.json"] = json.dumps(
        {"report": report, "files": rows},
        sort_keys=True,
    ).encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    return out.getvalue()


def rebuild_with_json_mutation(
    raw: bytes,
    target: str,
    mutator,
) -> bytes:
    zin = zipfile.ZipFile(io.BytesIO(raw))
    payload: dict[str, bytes] = {}
    report = json.loads(zin.read("PRISMA_MESH_GATEWAY_REPORT.json"))
    for name in zin.namelist():
        if name == "MANIFEST.json":
            continue
        data = zin.read(name)
        if name == target:
            value = json.loads(data.decode("utf-8"))
            mutator(value)
            data = json.dumps(value, sort_keys=True).encode()
        payload[name] = data
    rows = [
        {
            "path": n,
            "sha256": hashlib.sha256(b).hexdigest(),
            "bytes": len(b),
        }
        for n, b in sorted(payload.items())
    ]
    payload["MANIFEST.json"] = json.dumps(
        {"report": report, "files": rows}, sort_keys=True
    ).encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, b in payload.items():
            zout.writestr(n, b)
    return out.getvalue()


def outer_artifact(
    path: Path,
    composed: bytes,
    member: str = "prisma-automesh-composed-result.zip",
) -> str:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(member, composed)
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RevalidationTests(unittest.TestCase):
    def test_same_head_reuses_validated_authority_bytes_without_repack(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            raw = composed_bytes(r)
            art = b / "a.zip"
            digest = outer_artifact(art, raw)
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_ALREADY_CURRENT)
            self.assertEqual(
                result["artifactReuse"],
                "VALIDATED_AUTHORITY_BYTES_NO_REPACK",
            )
            self.assertEqual(Path(result["artifact"]).read_bytes(), raw)
            self.assertEqual(result["certifiedGitBlobPinCount"], 1)

    def test_unrelated_and_candidate_drift_do_not_destroy_authority(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            (r / "notes/unrelated.md").write_text("u2\n")
            (r / "candidate/retrieved.txt").write_text("candidate-v2\n")
            commit(r, "unrelated")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_NO_RELEVANT_DRIFT)
            self.assertEqual(result["relevantChangedPaths"], [])
            self.assertFalse(result["candidateRetrievalIsAuthority"])

    def test_revalidated_github_outer_artifact_can_chain(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            (r / "notes/unrelated.md").write_text("u2\n")
            commit(r, "one")
            first = m.revalidate(r, art, b / "one", digest)
            github_outer = b / "github.zip"
            outer_digest = outer_artifact(
                github_outer,
                Path(first["artifact"]).read_bytes(),
                "prisma-automesh-revalidated-result.zip",
            )
            (r / "notes/unrelated.md").write_text("u3\n")
            head_two = commit(r, "two")
            second = m.revalidate(r, github_outer, b / "two", outer_digest)
            self.assertEqual(second["status"], m.PASS_NO_RELEVANT_DRIFT)
            self.assertEqual(second["currentHead"], head_two)
            self.assertEqual(
                second["priorAuthorityMember"],
                "prisma-automesh-revalidated-result.zip",
            )

    def test_required_authority_drift_blocks_with_reasons_and_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            (r / "authority/core.txt").write_text("authority-v2\n")
            commit(r, "authority change")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_RELEVANT_DRIFT)
            self.assertIn("authority/core.txt", result["relevanceReasons"])
            fallback = json.loads((b / "out/fallback_request.json").read_text())
            self.assertEqual(
                fallback["expectedHead"],
                git(r, "rev-parse", "HEAD"),
            )
            self.assertNotIn("requestDigest", fallback)

    def test_required_directory_drift_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            (r / "scope/new.txt").write_text("new\n")
            commit(r, "scope change")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_RELEVANT_DRIFT)
            self.assertIn("scope/new.txt", result["relevantChangedPaths"])

    def test_both_workflows_are_trust_anchors(self):
        for target in (
            "prisma-remote-automesh.yml",
            "prisma-remote-automesh-revalidate.yml",
        ):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as td:
                b = Path(td)
                r = repo(b)
                art = b / "a.zip"
                digest = outer_artifact(art, composed_bytes(r))
                p = r / ".github/workflows" / target
                p.write_text("name: changed\n")
                commit(r, "trust change")
                result = m.revalidate(r, art, b / "out", digest)
                self.assertEqual(result["status"], m.BLOCK_RELEVANT_DRIFT)
                self.assertIn(
                    p.relative_to(r).as_posix(),
                    result["relevantChangedPaths"],
                )

    def test_pinned_hashes_use_git_object_database_not_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            (r / "notes/unrelated.md").write_text("u2\n")
            commit(r, "unrelated")
            (r / "authority/core.txt").unlink()
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_NO_RELEVANT_DRIFT)
            self.assertEqual(
                result["pinnedHashSource"],
                "certified-repository-inventory-git-object-id",
            )
            self.assertEqual(result["pinnedHashMismatches"], [])

    def test_crlf_worktree_pin_uses_certified_git_blob_identity(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            git(r, "config", "core.autocrlf", "true")
            (r / "authority/core.txt").write_bytes(b"authority-v1\r\n")
            (r / "notes/unrelated.md").write_text("crlf-base\n")
            commit(r, "crlf base fixture")
            self.assertNotEqual(
                sha(r / "authority/core.txt"),
                hashlib.sha256(
                    subprocess.check_output(
                        ["git", "-C", str(r), "show", "HEAD:authority/core.txt"]
                    )
                ).hexdigest(),
            )
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            (r / "notes/unrelated.md").write_text("crlf-drift\n")
            commit(r, "unrelated drift")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_NO_RELEVANT_DRIFT)
            self.assertEqual(result["certifiedGitBlobPinCount"], 1)
            self.assertEqual(result["pinnedHashMismatches"], [])

    def test_tampered_inventory_blob_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            raw = composed_bytes(r)
            wrong_oid = blob_oid(r, "candidate/retrieved.txt")

            def mutate(value):
                for row in value["files"]:
                    if row.get("path") == "authority/core.txt":
                        row["gitBlobSha"] = wrong_oid

            tampered = rebuild_with_json_mutation(
                raw,
                "authority/repository_inventory.json",
                mutate,
            )
            art = b / "a.zip"
            digest = outer_artifact(art, tampered)
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn("PRIOR_PINNED_IDENTITY_MISMATCH", result["error"])
            self.assertFalse(result["canFallbackFullMesh"])

    def test_non_ancestor_requires_full_refresh(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            root = git(r, "rev-parse", "HEAD")
            (r / "notes/unrelated.md").write_text("branch-a\n")
            commit(r, "a")
            art = b / "a.zip"
            digest = outer_artifact(art, composed_bytes(r))
            git(r, "checkout", "--detach", root)
            (r / "notes/unrelated.md").write_text("branch-b\n")
            commit(r, "b")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_NON_ANCESTOR)
            self.assertTrue(result["canFallbackFullMesh"])

    def test_digest_mismatch_is_invalid_without_trusted_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            outer_artifact(art, composed_bytes(r))
            result = m.revalidate(r, art, b / "out", "0" * 64)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertFalse(result["canFallbackFullMesh"])

    def test_manifest_tamper_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            raw = composed_bytes(r)
            zin = zipfile.ZipFile(io.BytesIO(raw))
            out = io.BytesIO()
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
                for n in zin.namelist():
                    data = zin.read(n)
                    if n == "authority/normalized_request.json":
                        data += b" \n"
                    zout.writestr(n, data)
            art = b / "a.zip"
            digest = outer_artifact(art, out.getvalue())
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn("COMPOSED_MANIFEST_", result["error"])

    def test_unmanifested_composed_member_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            zin = zipfile.ZipFile(io.BytesIO(composed_bytes(r)))
            out = io.BytesIO()
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
                for n in zin.namelist():
                    zout.writestr(n, zin.read(n))
                zout.writestr("extra.txt", b"not in manifest")
            art = b / "a.zip"
            digest = outer_artifact(art, out.getvalue())
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn("COMPOSED_UNMANIFESTED_FILE", result["error"])

    def test_outer_zip_traversal_member_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            with zipfile.ZipFile(art, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr(
                    "prisma-automesh-composed-result.zip",
                    composed_bytes(r),
                )
                z.writestr("../escape", b"x")
            result = m.revalidate(
                r,
                art,
                b / "out",
                hashlib.sha256(art.read_bytes()).hexdigest(),
            )
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn("OUTER_ARTIFACT_UNSAFE_MEMBER", result["error"])

    def test_outer_zip_symlink_member_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            with zipfile.ZipFile(art, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr(
                    "prisma-automesh-composed-result.zip",
                    composed_bytes(r),
                )
                info = zipfile.ZipInfo("link")
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(info, "target")
            result = m.revalidate(
                r,
                art,
                b / "out",
                hashlib.sha256(art.read_bytes()).hexdigest(),
            )
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn("OUTER_ARTIFACT_SYMLINK_MEMBER", result["error"])

    def test_visual_request_without_legacy_layer_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(
                art,
                composed_bytes(r, visual=True, include_legacy=False),
            )
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.BLOCK_INVALID_EVIDENCE)
            self.assertIn(
                "VISUAL_LEGACY_SURFACE_MESH_MISSING",
                result["error"],
            )

    def test_visual_request_with_layer_map_can_revalidate(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(
                art,
                composed_bytes(r, visual=True, include_legacy=True),
            )
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_ALREADY_CURRENT)

    def test_legacy_artifact_without_inventory_still_revalidates_by_diff(self):
        with tempfile.TemporaryDirectory() as td:
            b = Path(td)
            r = repo(b)
            art = b / "a.zip"
            digest = outer_artifact(
                art,
                composed_bytes(r, include_inventory=False),
            )
            (r / "notes/unrelated.md").write_text("u2\n")
            commit(r, "unrelated")
            result = m.revalidate(r, art, b / "out", digest)
            self.assertEqual(result["status"], m.PASS_NO_RELEVANT_DRIFT)


if __name__ == "__main__":
    unittest.main()
