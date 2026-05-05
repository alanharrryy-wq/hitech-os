"""Stage order helpers for the homologated bundle."""

from __future__ import annotations

from contracts.shared_canon import STAGE_ORDER


def is_valid_stage_sequence(sequence: list[str]) -> bool:
    return sequence == STAGE_ORDER


def stage_position(stage_name: str) -> int:
    return STAGE_ORDER.index(stage_name)


def explain_stage_order() -> list[tuple[str, str]]:
    return [
        ("stage_01_scan", "Scanner emits observations only."),
        ("stage_02_registry_build", "Registry Builder promotes and writes canonical registries."),
        ("stage_03_switch_resolve", "Switch Engine resolves deterministic switch outputs."),
        ("stage_04_contract_validate", "Contract Validator judges conformance and gates."),
        ("stage_05_ai_annotate", "AI Annotator adds advisory-only metadata."),
    ]
