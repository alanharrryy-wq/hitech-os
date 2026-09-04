from __future__ import annotations

import unittest

from visual_application.surface_batch import plan_surface


def base_index(records):
    return {
        "schema": "prisma.visual.application.target-index.v1",
        "globalBlockers": [],
        "records": records,
    }


class SurfaceBatchTests(unittest.TestCase):
    def test_discovery_only_target_blocks_whole_surface(self):
        plan = plan_surface(
            "tablet",
            index=base_index([
                {
                    "targetId": "TGT.CENSUS.TABLET.X.V1",
                    "surface": "tablet",
                    "recordKind": "VISUAL_CONTROL_CENSUS_TARGET",
                    "enforcement": "DISCOVERY_ONLY",
                    "status": "BLOCKED",
                    "blockers": ["semantic", "recipe"],
                }
            ]),
        )
        self.assertFalse(plan["ready"])
        self.assertEqual(plan["status"], "BLOCKED_SURFACE_BATCH")
        self.assertEqual(plan["discoveryOnlyCount"], 1)

    def test_all_exact_ready_targets_form_bounded_waves(self):
        records = [
            {
                "targetId": f"TGT.TABLET.EXACT.{i}.V1",
                "surface": "tablet",
                "recordKind": "EXACT_APPLICATION_TARGET",
                "enforcement": "GVAE_ENFORCED",
                "status": "APPLY_READY",
                "blockers": [],
            }
            for i in range(5)
        ]
        plan = plan_surface("tablet", index=base_index(records), wave_size=2)
        self.assertTrue(plan["ready"])
        self.assertEqual(plan["status"], "SURFACE_BATCH_READY")
        self.assertEqual(plan["waveCount"], 3)
        self.assertEqual([len(wave) for wave in plan["waves"]], [2, 2, 1])

    def test_blocked_exact_target_blocks_whole_surface(self):
        plan = plan_surface(
            "pc",
            index=base_index([
                {
                    "targetId": "TGT.PC.EXACT.ONE.V1",
                    "surface": "pc",
                    "recordKind": "EXACT_APPLICATION_TARGET",
                    "enforcement": "GVAE_ENFORCED",
                    "status": "BLOCKED",
                    "blockers": ["recipe"],
                }
            ]),
        )
        self.assertFalse(plan["ready"])
        self.assertEqual(plan["blockedExactCount"], 1)
        self.assertEqual(plan["blockerCounts"]["recipe"], 1)


if __name__ == "__main__":
    unittest.main()
