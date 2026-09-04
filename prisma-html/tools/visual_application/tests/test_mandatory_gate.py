from __future__ import annotations

import copy
import unittest

from visual_application.mandatory_gate import evaluate
from visual_application.receipts import _receipt_digest


SOURCE = "prisma-html/authority/rifat/tablet/runtime-sources/modules/pos/pos.module.css"
OUTPUT = "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
TARGET = "TGT.TABLET.POS.COBRAR.PRIMARY.V1"


def index():
    return {
        "schema": "prisma.visual.application.target-index.v1",
        "globalBlockers": [],
        "records": [
            {
                "targetId": TARGET,
                "surface": "tablet",
                "canonicalSourcePath": SOURCE,
                "generatedOutputPath": OUTPUT,
            }
        ],
    }


def receipt(*, before_source="1"*64, after_source="2"*64, before_output="3"*64, after_output="4"*64, tx="gvae-test01"):
    doc = {
        "schema": "prisma.visual.application.receipt.v1",
        "transactionId": tx,
        "targetId": TARGET,
        "surface": "tablet",
        "status": "APPLIED_SOURCE_STATIC",
        "authorityCommit": "a"*40,
        "requestDigest": "b"*64,
        "sourcePath": SOURCE,
        "generatedOutputPath": OUTPUT,
        "files": [
            {"path": SOURCE, "beforeSha256": before_source, "afterSha256": after_source},
            {"path": OUTPUT, "beforeSha256": before_output, "afterSha256": after_output},
        ],
        "authorization": {
            "authorityTaskId": "gvae-test",
            "authorityMeshArtifactSha256": "c"*64,
            "authorityMeshRequestDigest": "d"*64,
            "mesh": {
                "status": "PASS_COMPOSED_AUTHORITY_MESH",
                "repoHead": "a"*40,
                "requiredAuthorityCoveragePct": 100,
                "blockers": 0,
                "requestDigest": "d"*64,
                "artifactDigest": "c"*64,
                "layerMapPresent": True,
            },
            "factoryLedgerDecisionDigest": "e"*64,
            "uiBridge": {"planId": "plan-1", "semanticDiffChecksum": "f"*64},
            "uiBridgePlanSha256": "6"*64,
            "uiBridgeSemanticDiffSha256": "7"*64,
        },
        "evidenceClassification": "SOURCE_STATIC_ONLY",
        "runtimeVisualGreen": False,
        "ready": False,
        "doesNotProve": ["runtime visual certification"],
    }
    doc["receiptDigest"] = _receipt_digest(doc)
    return doc


class MandatoryGateTests(unittest.TestCase):
    def test_no_registered_target_change_passes_without_receipt(self):
        result = evaluate(
            index=index(),
            changed={"README.md"},
            receipts=[],
            before_hash=lambda path: None,
            after_hash=lambda path: None,
        )
        self.assertEqual(result["status"], "PASS_GVAE_MANDATORY_GATE")

    def test_registered_source_change_without_receipt_blocks(self):
        result = evaluate(
            index=index(),
            changed={SOURCE},
            receipts=[],
            before_hash=lambda path: "1"*64,
            after_hash=lambda path: "2"*64,
        )
        self.assertEqual(result["status"], "BLOCKED_GVAE_MANDATORY_GATE")
        self.assertIn(f"GVAE_RECEIPT_REQUIRED:{SOURCE}", result["errors"])

    def test_valid_receipt_covers_source_and_projection(self):
        hashes_before = {SOURCE: "1"*64, OUTPUT: "3"*64}
        hashes_after = {SOURCE: "2"*64, OUTPUT: "4"*64}
        result = evaluate(
            index=index(),
            changed={SOURCE, OUTPUT},
            receipts=[receipt()],
            before_hash=hashes_before.get,
            after_hash=hashes_after.get,
        )
        self.assertEqual(result["status"], "PASS_GVAE_MANDATORY_GATE")
        self.assertEqual(result["receiptCount"], 1)

    def test_two_receipts_must_form_hash_chain(self):
        first = receipt(after_source="8"*64, after_output="9"*64, tx="gvae-chain01")
        second = receipt(
            before_source="8"*64,
            after_source="2"*64,
            before_output="9"*64,
            after_output="4"*64,
            tx="gvae-chain02",
        )
        result = evaluate(
            index=index(),
            changed={SOURCE, OUTPUT},
            receipts=[second, first],
            before_hash={SOURCE: "1"*64, OUTPUT: "3"*64}.get,
            after_hash={SOURCE: "2"*64, OUTPUT: "4"*64}.get,
        )
        self.assertEqual(result["status"], "PASS_GVAE_MANDATORY_GATE")

    def test_broken_receipt_chain_blocks(self):
        bad = receipt(before_source="0"*64)
        result = evaluate(
            index=index(),
            changed={SOURCE},
            receipts=[bad],
            before_hash=lambda path: "1"*64,
            after_hash=lambda path: "2"*64,
        )
        self.assertEqual(result["status"], "BLOCKED_GVAE_MANDATORY_GATE")
        self.assertTrue(any(x.startswith("RECEIPT_CHAIN_INVALID:") for x in result["errors"]))

    def test_fake_ready_receipt_blocks(self):
        bad = receipt()
        bad["ready"] = True
        bad["receiptDigest"] = _receipt_digest(bad)
        result = evaluate(
            index=index(),
            changed={SOURCE},
            receipts=[bad],
            before_hash=lambda path: "1"*64,
            after_hash=lambda path: "2"*64,
        )
        self.assertEqual(result["status"], "BLOCKED_GVAE_MANDATORY_GATE")
        self.assertIn(f"RECEIPT_FAKE_READY:{TARGET}", result["errors"])

    def test_tampered_receipt_digest_blocks(self):
        bad = receipt()
        bad["receiptDigest"] = "0"*64
        result = evaluate(
            index=index(),
            changed={SOURCE},
            receipts=[bad],
            before_hash=lambda path: "1"*64,
            after_hash=lambda path: "2"*64,
        )
        self.assertEqual(result["status"], "BLOCKED_GVAE_MANDATORY_GATE")
        self.assertIn("RECEIPT_DIGEST_INVALID", result["errors"])


if __name__ == "__main__":
    unittest.main()
