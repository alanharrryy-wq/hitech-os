from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ATLAS = Path(__file__).resolve().parents[1]
DATA_PATH = ATLAS / "assets/data/visual-control.cobrar.pilot.json"
JS_PATH = ATLAS / "assets/data/visual-control.cobrar.pilot.js"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


class CanonicalVisualControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    def test_exact_cobrar_hierarchy(self) -> None:
        pilot = self.payload["pilot"]
        self.assertEqual(pilot["surfaceId"], "SURF.tb.pos")
        self.assertEqual(pilot["routeId"], "ROUTE.tb.pos")
        self.assertEqual(pilot["ownerId"], "OWN.tb.pos_ticket_panel")
        self.assertEqual(pilot["regionId"], "ZONE.tb.pos.payment")
        self.assertEqual(pilot["slotId"], "SLOT.tb.pos.payment.cobrar")
        self.assertEqual(pilot["componentUiId"], "TB-POS-PAY-COBRAR-BTN-01")
        self.assertEqual(pilot["layerId"], "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE")

    def test_source_only_guards(self) -> None:
        self.assertEqual(self.payload["status"], "READY_FOR_SOURCE_ONLY_PLANNING")
        self.assertFalse(self.payload["safety"]["runtimeMutationAllowed"])
        self.assertFalse(self.payload["safety"]["productApplicationAllowed"])
        self.assertFalse(self.payload["safety"]["sourceMutationPerformed"])
        self.assertFalse(self.payload["plan"]["applicationEnabled"])
        self.assertEqual(self.payload["plan"]["operationCount"], 11)
        self.assertEqual(self.payload["recipe"]["plannedPropertyCount"], 89)
        self.assertEqual(self.payload["recipe"]["missingPropertyCount"], 0)
        self.assertEqual(sum(row["propertyCount"] for row in self.payload["plan"]["operations"]), 89)

    def test_honest_evidence_gates(self) -> None:
        statuses = {gate["gateId"]: gate["status"] for gate in self.payload["gates"]}
        self.assertEqual(statuses["RECIPE_COVERAGE_FRESHNESS"], "BLOCKED_BY_STALE_RUNTIME_EVIDENCE")
        self.assertEqual(statuses["MAMASTROPHIC_VISUAL_EVIDENCE"], "BLOCKED_BY_MISSING_MAMASTROPHIC_EVIDENCE")
        self.assertEqual(self.payload["evidence"]["runtime"]["status"], "NOT_CERTIFIED")

    def test_portable_integrity_and_js_parity(self) -> None:
        integrity = self.payload.pop("integrity")
        try:
            actual = hashlib.sha256(canonical_bytes(self.payload)).hexdigest()
        finally:
            self.payload["integrity"] = integrity
        self.assertEqual(actual, integrity["canonicalPayloadSha256"])
        js = JS_PATH.read_text(encoding="utf-8")
        self.assertTrue(js.startswith("window.PRISMA_ATLASFIN_VISUAL_CONTROL = "))
        js_payload = json.loads(js.removeprefix("window.PRISMA_ATLASFIN_VISUAL_CONTROL = ").removesuffix(";\n"))
        self.assertEqual(js_payload, self.payload)
        portable_text = DATA_PATH.read_text(encoding="utf-8")
        self.assertNotIn(":\\\\", portable_text)
        self.assertNotIn("F:\\\\", portable_text)


if __name__ == "__main__":
    unittest.main()
