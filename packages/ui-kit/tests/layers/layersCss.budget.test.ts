import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

const LAYERS_CSS_PATH = resolve(process.cwd(), "packages/ui-kit/src/styles/layers.css");
const LAYERS_CSS_TEXT = readFileSync(LAYERS_CSS_PATH, "utf8");

test("layers.css contains all canonical data-layer hooks", () => {
  const requiredHooks = [
    'data-layer-stage-noise="on"',
    'data-layer-stage-scanlines="on"',
    'data-layer-stage-glow="on"',
    'data-layer-card-inner-stroke="on"',
    'data-layer-card-specular="on"',
    'data-layer-card-grain="on"',
    'data-layer-card-blur="on"',
    'data-layer-motion="off"',
    'data-layer-frame-bezel="on"',
    'data-layer-inset-shadow="on"',
  ];

  for (const hook of requiredHooks) {
    assert.equal(LAYERS_CSS_TEXT.includes(hook), true, `missing css hook: ${hook}`);
  }
});

test("blur budget is guarded by @supports and flag", () => {
  assert.equal(LAYERS_CSS_TEXT.includes('.ui-layer-glass-card[data-layer-card-blur="on"]'), true);
  assert.equal(LAYERS_CSS_TEXT.includes('@supports (backdrop-filter: blur(1px))'), true);
});

test("motion off budget disables transitions and animations", () => {
  const requiredMotionBudgetTokens = [
    '[data-layer-motion="off"]',
    'animation: none !important;',
    'transition-duration: 0s !important;',
    'transition-property: none !important;',
  ];

  for (const token of requiredMotionBudgetTokens) {
    assert.equal(LAYERS_CSS_TEXT.includes(token), true, `missing motion budget token: ${token}`);
  }
});

test("fx remains hook-based and does not enforce heavy styling via profile class", () => {
  assert.equal(LAYERS_CSS_TEXT.includes('.profile-fx'), false);
  assert.equal(LAYERS_CSS_TEXT.includes('[data-layer-profile="fx"]'), false);
});
