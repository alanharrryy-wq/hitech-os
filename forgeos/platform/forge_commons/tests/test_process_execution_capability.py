import sys
import unittest

from forge_commons import ProcessExecutionCapability
from forge_commons.lifecycle import CapabilityRuntimeState
from forge_kernel import KernelBootstrap


class ProcessExecutionCapabilityTests(unittest.TestCase):
    def test_execute_command_records_finished_status(self) -> None:
        contracts = KernelBootstrap.start().contracts
        capability = ProcessExecutionCapability(contracts=contracts)
        capability.activate()
        result = capability.execute(
            command=[sys.executable, "-c", "print('ok')"],
            actor="test",
            correlation_id="proc-001",
            timeout_seconds=5,
        )
        self.assertEqual(result.status, "finished")
        self.assertEqual(result.return_code, 0)
        self.assertIn("ok", result.stdout)

    def test_execute_timeout_records_timed_out(self) -> None:
        contracts = KernelBootstrap.start().contracts
        capability = ProcessExecutionCapability(contracts=contracts)
        capability.activate()
        result = capability.execute(
            command=[sys.executable, "-c", "import time; time.sleep(2)"],
            actor="test",
            correlation_id="proc-002",
            timeout_seconds=0.2,
        )
        self.assertEqual(result.status, "timed_out")
        self.assertIsNone(result.return_code)

    def test_dispose_clears_ledger(self) -> None:
        contracts = KernelBootstrap.start().contracts
        capability = ProcessExecutionCapability(contracts=contracts)
        capability.activate()
        capability.execute(
            command=[sys.executable, "-c", "print('x')"],
            actor="test",
            correlation_id="proc-003",
            timeout_seconds=5,
        )
        state = capability.dispose()
        self.assertEqual(state, CapabilityRuntimeState.DISPOSED)
        self.assertEqual(capability.ledger(), [])


if __name__ == "__main__":
    unittest.main()
