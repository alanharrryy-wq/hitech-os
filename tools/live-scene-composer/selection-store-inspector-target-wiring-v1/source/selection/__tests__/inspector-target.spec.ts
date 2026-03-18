import { strict as assert } from "node:assert";
import { deriveInspectorTarget } from "../inspector-target";
import {
  fixtureLayoutCapabilityContext,
  fixtureLayoutNodeSelection,
  fixtureNoSelection,
  fixtureStaleWidgetSelection,
  fixtureWidgetCapabilityContext,
  fixtureWidgetSelection
} from "../selection-fixtures";

function test_empty_target(): void {
  const target = deriveInspectorTarget(fixtureNoSelection());
  assert.equal(target.status, "empty");
  assert.equal(target.editorKind, "empty-editor");
}

function test_widget_target(): void {
  const target = deriveInspectorTarget(fixtureWidgetSelection(), fixtureWidgetCapabilityContext());
  assert.equal(target.status, "ready");
  assert.equal(target.editorKind, "widget-editor");
  assert.ok(target.propertyGroups.includes("widget-style"));
}

function test_layout_target(): void {
  const target = deriveInspectorTarget(fixtureLayoutNodeSelection(), fixtureLayoutCapabilityContext());
  assert.equal(target.status, "ready");
  assert.equal(target.editorKind, "layout-node-editor");
  assert.ok(target.actions.includes("reorder-layout-node"));
}

function test_stale_target(): void {
  const target = deriveInspectorTarget(fixtureStaleWidgetSelection(), fixtureWidgetCapabilityContext());
  assert.equal(target.status, "unavailable");
  assert.equal(target.editorKind, "unavailable-editor");
  assert.equal(target.actions.length, 0);
}

function run(): void {
  test_empty_target();
  test_widget_target();
  test_layout_target();
  test_stale_target();
  console.log("inspector-target.spec.ts passed");
}

run();
