import sys
import unittest

from forge_commons import ForgeCommonsBootstrap
from forge_kernel import HostContribution, KernelBootstrap, RuntimeState
from orchestrator_bridge import (
    OrchestratorBridgeRuntime,
    OrchestratorBridgeState,
    WorkflowStep,
)


class OrchestratorBridgeRuntimeTests(unittest.TestCase):
    def test_run_workflow_finished(self) -> None:
        kernel = KernelBootstrap.start(kernel_version="0.1.0")
        commons = ForgeCommonsBootstrap.start(contracts=kernel.contracts)
        runtime = OrchestratorBridgeRuntime(
            process_runner=commons.process_execution,
            history_runs=commons.history_runs,
        )
        runtime.prepare()
        runtime.activate()
        runtime.register_workflow(
            workflow_id="wf.sample",
            steps=[
                WorkflowStep(
                    step_id="step-1",
                    command=(sys.executable, "-c", "print('ok')"),
                    timeout_seconds=5.0,
                )
            ],
        )
        report = runtime.run_workflow(
            workflow_id="wf.sample",
            actor="test.orchestrator_bridge",
            correlation_id="ob-001",
        )
        self.assertEqual(report.overall_status, "finished")
        self.assertEqual(report.total_steps, 1)
        self.assertEqual(len(commons.history_runs.all_runs()), 1)
        commons.dispose()

    def test_host_contribution_refresh_last_run(self) -> None:
        kernel = KernelBootstrap.start(kernel_version="0.1.0")
        commons = ForgeCommonsBootstrap.start(contracts=kernel.contracts)
        runtime_id = "product.orchestrator_bridge"
        kernel.lifecycle.register_runtime(runtime_id)
        kernel.lifecycle.transition(runtime_id, RuntimeState.PREPARED, "prepared")
        kernel.lifecycle.transition(runtime_id, RuntimeState.ACTIVE, "active")

        runtime = OrchestratorBridgeRuntime(
            process_runner=commons.process_execution,
            history_runs=commons.history_runs,
        )
        runtime.prepare()
        runtime.activate()
        runtime.register_workflow(
            workflow_id="wf.host",
            steps=[
                WorkflowStep(
                    step_id="step-1",
                    command=(sys.executable, "-c", "print('hello')"),
                    timeout_seconds=5.0,
                )
            ],
        )
        runtime.run_workflow(
            workflow_id="wf.host",
            actor="test.orchestrator_bridge",
            correlation_id="ob-010",
        )

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
            actor="test.orchestrator_bridge",
            correlation_id="ob-011",
        )
        kernel.host_shell.set_visible(runtime.slot_id, True)
        result = kernel.host_shell.invoke_action(
            contribution_id=runtime.contribution_id,
            action_id="refresh_last_run",
            actor="test.orchestrator_bridge",
            correlation_id="ob-012",
            timeout_seconds=1.0,
        )
        self.assertEqual(result.status, "completed")
        payload = result.value
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["workflow_id"], "wf.host")
        self.assertEqual(payload["overall_status"], "finished")
        kernel.host_shell.dispose(
            actor="test.orchestrator_bridge",
            correlation_id="ob-013",
        )
        kernel.lifecycle.transition(runtime_id, RuntimeState.SUSPENDED, "suspended")
        runtime.suspend()
        kernel.lifecycle.transition(runtime_id, RuntimeState.DISPOSING, "disposing")
        kernel.lifecycle.transition(runtime_id, RuntimeState.DISPOSED, "disposed")
        self.assertEqual(runtime.dispose(), OrchestratorBridgeState.DISPOSED)
        commons.dispose()


if __name__ == "__main__":
    unittest.main()
