import assert from "node:assert/strict";
import test from "node:test";

import { CANON_LAYER_IDS } from "../../src/layers/layerIds.js";
import { createStableResolvedSnapshot, resolveLayerFlags } from "../../src/layers/resolveLayerFlags.js";

test("default fallback is neutral with all flags off", () => {
  const resolved = resolveLayerFlags({ search: "", isDevelopment: true });

  assert.equal(resolved.source, "default");
  assert.equal(resolved.profile, "neutral");
  assert.equal(resolved.layersDirective, null);
  assert.equal(resolved.enabledLayerIds.length, 0);
  assert.deepEqual(resolved.disabledLayerIds, [...CANON_LAYER_IDS]);
});

test("layerProfile=neutral keeps all layers off", () => {
  const resolved = resolveLayerFlags({ search: "?layerProfile=neutral", isDevelopment: true });
  assert.equal(resolved.source, "layerProfile");
  assert.equal(resolved.profile, "neutral");
  assert.equal(resolved.enabledLayerIds.length, 0);
});

test("layerProfile=perf disables expensive effects and motion", () => {
  const resolved = resolveLayerFlags({ search: "?layerProfile=perf", isDevelopment: true });

  assert.equal(resolved.source, "layerProfile");
  assert.equal(resolved.profile, "perf");
  assert.deepEqual(resolved.enabledLayerIds, ["card.innerStroke", "frame.bezel", "inset.shadow"]);
  assert.equal(resolved.flags["motion.enabled"], false);
  assert.equal(resolved.flags["card.blur"], false);
  assert.equal(resolved.flags["stage.noise"], false);
  assert.equal(resolved.flags["stage.scanlines"], false);
});

test("layerProfile=fx enables all canonical hooks", () => {
  const resolved = resolveLayerFlags({ search: "?layerProfile=fx", isDevelopment: true });
  assert.equal(resolved.source, "layerProfile");
  assert.equal(resolved.profile, "fx");
  assert.deepEqual(resolved.enabledLayerIds, [...CANON_LAYER_IDS]);
});

test("layers=none overrides any profile", () => {
  const resolved = resolveLayerFlags({ search: "?layerProfile=fx&layers=none", isDevelopment: true });
  assert.equal(resolved.source, "layers");
  assert.equal(resolved.layersDirective, "none");
  assert.equal(resolved.enabledLayerIds.length, 0);
});

test("layers=all overrides any profile", () => {
  const resolved = resolveLayerFlags({ search: "?layerProfile=neutral&layers=all", isDevelopment: true });
  assert.equal(resolved.source, "layers");
  assert.equal(resolved.layersDirective, "all");
  assert.deepEqual(resolved.enabledLayerIds, [...CANON_LAYER_IDS]);
});

test("layers allowlist overrides profile and unknown IDs are tracked", () => {
  const resolved = resolveLayerFlags({
    search: "?layerProfile=perf&layers=inset.shadow,card.blur,unknown.layer,stage.noise",
    isDevelopment: true,
  });

  assert.equal(resolved.source, "layers");
  assert.equal(resolved.layersDirective, "allowlist");
  assert.deepEqual(resolved.enabledLayerIds, ["stage.noise", "card.blur", "inset.shadow"]);
  assert.deepEqual(resolved.unknownLayerIds, ["unknown.layer"]);
});

test("layers explicit prop has top priority over search", () => {
  const resolved = resolveLayerFlags({
    search: "?layers=none&layerProfile=fx",
    layers: "card.blur,frame.bezel",
    layerProfile: "perf",
    isDevelopment: true,
  });

  assert.equal(resolved.source, "layers");
  assert.equal(resolved.layersDirective, "allowlist");
  assert.deepEqual(resolved.enabledLayerIds, ["card.blur", "frame.bezel"]);
});

test("debug panel toggle only enabled in development", () => {
  const development = resolveLayerFlags({ search: "?debug=1", isDevelopment: true });
  const production = resolveLayerFlags({ search: "?debug=1", isDevelopment: false });

  assert.equal(development.debugRequested, true);
  assert.equal(development.debugPanelEnabled, true);
  assert.equal(production.debugRequested, true);
  assert.equal(production.debugPanelEnabled, false);
});

test("snapshot remains deterministic for same input", () => {
  const resolved = resolveLayerFlags({
    search: "?layerProfile=perf&debug=1",
    isDevelopment: true,
  });

  const left = createStableResolvedSnapshot(resolved);
  const right = createStableResolvedSnapshot(resolveLayerFlags({
    search: "?layerProfile=perf&debug=1",
    isDevelopment: true,
  }));

  assert.equal(left, right);
});
