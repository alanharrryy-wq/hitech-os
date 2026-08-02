from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from code_atlas.ui_bridge.application import APPLICATION_STATUS
from code_atlas.ui_bridge.cobrar_application import (
    ADAPTER_ID,
    AUTHORITY_CSS_PATH,
    BINDING_ID,
    COMPONENT_UI_ID,
    CONTROL_ID,
    EXPECTED_SELECTORS,
    IMPLEMENTATION_LAYER_ID,
    LAYER_ID,
    OLD_BLOCK,
    OWNER_PATH,
    PLAN_CHECKSUM,
    PLAN_ID,
    PRODUCT_CSS_PATH,
    RECIPE_ID,
    TASK_ID,
    TRANSACTION_ID,
    VISUAL_STACK_ID,
    _product_bytes,
    execute_cobrar_transaction,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ExactCobrarApplicationTests(unittest.TestCase):
    def test_preview_apply_and_second_execution_are_exact_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            evidence_root = root / "evidence"
            owner = repo / OWNER_PATH
            authority = repo / AUTHORITY_CSS_PATH
            product = repo / PRODUCT_CSS_PATH
            owner.parent.mkdir(parents=True, exist_ok=True)
            authority.parent.mkdir(parents=True, exist_ok=True)
            product.parent.mkdir(parents=True, exist_ok=True)
            owner.write_text("export function PosTicketPanel() {}\n", encoding="utf-8")
            authority_bytes = (".unrelated { color: red; }\n\n" + OLD_BLOCK + "\n.tail { color: blue; }\n").encode()
            authority.write_bytes(authority_bytes)
            product.write_bytes(_product_bytes(authority_bytes))
            before_evidence = root / "before-evidence.json"
            before_evidence.write_text('{"status":"PASS"}\n', encoding="utf-8")
            request = {
                "schema": "PRISMA_ATLASFIN_VISUAL_APPLICATION_REQUEST_V1",
                "schemaVersion": "1.0.0",
                "taskId": TASK_ID,
                "controlId": CONTROL_ID,
                "transactionId": TRANSACTION_ID,
                "componentUiId": COMPONENT_UI_ID,
                "recipeId": RECIPE_ID,
                "visualStackId": VISUAL_STACK_ID,
                "bindingId": BINDING_ID,
                "adapterId": ADAPTER_ID,
                "layerId": LAYER_ID,
                "implementationLayerId": IMPLEMENTATION_LAYER_ID,
                "planId": PLAN_ID,
                "planChecksum": PLAN_CHECKSUM,
                "authorization": "EXPLICIT_USER_AUTHORIZATION_ATLASFIN_COBRAR_V1",
                "maxProductFileCount": 1,
                "productFiles": [PRODUCT_CSS_PATH],
                "selectors": EXPECTED_SELECTORS,
                "before": {
                    "ownerSha256": sha(owner),
                    "authorityCssSha256": sha(authority),
                    "productCssSha256": sha(product),
                },
                "beforeEvidence": {
                    "phase": "BEFORE",
                    "status": "PASS",
                    "selector": ".cobrarReferenceButton",
                    "path": str(before_evidence),
                    "sha256": sha(before_evidence),
                },
            }
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")

            preview = execute_cobrar_transaction(request_path, repo, evidence_root / "preview", "preview")
            self.assertEqual(preview["status"], "PREVIEW_READY")
            self.assertEqual(preview["productFileCount"], 1)
            self.assertGreater(preview["preview"]["changedLineCount"], 0)
            self.assertEqual(authority.read_bytes(), authority_bytes)

            applied = execute_cobrar_transaction(request_path, repo, evidence_root / "apply", "apply")
            self.assertEqual(applied["status"], "APPLIED_SOURCE_VALIDATION_PENDING_RUNTIME_VISUAL_CERTIFICATION")
            self.assertTrue(applied["sourceMutationPerformed"])
            self.assertEqual(product.read_bytes(), _product_bytes(authority.read_bytes()))

            verified = execute_cobrar_transaction(request_path, repo, evidence_root / "verify", "verify")
            self.assertEqual(verified["idempotencyDisposition"], "ALREADY_APPLIED_AND_VERIFIED")
            self.assertEqual(verified["preview"]["changedLineCount"], 0)
            self.assertTrue(verified["sourceMutationPerformed"])

    def test_historical_source_only_v1_remains_disabled(self) -> None:
        self.assertFalse(APPLICATION_STATUS["applicationEnabled"])
        self.assertFalse(APPLICATION_STATUS["runtimeMutationAllowed"])
        self.assertFalse(APPLICATION_STATUS["productApplicationAllowed"])
        self.assertEqual(APPLICATION_STATUS["status"], "APPLICATION_DISABLED_SOURCE_ONLY_V1")


if __name__ == "__main__":
    unittest.main()
