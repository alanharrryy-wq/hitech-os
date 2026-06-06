import fs from 'node:fs';
import path from 'node:path';

const cwd = process.cwd();
const candidates = [
  process.env.PRISMA_PC_APP,
  cwd,
  path.join(cwd, 'products', 'pc', 'app'),
  path.join(cwd, 'apps', 'terminal-de-venta-system', 'products', 'pc', 'app'),
  'F:\\repos\\hitech-os\\apps\\terminal-de-venta-system\\products\\pc\\app',
].filter(Boolean);

function exists(p) { return fs.existsSync(p); }
function read(p) { return fs.readFileSync(p, 'utf8'); }
function findPcApp() {
  for (const candidate of candidates) {
    if (!candidate) continue;
    if (exists(path.join(candidate, 'package.json')) && exists(path.join(candidate, 'components'))) return candidate;
  }
  return null;
}
function fail(msg) {
  console.error('[glass-fix7-calibration] FAIL ' + msg);
  process.exit(1);
}
function ok(msg) { console.log('[glass-fix7-calibration] OK ' + msg); }
function must(text, needle, label) {
  if (!text.includes(needle)) fail(label + ' missing: ' + needle);
  ok(label);
}
function mustNot(text, needle, label) {
  if (text.includes(needle)) fail(label + ' forbidden: ' + needle);
  ok(label);
}
function cssVarPx(text, name) {
  const m = text.match(new RegExp(`${name}\\s*:\\s*([0-9.]+)px`));
  return m ? Number(m[1]) : NaN;
}

const pcApp = findPcApp();
if (!pcApp) fail('Could not detect products/pc/app. cwd=' + cwd);

const componentTsx = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx');
const componentCss = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css');
const appPage = path.join(pcApp, 'app', 'referencia-visual', 'liquid-glass-capsules', 'page.tsx');
const legacyPage = path.join(pcApp, 'referencia-visual', 'liquid-glass-capsules', 'page.tsx');

for (const file of [componentTsx, componentCss, appPage, legacyPage]) {
  if (!exists(file)) fail('missing required file: ' + file);
}

const tsx = read(componentTsx);
const css = read(componentCss);
const appPageText = read(appPage);
const legacyPageText = read(legacyPage);

if (!tsx.startsWith("'use client';")) fail("component must start with exact 'use client';");
ok("component starts with 'use client';");

for (const layer of ['styles.refraction', 'styles.lobeLens', 'styles.edgeFrame', 'styles.volumeFrame', 'styles.innerFrame', 'styles.specular', 'styles.liquidSheen', 'styles.content']) {
  must(tsx, layer, 'tsx optical layer ' + layer);
}

const blur = cssVarPx(css, '--pgc-blur');
if (!(Number.isFinite(blur) && blur <= 0.08)) fail('--pgc-blur must stay nearly zero <= 0.08px, got ' + blur);
ok('nearly zero blur ' + blur + 'px');

must(css, '--pgc-min-width: 136px;', 'base pill min-width calibrated');
must(css, '.root[data-density="regular"] { --pgc-height: 46px; --pgc-min-width: 136px; --pgc-padding-inline: 22px; }', 'regular density longer pill');
must(css, '.root[data-density="spacious"] { --pgc-height: 46px; --pgc-min-width: 152px; --pgc-padding-inline: 26px; }', 'spacious density longer pill');
must(css, '.statusPill { min-width: 208px; }', 'status pill longer');

must(css, 'rgba(4, 6, 14, .34)', 'root tint reduced from previous .42');
must(css, 'rgba(3,6,14,.070)', 'refraction dark overlay reduced');
must(css, 'rgba(0,0,0,.125)', 'volume frame darkness reduced');
must(css, 'opacity: .62;', 'volume frame lighter opacity');

must(css, 'brightness(1.74)', 'reactive edge brightness +30ish');
must(css, 'saturate(2.36)', 'reactive edge saturation boosted');
must(css, 'opacity: .98;', 'reactive edge stronger opacity');
must(css, 'rgba(255,255,255,.54)', 'outer edge bright stop boosted');

must(css, 'border: 1px solid rgba(255,255,255,.118);', 'inner frame slightly brighter');
must(css, 'opacity: .78;', 'specular highlight brighter');

must(css, '.root:not([data-variant="disabled"]):not(:disabled) .liquidSheen', 'default premium sheen enabled');
must(css, 'animation: prismaGlassSweep 6.8s', 'default slower sheen pass');
must(css, '.root[data-variant="thinking"] .liquidSheen', 'thinking sheen preset still stronger');
must(css, 'animation: prismaGlassSweep 4.9s', 'thinking faster sheen pass');

const generalIdx = css.indexOf('.root:not([data-variant="disabled"]):not(:disabled) .liquidSheen');
const thinkingIdx = css.indexOf('.root[data-variant="thinking"] .liquidSheen');
if (!(generalIdx >= 0 && thinkingIdx > generalIdx)) fail('thinking sheen rule must come after default sheen rule so it wins');
ok('thinking sheen rule order');

mustNot(css, 'rgba(4, 6, 14, .42)', 'old heavy root tint removed');
mustNot(css, 'rgba(0,0,0,.18);\\n  -webkit-mask', 'old heavy volume frame fallback removed');

must(appPageText, 'Fix7 calibrated', 'app route copy updated');
must(legacyPageText, 'Fix7 calibrated', 'legacy route copy updated');

console.log('[glass-fix7-calibration] PASS ' + JSON.stringify({ pcApp, blur, statusWidth: 208 }, null, 2));
