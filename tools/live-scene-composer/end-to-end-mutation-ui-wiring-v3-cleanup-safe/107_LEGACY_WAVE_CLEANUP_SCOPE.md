# 107_LEGACY_WAVE_CLEANUP_SCOPE

Legacy cleanup is intentionally narrow.

Legacy staging roots cleaned by default:
- tools/live-scene-composer/end-to-end-mutation-ui-wiring-v1
- tools/live-scene-composer/end-to-end-mutation-ui-wiring-v2-fixed

Legacy canonical docs cleaned by default if present:
- 90_END_TO_END_MUTATION_UI_WIRING_OVERVIEW.md
- 91_SURFACE_ACTION_TO_MUTATION_MAP.md
- 92_CANVAS_INTERACTION_TO_INTENT_PIPELINE.md
- 93_STRUCTURE_TREE_ACTION_ROUTING.md
- 94_INSPECTOR_PREVIEW_COMMIT_CONTROLLER.md
- 95_SELECTION_CONTEXT_AND_TARGET_RESOLUTION.md
- 96_UI_WIRING_STATE_MACHINE.md
- 97_KEYBOARD_POINTER_AND_TOOLBAR_BINDINGS.md
- 98_PREVIEW_COMPARE_APPLYBAR_DESIGN.md
- 99_UI_WIRING_ADAPTER_BOUNDARIES.md
- 100_END_TO_END_UI_SMOKE_PLAN.md
- 101_MUTATION_UI_EVIDENCE_MODEL.md
- 102_MUTATION_UI_FAILURE_ATLAS.md
- 103_REPO_STACKING_AND_MIRROR_RULES.md
- 104_OPERATOR_RUNBOOK_UI_WIRING.md
- 105_NEXT_WAVE_RECOMMENDATIONS.md

Not cleaned automatically:
- canonical architecture docs like 05, 10, 18, 19, 40, 41
- unrelated package staging roots
- arbitrary files not declared in the cleanup manifest
