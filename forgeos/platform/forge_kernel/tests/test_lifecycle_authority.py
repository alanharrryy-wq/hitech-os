import unittest

from forge_kernel import KernelRuleViolation, LifecycleAuthority, RuntimeState


class LifecycleAuthorityTests(unittest.TestCase):
    def test_lifecycle_happy_path(self) -> None:
        authority = LifecycleAuthority()
        authority.register_runtime("unit.alpha")
        authority.transition("unit.alpha", RuntimeState.PREPARED, "prepared")
        authority.transition("unit.alpha", RuntimeState.ACTIVE, "activated")
        authority.transition("unit.alpha", RuntimeState.SUSPENDED, "suspended")
        authority.transition("unit.alpha", RuntimeState.ACTIVE, "resumed")
        authority.transition("unit.alpha", RuntimeState.DISPOSING, "shutdown")
        authority.transition("unit.alpha", RuntimeState.DISPOSED, "closed")
        self.assertEqual(authority.state_for("unit.alpha"), RuntimeState.DISPOSED)
        self.assertGreaterEqual(len(authority.history("unit.alpha")), 6)

    def test_invalid_transition_is_rejected(self) -> None:
        authority = LifecycleAuthority()
        authority.register_runtime("unit.beta")
        with self.assertRaises(KernelRuleViolation):
            authority.transition("unit.beta", RuntimeState.ACTIVE, "skipped_prepare")


if __name__ == "__main__":
    unittest.main()
