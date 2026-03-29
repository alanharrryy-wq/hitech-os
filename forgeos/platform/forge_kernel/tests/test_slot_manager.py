import unittest

from forge_kernel import KernelRuleViolation, SlotManager, SlotState


class SlotManagerTests(unittest.TestCase):
    def test_default_slot_capacity_is_enforced(self) -> None:
        slots = SlotManager(default_slot_id="primary_workspace", default_capacity=1)
        slots.bind("primary_workspace", "surface.alpha")
        with self.assertRaises(KernelRuleViolation):
            slots.bind("primary_workspace", "surface.beta")

    def test_visibility_requires_binding(self) -> None:
        slots = SlotManager()
        with self.assertRaises(KernelRuleViolation):
            slots.set_visibility("primary_workspace", True)

    def test_unbind_returns_slot_to_unbound(self) -> None:
        slots = SlotManager()
        slots.bind("primary_workspace", "surface.alpha")
        slots.unbind("primary_workspace", "surface.alpha")
        state = slots.snapshot("primary_workspace")[0].state
        self.assertEqual(state, SlotState.UNBOUND)


if __name__ == "__main__":
    unittest.main()
