import unittest

from forge_commons import ForgeCommonsBootstrap
from forge_commons.lifecycle import CapabilityRuntimeState
from forge_kernel import KernelBootstrap


class ForgeCommonsBootstrapTests(unittest.TestCase):
    def test_bootstrap_activates_all_capabilities(self) -> None:
        contracts = KernelBootstrap.start().contracts
        commons = ForgeCommonsBootstrap.start(contracts=contracts)
        self.assertEqual(commons.config_policy.lifecycle.state, CapabilityRuntimeState.SERVING)
        self.assertEqual(commons.diagnostics.lifecycle.state, CapabilityRuntimeState.SERVING)
        self.assertEqual(commons.process_execution.lifecycle.state, CapabilityRuntimeState.SERVING)
        self.assertEqual(commons.history_runs.lifecycle.state, CapabilityRuntimeState.SERVING)
        self.assertEqual(commons.export_artifacts.lifecycle.state, CapabilityRuntimeState.SERVING)
        commons.dispose()
        self.assertEqual(commons.config_policy.lifecycle.state, CapabilityRuntimeState.DISPOSED)
        self.assertEqual(commons.export_artifacts.lifecycle.state, CapabilityRuntimeState.DISPOSED)


if __name__ == "__main__":
    unittest.main()
