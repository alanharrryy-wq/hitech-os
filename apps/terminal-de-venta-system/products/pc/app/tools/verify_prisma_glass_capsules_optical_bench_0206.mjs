import fs from 'node:fs';
import path from 'node:path';

const cwd = process.cwd();
const candidates = [
  cwd,
  path.join(cwd, 'products', 'pc', 'app'),
  path.join(cwd, 'apps', 'terminal-de-venta-system', 'products', 'pc', 'app'),
].filter(Boolean);

function exists(p) { return fs.existsSync(p); }
function read(p) { return fs.readFileSync(p, 'utf8'); }
function findPcApp() {
  for (const candidate of candidates) {
    if (exists(path.join(candidate, 'package.json')) && (exists(path.join(candidate, 'app')) || exists(path.join(candidate, 'src', 'app')))) {
      return candidate;
    }
  }
  return null;
}
function cssNumber(text, variableName) {
  const match = text.match(new RegExp(`${variableName}\\s*:\\s*([0-9.]+)px`));
  return match ? Number(match[1]) : Number.NaN;
}
function hasAll(text, needles) {
  return needles.every((needle) => text.includes(needle));
}

const pcApp = findPcApp();
if (!pcApp) {
  console.error('[glasscaps-liquid-spec] Could not detect PC app root from', cwd);
  process.exit(1);
}

const appDir = exists(path.join(pcApp, 'app')) ? path.join(pcApp, 'app') : path.join(pcApp, 'src', 'app');
const routeDir = path.join(appDir, 'referencia-visual', 'liquid-glass-capsules');
const page = path.join(routeDir, 'page.tsx');
const routeCss = path.join(routeDir, 'liquid-glass-capsules.module.css');
const component = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx');
const componentCss = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css');

const requiredFiles = [component, componentCss];
const missing = requiredFiles.filter((file) => !exists(file));
if (missing.length) {
  console.error('[glasscaps-liquid-spec] Missing files:');
  for (const file of missing) console.error(' -', file);
  process.exit(1);
}

const componentText = read(component);
const componentCssText = read(componentCss);
const pageText = exists(page) ? read(page) : '';
const routeCssText = exists(routeCss) ? read(routeCss) : '';
const blur = cssNumber(componentCssText, '--pgc-blur');

const checks = [
  ['route is present when visual proof exists', !exists(routeDir) || (pageText.length > 0 && routeCssText.length > 0)],
  ['component includes underGlow layer in DOM', componentText.includes('styles.underGlow')],
  ['component keeps optical DOM layers separate', hasAll(componentText, ['styles.refraction', 'styles.underGlow', 'styles.specular', 'styles.liquidSheen', 'styles.content'])],
  ['component css defines underGlow layer', componentCssText.includes('.underGlow') && componentCssText.includes('mix-blend-mode: screen')],
  ['root shell has no backdrop blur', hasAll(componentCssText, ['.root {', '-webkit-backdrop-filter: none;', 'backdrop-filter: none;'])],
  ['central lens is only backdrop-filter zone', componentCssText.includes('.refraction {') && componentCssText.includes('blur(var(--pgc-blur))')],
  ['central lens blur is exactly 1.5px', blur === 1.5],
  ['central lens blur does not exceed spec max 3px', Number.isFinite(blur) && blur <= 3],
  ['no obsolete heavy 26px capsule blur remains', !componentCssText.includes('--pgc-blur: 26px') && !componentCssText.includes('blur(26px)')],
  ['outer optical frame uses mask-composite exclude/xor', hasAll(componentCssText, ['.root::before', 'mask-composite: exclude', '-webkit-mask-composite: xor'])],
  ['outer optical frame z-index is 2', componentCssText.includes('.root::before') && componentCssText.includes('z-index: 2')],
  ['inner optical frame uses 3px gap and z-index 3', componentCssText.includes('inset: var(--pgc-frame-gap)') && componentCssText.includes('--pgc-frame-gap: 3px') && componentCssText.includes('z-index: 3')],
  ['central lens uses 6px inset and z-index 1', componentCssText.includes('--pgc-lens-inset: 6px') && componentCssText.includes('z-index: 1')],
  ['underglow uses z-index 4', componentCssText.includes('.underGlow') && componentCssText.includes('z-index: 4')],
  ['specular highlight uses z-index 5', componentCssText.includes('.specular') && componentCssText.includes('z-index: 5')],
  ['liquid sheen sweep uses z-index 6 and thinking-only animation', componentCssText.includes('.liquidSheen') && componentCssText.includes('z-index: 6') && componentCssText.includes('.root[data-variant="thinking"] .liquidSheen') && componentCssText.includes('4.1s')],
  ['content remains above optical layers', componentCssText.includes('.content') && componentCssText.includes('z-index: 10')],
  ['status pill matches 184px preset', componentCssText.includes('.statusPill { min-width: 184px; }')],
  ['circle pill matches 52px preset', componentCssText.includes('--pgc-height: 52px') && componentCssText.includes('--pgc-min-width: 52px')],
  ['prefers-reduced-motion is preserved', componentCssText.includes('prefers-reduced-motion')],
];

const failed = checks.filter(([, ok]) => !ok);
for (const [label, ok] of checks) console.log(`${ok ? 'OK' : 'FAIL'} ${label}`);
console.log('[glasscaps-liquid-spec] measured central blur:', Number.isFinite(blur) ? `${blur}px` : 'not found');
if (failed.length) {
  console.error(`[glasscaps-liquid-spec] ${failed.length} checks failed.`);
  process.exit(1);
}
console.log('[glasscaps-liquid-spec] PASS', JSON.stringify({ pcApp, routeDir: exists(routeDir) ? routeDir : null, blurPx: blur }, null, 2));
