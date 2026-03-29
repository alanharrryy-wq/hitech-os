import tempfile
import unittest
from pathlib import Path

from forge_commons import ForgeCommonsBootstrap
from forge_kernel import HostContribution, KernelBootstrap, RuntimeState
from repo_analyzer import RepoAnalyzerRuntime, RepoAnalyzerState


class RepoAnalyzerRuntimeTests(unittest.TestCase):
    def test_analyze_repository_generates_summary_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("hello\nworld\n", encoding="utf-8")
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")

            kernel = KernelBootstrap.start(kernel_version="0.1.0")
            commons = ForgeCommonsBootstrap.start(contracts=kernel.contracts)
            runtime = RepoAnalyzerRuntime(history_runs=commons.history_runs)
            runtime.prepare(str(root))
            runtime.activate()

            summary = runtime.analyze_repository(
                actor="test.repo_analyzer",
                correlation_id="ra-001",
            )
            self.assertGreaterEqual(summary.total_files, 2)
            self.assertGreaterEqual(summary.total_lines, 3)
            self.assertEqual(len(commons.history_runs.all_runs()), 1)
            commons.dispose()

    def test_search_and_preview(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "notes.txt"
            target.write_text("alpha\nneedle here\nomega\n", encoding="utf-8")
            runtime = RepoAnalyzerRuntime()
            runtime.prepare(str(root))
            runtime.activate()
            matches = runtime.search("needle", limit=10)
            self.assertEqual(len(matches), 1)
            self.assertIn("needle", matches[0].line_text)
            preview = runtime.preview_file(str(target), max_lines=2)
            self.assertEqual(preview, ["alpha", "needle here"])

    def test_host_contribution_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("line 1\nline 2\n", encoding="utf-8")

            kernel = KernelBootstrap.start(kernel_version="0.1.0")
            kernel.lifecycle.register_runtime("product.repo_analyzer")
            kernel.lifecycle.transition(
                "product.repo_analyzer",
                RuntimeState.PREPARED,
                "prepared",
            )
            kernel.lifecycle.transition(
                "product.repo_analyzer",
                RuntimeState.ACTIVE,
                "active",
            )

            runtime = RepoAnalyzerRuntime()
            runtime.prepare(str(root))
            runtime.activate()
            contribution = HostContribution(
                contribution_id=runtime.contribution_id,
                slot_id=runtime.slot_id,
                product_id=runtime.product_id,
                surface_kind=runtime.surface_kind,
                metadata={"product": runtime.product_id},
                actions=runtime.contribution_actions(),
            )
            kernel.host_shell.register_contribution(
                contribution=contribution,
                actor="test.repo_analyzer",
                correlation_id="ra-host-001",
            )
            kernel.host_shell.set_visible(runtime.slot_id, True)
            result = kernel.host_shell.invoke_action(
                contribution_id=runtime.contribution_id,
                action_id="refresh_summary",
                actor="test.repo_analyzer",
                correlation_id="ra-host-002",
                timeout_seconds=1.0,
            )
            self.assertEqual(result.status, "completed")
            payload = result.value
            self.assertIsInstance(payload, dict)
            self.assertGreaterEqual(payload["total_files"], 1)
            kernel.host_shell.dispose(
                actor="test.repo_analyzer",
                correlation_id="ra-host-003",
            )
            kernel.lifecycle.transition(
                "product.repo_analyzer",
                RuntimeState.SUSPENDED,
                "suspended",
            )
            runtime.suspend()
            kernel.lifecycle.transition(
                "product.repo_analyzer",
                RuntimeState.DISPOSING,
                "disposing",
            )
            kernel.lifecycle.transition(
                "product.repo_analyzer",
                RuntimeState.DISPOSED,
                "disposed",
            )
            self.assertEqual(runtime.dispose(), RepoAnalyzerState.DISPOSED)


if __name__ == "__main__":
    unittest.main()
