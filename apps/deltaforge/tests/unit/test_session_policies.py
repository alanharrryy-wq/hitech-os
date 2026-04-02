from types import SimpleNamespace

from application.refresh_policy import begin_refresh, build_refresh_decision, finish_refresh
from application.stale_policy import mark_stale


def _workspace(**overrides):
    base = {
        "session_id": "s-1",
        "state": "IDLE",
        "dirty": False,
        "stale": False,
        "busy": False,
        "results": {},
        "event_feed": [],
        "selection": {},
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_mark_stale_preserves_active_operation_state() -> None:
    workspace = _workspace(state="VALIDATING", busy=True)
    updated = mark_stale(workspace)

    assert updated.stale is True
    assert updated.state == "VALIDATING"


def test_refresh_clears_stale_but_preserves_dirty() -> None:
    workspace = _workspace(state="DIRTY_OR_STALE", dirty=True, stale=True)
    decision = build_refresh_decision(workspace)

    assert decision.should_refresh is True

    refreshing = begin_refresh(workspace)
    completed = finish_refresh(refreshing)

    assert completed.busy is False
    assert completed.stale is False
    assert completed.dirty is True
    assert completed.state == "DIRTY_OR_STALE"
