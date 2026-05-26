#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || process.env.PRISMA_ROOT || process.cwd());
const sourceDir = process.env.PRISMA_TABLET_VISUAL_SOURCE_DIR
  ? path.resolve(process.env.PRISMA_TABLET_VISUAL_SOURCE_DIR)
  : path.join(root, 'docs', 'design', 'tablet-light-visual-preset-engine');
const report = { id: 'prisma-tablet-background-storm-glass-v8', root, sourceDir, ok: true, checks: [] };
function check(name, ok, detail='') { report.checks.push({ name, ok: Boolean(ok), detail }); if (!ok) report.ok = false; }
function read(file) { return fs.readFileSync(file, 'utf8'); }
function exists(rel) { return fs.existsSync(path.join(sourceDir, rel)); }

const required = [
  'tablet-codex-background-gallery-smoke-test.html',
  'prisma-tablet-background-storm-glass-v8.css',
  'prisma-tablet-background-storm-glass-v8.js',
  'tablet-background-presets.storm-glass-v8.json',
  'tablet-background-presets.storm-glass-v8.patch.json',
  'assets/backgrounds/storm-cloud-operations-real.jpg'
];
for (const rel of required) check(`required:${rel}`, exists(rel), path.join(sourceDir, rel));

let html='', css='', js='', presets=null;
try { html = read(path.join(sourceDir, 'tablet-codex-background-gallery-smoke-test.html')); } catch {}
try { css = read(path.join(sourceDir, 'prisma-tablet-background-storm-glass-v8.css')); } catch {}
try { js = read(path.join(sourceDir, 'prisma-tablet-background-storm-glass-v8.js')); } catch {}
try { presets = JSON.parse(read(path.join(sourceDir, 'tablet-background-presets.storm-glass-v8.json'))); check('json_parse:tablet-background-presets.storm-glass-v8.json', true, 'parse ok'); } catch (error) { check('json_parse:tablet-background-presets.storm-glass-v8.json', false, String(error)); }

check('html_references_v8_css', html.includes('prisma-tablet-background-storm-glass-v8.css'));
check('html_references_v8_js', html.includes('prisma-tablet-background-storm-glass-v8.js'));
check('html_default_storm_real', html.includes('data-preset="storm-cloud-operations-real"'));
check('css_uses_real_storm_image', css.includes('storm-cloud-operations-real.jpg'));
check('css_backdrop_filter_present', /backdrop-filter\s*:\s*blur/i.test(css));
check('css_hydro_rim_present', /mask-composite|hydro|prisma-hydro/i.test(css));
check('reduced_motion_present', /prefers-reduced-motion\s*:\s*reduce/i.test(css));
check('touch_target_48px_present', /min-height\s*:\s*48px|min-width\s*:\s*48px|48px/.test(css + html));
check('js_sets_storm_default', js.includes("setPreset('storm-cloud-operations-real')"));
if (presets) {
  const p = (presets.presets || []).find(x => x.id === 'storm-cloud-operations-real');
  check('preset_storm_exists', Boolean(p));
  check('preset_storm_has_image_asset', Boolean(p && p.imageAsset && p.imageAsset.includes('storm-cloud-operations-real.jpg')));
  check('dark_showcase_not_product_default', Boolean(p && p.darkShowcase === true && p.applyDefault === false));
  check('policy_no_pos_mutation', Boolean(presets.policy && presets.policy.doNotMutatePos === true));
  check('light_candidate_remains_soft_clouds', presets.policy?.productLightPresetId === 'tablet-soft-gray-clouds', String(presets.policy?.productLightPresetId));
}

// Confirm no productive POS file is part of this verifier's intended write set.
const routePage = path.join(root, 'products', 'tablet', 'app', 'app', 'visual-os', 'tablet-background-gallery', 'page.tsx');
check('route_page_exists', fs.existsSync(routePage), routePage);
console.log(JSON.stringify(report, null, 2));
process.exit(report.ok ? 0 : 1);
