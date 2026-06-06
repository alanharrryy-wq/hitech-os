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

let pcApp = null;
for (const candidate of candidates) {
  if (exists(path.join(candidate, 'package.json')) && (exists(path.join(candidate, 'app')) || exists(path.join(candidate, 'src', 'app')))) {
    pcApp = candidate;
    break;
  }
}

if (!pcApp) {
  console.error('[glasscaps-clear1] Could not detect PC app root from', cwd);
  process.exit(1);
}

const appDir = exists(path.join(pcApp, 'app')) ? path.join(pcApp, 'app') : path.join(pcApp, 'src', 'app');
const routeDir = path.join(appDir, 'referencia-visual', 'liquid-glass-capsules');
const routeCss = path.join(routeDir, 'liquid-glass-capsules.module.css');
const componentCss = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css');

const missing = [routeCss, componentCss].filter((file) => !exists(file));
if (missing.length) {
  console.error('[glasscaps-clear1] Missing files:');
  for (const file of missing) console.error(' -', file);
  process.exit(1);
}

const routeCssText = read(routeCss);
const componentCssText = read(componentCss);

const forbiddenColorFragments = [
  'rgba(126, 42, 86',
  'rgba(79, 54, 154',
  'rgba(37, 74, 129',
  'rgba(44, 88, 154',
  'rgba(160, 42, 56',
  'rgb(126, 190, 255)',
  'rgb(136, 201, 255)',
];

const checks = [
  ['Test 01 proofStage no longer participates in card-shell selector', !routeCssText.includes('.messageCard,\n.proofStage,\n.lensLab')],
  ['Test 01 proofStage is transparent', routeCssText.includes('.proofStage') && routeCssText.includes('background: transparent !important')],
  ['Test 01 proofStage has no border', routeCssText.includes('border: 0 !important')],
  ['Test 01 proofStage has no box shadow', routeCssText.includes('box-shadow: none !important')],
  ['component css uses backdrop-filter', componentCssText.includes('backdrop-filter')],
  ['component css declares clear1 neutral material', componentCssText.includes('glasscaps clear1: material first, color later')],
  ['all declared tones are grouped into neutral override', componentCssText.includes('.root[data-tone="graphite"],') && componentCssText.includes('.root[data-tone="rose"],') && componentCssText.includes('.root[data-tone="violet"],') && componentCssText.includes('.root[data-tone="blue"],')],
  ['thinking variant is neutral', componentCssText.includes('.root[data-variant="active"],') && componentCssText.includes('.root[data-variant="thinking"],') && !componentCssText.includes('rgba(74, 164, 255')],
  ['status text is not blue', !componentCssText.includes('rgb(136, 201, 255)') && !componentCssText.includes('rgb(126, 190, 255)')],
  ['removed old colored material fragments', forbiddenColorFragments.every((fragment) => !componentCssText.includes(fragment))],
];

const failed = checks.filter(([, ok]) => !ok);
for (const [label, ok] of checks) console.log(`${ok ? 'OK' : 'FAIL'} ${label}`);

if (failed.length) {
  console.error(`[glasscaps-clear1] ${failed.length} checks failed.`);
  process.exit(1);
}

console.log('[glasscaps-clear1] PASS', JSON.stringify({ pcApp, routeDir }, null, 2));
