from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import orchestrator  # noqa: E402
from factory.shared_bridge import (  # noqa: E402
    resolve_shared_current_run_root,
    resolve_shared_root,
    stable_copy_tree,
    write_factory_pointer,
    write_ledger_event,
    write_shared_pointer,
)
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class SharedBridgeUnitTests(unittest.TestCase):
    def test_resolve_shared_root_prefers_repo_mount(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shared_root_") as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            mounted = repo_root / "tools" / "codex" / "shared"
            mounted.mkdir(parents=True, exist_ok=True)

            override = Path(temp_dir) / "override_shared"
            override.mkdir(parents=True, exist_ok=True)

            resolved = resolve_shared_root(
                repo_root,
                shared_root_override=override.as_posix(),
            )
            self.assertEqual(mounted.resolve(strict=False), resolved)

    def test_resolve_shared_current_run_root_supports_current_and_run_mounted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shared_current_") as temp_dir:
            shared_root = Path(temp_dir) / "shared"
            current = shared_root / "CURRENT"
            for name in ("META", "WORKERS", "HEALTH"):
                (current / name).mkdir(parents=True, exist_ok=True)
            resolved = resolve_shared_current_run_root(shared_root, require_current=True)
            self.assertEqual(current.resolve(strict=False), resolved)

            run_mounted = Path(temp_dir) / "run_mounted"
            for name in ("META", "WORKERS", "HEALTH"):
                (run_mounted / name).mkdir(parents=True, exist_ok=True)
            resolved_fallback = resolve_shared_current_run_root(run_mounted, require_current=True)
            self.assertEqual(run_mounted.resolve(strict=False), resolved_fallback)

    def test_stable_copy_tree_excludes_and_hash_skip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shared_copy_") as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            destination = root / "destination"
            (source / "keep").mkdir(parents=True, exist_ok=True)
            (source / "node_modules").mkdir(parents=True, exist_ok=True)
            (source / "dist").mkdir(parents=True, exist_ok=True)

            (source / "keep" / "a.txt").write_text("alpha\n", encoding="utf-8")
            (source / "keep" / "b.txt").write_text("beta\n", encoding="utf-8")
            (source / "node_modules" / "skip.js").write_text("skip\n", encoding="utf-8")
            (source / "dist" / "skip.txt").write_text("skip\n", encoding="utf-8")

            first = stable_copy_tree(source, destination, hash_strategy="sha256", dry_run=False)
            self.assertEqual(["keep/a.txt", "keep/b.txt"], first["copied"])
            self.assertEqual([], first["unchanged"])

            second = stable_copy_tree(source, destination, hash_strategy="sha256", dry_run=False)
            self.assertEqual([], second["copied"])
            self.assertEqual(["keep/a.txt", "keep/b.txt"], second["unchanged"])
            self.assertTrue((destination / "keep" / "a.txt").exists())
            self.assertFalse((destination / "node_modules" / "skip.js").exists())
            self.assertFalse((destination / "dist" / "skip.txt").exists())

    def test_write_ledger_event_uses_stable_serialization(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shared_ledger_") as temp_dir:
            ledger = Path(temp_dir) / "BRIDGE_EVENTS.ndjson"
            payload = {"z": 1, "a": "x", "nested": {"b": 2, "a": 1}}
            write_ledger_event(ledger, payload, dry_run=False)
            line = ledger.read_text(encoding="utf-8").strip()
            self.assertEqual('{"a":"x","nested":{"a":1,"b":2},"z":1}', line)

    def test_pointer_writers_create_expected_payloads(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shared_pointer_") as temp_dir:
            root = Path(temp_dir)
            run_root = root / "runs" / "RUN_X"
            worktrees_root = root / "worktrees" / "RUN_X"
            shared_root = root / "shared"
            shared_current = shared_root / "CURRENT"
            (shared_current / "META").mkdir(parents=True, exist_ok=True)
            run_root.mkdir(parents=True, exist_ok=True)
            worktrees_root.mkdir(parents=True, exist_ok=True)

            pointer_a = write_factory_pointer(
                run_id="RUN_X",
                factory_run_root=run_root,
                factory_worktrees_root=worktrees_root,
                shared_current_run_root=shared_current,
                mode="both",
                dry_run=False,
            )
            pointer_b = write_shared_pointer(
                run_id="RUN_X",
                factory_run_root=run_root,
                shared_root=shared_root,
                shared_current_run_root=shared_current,
                mode="both",
                dry_run=False,
            )

            payload_a = json.loads(Path(pointer_a["path"]).read_text(encoding="utf-8"))
            payload_b = json.loads(Path(pointer_b["path"]).read_text(encoding="utf-8"))
            self.assertEqual("RUN_X", payload_a["run_id"])
            self.assertEqual("both", payload_a["mode"])
            self.assertEqual("RUN_X", payload_b["run_id"])
            self.assertEqual("both", payload_b["mode"])


class SharedBridgeSmokeTests(unittest.TestCase):
    def test_orchestrator_shared_mode_off_no_side_effects(self) -> None:
        with isolated_factory_env() as env:
            run_id = "shared_off_001"
            run_root = env["runs_dir"] / run_id
            run_root.mkdir(parents=True, exist_ok=True)

            consume_payload = orchestrator.run_shared_consume_hook(
                run_id=run_id,
                dry_run=False,
                env={"HITECH_SHARED_MODE": "off"},
            )
            publish_payload = orchestrator.run_shared_publish_hook(
                run_id=run_id,
                dry_run=False,
                env={"HITECH_SHARED_MODE": "off"},
            )

            self.assertEqual("PASS", consume_payload["status"])
            self.assertFalse(consume_payload["enabled"])
            self.assertEqual("PASS", publish_payload["status"])
            self.assertFalse(publish_payload["enabled"])
            self.assertFalse((run_root / "incoming_shared").exists())
            self.assertFalse((run_root / "SHARED_POINTER.json").exists())

    def test_orchestrator_shared_mode_both_smoke(self) -> None:
        with isolated_factory_env() as env:
            run_id = "shared_both_001"
            run_root = env["runs_dir"] / run_id
            (run_root / "A_worker").mkdir(parents=True, exist_ok=True)
            (run_root / "A_worker" / "STATUS.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
            (run_root / "RUN_MANIFEST.json").write_text('{"run_id":"shared_both_001"}\n', encoding="utf-8")
            (run_root / "Z_integrator").mkdir(parents=True, exist_ok=True)
            (run_root / "Z_integrator" / "FINAL_REPORT.txt").write_text("report\n", encoding="utf-8")
            (run_root / "attestations").mkdir(parents=True, exist_ok=True)
            (run_root / "attestations" / "bundles.sha256").write_text("hash bundles\n", encoding="utf-8")
            (run_root / "attestations" / "ledger.sha256").write_text("hash ledger\n", encoding="utf-8")
            (run_root / "attestations" / "report.sha256").write_text("hash report\n", encoding="utf-8")

            shared_root = env["codex_dir"] / "shared"
            shared_current = shared_root / "CURRENT"
            for name in ("META", "WORKERS", "AGGREGATE", "HEALTH", "LEDGER"):
                (shared_current / name).mkdir(parents=True, exist_ok=True)
            incoming = shared_current / "INCOMING" / "FACTORY" / run_id / "incoming_shared"
            incoming.mkdir(parents=True, exist_ok=True)
            (incoming / "seed.txt").write_text("hello from shared\n", encoding="utf-8")

            env_flags = {
                "HITECH_SHARED_MODE": "both",
                "HITECH_SHARED_REQUIRE_CURRENT": "1",
                "HITECH_SHARED_HASH_STRATEGY": "sha256",
                "HITECH_SHARED_DRYRUN": "0",
            }

            consume_payload = orchestrator.run_shared_consume_hook(
                run_id=run_id,
                dry_run=False,
                env=env_flags,
            )
            self.assertEqual("PASS", consume_payload["status"])
            self.assertTrue((run_root / "incoming_shared" / "seed.txt").exists())

            publish_payload = orchestrator.run_shared_publish_hook(
                run_id=run_id,
                dry_run=False,
                env=env_flags,
            )
            self.assertEqual("PASS", publish_payload["status"])
            self.assertTrue((shared_current / "WORKERS" / "A_worker" / "STATUS.json").exists())
            self.assertTrue((shared_current / "AGGREGATE" / "FINAL_REPORT.txt").exists())
            self.assertTrue((shared_current / "META" / "FACTORY_POINTER.json").exists())
            self.assertTrue((run_root / "SHARED_POINTER.json").exists())
            self.assertTrue((shared_current / "HEALTH" / "publish_manifest.json").exists())

            ledger_lines = (shared_current / "LEDGER" / "BRIDGE_EVENTS.ndjson").read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(ledger_lines), 2)
            self.assertTrue(any('"event_type":"CONSUME"' in line for line in ledger_lines))
            self.assertTrue(any('"event_type":"PUBLISH"' in line for line in ledger_lines))


if __name__ == "__main__":
    unittest.main()
