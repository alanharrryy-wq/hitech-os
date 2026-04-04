from __future__ import annotations

import json

from domain.models.ops_document import OpsDocument


def test_ops_document_parses_envelope_and_operations() -> None:
    payload = {
        "version": "1",
        "ops": [
            {
                "type": "ReplaceExactOnce",
                "label": "swap",
                "file": "demo.txt",
                "old_text": "before",
                "new_text": "after",
            }
        ],
    }

    document = OpsDocument(text=json.dumps(payload), source_path="ops.json")

    assert document.is_loaded is True
    assert document.has_source_path is True
    assert document.operation_count == 1
    assert document.has_operations is True
    assert document.parsed_payload()["version"] == "1"
    assert document.operation_items()[0]["label"] == "swap"


def test_ops_document_handles_invalid_json_safely() -> None:
    document = OpsDocument(text="{ invalid json", source_path="ops.json")

    assert document.parsed_payload() == {}
    assert document.operation_items() == []
    assert document.operation_count == 0
    assert document.has_operations is False


def test_ops_document_summary_payload_includes_contract_fields() -> None:
    payload = [
        {
            "type": "InsertAfterExact",
            "label": "insert",
            "file": "demo.txt",
            "anchor": "x",
            "insert_text": "y",
        }
    ]
    document = OpsDocument(text=json.dumps(payload), source_path="ops.json")
    summary = document.summary_payload()

    assert summary["has_source_path"] is True
    assert summary["operation_count"] == 1
    assert summary["has_operations"] is True
