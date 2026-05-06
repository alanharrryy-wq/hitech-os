import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const configPath = path.join(root, "config/prisma-visual-os/prisma-visual-controls.active.json");
const outPath = path.join(root, "styles/prisma-visual-os/prisma-visual-controls.generated.css");
const presets = new Set(["BLACK_PREMIUM", "LIGHT_OPERATIONAL", "DUAL_BALANCE", "POS_TOUCH_REFERENCE", "PC_DENSE_ADMIN", "MOBILE_PULSE"]);
const surfaces = new Set(["tablet-pos", "tablet-checkout", "tablet-shell", "pc-backoffice", "mobile-pulse"]);
const requiredLayers = ["background", "atmosphere", "shell", "surface", "content", "action", "state", "focus", "overlay", "debug"];

function fail(message) {
  console.error(`ERROR ${message}`);
  process.exit(1);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function numberInRange(value, min, max, name) {
  if (typeof value !== "number" || value < min || value > max) fail(`${name} fuera de rango ${min}-${max}: ${value}`);
}

const config = readJson(configPath);
if (!presets.has(config.preset)) fail(`preset no permitido: ${config.preset}`);
if (!surfaces.has(config.surface)) fail(`surface no permitida: ${config.surface}`);
for (const key of ["glass", "glow", "depth", "density", "contrast", "motion", "touch", "actionWeight", "stateSignal"]) {
  numberInRange(config.controls?.[key], 0, 100, `controls.${key}`);
}
for (const layer of requiredLayers) {
  if (!config.layers?.[layer]) fail(`layer faltante: ${layer}`);
  numberInRange(config.layers[layer].strength, 0, 100, `layers.${layer}.strength`);
}
if (config.controls.contrast < 68 && config.controls.glow > 75) fail("combinacion bloqueada: contraste bajo con glow alto");
if (config.surface === "tablet-pos" && config.controls.touch < 80) fail("combinacion bloqueada: Tablet POS requiere touch >= 80");
if ((config.surface === "tablet-checkout" || config.surface === "tablet-pos") && config.controls.actionWeight < 86) fail("combinacion bloqueada: cobro/POS requiere actionWeight >= 86");

const css = `/*
  PRISMA Visual OS 00E - generated from config/prisma-visual-os/prisma-visual-controls.active.json.
  Regenerate with: node tools/prisma-visual-os/generate_prisma_visual_os_controls_00e.mjs
*/
:root,
[data-prisma-vos-runtime="00E"] {
  --prisma-vos-active-preset: ${config.preset};
  --prisma-vos-active-surface: ${config.surface};
  --prisma-vos-control-glass: ${config.controls.glass};
  --prisma-vos-control-glow: ${config.controls.glow};
  --prisma-vos-control-depth: ${config.controls.depth};
  --prisma-vos-control-density: ${config.controls.density};
  --prisma-vos-control-contrast: ${config.controls.contrast};
  --prisma-vos-control-motion: ${config.controls.motion};
  --prisma-vos-control-touch: ${config.controls.touch};
  --prisma-vos-control-action-weight: ${config.controls.actionWeight};
  --prisma-vos-control-state-signal: ${config.controls.stateSignal};
  --prisma-vos-layer-background-strength: ${config.layers.background.strength};
  --prisma-vos-layer-atmosphere-strength: ${config.layers.atmosphere.strength};
  --prisma-vos-layer-shell-strength: ${config.layers.shell.strength};
  --prisma-vos-layer-surface-strength: ${config.layers.surface.strength};
  --prisma-vos-layer-content-strength: ${config.layers.content.strength};
  --prisma-vos-layer-action-strength: ${config.layers.action.strength};
  --prisma-vos-layer-state-strength: ${config.layers.state.strength};
  --prisma-vos-layer-focus-strength: ${config.layers.focus.strength};
  --prisma-vos-layer-overlay-strength: ${config.layers.overlay.strength};
  --prisma-vos-layer-debug-strength: ${config.layers.debug.strength};
  --prisma-vos-min-touch-target-runtime: ${config.safety.minTouchTargetPx}px;
  --prisma-vos-pos-primary-touch-target-runtime: ${config.safety.posPrimaryTouchTargetPx}px;
  --prisma-vos-runtime-panel-blur: ${Math.max(12, Math.round(config.controls.glass / 4 + 5))}px;
  --prisma-vos-runtime-card-radius: ${Math.max(16, Math.round(config.controls.depth / 5 + 6))}px;
  --prisma-vos-runtime-action-shadow: 0 24px 64px rgba(232, 189, 103, ${(config.controls.actionWeight / 400).toFixed(2)});
}

[data-prisma-vsurface="tablet-pos"],
[data-prisma-vsurface="tablet-checkout"],
[data-prisma-visual-surface="tablet-pos"],
[data-prisma-visual-surface="tablet-checkout"] {
  --prisma-vos-runtime-surface-border: color-mix(in srgb, var(--prisma-accent-gold, #e8bd67) ${Math.round(config.layers.surface.strength / 2)}%, var(--prisma-border-soft, rgba(255,255,255,.1)));
  --prisma-vos-runtime-action-border: color-mix(in srgb, var(--prisma-accent-gold, #e8bd67) ${Math.round(config.layers.action.strength * 0.65)}%, var(--prisma-border-soft, rgba(255,255,255,.1)));
  --prisma-vos-runtime-total-glow: 0 0 38px rgba(232, 189, 103, ${(config.layers.action.strength / 600).toFixed(2)});
  --prisma-vos-runtime-safe-motion: ${Math.max(80, 240 - config.controls.motion * 2)}ms;
}

@media (prefers-reduced-motion: reduce) {
  :root,
  [data-prisma-vos-runtime="00E"] {
    --prisma-vos-runtime-safe-motion: 1ms;
  }
}
`;
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, css, "utf8");
console.log(`OK generated ${path.relative(root, outPath)}`);
