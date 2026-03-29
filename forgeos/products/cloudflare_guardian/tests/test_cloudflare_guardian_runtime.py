import unittest

from cloudflare_guardian import CloudflareGuardianRuntime, CloudflareGuardianState, ZoneSnapshot
from forge_commons import ForgeCommonsBootstrap
from forge_kernel import HostContribution, KernelBootstrap, RuntimeState


class CloudflareGuardianRuntimeTests(unittest.TestCase):
    def _sample_snapshots(self) -> list[ZoneSnapshot]:
        return [
            ZoneSnapshot(
                zone_id="zone-a",
                status="ok",
                latency_ms=220,
                error_rate=0.002,
                checked_at_utc="2026-03-29T10:00:00Z",
            ),
            ZoneSnapshot(
                zone_id="zone-b",
                status="ok",
                latency_ms=760,
                error_rate=0.02,
                checked_at_utc="2026-03-29T10:00:00Z",
            ),
            ZoneSnapshot(
                zone_id="zone-c",
                status="down",
                latency_ms=2000,
                error_rate=0.4,
                checked_at_utc="2026-03-29T10:00:00Z",
            ),
        ]

    def test_evaluate_health_and_record_run(self) -> None:
        kernel = KernelBootstrap.start(kernel_version="0.1.0")
        commons = ForgeCommonsBootstrap.start(contracts=kernel.contracts)
        runtime = CloudflareGuardianRuntime(history_runs=commons.history_runs)
        runtime.prepare()
        runtime.activate()
        runtime.ingest_snapshots(self._sample_snapshots())
        report = runtime.evaluate_health(
            actor="test.cloudflare_guardian",
            correlation_id="cg-001",
        )
        self.assertEqual(report.total_zones, 3)
        self.assertEqual(report.unhealthy_zones, 1)
        self.assertEqual(report.risk_level, "high")
        self.assertEqual(len(commons.history_runs.all_runs()), 1)
        commons.dispose()

    def test_host_contribution_refresh(self) -> None:
        kernel = KernelBootstrap.start(kernel_version="0.1.0")
        runtime_id = "product.cloudflare_guardian"
        kernel.lifecycle.register_runtime(runtime_id)
        kernel.lifecycle.transition(runtime_id, RuntimeState.PREPARED, "prepared")
        kernel.lifecycle.transition(runtime_id, RuntimeState.ACTIVE, "active")

        runtime = CloudflareGuardianRuntime()
        runtime.prepare()
        runtime.activate()
        runtime.ingest_snapshots(self._sample_snapshots())
        runtime.evaluate_health(
            actor="test.cloudflare_guardian",
            correlation_id="cg-010",
        )

        contribution = HostContribution(
            contribution_id=runtime.contribution_id,
            slot_id=runtime.slot_id,
            product_id=runtime.product_id,
            surface_kind=runtime.surface_kind,
            metadata={"product": runtime.product_id},
            actions=runtime.contribution_actions(),
        )
        kernel.host_shell.register_contribution(
            contribution=contribution,
            actor="test.cloudflare_guardian",
            correlation_id="cg-011",
        )
        kernel.host_shell.set_visible(runtime.slot_id, True)
        result = kernel.host_shell.invoke_action(
            contribution_id=runtime.contribution_id,
            action_id="refresh_radar",
            actor="test.cloudflare_guardian",
            correlation_id="cg-012",
            timeout_seconds=1.0,
        )
        self.assertEqual(result.status, "completed")
        payload = result.value
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["risk_level"], "high")
        kernel.host_shell.dispose(
            actor="test.cloudflare_guardian",
            correlation_id="cg-013",
        )
        kernel.lifecycle.transition(runtime_id, RuntimeState.SUSPENDED, "suspended")
        runtime.suspend()
        kernel.lifecycle.transition(runtime_id, RuntimeState.DISPOSING, "disposing")
        kernel.lifecycle.transition(runtime_id, RuntimeState.DISPOSED, "disposed")
        self.assertEqual(runtime.dispose(), CloudflareGuardianState.DISPOSED)


if __name__ == "__main__":
    unittest.main()
