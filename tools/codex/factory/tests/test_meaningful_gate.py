from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import contracts, diffing  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402
from verify.meaningful_gate import (  # noqa: E402
    EMPTY_DECLARATIONS,
    EMPTY_PATCH,
    PATCH_NOT_APPLICABLE,
    PHANTOM_PATHS,
    run_meaningful_gate,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_manifest(path: Path, run_id: str) -> None:
    _write_json(
        path,
        {
            "schema_version": 1,
            "run_id": run_id,
            "kind": "factory",
            "base_ref": "HEAD",
            "workers": ["A_worker", "B_worker", "C_worker", "D_worker"],
            "integrator": "Z_integrator",
        },
    )


class MeaningfulGateTests(unittest.TestCase):
    def test_empty_artifacts_fail(self) -> None:
        run_id = "meaningful_gate_empty_20260219_000001"
        with isolated_factory_env() as env:
            contracts.scaffold_integrator_bundle(run_id)
            run_dir = env["runs_dir"] / run_id
            z_dir = run_dir / "Z_integrator"
            _write_manifest(run_dir / "RUN_MANIFEST.json", run_id)

            _write_json(
                z_dir / "FILES_CHANGED.json",
                {
                    "schema_version": 1,
                    "run_id": run_id,
                    "owner": "Z_integrator",
                    "changes": [],
                    "noop": False,
                    "noop_reason": "",
                    "noop_ack": "",
                },
            )
            (z_dir / "DIFF.patch").write_text("", encoding="utf-8", newline="\n")

            payload = run_meaningful_gate(run_id, repo_root=env["repo_root"], runs_dir=env["runs_dir"], write_outputs=True)
            self.assertEqual("FAIL", payload["verdict"])
            self.assertIn(EMPTY_DECLARATIONS, payload["fail_modes"])
            self.assertIn(EMPTY_PATCH, payload["fail_modes"])
            self.assertTrue((run_dir / "VERIFY_MEANINGFUL_GATE.json").exists())
            self.assertTrue((run_dir / "VERIFY_MEANINGFUL_GATE.md").exists())

    def test_phantom_paths_fail(self) -> None:
        run_id = "meaningful_gate_phantom_20260219_000002"
        with isolated_factory_env() as env:
            contracts.scaffold_integrator_bundle(run_id)
            run_dir = env["runs_dir"] / run_id
            z_dir = run_dir / "Z_integrator"
            _write_manifest(run_dir / "RUN_MANIFEST.json", run_id)

            _write_json(
                z_dir / "FILES_CHANGED.json",
                {
                    "schema_version": 1,
                    "run_id": run_id,
                    "owner": "Z_integrator",
                    "changes": [
                        {
                            "path": "apps/phantom/not_there.txt",
                            "change_type": "modified",
                            "reason": "phantom fixture",
                            "sha256": "abc123",
                        }
                    ],
                    "noop": False,
                    "noop_reason": "",
                    "noop_ack": "",
                },
            )
            (z_dir / "DIFF.patch").write_text(
                (
                    "diff --git a/apps/phantom/not_there.txt b/apps/phantom/not_there.txt\n"
                    "--- a/apps/phantom/not_there.txt\n"
                    "+++ b/apps/phantom/not_there.txt\n"
                    "@@ -1 +1 @@\n"
                    "-old\n"
                    "+new\n"
                ),
                encoding="utf-8",
                newline="\n",
            )

            payload = run_meaningful_gate(run_id, repo_root=env["repo_root"], runs_dir=env["runs_dir"], write_outputs=True)
            self.assertEqual("FAIL", payload["verdict"])
            self.assertIn(PHANTOM_PATHS, payload["fail_modes"])

    def test_patch_not_applicable_fails(self) -> None:
        run_id = "meaningful_gate_patch_20260219_000003"
        rel_path = "apps/meaningful/patch_not_applicable.txt"
        with isolated_factory_env() as env:
            contracts.scaffold_integrator_bundle(run_id)
            run_dir = env["runs_dir"] / run_id
            z_dir = run_dir / "Z_integrator"
            _write_manifest(run_dir / "RUN_MANIFEST.json", run_id)

            target = env["repo_root"] / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("line-1\n", encoding="utf-8", newline="\n")

            _write_json(
                z_dir / "FILES_CHANGED.json",
                {
                    "schema_version": 1,
                    "run_id": run_id,
                    "owner": "Z_integrator",
                    "changes": [
                        {
                            "path": rel_path,
                            "change_type": "modified",
                            "reason": "invalid patch fixture",
                            "sha256": "def456",
                        }
                    ],
                    "noop": False,
                    "noop_reason": "",
                    "noop_ack": "",
                },
            )
            (z_dir / "DIFF.patch").write_text(
                (
                    f"diff --git a/{rel_path} b/{rel_path}\n"
                    f"--- a/{rel_path}\n"
                    f"+++ b/{rel_path}\n"
                    "@@ -99,1 +99,1 @@\n"
                    "-missing-old-line\n"
                    "+missing-new-line\n"
                ),
                encoding="utf-8",
                newline="\n",
            )

            payload = run_meaningful_gate(run_id, repo_root=env["repo_root"], runs_dir=env["runs_dir"], write_outputs=True)
            self.assertEqual("FAIL", payload["verdict"])
            self.assertIn(PATCH_NOT_APPLICABLE, payload["fail_modes"])

    def test_real_sentinel_mutation_passes_and_is_deterministic(self) -> None:
        run_id = "meaningful_gate_sentinel_20260219_000004"
        rel_path = "packages/tooling/_smoke/MEANINGFUL_GATE_SENTINEL_20260219.txt"
        with isolated_factory_env() as env:
            contracts.scaffold_integrator_bundle(run_id)
            run_dir = env["runs_dir"] / run_id
            z_dir = run_dir / "Z_integrator"
            _write_manifest(run_dir / "RUN_MANIFEST.json", run_id)

            target = env["repo_root"] / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"run_id={run_id}\nsource=meaningful_gate_test\n", encoding="utf-8", newline="\n")
            patch_text = diffing.unified_patch_for_paths([rel_path])
            self.assertTrue(len(patch_text.strip()) > 0)

            _write_json(
                z_dir / "FILES_CHANGED.json",
                {
                    "schema_version": 1,
                    "run_id": run_id,
                    "owner": "Z_integrator",
                    "changes": [
                        {
                            "path": rel_path,
                            "change_type": "added",
                            "reason": "sentinel mutation fixture",
                            "sha256": "012345",
                        }
                    ],
                    "noop": False,
                    "noop_reason": "",
                    "noop_ack": "",
                },
            )
            (z_dir / "DIFF.patch").write_text(patch_text, encoding="utf-8", newline="\n")

            first = run_meaningful_gate(run_id, repo_root=env["repo_root"], runs_dir=env["runs_dir"], write_outputs=True)
            second = run_meaningful_gate(run_id, repo_root=env["repo_root"], runs_dir=env["runs_dir"], write_outputs=True)

            self.assertEqual("PASS", first["verdict"])
            self.assertEqual("PASS", second["verdict"])
            self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
