# code-atlas Sacred Capabilities Contract

This contract defines the **40 release-blocking capabilities** for the workbench/editor.

Release policy:
- Every capability below is a release gate.
- A failing capability blocks release.
- The release gate script validates this contract plus critical automated checks.

Authoritative relationship:
- Full 100-capability premium model: `forgeos/shared/pyside6_glass/contracts/premium_capabilities_100.md`
- Golden sessions spec: `forgeos/shared/pyside6_glass/golden_sessions/golden_sessions_v1.json`
- Semantic baseline store: `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/semantic_baseline.json`
- UX proof artifacts: `forgeos/shared/pyside6_glass/artifacts/ux_release_proof/<timestamp>/`

## Interaction Premium (A)
1. Window resize is stable from corners and edges.
2. Window drag works from intended chrome/header zones.
3. Direct panel drag is available where supported by the editor model.
4. Direct panel resize has a clear affordance and consistent behavior.
5. Drag/resize interactions are clamped to workspace bounds.
6. Panel move operations preserve valid drop targets and slot compatibility.
7. Mouse and touch interactions are accepted for panel direct manipulation.
8. Keyboard focus remains visible and deterministic across controls.
9. Hover/pressed/selected/focus states are visually distinct.
10. No visible control is a no-op.
11. Workspace splitters resize reliably without layout corruption.
12. Active context is always visually identifiable.

## Operational Trust (B)
13. Data origin is inspectable for selected entries.
14. Provider identity and query identity are always visible for data-backed entries.
15. Freshness and stale state are explicit in probe and diagnostics outputs.
16. Preview state, working state, and saved clone state are not conflated.
17. Actions that change state leave a visible trace.
18. Runtime diagnostics expose provider and integration boundaries.
19. Sync/dispatch and error-related diagnostics remain inspectable.
20. Query probe reports include latency and refreshed timestamps.
21. Loading/empty/error/stale states remain modelled and available.
22. Non-destructive editing is preserved by default.
23. Close-without-save does not overwrite pristine examples.
24. Save Clone writes to dedicated clone storage and continues editing on clone.

## Hardening and Blindage (C)
25. Sacred capabilities contract exists and is versioned in repo.
26. Release gate script validates contract and critical checks.
27. Release gate emits machine-readable evidence artifacts.
28. Import/compile sanity is part of release gate checks.
29. Critical workbench tests are part of release gate checks.
30. Panel budget policies are enforced (heavy/live widgets).
31. Inactive tabs remain lazy/non-live by default.
32. Budget breaches degrade safely (defer/hold/background), not crash.

## Premium Polish (D)
33. Empty workspace state is actionable and not a dead end.
34. Empty-state guidance is concise and task-oriented.
35. Feedback messages support auto-dismiss for transient info/success.
36. Warning/error feedback remains persistent enough for operator notice.
37. Action/status timeline is inspectable from runtime tools.
38. Catalog/workbench visual language remains consistent across surfaces.
39. Iconography remains high-contrast and readable on glass surfaces.
40. Multi-workspace operation remains clean after repeated add/remove/hide/reopen cycles.

## Validation contract

Required validation paths:
- `python -m unittest forgeos.shared.pyside6_glass.tests.test_catalog_workbench`
- `python -m unittest forgeos.shared.pyside6_glass.tests.test_data_result_states`
- `python -m unittest forgeos.shared.pyside6_glass.tests.test_data_registry`
- `python -m unittest forgeos.shared.pyside6_glass.tests.test_ux_flight_recorder`
- `python forgeos/shared/pyside6_glass/release_gate.py`
