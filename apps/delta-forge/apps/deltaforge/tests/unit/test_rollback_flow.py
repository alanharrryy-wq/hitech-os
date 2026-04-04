from __future__ import annotations

import json

from domain.models.ops_document import OpsDocument
from domain.models.scope import ScopeSelection
from domain.models.session import SessionWorkspace
from infrastructure.engine.local_patch_engine import LocalPatchEngine


def test_rollback_flow_restores_original_content(tmp_path) -> None:
    target = tmp_path / "demo.txt"
    target.write_text("first\nsecond\n", encoding="utf-8")

    ops = [
        {
            "type": "InsertAfterExact",
            "label": "insert-after-first",
            "file": "demo.txt",
            "anchor": "first",
            "insert_text": "\ninserted",
        }
    ]

    scope = ScopeSelection.for_directory(str(tmp_path), source="test")
    session = SessionWorkspace(
        session_id="s-rollback",
        title="rollback",
        scope=scope,
        ops_document=OpsDocument(text=json.dumps(ops)),
    )

    engine = LocalPatchEngine(root_dir=tmp_path)

    apply_result = engine.apply(session)
    assert apply_result.ok is True
    token = apply_result.rollback_token
    assert token
    assert "inserted" in target.read_text(encoding="utf-8")

    rollback_result = engine.rollback(session, token)
    assert rollback_result.ok is True
    assert target.read_text(encoding="utf-8") == "first\nsecond\n"
