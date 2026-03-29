import unittest

from forge_commons import DiagnosticsCapability
from forge_commons.lifecycle import CapabilityRuntimeState


class DiagnosticsCapabilityTests(unittest.TestCase):
    def test_emit_and_health_snapshot(self) -> None:
        capability = DiagnosticsCapability()
        capability.activate()
        capability.emit(
            severity="info",
            component="kernel",
            message="boot completed",
            actor="runtime",
        )
        capability.emit(
            severity="error",
            component="commons",
            message="failure",
            actor="runtime",
        )
        snapshot = capability.health_snapshot()
        self.assertEqual(snapshot["info"], 1)
        self.assertEqual(snapshot["error"], 1)

    def test_dispose_clears_events(self) -> None:
        capability = DiagnosticsCapability()
        capability.activate()
        capability.emit(
            severity="warning",
            component="commons",
            message="degraded",
            actor="runtime",
        )
        state = capability.dispose()
        self.assertEqual(state, CapabilityRuntimeState.DISPOSED)
        self.assertEqual(capability.events(), [])


if __name__ == "__main__":
    unittest.main()
