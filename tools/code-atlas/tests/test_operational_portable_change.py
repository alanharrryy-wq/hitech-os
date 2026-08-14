from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from code_atlas.change_intelligence import (
    build_authority_pack,
    build_portable_bundle_manifest,
    render_change_model_markdown,
    render_verification_markdown,
    verify_change,
)
from code_atlas.change_intelligence.cli import main
from code_atlas.change_intelligence.contracts import ContractError, sha256_json


class PortableChangeTests(unittest.TestCase):
    def _pack(self):
        return build_authority_pack(
            repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
            normalized_task="change auth", allowed_scope=["src/auth"], required_evidence=["tests"],
            tool_version="1", profile_version="1", generated_at="2026-08-14T10:00:00Z",
        )

    def test_portable_bundle_rejects_traversal(self) -> None:
        with self.assertRaises(ContractError):
            build_portable_bundle_manifest(
                repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
                artifacts=[{"name": "../secret.txt", "kind": "report", "digest": sha256_json({}), "size": 1}],
                purpose="evidence",
            )

    def test_portable_bundle_has_manifest_digest(self) -> None:
        manifest = build_portable_bundle_manifest(
            repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
            artifacts=[{"name": "reports/result.json", "kind": "verification", "digest": sha256_json({}), "size": 10}],
            purpose="change verification",
        )
        self.assertTrue(manifest["manifestDigest"].startswith("sha256:"))
        self.assertFalse(manifest["sourceCodeIncluded"])

    def test_verification_markdown_is_human_readable(self) -> None:
        pack = self._pack()
        report = verify_change(
            authority_pack=pack,
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
            produced_evidence=["tests"],
        )
        text = render_verification_markdown(report)
        self.assertIn("Decision: **PASS**", text)
        self.assertIn("Authority pack", text)

    def test_change_model_renderer_rejects_unknown_schema(self) -> None:
        with self.assertRaises(ContractError):
            render_change_model_markdown({"schemaVersion": "other"})

    def test_cli_validate_pack_round_trip(self) -> None:
        pack = self._pack()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pack.json"
            path.write_text(json.dumps(pack), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                rc = main(["validate-pack", "--pack", str(path)])
            self.assertEqual(rc, 0)
            parsed = json.loads(out.getvalue())
            self.assertEqual(parsed["packId"], pack["packId"])


if __name__ == "__main__":
    unittest.main()
