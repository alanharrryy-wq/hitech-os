from __future__ import annotations

from collections import defaultdict

from pya.contracts.enums import State

STATE_PRODUCERS = {
    State.OBSERVED.value: {"scanner"},
    State.DECLARED.value: {"scanner", "registry_builder"},
    State.CANDIDATE.value: {"scanner", "registry_builder"},
    State.CANONICAL.value: {"registry_builder"},
    State.RESOLVED.value: {"switch_engine"},
    State.VALIDATED.value: {"contract_validator"},
    State.SUGGESTED.value: {"ai_annotator"},
    State.EFFECTIVE.value: {"switch_engine"},
    State.DEPRECATED.value: {"registry_builder"},
    State.SUPERSEDED.value: {"registry_builder"},
    State.QUARANTINED.value: {"contract_validator"},
    State.AMBIGUOUS.value: {"scanner"},
    State.REVIEWED.value: {"ai_annotator"},
    State.ACCEPTED.value: {"ai_annotator"},
    State.REJECTED.value: {"contract_validator", "ai_annotator"},
    State.STALE.value: {"ai_annotator"},
}

VALID_TRANSITIONS = {
    State.OBSERVED.value: {State.CANDIDATE.value, State.AMBIGUOUS.value},
    State.CANDIDATE.value: {State.CANONICAL.value, State.DEPRECATED.value, State.SUPERSEDED.value},
    State.CANONICAL.value: {State.RESOLVED.value, State.VALIDATED.value, State.DEPRECATED.value},
    State.RESOLVED.value: {State.EFFECTIVE.value, State.VALIDATED.value},
    State.VALIDATED.value: {State.SUGGESTED.value, State.QUARANTINED.value},
    State.SUGGESTED.value: {State.REVIEWED.value, State.ACCEPTED.value, State.REJECTED.value, State.STALE.value},
    State.REVIEWED.value: {State.ACCEPTED.value, State.REJECTED.value, State.STALE.value},
    State.ACCEPTED.value: {State.STALE.value},
    State.REJECTED.value: {State.SUGGESTED.value},
}

FORBIDDEN_STATE_PRODUCERS = defaultdict(set)
ALL_STATES = {item.value for item in State}
for state in ALL_STATES:
    FORBIDDEN_STATE_PRODUCERS[state] = {"scanner", "registry_builder", "switch_engine", "contract_validator", "ai_annotator"} - STATE_PRODUCERS.get(state, set())


def validate_state_producer(engine_id: str, state: str) -> None:
    allowed = STATE_PRODUCERS.get(state)
    if not allowed or engine_id not in allowed:
        raise ValueError(f"Engine {engine_id!r} is not allowed to produce state {state!r}")


def is_valid_transition(old_state: str, new_state: str) -> bool:
    return new_state in VALID_TRANSITIONS.get(old_state, set())
