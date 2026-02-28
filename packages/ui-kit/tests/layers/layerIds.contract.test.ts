import assert from "node:assert/strict";
import test from "node:test";

import {
  CANON_LAYER_IDS,
  EXPENSIVE_LAYER_IDS,
  LAYER_DATA_ATTR_MAP,
  PROFILE_LAYER_FLAGS,
  createAllLayersOff,
  getEnabledLayerIds,
  isLayerId,
  stableSortLayerIds,
} from "../../src/layers/layerIds.js";

test("canonical layer IDs remain exact and ordered", () => {
  assert.deepEqual(CANON_LAYER_IDS, [
    "stage.noise",
    "stage.scanlines",
    "stage.glow",
    "card.innerStroke",
    "card.specular",
    "card.grain",
    "card.blur",
    "motion.enabled",
    "frame.bezel",
    "inset.shadow",
  ]);
});

test("each canonical layer has an exact data-layer-* mapping", () => {
  assert.deepEqual(LAYER_DATA_ATTR_MAP, {
    "stage.noise": "data-layer-stage-noise",
    "stage.scanlines": "data-layer-stage-scanlines",
    "stage.glow": "data-layer-stage-glow",
    "card.innerStroke": "data-layer-card-inner-stroke",
    "card.specular": "data-layer-card-specular",
    "card.grain": "data-layer-card-grain",
    "card.blur": "data-layer-card-blur",
    "motion.enabled": "data-layer-motion",
    "frame.bezel": "data-layer-frame-bezel",
    "inset.shadow": "data-layer-inset-shadow",
  });
});

test("isLayerId only accepts canonical IDs", () => {
  for (const id of CANON_LAYER_IDS) {
    assert.equal(isLayerId(id), true);
  }

  assert.equal(isLayerId("stage-noise"), false);
  assert.equal(isLayerId("card.blurr"), false);
  assert.equal(isLayerId("motion"), false);
});

test("neutral profile is fully off", () => {
  assert.deepEqual(getEnabledLayerIds(PROFILE_LAYER_FLAGS.neutral), []);
});

test("perf profile keeps only structural low-cost layers", () => {
  assert.deepEqual(getEnabledLayerIds(PROFILE_LAYER_FLAGS.perf), ["card.innerStroke", "frame.bezel", "inset.shadow"]);
});

test("perf profile disables all expensive layers", () => {
  const enabledPerf = new Set(getEnabledLayerIds(PROFILE_LAYER_FLAGS.perf));
  for (const expensiveLayer of EXPENSIVE_LAYER_IDS) {
    assert.equal(enabledPerf.has(expensiveLayer), false);
  }
});

test("fx profile enables every hook", () => {
  assert.deepEqual(getEnabledLayerIds(PROFILE_LAYER_FLAGS.fx), [...CANON_LAYER_IDS]);
});

test("stableSortLayerIds always returns canonical order", () => {
  assert.deepEqual(stableSortLayerIds(["inset.shadow", "stage.noise", "card.blur"]), [
    "stage.noise",
    "card.blur",
    "inset.shadow",
  ]);
});

test("createAllLayersOff creates all false values", () => {
  const flags = createAllLayersOff();
  for (const id of CANON_LAYER_IDS) {
    assert.equal(flags[id], false);
  }
});
