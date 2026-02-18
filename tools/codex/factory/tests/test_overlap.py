from __future__ import annotations

import os
import random
import sys
import time
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import common  # noqa: E402
from factory.overlap import detect_file_overlaps, detect_scope_violations  # noqa: E402
from factory.tests.test_support import isolated_factory_env, make_change, write_worker_bundle  # noqa: E402


class OverlapAndScopeTests(unittest.TestCase):
    def test_collision_blocks_when_shared_not_allowed(self) -> None:
        run_id = "collision_20260218_000001"
        with isolated_factory_env():
            write_worker_bundle(
                run_id=run_id,
                worker="A_worker",
                changes=[make_change("apps/demo/shared.ts", sha256="a")],
                allow_shared_paths=[],
            )
            write_worker_bundle(
                run_id=run_id,
                worker="B_worker",
                changes=[make_change("apps/demo/shared.ts", sha256="b")],
                allow_shared_paths=[],
            )
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("docs/demo/c.md", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("tools/demo/d.py", sha256="d")])

            payload = detect_file_overlaps(run_id, workers=list(common.WORKERS))
            self.assertEqual("BLOCKED", payload["status"])
            self.assertEqual(1, payload["blocked"])
            self.assertEqual("apps/demo/shared.ts", payload["overlaps"][0]["path"])
            self.assertEqual(["A_worker", "B_worker"], payload["overlaps"][0]["workers"])

    def test_collision_warns_when_shared_allowed_by_all(self) -> None:
        run_id = "collision_20260218_000002"
        with isolated_factory_env():
            shared_path = "apps/demo/shared_allowed.ts"
            write_worker_bundle(
                run_id=run_id,
                worker="A_worker",
                changes=[make_change(shared_path, sha256="a")],
                allow_shared_paths=[shared_path],
            )
            write_worker_bundle(
                run_id=run_id,
                worker="B_worker",
                changes=[make_change(shared_path, sha256="b")],
                allow_shared_paths=[shared_path],
            )
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("docs/demo/c.md", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("tools/demo/d.py", sha256="d")])

            payload = detect_file_overlaps(run_id, workers=list(common.WORKERS), strict_mode=False)
            self.assertEqual("PASS", payload["status"])
            self.assertEqual(0, payload["blocked"])
            self.assertEqual(1, len(payload["overlaps"]))
            self.assertEqual("WARN", payload["overlaps"][0]["status"])

    def test_scope_violation_is_blocked(self) -> None:
        run_id = "scope_20260218_000003"
        with isolated_factory_env():
            write_worker_bundle(
                run_id=run_id,
                worker="A_worker",
                changes=[make_change("services/api/private.py", sha256="a")],
                allowed_globs=["apps/**"],
                blocked_globs=["services/**"],
            )
            write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/demo/b.ts", sha256="b")])
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("docs/demo/c.md", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("tools/demo/d.py", sha256="d")])

            payload = detect_scope_violations(run_id, workers=list(common.WORKERS))
            self.assertEqual("BLOCKED", payload["status"])
            self.assertGreaterEqual(payload["blocked"], 1)
            paths = [entry["path"] for entry in payload["violations"]]
            self.assertIn("services/api/private.py", paths)

    def test_conflict_listing_is_stably_sorted(self) -> None:
        run_id = "stable_order_20260218_000004"
        with isolated_factory_env():
            write_worker_bundle(
                run_id=run_id,
                worker="A_worker",
                changes=[
                    make_change("apps/demo/z_last.ts", sha256="1"),
                    make_change("apps/demo/a_first.ts", sha256="2"),
                ],
            )
            write_worker_bundle(
                run_id=run_id,
                worker="B_worker",
                changes=[
                    make_change("apps/demo/a_first.ts", sha256="3"),
                    make_change("apps/demo/z_last.ts", sha256="4"),
                ],
            )
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("docs/demo/c.md", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("tools/demo/d.py", sha256="d")])

            payload = detect_file_overlaps(run_id, workers=list(common.WORKERS))
            ordered_paths = [entry["path"] for entry in payload["overlaps"]]
            self.assertEqual(["apps/demo/a_first.ts", "apps/demo/z_last.ts"], ordered_paths)

    def test_hidden_overlap_detected_from_patch_only(self) -> None:
        run_id = "hidden_overlap_20260218_000006"
        with isolated_factory_env():
            root_a = write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change("apps/demo/a.ts", sha256="a")])
            root_b = write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/demo/b.ts", sha256="b")])
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("tools/demo/c.py", sha256="c")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("docs/demo/d.md", sha256="d")])

            # Add hidden overlap path in DIFF.patch that was not declared in FILES_CHANGED.
            (root_a / "DIFF.patch").write_text(
                "diff --git a/apps/shared/secret.ts b/apps/shared/secret.ts\n--- a/apps/shared/secret.ts\n+++ b/apps/shared/secret.ts\n",
                encoding="utf-8",
            )
            (root_b / "DIFF.patch").write_text(
                "diff --git a/apps/shared/secret.ts b/apps/shared/secret.ts\n--- a/apps/shared/secret.ts\n+++ b/apps/shared/secret.ts\n",
                encoding="utf-8",
            )

            payload = detect_file_overlaps(run_id, workers=list(common.WORKERS), strict_mode=True)
            self.assertEqual("BLOCKED", payload["status"])
            self.assertGreaterEqual(len(payload["hidden_overlaps"]), 2)
            hidden_paths = sorted({entry["path"] for entry in payload["hidden_overlaps"]})
            self.assertEqual(["apps/shared/secret.ts"], hidden_paths)

    def test_identical_patch_exception_flag(self) -> None:
        run_id = "identical_patch_20260218_000007"
        with isolated_factory_env():
            root_a = write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change("apps/shared/x.ts", sha256="1")])
            root_b = write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/shared/x.ts", sha256="2")])
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("tools/c.py", sha256="3")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("docs/d.md", sha256="4")])

            patch_text = (
                "diff --git a/apps/shared/x.ts b/apps/shared/x.ts\n"
                "--- a/apps/shared/x.ts\n"
                "+++ b/apps/shared/x.ts\n"
                "@@ -1 +1 @@\n+line\n"
            )
            (root_a / "DIFF.patch").write_text(patch_text, encoding="utf-8")
            (root_b / "DIFF.patch").write_text(patch_text, encoding="utf-8")

            strict_payload = detect_file_overlaps(
                run_id,
                workers=list(common.WORKERS),
                strict_mode=True,
                allow_identical_patch_overlap=False,
            )
            self.assertEqual("BLOCKED", strict_payload["status"])

            relaxed_payload = detect_file_overlaps(
                run_id,
                workers=list(common.WORKERS),
                strict_mode=True,
                allow_identical_patch_overlap=True,
            )
            self.assertEqual("PASS", relaxed_payload["status"])
            self.assertEqual(0, relaxed_payload["blocked"])
            self.assertEqual("WARN", relaxed_payload["overlaps"][0]["status"])

    def test_invalid_path_in_files_changed_is_blocked(self) -> None:
        run_id = "invalid_path_20260218_000008"
        with isolated_factory_env():
            write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change(r"..\..\evil.ts", sha256="1")])
            write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/demo/b.ts", sha256="2")])
            write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("tools/demo/c.py", sha256="3")])
            write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("docs/demo/d.md", sha256="4")])
            payload = detect_file_overlaps(run_id, workers=list(common.WORKERS))
            self.assertEqual("BLOCKED", payload["status"])
            self.assertGreaterEqual(len(payload["invalid_paths"]), 1)

    def test_property_order_independence_with_seeded_inputs(self) -> None:
        seeds = [7, 11, 23, 29, 31]
        for seed in seeds:
            run_id = f"property_{seed:02d}"
            rng = random.Random(seed)
            with isolated_factory_env():
                all_paths = [f"apps/demo/file_{idx:03d}.ts" for idx in range(40)]
                rng.shuffle(all_paths)

                # Force deterministic collisions on a subset.
                a_paths = all_paths[:20]
                b_paths = all_paths[10:30]
                c_paths = all_paths[30:35]
                d_paths = all_paths[35:40]

                write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change(path, sha256="a") for path in a_paths])
                write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change(path, sha256="b") for path in b_paths])
                write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change(path, sha256="c") for path in c_paths])
                write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change(path, sha256="d") for path in d_paths])

                first = detect_file_overlaps(run_id, workers=["A_worker", "B_worker", "C_worker", "D_worker"])
                second = detect_file_overlaps(run_id, workers=["D_worker", "C_worker", "B_worker", "A_worker"])

                self.assertEqual(first["status"], second["status"])
                self.assertEqual(first["blocked"], second["blocked"])
                self.assertEqual(first["overlaps"], second["overlaps"])

    def test_stress_lite_10k_paths_per_worker(self) -> None:
        if os.getenv("FACTORY_SLOW_TESTS", "").strip() not in {"1", "true", "TRUE"}:
            self.skipTest("slow tests skipped by HITECH_FACTORY_SKIP_SLOW")

        run_id = "stress_20260218_000005"
        local_default = 2.0
        ci_default = 10.0
        bound_default = ci_default if os.getenv("CI") else local_default
        max_seconds = float(os.getenv("HITECH_FACTORY_STRESS_MAX_SECONDS", str(bound_default)))

        with isolated_factory_env():
            total = 10_000
            overlap_size = 500
            common_paths = [f"apps/stress/shared_{idx:05d}.ts" for idx in range(overlap_size)]
            a_unique = [f"apps/stress/a_{idx:05d}.ts" for idx in range(total - overlap_size)]
            b_unique = [f"apps/stress/b_{idx:05d}.ts" for idx in range(total - overlap_size)]
            c_unique = [f"apps/stress/c_{idx:05d}.ts" for idx in range(total - overlap_size)]
            d_unique = [f"apps/stress/d_{idx:05d}.ts" for idx in range(total - overlap_size)]

            write_worker_bundle(
                run_id=run_id,
                worker="A_worker",
                changes=[make_change(path, sha256="a") for path in (common_paths + a_unique)],
            )
            write_worker_bundle(
                run_id=run_id,
                worker="B_worker",
                changes=[make_change(path, sha256="b") for path in (common_paths + b_unique)],
            )
            write_worker_bundle(
                run_id=run_id,
                worker="C_worker",
                changes=[make_change(path, sha256="c") for path in c_unique],
            )
            write_worker_bundle(
                run_id=run_id,
                worker="D_worker",
                changes=[make_change(path, sha256="d") for path in d_unique],
            )

            start = time.perf_counter()
            overlaps = detect_file_overlaps(run_id, workers=list(common.WORKERS))
            elapsed = time.perf_counter() - start

            self.assertEqual("BLOCKED", overlaps["status"])
            self.assertEqual(overlap_size, overlaps["blocked"])
            self.assertLessEqual(elapsed, max_seconds)


if __name__ == "__main__":
    unittest.main()
