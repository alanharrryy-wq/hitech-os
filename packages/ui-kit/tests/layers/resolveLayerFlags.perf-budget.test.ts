import assert from "node:assert/strict";
import test from "node:test";

import { EXPENSIVE_LAYER_IDS } from "../../src/layers/layerIds.js";
import { resolveLayerFlags } from "../../src/layers/resolveLayerFlags.js";

test("perf profile forces expensive features off", () => {
  const resolved = resolveLayerFlags({ search: "?layerProfile=perf", isDevelopment: true });

  for (const expensive of EXPENSIVE_LAYER_IDS) {
    assert.equal(resolved.flags[expensive], false, `expected expensive flag to be off in perf: ${expensive}`);
  }

  assert.equal(resolved.budget.motionEnabled, false);
  assert.equal(resolved.budget.blurEnabled, false);
  assert.deepEqual(resolved.budget.expensiveEnabledLayerIds, []);
});

test("perf profile still remains deterministic with query order changes", () => {
  const queryA = "?layerProfile=perf&debug=1";
  const queryB = "?debug=1&layerProfile=perf";

  const left = resolveLayerFlags({ search: queryA, isDevelopment: true });
  const right = resolveLayerFlags({ search: queryB, isDevelopment: true });

  assert.deepEqual(left.enabledLayerIds, right.enabledLayerIds);
  assert.deepEqual(left.budget, right.budget);
});

test("layers override can intentionally enable expensive feature over perf", () => {
  const resolved = resolveLayerFlags({
    search: "?layerProfile=perf&layers=card.blur,motion.enabled",
    isDevelopment: true,
  });

  assert.equal(resolved.source, "layers");
  assert.equal(resolved.flags["card.blur"], true);
  assert.equal(resolved.flags["motion.enabled"], true);
  assert.deepEqual(resolved.enabledLayerIds, ["card.blur", "motion.enabled"]);
});
