from __future__ import annotations

import json

from application.contracts.engine_adapter import EngineAdapter
from domain.models.ops_document import OpsDocument
from domain.models.scope import ScopeSelection
from domain.models.session import SessionWorkspace
from infrastructure.engine.local_patch_engine import LocalPatchEngine
from infrastructure.engine.mock_engine_adapter import MockEngineAdapter


def test_local_patch_engine_respects_contract_surface(tmp_path) -> None:
    target = tmp_path / "demo.txt"
    target.write_text("hello\n", encoding="utf-8")

    ops = [
        {
            "type": "ReplaceExactOnce",
            "label": "replace",
            "file": "demo.txt",
            "old_text": "hello",
            "new_text": "hi",
        }
    ]

    session = SessionWorkspace(
        session_id="s-contract",
        title="contract",
        scope=ScopeSelection.for_directory(str(tmp_path), source="test"),
        ops_document=OpsDocument(text=json.dumps(ops)),
    )

    engine: EngineAdapter = LocalPatchEngine(root_dir=tmp_path)
    validation = engine.validate(session)
    assert validation.ok is True

    plan = engine.plan(session)
    assert plan.ok is True

    apply_result = engine.apply(session)
    assert apply_result.ok is True

    rollback_result = engine.rollback(session, apply_result.rollback_token)
    assert rollback_result.ok is True

    refresh = engine.refresh(session)
    assert refresh.ok is True


def test_mock_engine_adapter_is_explicit_fallback() -> None:
    adapter = MockEngineAdapter()
    assert getattr(adapter, "is_fallback", False) is True
