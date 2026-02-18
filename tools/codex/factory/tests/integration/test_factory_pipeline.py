from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import cli, common, contracts, ledger  # noqa: E402
from factory.integrator import integrate_run  # noqa: E402
from factory.tests.test_support import isolated_factory_env, make_change, write_worker_bundle  # noqa: E402


class FactoryPipelineIntegrationTests(unittest.TestCase):
    def _seed_minimal_bundles(self, run_id: str) -> None:
        write_worker_bundle(
            run_id=run_id,
            worker="A_worker",
            changes=[make_change("apps/min/a.ts", sha256="a1")],
            summary="# A summary\n\n- done\n",
        )
        write_worker_bundle(
            run_id=run_id,
            worker="B_worker",
            changes=[make_change("apps/min/b.ts", sha256="b1")],
            summary="# B summary\n\n- done\n",
        )
        write_worker_bundle(
            run_id=run_id,
            worker="C_worker",
            changes=[make_change("tools/min/c.py", sha256="c1")],
            summary="# C summary\n\n- done\n",
        )
        write_worker_bundle(
            run_id=run_id,
            worker="D_worker",
            changes=[make_change("docs/min/d.md", sha256="d1")],
            summary="# D summary\n\n- done\n",
        )

    def test_minimal_integration_run_passes_and_writes_artifacts(self) -> None:
        run_id = "integration_minimal_20260218_000001"
        with isolated_factory_env() as env:
            self._seed_minimal_bundles(run_id)
            contracts.scaffold_integrator_bundle(run_id)

            result = integrate_run(run_id, workers=list(common.WORKERS))
            self.assertEqual("PASS", result["status"])

            z_dir = Path(result["z_dir"])
            self.assertTrue((z_dir / "FINAL_REPORT.txt").exists())
            self.assertTrue((z_dir / "STATUS.json").exists())
            self.assertTrue((z_dir / "FILES_CHANGED.json").exists())
            self.assertTrue((z_dir / "DIFF.patch").exists())
            self.assertTrue((z_dir / "MERGE_PLAN.md").exists())
            self.assertTrue((z_dir / "LOGS" / "INDEX.json").exists())

            report = (z_dir / "FINAL_REPORT.txt").read_text(encoding="utf-8")
            self.assertIn("Worker bundles processed: 4", report)
            self.assertIn("Final status: PASS", report)

            status_payload = json.loads((z_dir / "STATUS.json").read_text(encoding="utf-8"))
            self.assertEqual("PASS", status_payload["status"])
            self.assertGreaterEqual(len(status_payload["required_checks"]), 4)

            # Ledger is append-only JSONL and should contain report events.
            entries = ledger.read_events(path=env["runs_dir"] / "factory_ledger.jsonl")
            event_types = [entry["event_type"] for entry in entries]
            self.assertIn("REPORT_WRITTEN", event_types)

    def test_collision_blocks_and_lists_conflicts(self) -> None:
        run_id = "integration_collision_20260218_000002"
        with isolated_factory_env():
            write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change("apps/collision/shared.ts", sha256="a")])
            write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/collision/shared.ts", sha256="b")])
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("docs/collision/c.md", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("tools/collision/d.py", sha256="d")])

            result = integrate_run(run_id, workers=list(common.WORKERS))
            self.assertEqual("BLOCKED", result["status"])

            report = (Path(result["z_dir"]) / "FINAL_REPORT.txt").read_text(encoding="utf-8")
            self.assertIn("overlap: apps/collision/shared.ts", report)
            self.assertIn("Final status: BLOCKED", report)

    def test_scope_violation_blocks_and_lists_violations(self) -> None:
        run_id = "integration_scope_20260218_000003"
        with isolated_factory_env():
            write_worker_bundle(
                run_id=run_id,
                worker="A_worker",
                changes=[make_change("services/private/secret.py", sha256="a")],
                allowed_globs=["apps/**"],
                blocked_globs=["services/**"],
            )
            write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/scope/b.ts", sha256="b")])
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("tools/scope/c.py", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("docs/scope/d.md", sha256="d")])

            result = integrate_run(run_id, workers=list(common.WORKERS))
            self.assertEqual("BLOCKED", result["status"])

            report = (Path(result["z_dir"]) / "FINAL_REPORT.txt").read_text(encoding="utf-8")
            self.assertIn("scope: A_worker services/private/secret.py", report)
            self.assertIn("Final status: BLOCKED", report)

    def test_z_no_write_policy_blocks_on_external_write_attempt(self) -> None:
        run_id = "integration_policy_20260218_000004"
        with isolated_factory_env() as env:
            self._seed_minimal_bundles(run_id)
            contracts.scaffold_integrator_bundle(run_id)
            outside_target = env["repo_root"] / "outside.txt"

            result = integrate_run(
                run_id,
                workers=list(common.WORKERS),
                extra_writes=[{"path": outside_target.as_posix(), "text": "forbidden"}],
            )
            self.assertEqual("BLOCKED", result["status"])

            report = (Path(result["z_dir"]) / "FINAL_REPORT.txt").read_text(encoding="utf-8")
            self.assertIn("policy: Z no-write policy violation", report)
            self.assertFalse(outside_target.exists())

    def test_oneshot_populates_ledger_and_report(self) -> None:
        run_id = "integration_oneshot_20260218_000005"
        with isolated_factory_env() as env:
            with redirect_stdout(io.StringIO()):
                rc = cli.main(["oneshot", "--run-id", run_id, "--base-ref", "HEAD", "--dry-run"])
            self.assertEqual(0, rc)

            z_report = env["runs_dir"] / run_id / "Z_integrator" / "FINAL_REPORT.txt"
            self.assertTrue(z_report.exists())
            report = z_report.read_text(encoding="utf-8")
            self.assertIn("Worker bundles processed: 4", report)

            events = ledger.read_events(path=env["runs_dir"] / "factory_ledger.jsonl")
            event_types = [entry["event_type"] for entry in events]
            self.assertIn("RUN_START", event_types)
            self.assertIn("WORKTREE_CREATE", event_types)
            self.assertIn("ONESHOT_SUMMARY", event_types)
            self.assertIn("REPORT_WRITTEN", event_types)

    def test_oneshot_stops_when_preflight_blocked(self) -> None:
        run_id = "integration_oneshot_20260218_000006"
        with isolated_factory_env() as env:
            # Remove required file to force preflight BLOCKED.
            (env["codex_dir"] / "validation.json").unlink()
            with redirect_stdout(io.StringIO()):
                rc = cli.main(["oneshot", "--run-id", run_id, "--base-ref", "HEAD", "--dry-run"])
            self.assertNotEqual(0, rc)

            run_dir = env["runs_dir"] / run_id
            self.assertTrue(run_dir.exists())
            self.assertFalse((run_dir / "RUN_MANIFEST.json").exists())
            self.assertFalse((run_dir / "Z_integrator" / "FINAL_REPORT.txt").exists())


if __name__ == "__main__":
    unittest.main()
