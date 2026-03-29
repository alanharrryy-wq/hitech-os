import unittest

from forge_commons import HistoryRunsCapability
from forge_commons.lifecycle import CapabilityRuntimeState
from forge_kernel import KernelBootstrap


class HistoryRunsCapabilityTests(unittest.TestCase):
    def test_append_adds_run_record(self) -> None:
        contracts = KernelBootstrap.start().contracts
        capability = HistoryRunsCapability(contracts=contracts)
        capability.activate()
        record = capability.append(
            run_id="run-001",
            producer="unit-test",
            status="finished",
            actor="test",
            correlation_id="hist-001",
        )
        self.assertEqual(record.run_id, "run-001")
        self.assertEqual(len(capability.all_runs()), 1)

    def test_dispose_clears_runs(self) -> None:
        contracts = KernelBootstrap.start().contracts
        capability = HistoryRunsCapability(contracts=contracts)
        capability.activate()
        capability.append(
            run_id="run-002",
            producer="unit-test",
            status="failed",
            actor="test",
            correlation_id="hist-002",
        )
        state = capability.dispose()
        self.assertEqual(state, CapabilityRuntimeState.DISPOSED)
        self.assertEqual(capability.all_runs(), [])


if __name__ == "__main__":
    unittest.main()
