import fs from 'node:fs';
import path from 'node:path';
const cwd = process.cwd();
const candidates = [cwd, path.join(cwd, 'products', 'pc', 'app'), path.join(cwd, 'apps', 'terminal-de-venta-system', 'products', 'pc', 'app')];
const exists = (p) => fs.existsSync(p);
const read = (p) => fs.readFileSync(p, 'utf8');
let pcApp = null;
for (const candidate of candidates) {
  if (exists(path.join(candidate, 'package.json')) && (exists(path.join(candidate, 'app')) || exists(path.join(candidate, 'src', 'app')))) { pcApp = candidate; break; }
}
if (!pcApp) { console.error('[glasscaps-clear3] No detecté PC app desde', cwd); process.exit(1); }
const appDir = exists(path.join(pcApp, 'app')) ? path.join(pcApp, 'app') : path.join(pcApp, 'src', 'app');
const routeCss = path.join(appDir, 'referencia-visual', 'liquid-glass-capsules', 'liquid-glass-capsules.module.css');
const compCss = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css');
const routeText = read(routeCss);
const compText = read(compCss);
const checks = [
  ['stageBackdrop hidden', routeText.includes('.stageBackdrop {') && routeText.includes('display: none;')],
  ['proofStage auto height', routeText.includes('min-height: auto;')],
  ['readTrack styled', routeText.includes('.readTrack {') && routeText.includes('max-width: 74ch;')],
  ['double frame inner ring', compText.includes('inset: var(--pgc-frame-gap);') && compText.includes('border: 1px solid rgba(255,255,255,.14);')],
  ['inner lens blur only', compText.includes('.refraction {') && compText.includes('inset: var(--pgc-lens-inset);') && compText.includes('backdrop-filter: blur(var(--pgc-blur))')],
  ['neutral tone comment', compText.includes('optical structure, not color')],
];
for (const [label, ok] of checks) console.log(`${ok ? 'OK' : 'FAIL'} ${label}`);
const failed = checks.filter(([, ok]) => !ok);
if (failed.length) { console.error(`[glasscaps-clear3] ${failed.length} checks failed.`); process.exit(1); }
console.log('[glasscaps-clear3] PASS', JSON.stringify({ pcApp }, null, 2));
