
from __future__ import annotations

from pyside6_glass.foundry_interaction import (
    INTERACTION_SAFETY_VERSION,
    OverlaySpec,
    interaction_registry_snapshot,
    list_interaction_profiles,
)


def test_interaction_version() -> None:
    assert INTERACTION_SAFETY_VERSION == "foundry.interaction_safety.v1"


def test_profiles_are_available() -> None:
    profiles = list_interaction_profiles()
    assert "operator_dense" in profiles
    assert "diagnostic_lab" in profiles


def test_registry_snapshot_has_overlays() -> None:
    snapshot = interaction_registry_snapshot()
    assert snapshot["version"] == INTERACTION_SAFETY_VERSION
    assert "context_sheet" in snapshot["overlays"]


def test_overlay_spec_defaults() -> None:
    spec = OverlaySpec("sheet", "Context Sheet")
    assert spec.close_on_escape is True
    assert spec.role == "sheet"
