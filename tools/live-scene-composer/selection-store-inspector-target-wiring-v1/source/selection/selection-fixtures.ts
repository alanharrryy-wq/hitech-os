import {
  createActiveSelection,
  createLayoutNodeRef,
  createNoSelection,
  createSceneRef,
  createSlotRef,
  createWidgetRef,
  createStaleSelection,
  type InspectorCapabilityContext,
  type SelectionState
} from "./contracts";
import { createDefaultCapabilityContext } from "./inspector-target";

export const FIXTURE_SCENE_ID = "scene-home-dashboard";

export function fixtureNoSelection(): SelectionState {
  return createNoSelection();
}

export function fixtureSceneSelection(revision = "rev-001"): SelectionState {
  return createActiveSelection({
    ref: createSceneRef(FIXTURE_SCENE_ID),
    origin: "system",
    revision,
    reason: "initial-select",
    context: { breadcrumb: ["Home Dashboard"] }
  });
}

export function fixtureLayoutNodeSelection(revision = "rev-001"): SelectionState {
  return createActiveSelection({
    ref: createLayoutNodeRef(FIXTURE_SCENE_ID, "layout-hero"),
    origin: "structure-tree",
    revision,
    reason: "surface-select",
    context: { breadcrumb: ["Home Dashboard", "Hero Layout"] }
  });
}

export function fixtureSlotSelection(revision = "rev-001"): SelectionState {
  return createActiveSelection({
    ref: createSlotRef(FIXTURE_SCENE_ID, "slot-kpi-top-left"),
    origin: "canvas",
    revision,
    reason: "surface-select",
    context: { breadcrumb: ["Home Dashboard", "KPI Slot"] }
  });
}

export function fixtureWidgetSelection(revision = "rev-001"): SelectionState {
  return createActiveSelection({
    ref: createWidgetRef(FIXTURE_SCENE_ID, "widget-kpi-revenue", "slot-kpi-top-left"),
    origin: "canvas",
    revision,
    reason: "surface-select",
    context: { breadcrumb: ["Home Dashboard", "Revenue KPI"] }
  });
}

export function fixtureStaleWidgetSelection(revision = "rev-002"): SelectionState {
  const active = fixtureWidgetSelection("rev-001");
  return createStaleSelection(active as Exclude<SelectionState, { status: "none" }>, "entity-removed", revision);
}

export function fixtureWidgetCapabilityContext(): InspectorCapabilityContext {
  return createDefaultCapabilityContext({
    editable: true,
    removable: true,
    resettable: true,
    styleEditable: true,
    propsEditable: true,
    warnings: []
  });
}

export function fixtureLayoutCapabilityContext(): InspectorCapabilityContext {
  return createDefaultCapabilityContext({
    editable: true,
    reorderable: true,
    resizable: true,
    resettable: true,
    styleEditable: true,
    propsEditable: false
  });
}
