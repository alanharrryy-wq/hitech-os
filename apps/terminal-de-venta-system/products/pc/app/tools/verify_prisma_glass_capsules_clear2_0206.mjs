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
if (!pcApp) { console.error('[glasscaps-clear2] No detecté PC app desde', cwd); process.exit(1); }
const appDir = exists(path.join(pcApp, 'app')) ? path.join(pcApp, 'app') : path.join(pcApp, 'src', 'app');
const routeCss = path.join(appDir, 'referencia-visual', 'liquid-glass-capsules', 'liquid-glass-capsules.module.css');
const compCss = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css');
const routeText = read(routeCss);
const compText = read(compCss);
const checks = [
  ['stageContent is transparent', routeText.includes('background: transparent !important;') && routeText.includes('backdrop-filter: none !important;')],
  ['stageContent shell removed', routeText.includes('border: 0 !important;') && routeText.includes('box-shadow: none !important;')],
  ['all tones neutralized', compText.includes('Every visible pill must stay translucent clear/smoke glass')],
  ['no colored variant boost remains', compText.includes('.root[data-variant="active"]') && compText.includes('--pgc-bg-a: rgba(255, 255, 255, 0.095);')],
  ['thinking sheen still exists', compText.includes('.root[data-variant="thinking"] .liquidSheen')],
  ['backdrop-filter still used', compText.includes('backdrop-filter')],
];
for (const [label, ok] of checks) console.log(`${ok ? 'OK' : 'FAIL'} ${label}`);
const failed = checks.filter(([, ok]) => !ok);
if (failed.length) { console.error(`[glasscaps-clear2] ${failed.length} checks failed.`); process.exit(1); }
console.log('[glasscaps-clear2] PASS', JSON.stringify({ pcApp }, null, 2));
