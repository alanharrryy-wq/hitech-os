import pytest

from application.state_machine import InvalidTransitionError, assert_transition, can_transition, derive_idle_state


def test_idle_can_transition_to_dirty_or_stale() -> None:
    assert can_transition("idle", "DIRTY_OR_STALE") is True
    assert assert_transition("idle", "DIRTY_OR_STALE") == "DIRTY_OR_STALE"


def test_closed_rejects_new_work() -> None:
    with pytest.raises(InvalidTransitionError):
        assert_transition("closed", "refreshing")


def test_derive_idle_state_prefers_dirty_or_stale() -> None:
    assert derive_idle_state(False, False) == "IDLE"
    assert derive_idle_state(True, False) == "DIRTY_OR_STALE"
    assert derive_idle_state(False, True) == "DIRTY_OR_STALE"
