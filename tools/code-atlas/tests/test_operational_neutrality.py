from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from code_atlas.core.neutrality_gate import scan_code_atlas
from code_atlas.operational.runner import run_operational_atlas


def _tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(path.relative_to(root).as_posix().encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


class OperationalNeutralityTests(unittest.TestCase):
    def test_reusable_source_boundary_is_fail_closed_and_clean(self) -> None:
        code_atlas_root = Path(__file__).resolve().parents[1]
        result = scan_code_atlas(code_atlas_root)
        self.assertEqual(result["status"], "PASS_CODE_ATLAS_TOTAL_NEUTRALITY", result["findings"][:10])
        self.assertEqual(result["blockingCount"], 0)
        self.assertGreater(result["scannedFileCount"], 5)
        self.assertFalse(result["productionCertified"])

    def test_gate_blocks_machine_specific_value_in_neutral_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "CODE_ATLAS_NEUTRALITY_CONTRACT.json").write_text(json.dumps({
                "neutralRoots": ["src"], "neutralFiles": [], "adapterRoots": [], "adapterFiles": []
            }), encoding="utf-8")
            (root / "src" / "bad.py").write_text('ROOT = "C:\\\\Users\\\\developer\\\\project"\n', encoding="utf-8")
            result = scan_code_atlas(root)
            self.assertEqual(result["status"], "BLOCKED_CODE_ATLAS_NEUTRALITY_VIOLATION")
            self.assertGreater(result["blockingCount"], 0)

    def test_generic_repository_run_is_profile_driven_read_only_and_product_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "neutral-repository"
            out = base / "evidence"
            results = base / "prior-results"
            repo.mkdir()
            results.mkdir()
            (repo / "src").mkdir()
            (repo / "src" / "main.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
            profile = base / "profile.json"
            profile.write_text(json.dumps({
                "profileId": "external-neutral-trial",
                "projectName": "External Neutral Trial",
                "projectRoot": "${CODE_ATLAS_PROJECT_ROOT}",
                "outputRoot": "${CODE_ATLAS_OUTPUT_ROOT}",
                "apps": [{
                    "id": "service",
                    "label": "Service",
                    "root": "src",
                    "routes": [],
                    "kind": "service"
                }],
                "protectedGlobs": [],
                "metadata": {"trial": True}
            }), encoding="utf-8")
            before = _tree_digest(repo)
            env = {
                "CODE_ATLAS_PROFILE": str(profile),
                "CODE_ATLAS_PROJECT_ROOT": str(repo),
                "CODE_ATLAS_OUTPUT_ROOT": str(out),
                "CODE_ATLAS_RESULT_ROOT": str(results),
            }
            with mock.patch.dict(os.environ, env, clear=False):
                manifest = run_operational_atlas(str(repo), str(out), str(results))
            after = _tree_digest(repo)

            self.assertEqual(before, after)
            self.assertEqual(manifest["profileId"], "external-neutral-trial")
            self.assertFalse(manifest["productionCertified"])
            payload = json.loads((out / "operational_evidence_atlas.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["surfaceRoleMatrix"][0]["appId"], "service")
            self.assertEqual(payload["adapterSummary"]["status"], "NOT_CONFIGURED")
            self.assertEqual(payload["adapterSummary"]["decision"], "NO_IMPLICIT_PRODUCT_ADAPTER")

            text = "\n".join(
                path.read_text(encoding="utf-8", errors="replace")
                for path in out.rglob("*")
                if path.is_file() and path.suffix.lower() in {".json", ".md", ".html", ".csv"}
            ).lower()
            for forbidden in ("hitech-os", "terminal-de-venta-system", "app.hitechrts.com"):
                self.assertNotIn(forbidden, text)
            self.assertNotIn("f:\\", text)

    def test_app_roots_are_not_fixed_surface_taxonomy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            out = base / "out"
            repo.mkdir()
            (repo / "worker").mkdir()
            profile = base / "profile.json"
            profile.write_text(json.dumps({
                "profileId": "arbitrary-app-id",
                "projectName": "Arbitrary",
                "projectRoot": "${CODE_ATLAS_PROJECT_ROOT}",
                "outputRoot": "${CODE_ATLAS_OUTPUT_ROOT}",
                "apps": [{"id": "edge-worker", "label": "Edge Worker", "root": "worker", "kind": "edge"}],
                "metadata": {}
            }), encoding="utf-8")
            with mock.patch.dict(os.environ, {"CODE_ATLAS_PROFILE": str(profile)}, clear=False):
                run_operational_atlas(str(repo), str(out), str(out))
            payload = json.loads((out / "operational_evidence_atlas.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["surfaceRoleMatrix"][0]["appId"], "edge-worker")
            self.assertEqual(payload["surfaceRoleMatrix"][0]["surface"], "edge")


if __name__ == "__main__":
    unittest.main()
