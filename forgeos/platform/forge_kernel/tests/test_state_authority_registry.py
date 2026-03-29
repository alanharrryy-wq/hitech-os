import unittest

from forge_kernel import KernelRuleViolation, StateAuthorityRegistry, StateSliceAuthority


class StateAuthorityRegistryTests(unittest.TestCase):
    def test_register_and_access_rights(self) -> None:
        registry = StateAuthorityRegistry()
        registry.register(
            StateSliceAuthority(
                slice_id="kernel.session",
                owner="forge_kernel",
                source_of_truth="kernel_session_store",
                readers=("forge_kernel", "diagnostics"),
                writers=("forge_kernel",),
            )
        )
        self.assertTrue(registry.can_write("kernel.session", "forge_kernel"))
        self.assertTrue(registry.can_read("kernel.session", "diagnostics"))
        self.assertFalse(registry.can_write("kernel.session", "diagnostics"))

    def test_owner_must_be_writer(self) -> None:
        registry = StateAuthorityRegistry()
        with self.assertRaises(KernelRuleViolation):
            registry.register(
                StateSliceAuthority(
                    slice_id="kernel.layout",
                    owner="forge_kernel",
                    source_of_truth="layout_store",
                    readers=("forge_kernel",),
                    writers=("host_shell_adapter",),
                )
            )


if __name__ == "__main__":
    unittest.main()
