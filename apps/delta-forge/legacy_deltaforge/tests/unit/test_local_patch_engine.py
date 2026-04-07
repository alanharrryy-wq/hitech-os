from __future__ import annotations

import json

from domain.models.ops_document import OpsDocument
from domain.models.scope import ScopeSelection
from domain.models.session import SessionWorkspace
from infrastructure.engine.local_patch_engine import LocalPatchEngine


def _build_session(tmp_path, ops_payload):
    scope = ScopeSelection.for_directory(str(tmp_path), source="test")
    document = OpsDocument(text=json.dumps(ops_payload), source_path=str(tmp_path / "ops.json"))
    return SessionWorkspace(session_id="s-1", title="test", scope=scope, ops_document=document)


def test_local_patch_engine_validate_and_plan(tmp_path) -> None:
    target = tmp_path / "demo.txt"
    target.write_text("line1\nline2\n", encoding="utf-8")

    ops = [
        {
            "type": "ReplaceLineRange",
            "label": "replace-line",
            "file": "demo.txt",
            "start_line": 2,
            "end_line": 2,
            "new_text": "line2-updated",
        }
    ]

    session = _build_session(tmp_path, ops)
    engine = LocalPatchEngine(root_dir=tmp_path)

    validation = engine.validate(session)
    assert validation.ok is True
    assert validation.touched_files == [str(target.resolve())]

    plan = engine.plan(session)
    assert plan.ok is True
    assert len(plan.steps) == 1
    assert "replace lines" in plan.steps[0].preview


def test_local_patch_engine_apply_changes_file_contents(tmp_path) -> None:
    target = tmp_path / "demo.txt"
    target.write_text("alpha\nbeta\n", encoding="utf-8")

    ops = [
        {
            "type": "ReplaceExactOnce",
            "label": "swap-beta",
            "file": "demo.txt",
            "old_text": "beta",
            "new_text": "gamma",
        }
    ]

    session = _build_session(tmp_path, ops)
    engine = LocalPatchEngine(root_dir=tmp_path)

    apply_result = engine.apply(session)
    assert apply_result.ok is True
    assert apply_result.rollback_token
    assert "gamma" in target.read_text(encoding="utf-8")
