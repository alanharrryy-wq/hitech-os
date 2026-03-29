import sys
import tempfile
import unittest
from pathlib import Path

from cloudflare_guardian import CloudflareGuardianRuntime, ZoneSnapshot
from forge_commons import ForgeCommonsBootstrap
from forge_kernel import KernelBootstrap, RuntimeState
from orchestrator_bridge import OrchestratorBridgeRuntime, WorkflowStep
from repo_analyzer import RepoAnalyzerRuntime


class FullRuntimeShutdownTests(unittest.TestCase):
    def test_ordered_shutdown_across_kernel_commons_and_products(self) -> None:
        kernel = KernelBootstrap.start(kernel_version="0.1.0")
        commons = ForgeCommonsBootstrap.start(contracts=kernel.contracts)

        kernel.lifecycle.register_runtime("kernel.session")
        kernel.lifecycle.transition("kernel.session", RuntimeState.PREPARED, "prepared")
        kernel.lifecycle.transition("kernel.session", RuntimeState.ACTIVE, "active")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "file.txt").write_text("line one\nline two\n", encoding="utf-8")

            repo_runtime_id = "product.repo_analyzer"
            kernel.lifecycle.register_runtime(repo_runtime_id)
            kernel.lifecycle.transition(repo_runtime_id, RuntimeState.PREPARED, "prepared")
            kernel.lifecycle.transition(repo_runtime_id, RuntimeState.ACTIVE, "active")
            repo = RepoAnalyzerRuntime(history_runs=commons.history_runs)
            repo.prepare(str(root))
            repo.activate()
            repo.analyze_repository(actor="shutdown-test", correlation_id="sd-001")

            cloud_runtime_id = "product.cloudflare_guardian"
            kernel.lifecycle.register_runtime(cloud_runtime_id)
            kernel.lifecycle.transition(cloud_runtime_id, RuntimeState.PREPARED, "prepared")
            kernel.lifecycle.transition(cloud_runtime_id, RuntimeState.ACTIVE, "active")
            cloud = CloudflareGuardianRuntime(history_runs=commons.history_runs)
            cloud.prepare()
            cloud.activate()
            cloud.ingest_snapshots(
                [
                    ZoneSnapshot(
                        zone_id="zone-1",
                        status="ok",
                        latency_ms=120,
                        error_rate=0.001,
                        checked_at_utc="2026-03-29T12:00:00Z",
                    )
                ]
            )
            cloud.evaluate_health(actor="shutdown-test", correlation_id="sd-002")

            orchestrator_runtime_id = "product.orchestrator_bridge"
            kernel.lifecycle.register_runtime(orchestrator_runtime_id)
            kernel.lifecycle.transition(orchestrator_runtime_id, RuntimeState.PREPARED, "prepared")
            kernel.lifecycle.transition(orchestrator_runtime_id, RuntimeState.ACTIVE, "active")
            orchestrator = OrchestratorBridgeRuntime(
                process_runner=commons.process_execution,
                history_runs=commons.history_runs,
            )
            orchestrator.prepare()
            orchestrator.activate()
            orchestrator.register_workflow(
                workflow_id="wf.shutdown",
                steps=[
                    WorkflowStep(
                        step_id="step-1",
                        command=(sys.executable, "-c", "print('shutdown')"),
                        timeout_seconds=5.0,
                    )
                ],
            )
            orchestrator.run_workflow(
                workflow_id="wf.shutdown",
                actor="shutdown-test",
                correlation_id="sd-003",
            )

            for runtime_id, runtime in (
                (repo_runtime_id, repo),
                (cloud_runtime_id, cloud),
                (orchestrator_runtime_id, orchestrator),
            ):
                kernel.lifecycle.transition(runtime_id, RuntimeState.SUSPENDED, "suspended")
                runtime.suspend()
                kernel.lifecycle.transition(runtime_id, RuntimeState.DISPOSING, "disposing")
                kernel.lifecycle.transition(runtime_id, RuntimeState.DISPOSED, "disposed")
                runtime.dispose()
                self.assertEqual(kernel.lifecycle.state_for(runtime_id), RuntimeState.DISPOSED)

            commons.dispose()
            kernel.lifecycle.transition("kernel.session", RuntimeState.DISPOSING, "disposing")
            kernel.lifecycle.transition("kernel.session", RuntimeState.DISPOSED, "disposed")
            self.assertEqual(kernel.lifecycle.state_for("kernel.session"), RuntimeState.DISPOSED)


if __name__ == "__main__":
    unittest.main()
