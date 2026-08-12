#!/usr/bin/env python3
from __future__ import annotations

import json
import multiprocessing as mp
import shutil
import subprocess
import sys
import time
import unittest
import uuid
import zipfile
from pathlib import Path

CODE_ATLAS_ROOT = Path(__file__).resolve().parents[1]
SRC = CODE_ATLAS_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from code_atlas.motors.prisma_automesh_runtime import GlobalWorkerBudget
from code_atlas.motors.smart_allmesh_parallel import compare_snapshots, repo_snapshot, worker_caps


def _budget_probe(
    budget_root: str,
    run_id: str,
    index: int,
    slots: int,
    start_event: object,
    active: object,
    peak: object,
    lock: object,
) -> None:
    budget = GlobalWorkerBudget(Path(budget_root), slots=slots, run_id=run_id)
    start_event.wait(10)
    with budget.lease(f"probe-{index}"):
        with lock:
            active.value += 1
            peak.value = max(peak.value, active.value)
        time.sleep(0.12)
        with lock:
            active.value -= 1
    budget.close()


class SmartAllMeshParallelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_root = Path.cwd() / f".automesh_parallel_test_{uuid.uuid4().hex[:10]}"
        self.test_root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_root, ignore_errors=True)

    def test_worker_caps_never_exceed_global_contract(self) -> None:
        for task_count in (2, 4, 6, 18, 30):
            for parallel in (1, 2, 4, 7, 18, 30):
                caps = worker_caps(task_count, parallel, 18)
                self.assertLessEqual(sum(caps), 18)
                self.assertTrue(all(1 <= value <= 18 for value in caps))

    def test_global_worker_budget_is_cross_process(self) -> None:
        ctx = mp.get_context("spawn")
        budget_root = self.test_root / "budget"
        slots = 3
        process_count = 10
        start_event = ctx.Event()
        active = ctx.Value("i", 0)
        peak = ctx.Value("i", 0)
        lock = ctx.Lock()
        processes = [
            ctx.Process(
                target=_budget_probe,
                args=(
                    str(budget_root),
                    "parallel-cert-budget",
                    index,
                    slots,
                    start_event,
                    active,
                    peak,
                    lock,
                ),
            )
            for index in range(process_count)
        ]
        for process in processes:
            process.start()
        start_event.set()
        for process in processes:
            process.join(30)
            self.assertEqual(process.exitcode, 0)

        self.assertGreaterEqual(peak.value, 2)
        self.assertLessEqual(peak.value, slots)
        self.assertEqual(active.value, 0)
        self.assertEqual(list(budget_root.glob("slot_*.lock")), [])
        self.assertEqual(list(budget_root.glob("active_*.json")), [])

    def _git(self, repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=str(repo),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def _make_fixture_repo(self) -> Path:
        repo = self.test_root / "fixture-repo"
        (repo / "apps/terminal-de-venta-system/docs/ops").mkdir(parents=True, exist_ok=True)
        pos = repo / "apps/terminal-de-venta-system/products/tablet/app/components/pos"
        pos.mkdir(parents=True, exist_ok=True)
        (repo / "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md").write_text(
            "# Fixture manual\nTablet POS exact target authority.\n",
            encoding="utf-8",
        )
        (pos / "pos.module.css").write_text(
            ".payButton { background: rgba(20, 30, 40, .5); }\n"
            ".cartPanel { backdrop-filter: blur(12px); }\n",
            encoding="utf-8",
        )
        (pos / "pos-live-binding.tsx").write_text(
            "export function PosFixture(){ return <><button className=\"payButton\">Cobrar</button><div className=\"cartPanel\">Cart</div></>; }\n",
            encoding="utf-8",
        )
        self._git(repo, "init")
        self._git(repo, "config", "user.email", "automesh-cert@example.invalid")
        self._git(repo, "config", "user.name", "AutoMesh Cert")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-m", "fixture")
        return repo

    def test_repo_snapshot_detects_drift(self) -> None:
        repo = self._make_fixture_repo()
        before = repo_snapshot(repo)
        css = repo / "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
        css.write_text(css.read_text(encoding="utf-8") + ".drift { opacity: .8; }\n", encoding="utf-8")
        after = repo_snapshot(repo)
        comparison = compare_snapshots(before, after)
        self.assertFalse(comparison["stable"])
        self.assertGreaterEqual(comparison["changed_count"], 1)

    def test_two_real_automesh_tasks_run_in_parallel_and_publish_one_zip(self) -> None:
        repo = self._make_fixture_repo()
        out_root = self.test_root / "out"
        budget_root = self.test_root / "shared-budget"
        parallel_script = CODE_ATLAS_ROOT / "src/code_atlas/motors/smart_allmesh_parallel.py"
        command = [
            sys.executable,
            str(parallel_script),
            "--repo", str(repo),
            "--out-root", str(out_root),
            "--budget-root", str(budget_root),
            "--task", "Tablet POS pay button exact owner and layer",
            "--task", "Tablet POS cart panel exact owner and layer",
            "--parallel", "2",
            "--workers", "2",
            "--shards", "4",
            "--max-files", "30",
            "--max-mb", "10",
        ]
        proc = subprocess.run(
            command,
            cwd=str(CODE_ATLAS_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
            shell=False,
        )
        if proc.returncode != 0:
            self.fail(f"parallel supervisor failed ({proc.returncode}):\n{proc.stdout}")

        marker = next(
            (line.split("=", 1)[1].strip() for line in proc.stdout.splitlines() if line.startswith("FINAL_RESULT_ZIP=")),
            "",
        )
        self.assertTrue(marker, proc.stdout)
        final_zip = Path(marker)
        self.assertTrue(final_zip.exists())
        self.assertEqual(len(list(out_root.glob("*.zip"))), 1)

        with zipfile.ZipFile(final_zip, "r") as archive:
            self.assertIsNone(archive.testzip())
            certification = json.loads(archive.read("PARALLEL_CERTIFICATION.json").decode("utf-8"))
            drift = json.loads(archive.read("REPO_DRIFT_REPORT.json").decode("utf-8"))
            names = set(archive.namelist())

        self.assertEqual(certification["status"], "PASS")
        self.assertEqual(
            certification["certification"],
            "PASS_AUTOMESH_MULTI_TASK_CROSS_PROCESS_PARALLEL_SAFE",
        )
        self.assertEqual(certification["task_count"], 2)
        self.assertEqual(len(certification["children"]), 2)
        self.assertTrue(certification["unique_child_run_ids"])
        self.assertLessEqual(certification["wave_worker_sum_cap"], 18)
        self.assertTrue(drift["stable"])
        self.assertIn("tasks/task-1/authority_mesh/RUN_MANIFEST.json", names)
        self.assertIn("tasks/task-2/authority_mesh/RUN_MANIFEST.json", names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
