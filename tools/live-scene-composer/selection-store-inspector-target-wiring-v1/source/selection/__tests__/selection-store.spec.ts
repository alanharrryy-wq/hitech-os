import { strict as assert } from "node:assert";
import { createWidgetRef } from "../contracts";
import { createSelectionStore } from "../selection-store";

function test_select_and_clear(): void {
  const store = createSelectionStore();
  const seen: string[] = [];
  store.subscribe((snapshot) => {
    seen.push(`${snapshot.version}:${snapshot.selection.status}`);
  });

  const selected = store.select({
    ref: createWidgetRef("scene-1", "widget-1", "slot-a"),
    origin: "canvas",
    revision: "rev-1"
  });
  assert.equal(selected.selection.status, "active");
  assert.equal(selected.selection.ref.kind, "widget");

  const cleared = store.clear();
  assert.equal(cleared.selection.status, "none");
  assert.deepEqual(seen, ["1:active", "2:none"]);
}

function test_mark_stale_on_revision_replace(): void {
  const store = createSelectionStore();
  store.select({
    ref: createWidgetRef("scene-1", "widget-1"),
    origin: "canvas",
    revision: "rev-1"
  });
  const next = store.replaceRevision("rev-2");
  assert.equal(next.selection.status, "stale");
}

function test_explicit_recovery(): void {
  const store = createSelectionStore();
  store.select({
    ref: createWidgetRef("scene-1", "widget-1"),
    origin: "canvas",
    revision: "rev-1"
  });
  store.markStale("entity-removed", "rev-2");
  const recovered = store.recover({
    ref: createWidgetRef("scene-1", "widget-2"),
    origin: "system",
    revision: "rev-2",
    recoveryReason: "explicit-recovery"
  });
  assert.equal(recovered.selection.status, "active");
  assert.equal(recovered.selection.ref.kind, "widget");
  assert.equal(recovered.selection.ref.widgetId, "widget-2");
}

function run(): void {
  test_select_and_clear();
  test_mark_stale_on_revision_replace();
  test_explicit_recovery();
  console.log("selection-store.spec.ts passed");
}

run();
