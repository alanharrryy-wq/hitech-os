import json
import unittest
from pathlib import Path

from dummy_product import DummyProductRuntime, DummyProductState
from forge_kernel import HostContribution, KernelBootstrap, RuntimeState


class DummyProductSkeletonTests(unittest.TestCase):
    def test_dummy_product_can_register_activate_suspend_dispose(self) -> None:
        session = KernelBootstrap.start(kernel_version="0.1.0")
        runtime_id = "product.dummy_product"
        session.lifecycle.register_runtime(runtime_id)
        session.lifecycle.transition(runtime_id, RuntimeState.PREPARED, "prepared")
        session.lifecycle.transition(runtime_id, RuntimeState.ACTIVE, "active")

        product = DummyProductRuntime()
        self.assertEqual(product.prepare(), DummyProductState.PREPARED)
        self.assertEqual(product.activate(), DummyProductState.ACTIVE)

        contribution = HostContribution(
            contribution_id=product.contribution.contribution_id,
            slot_id=product.contribution.slot_id,
            product_id=product.product_id,
            surface_kind=product.contribution.surface_kind,
            metadata={"source": "dummy_product"},
            actions={"heartbeat": lambda: "alive"},
        )
        session.host_shell.register_contribution(
            contribution=contribution,
            actor="test.product",
            correlation_id="prod-001",
        )
        session.host_shell.set_visible("primary_workspace", True)
        invocation = session.host_shell.invoke_action(
            contribution_id=contribution.contribution_id,
            action_id="heartbeat",
            actor="test.product",
            correlation_id="prod-002",
            timeout_seconds=1.0,
        )
        self.assertEqual(invocation.status, "completed")
        self.assertEqual(invocation.value, "alive")

        self.assertEqual(product.suspend(), DummyProductState.SUSPENDED)
        session.lifecycle.transition(runtime_id, RuntimeState.SUSPENDED, "suspended")

        session.host_shell.dispose(actor="test.product", correlation_id="prod-003")
        session.lifecycle.transition(runtime_id, RuntimeState.DISPOSING, "disposing")
        session.lifecycle.transition(runtime_id, RuntimeState.DISPOSED, "disposed")
        self.assertEqual(product.dispose(), DummyProductState.DISPOSED)
        self.assertEqual(session.lifecycle.state_for(runtime_id), RuntimeState.DISPOSED)

    def test_dummy_product_skeleton_files_exist(self) -> None:
        forgeos_root = Path(__file__).resolve().parents[3]
        product_root = forgeos_root / "products" / "dummy_product"
        required_files = [
            "PRODUCT_MANIFEST.json",
            "README.md",
            "OWNERSHIP.md",
            "STATE_AUTHORITY.md",
            "LIFECYCLE.md",
            "CONTRACT_INDEX.md",
            "HOST_CONTRIBUTIONS.md",
            "TEARDOWN.md",
            "PACKAGING.md",
            "DEPENDENCIES.md",
            "ERROR_BOUNDARIES.md",
            "COMPATIBILITY.md",
        ]
        for name in required_files:
            self.assertTrue((product_root / name).exists(), f"missing {name}")
        manifest = json.loads((product_root / "PRODUCT_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["product_id"], "dummy_product")


if __name__ == "__main__":
    unittest.main()
