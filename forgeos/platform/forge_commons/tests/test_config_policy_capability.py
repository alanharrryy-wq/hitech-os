import unittest

from forge_commons import ConfigPolicyCapability
from forge_commons.lifecycle import CapabilityRuntimeState


class ConfigPolicyCapabilityTests(unittest.TestCase):
    def test_profile_resolution_uses_override_precedence(self) -> None:
        capability = ConfigPolicyCapability()
        capability.activate()
        capability.set_profile("default", {"mode": "safe", "retries": 1})
        capability.apply_override("retries", 3)
        resolved = capability.resolve("default")
        self.assertEqual(resolved["mode"], "safe")
        self.assertEqual(resolved["retries"], 3)

    def test_dispose_clears_state(self) -> None:
        capability = ConfigPolicyCapability()
        capability.activate()
        capability.set_profile("default", {"mode": "safe"})
        capability.apply_override("mode", "strict")
        state = capability.dispose()
        self.assertEqual(state, CapabilityRuntimeState.DISPOSED)
        self.assertEqual(capability.resolve("default"), {})


if __name__ == "__main__":
    unittest.main()
