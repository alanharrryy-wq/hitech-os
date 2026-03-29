import { strict as assert } from "node:assert";
import { createWidgetRef } from "../contracts";
import { getSelectionKey, matchesSelectionRef } from "../selection-selectors";
import { createSelectionStore } from "../selection-store";

function test_selection_key(): void {
  const store = createSelectionStore();
  store.select({
    ref: createWidgetRef("scene-1", "widget-2", "slot-z"),
    origin: "canvas",
    revision: "rev-1"
  });
  const key = getSelectionKey(store.getSnapshot());
  assert.equal(key, "widget:scene-1:widget-2");
}

function test_ref_match(): void {
  const ref = createWidgetRef("scene-1", "widget-2", "slot-z");
  const store = createSelectionStore();
  store.select({
    ref,
    origin: "canvas",
    revision: "rev-1"
  });
  assert.equal(matchesSelectionRef(store.getSnapshot().selection, ref), true);
}

function run(): void {
  test_selection_key();
  test_ref_match();
  console.log("selection-selectors.spec.ts passed");
}

run();
