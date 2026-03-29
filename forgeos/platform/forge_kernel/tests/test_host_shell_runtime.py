import time
import unittest

from forge_kernel import HostContribution, KernelBootstrap


class HostShellRuntimeTests(unittest.TestCase):
    def test_register_invoke_and_dispose_dummy_contribution(self) -> None:
        session = KernelBootstrap.start(kernel_version="0.1.0")
        contribution = HostContribution(
            contribution_id="contrib.dummy.surface",
            slot_id="primary_workspace",
            product_id="dummy_product",
            surface_kind="panel",
            metadata={"purpose": "test"},
            actions={"ping": lambda: "pong"},
        )
        session.host_shell.register_contribution(
            contribution=contribution,
            actor="test.host",
            correlation_id="host-001",
        )
        session.host_shell.set_visible("primary_workspace", True)
        result = session.host_shell.invoke_action(
            contribution_id="contrib.dummy.surface",
            action_id="ping",
            actor="test.host",
            correlation_id="host-002",
            timeout_seconds=1.0,
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.value, "pong")
        session.host_shell.dispose(actor="test.host", correlation_id="host-003")
        snapshot = session.host_shell.snapshot()
        self.assertEqual(snapshot.contribution_count, 0)

    def test_timeout_isolated_as_fault(self) -> None:
        session = KernelBootstrap.start(kernel_version="0.1.0")
        contribution = HostContribution(
            contribution_id="contrib.dummy.slow",
            slot_id="primary_workspace",
            product_id="dummy_product",
            surface_kind="panel",
            metadata={"purpose": "timeout"},
            actions={"slow": lambda: (time.sleep(0.5), "done")[1]},
        )
        session.host_shell.register_contribution(
            contribution=contribution,
            actor="test.host",
            correlation_id="host-010",
        )
        result = session.host_shell.invoke_action(
            contribution_id="contrib.dummy.slow",
            action_id="slow",
            actor="test.host",
            correlation_id="host-011",
            timeout_seconds=0.05,
        )
        self.assertEqual(result.status, "timed_out")
        self.assertEqual(result.error, "timeout")


if __name__ == "__main__":
    unittest.main()
