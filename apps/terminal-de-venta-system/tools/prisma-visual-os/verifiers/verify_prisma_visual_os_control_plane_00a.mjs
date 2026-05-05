#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.argv.includes('--root')
  ? path.resolve(process.argv[process.argv.indexOf('--root') + 1])
  : process.cwd();

const rels = {
  controls: 'products/shared-ui/prisma/visual-os/prisma-visual-os.controls.json',
  presets: 'products/shared-ui/prisma/visual-os/prisma-visual-os.presets.json',
  recipes: 'products/shared-ui/prisma/visual-os/prisma-visual-os.recipes.json',
  scorecard: 'products/shared-ui/prisma/visual-os/prisma-visual-os.scorecard.json',
  css: 'products/shared-ui/prisma/visual-os/prisma-visual-os.tokens.css',
  doc: 'docs/design/PRISMA_VISUAL_OS_CONTROL_PLANE_00A.md',
  manifest: 'manifests/PRISMA_VISUAL_OS_CONTROL_PLANE_00A.manifest.json'
};

function fail(message) {
  console.error(`[VOS 00A FAIL] ${message}`);
  process.exit(1);
}

function readJson(rel) {
  const p = path.join(ROOT, rel);
  if (!fs.existsSync(p)) fail(`Missing ${rel}`);
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (error) {
    fail(`Invalid JSON ${rel}: ${error.message}`);
  }
}

for (const rel of Object.values(rels)) {
  if (!fs.existsSync(path.join(ROOT, rel))) fail(`Missing ${rel}`);
}

const controls = readJson(rels.controls);
const presets = readJson(rels.presets);
const recipes = readJson(rels.recipes);
const scorecard = readJson(rels.scorecard);
const manifest = readJson(rels.manifest);
const css = fs.readFileSync(path.join(ROOT, rels.css), 'utf8');

if (!Array.isArray(controls.controls) || controls.controls.length !== 12) {
  fail(`Expected exactly 12 controls, got ${controls.controls?.length}`);
}

const ids = new Set();
for (const control of controls.controls) {
  if (!control.id || ids.has(control.id)) fail(`Duplicate or empty control id: ${control.id}`);
  ids.add(control.id);
  if (!control.type) fail(`Control ${control.id} has no type`);
  if (control.type === 'number') {
    if (typeof control.min !== 'number' || typeof control.max !== 'number') fail(`Control ${control.id} has invalid range`);
    if (control.min >= control.max) fail(`Control ${control.id} min >= max`);
    if (typeof control.default !== 'number') fail(`Control ${control.id} default must be number`);
    if (control.default < control.min || control.default > control.max) fail(`Control ${control.id} default out of range`);
  }
  if (control.type === 'enum') {
    if (!Array.isArray(control.values) || !control.values.includes(control.default)) fail(`Control ${control.id} invalid enum default`);
  }
}

for (const [presetName, preset] of Object.entries(presets.presets || {})) {
  if (!preset.intent) fail(`Preset ${presetName} missing intent`);
  for (const [key, value] of Object.entries(preset)) {
    if (key === 'intent') continue;
    if (!ids.has(key)) fail(`Preset ${presetName} references unknown control ${key}`);
    const control = controls.controls.find((x) => x.id === key);
    if (control.type === 'number' && (typeof value !== 'number' || value < control.min || value > control.max)) {
      fail(`Preset ${presetName}.${key} out of range`);
    }
    if (control.type === 'enum' && !control.values.includes(value)) {
      fail(`Preset ${presetName}.${key} invalid enum ${value}`);
    }
  }
}

if (!Array.isArray(recipes.recipes) || recipes.recipes.length < 8) fail('Expected at least 8 recipes');
for (const recipe of recipes.recipes) {
  if (!recipe.id) fail('Recipe without id');
  for (const controlId of recipe.controls || []) {
    if (!ids.has(controlId)) fail(`Recipe ${recipe.id} references unknown control ${controlId}`);
  }
  if (!Array.isArray(recipe.must_not) || recipe.must_not.length === 0) fail(`Recipe ${recipe.id} missing must_not guardrails`);
}

if (!Array.isArray(scorecard.axes) || scorecard.axes.length < 6) fail('Scorecard axes incomplete');
for (const required of ['--prisma-vos-operational-contrast', '--prisma-vos-depth-glass', '--prisma-vos-critical-action-weight', '--prisma-vos-state-signal-strength']) {
  if (!css.includes(required)) fail(`CSS contract missing ${required}`);
}

if (manifest.package !== 'PRISMA_VISUAL_OS_CONTROL_PLANE_00A_20260503_v01') fail('Unexpected package manifest id');
if (!Array.isArray(manifest.files) || manifest.files.length < 10) fail('Manifest file list incomplete');

console.log('[VOS 00A OK] Control plane verified');
console.log(`[VOS 00A OK] Controls: ${controls.controls.length}`);
console.log(`[VOS 00A OK] Presets: ${Object.keys(presets.presets).length}`);
console.log(`[VOS 00A OK] Recipes: ${recipes.recipes.length}`);
console.log(`[VOS 00A OK] Root: ${ROOT}`);
