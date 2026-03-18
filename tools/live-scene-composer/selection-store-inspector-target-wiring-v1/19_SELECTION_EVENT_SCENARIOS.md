# 19_SELECTION_EVENT_SCENARIOS

## Purpose

This document enumerates concrete selection and inspector scenarios that the team can use as a behavior matrix during implementation and review.

Each scenario describes:

- trigger
- expected store transition
- surface synchronization expectations
- inspector expectations
- mutation-targeting implications

---

## Scenario catalog

### Scenario 01: Initial scene bootstrap
- Trigger: scene loads and the shell chooses the scene root.
- Transition: `none -> active(scene)`.
- Canvas: frame scene shell.
- Tree: focus scene root.
- Inspector: `scene-editor` with scene groups.
- Mutation implication: scene-level actions must still use explicit scene target refs.

### Scenario 02: Canvas widget click
- Trigger: user clicks a visible widget overlay region.
- Transition: `active(scene) -> active(widget)` or `none -> active(widget)`.
- Canvas: widget overlay becomes active.
- Tree: matching widget node becomes active.
- Inspector: widget editor shows content/style groups only.
- Mutation implication: no write should execute against a hidden global selected widget; compose explicit widget target.

### Scenario 03: Structure tree slot click
- Trigger: user selects a slot node in the tree.
- Transition: `active(widget) -> active(slot)`.
- Canvas: widget overlay disappears; slot framing appears.
- Tree: slot node becomes active.
- Inspector: slot editor.
- Mutation implication: slot actions must target slot ref explicitly.

### Scenario 04: Empty canvas click
- Trigger: user clicks safe empty area.
- Transition: `active(any) -> none`.
- Canvas: clear affordances.
- Tree: clear active highlight.
- Inspector: empty editor.
- Mutation implication: target-scoped action buttons should disappear or disable.

### Scenario 05: Widget removed by external structure change
- Trigger: selected widget deleted by a structure operation.
- Transition: `active(widget) -> stale(widget)`.
- Canvas: clear widget handles immediately.
- Tree: clear active widget state.
- Inspector: unavailable editor with recovery message.
- Mutation implication: remove ability to issue widget-targeted writes.

### Scenario 06: Layout node replaced during draft refresh
- Trigger: current layout node id no longer resolves after draft refresh.
- Transition: `active(layout-node) -> stale(layout-node)`.
- Canvas: no old resize handles remain.
- Tree: no auto-sibling promotion.
- Inspector: unavailable editor.
- Mutation implication: layout mutation clients must reject stale targets.

### Scenario 07: Explicit fallback to scene root
- Trigger: stale selection recovery rule chooses scene root explicitly.
- Transition: `stale(widget) -> active(scene)`.
- Canvas: frame scene shell.
- Tree: focus scene root.
- Inspector: scene editor.
- Mutation implication: the recovery event should be observable in logs.

### Scenario 08: Valid ref remap during migration
- Trigger: migration supplies authoritative old-ref to new-ref mapping.
- Transition: `stale(slot) -> active(slot)` with new ref.
- Canvas: new slot highlight appears.
- Tree: new slot node active.
- Inspector: slot editor for the mapped slot.
- Mutation implication: mapped target must be explicit in the event record.

### Scenario 09: Inspector tab memory with same target
- Trigger: inspector section expands while widget target remains the same.
- Transition: no selection transition.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: local section memory may persist.
- Mutation implication: none.

### Scenario 10: Inspector tab memory with different target
- Trigger: selection switches widget A to widget B.
- Transition: `active(widgetA) -> active(widgetB)`.
- Canvas: move highlight to widget B.
- Tree: activate widget B node.
- Inspector: reset target-local UI that should not leak across identities.
- Mutation implication: pending action payloads must not retarget silently.

### Scenario 11: Fast repeated widget picks
- Trigger: user clicks widget A, B, C quickly.
- Transition: three ordered `active -> active` transitions.
- Canvas: final highlight only on widget C.
- Tree: final active node only C.
- Inspector: final ready target only C.
- Mutation implication: store ordering matters; no stale late paint should resurrect old target UI.

### Scenario 12: Clear on scene unload
- Trigger: current scene unloads.
- Transition: `active(any) -> none`.
- Canvas: clear.
- Tree: clear.
- Inspector: empty editor.
- Mutation implication: pending target-scoped actions should die safely.

### Scenario 13: System boot with no scene data
- Trigger: shell has no scene yet.
- Transition: remain `none`.
- Canvas: shell empty state.
- Tree: empty state.
- Inspector: empty editor.
- Mutation implication: no target-scoped actions available.

### Scenario 14: Widget selection from search results
- Trigger: future global search selects a widget by ref.
- Transition: `none -> active(widget)` or `active(any) -> active(widget)`.
- Canvas: reveal and highlight widget.
- Tree: focus widget node.
- Inspector: widget editor.
- Mutation implication: search must still provide typed refs, not raw DOM handles.

### Scenario 15: Slot accepts prefab insertion
- Trigger: slot target derives insertion capability.
- Transition: selection unchanged.
- Canvas: slot remains framed.
- Tree: slot remains active.
- Inspector: slot editor includes insert action.
- Mutation implication: insert action must use explicit slot target.

### Scenario 16: Slot blocks prefab insertion
- Trigger: capability context says insertion forbidden.
- Transition: selection unchanged.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: slot editor without insert action or clearly disabled action.
- Mutation implication: UI narrowing must align with bridge policy.

### Scenario 17: Widget hidden but still selected
- Trigger: widget visibility false but target still valid.
- Transition: selection unchanged.
- Canvas: may show non-rendered placeholder framing if product chooses.
- Tree: widget remains active.
- Inspector: widget editor.
- Mutation implication: visibility change remains widget-targeted.

### Scenario 18: Structure tree expansion change
- Trigger: user expands a branch unrelated to selection.
- Transition: none.
- Canvas: unchanged.
- Tree: expansion state changes only.
- Inspector: unchanged.
- Mutation implication: none.

### Scenario 19: Hover enters different widget
- Trigger: hover changes, selection does not.
- Transition: none.
- Canvas: hover decoration may change, selection highlight remains.
- Tree: unchanged.
- Inspector: unchanged.
- Mutation implication: hover must not become target identity.

### Scenario 20: Drag handle interaction on selected layout node
- Trigger: user drags a resize handle.
- Transition: selection remains current layout node.
- Canvas: active resize affordance.
- Tree: same node active.
- Inspector: layout editor remains.
- Mutation implication: drag handle is not itself the selected target.

### Scenario 21: Drag handle interaction on unselected layout node
- Trigger: user starts drag from a different node handle.
- Transition: explicit `active -> active(layout-node)` before drag mutation composition.
- Canvas: new layout node becomes active.
- Tree: reflect new active node.
- Inspector: layout editor for the newly selected node.
- Mutation implication: target must be explicit before mutation composition.

### Scenario 22: Widget duplicated through command palette
- Trigger: user duplicates the selected widget.
- Transition: either remain on original or explicitly move to duplicate according to product rule.
- Canvas: reflect the chosen rule clearly.
- Tree: reflect the chosen rule clearly.
- Inspector: must match the chosen post-action selection target.
- Mutation implication: duplicate mutation target and post-selection target are separate concerns.

### Scenario 23: Scene-level reset while widget selected
- Trigger: user invokes scene reset from a shell command.
- Transition: selection may remain widget or become stale depending on structural effect.
- Canvas: must reconcile from authoritative result, not assumption.
- Tree: same.
- Inspector: if target survives, remain ready; if not, unavailable.
- Mutation implication: action target is scene; selection target may be affected later.

### Scenario 24: Widget moved to a different slot but same widget id survives
- Trigger: layout operation rehomes widget.
- Transition: selection can remain active(widget) if ref stays valid.
- Canvas: highlight new location.
- Tree: move active node visually.
- Inspector: widget editor remains.
- Mutation implication: movement should not force unnecessary stale state when the ref remains authoritative.

### Scenario 25: Widget replaced with a new id during prefab swap
- Trigger: swap operation creates a new widget instance.
- Transition: current selection becomes stale unless explicit remap exists.
- Canvas: clear old widget handles.
- Tree: old node clears.
- Inspector: unavailable unless explicit recovery occurs.
- Mutation implication: replacement should be observable, not hidden.

### Scenario 26: Safe mode narrows available actions
- Trigger: same widget selected under safe mode.
- Transition: none.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: fewer actions than advanced mode.
- Mutation implication: UI capability narrowing does not replace bridge enforcement.

### Scenario 27: Advanced mode broadens widget editor groups
- Trigger: same widget selected under advanced mode.
- Transition: none.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: may show more property groups or actions.
- Mutation implication: still explicit target contract.

### Scenario 28: Revision replacement with authoritative validity check pass
- Trigger: model revision changes but selected widget still resolves.
- Transition: `active(widget rev1) -> active(widget rev2)`.
- Canvas: preserve highlight.
- Tree: preserve active node.
- Inspector: remain ready.
- Mutation implication: event should record revision replacement for diagnostics.

### Scenario 29: Revision replacement with validity check fail
- Trigger: selected slot no longer resolves.
- Transition: `active(slot) -> stale(slot)`.
- Canvas: clear slot frame.
- Tree: clear slot active node.
- Inspector: unavailable editor.
- Mutation implication: blocked until recovery.

### Scenario 30: Search results still showing old target after stale event
- Trigger: async UI list lags behind store update.
- Transition: selection already stale.
- Canvas: clear.
- Tree: clear.
- Inspector: unavailable.
- Mutation implication: lagging list must not be allowed to fire stale action payloads.

### Scenario 31: Scene root chosen after explicit clear button
- Trigger: user clears selection, then chooses scene root in tree.
- Transition: `none -> active(scene)`.
- Canvas: frame scene.
- Tree: scene root active.
- Inspector: scene editor.
- Mutation implication: scene target explicit.

### Scenario 32: Slot selected while widget inside remains visually emphasized by runtime
- Trigger: slot chosen, runtime still shows widget content strongly.
- Transition: `active(widget) -> active(slot)`.
- Canvas: slot framing should win over widget highlight.
- Tree: slot node active.
- Inspector: slot editor.
- Mutation implication: visual prominence does not redefine target identity.

### Scenario 33: Widget selected from inspector breadcrumb
- Trigger: user clicks breadcrumb link to nested widget.
- Transition: explicit `active(any) -> active(widget)`.
- Canvas: focus widget.
- Tree: focus widget node.
- Inspector: widget editor.
- Mutation implication: breadcrumb navigation still issues typed selection requests.

### Scenario 34: Unknown target kind attempted by a rogue surface
- Trigger: bad caller tries to select `panel` or raw element.
- Transition: rejected; store unchanged.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: unchanged.
- Mutation implication: fail fast.

### Scenario 35: Multi-select array attempted accidentally
- Trigger: caller passes a list of refs.
- Transition: rejected; store unchanged.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: unchanged.
- Mutation implication: multi-select remains out of scope.

### Scenario 36: Stale selection manually cleared
- Trigger: user chooses clear while target unavailable.
- Transition: `stale -> none`.
- Canvas: clear.
- Tree: clear.
- Inspector: empty editor.
- Mutation implication: safe reset.

### Scenario 37: Stale selection recovered to scene root by system rule
- Trigger: scene-safe fallback policy runs.
- Transition: `stale(widget) -> active(scene)`.
- Canvas: frame scene.
- Tree: scene root active.
- Inspector: scene editor.
- Mutation implication: recovery reason must be visible in transition metadata.

### Scenario 38: Slot capacity change while slot selected
- Trigger: slot policy updates but slot survives.
- Transition: none.
- Canvas: slot still framed.
- Tree: slot still active.
- Inspector: slot editor updates capability context.
- Mutation implication: selection identity stays stable; actions may change.

### Scenario 39: Widget binding warning appears
- Trigger: capability context adds warning.
- Transition: none.
- Canvas: unchanged.
- Tree: unchanged.
- Inspector: widget editor with warning banner.
- Mutation implication: warning narrows user understanding, not target identity.

### Scenario 40: Cross-surface race between tree click and canvas click
- Trigger: two surface events arrive close together.
- Transition: store ordering decides final target.
- Canvas: final highlight must match final store snapshot.
- Tree: same.
- Inspector: same.
- Mutation implication: action payloads must use the committed target they were composed with.

---

## Summary

This matrix is intentionally concrete. It gives the team a way to review selection behavior as a product contract rather than a pile of lucky UI side effects.
