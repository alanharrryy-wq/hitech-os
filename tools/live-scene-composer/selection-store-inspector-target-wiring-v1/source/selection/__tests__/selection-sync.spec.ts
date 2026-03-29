import { strict as assert } from "node:assert";
import { buildSelectionSurfaceSyncPlan, summarizeSurfaceSyncPlan } from "../selection-sync";
import { fixtureNoSelection, fixtureStaleWidgetSelection, fixtureWidgetSelection } from "../selection-fixtures";

function test_none_sync_plan(): void {
  const plan = buildSelectionSurfaceSyncPlan(fixtureNoSelection());
  assert.equal(plan.instructions.length, 3);
  assert.deepEqual(summarizeSurfaceSyncPlan(plan), [
    "canvas:clear:none",
    "structure-tree:clear:none",
    "inspector:show-empty:none"
  ]);
}

function test_widget_sync_plan(): void {
  const plan = buildSelectionSurfaceSyncPlan(fixtureWidgetSelection());
  assert.equal(plan.instructions[0].action, "highlight-widget");
  assert.equal(plan.instructions[2].action, "show-ready");
}

function test_stale_sync_plan(): void {
  const plan = buildSelectionSurfaceSyncPlan(fixtureStaleWidgetSelection());
  assert.deepEqual(summarizeSurfaceSyncPlan(plan), [
    "canvas:clear:widget",
    "structure-tree:clear:widget",
    "inspector:show-unavailable:widget"
  ]);
}

function run(): void {
  test_none_sync_plan();
  test_widget_sync_plan();
  test_stale_sync_plan();
  console.log("selection-sync.spec.ts passed");
}

run();
