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
function countNeedles(text, needles) {
  return needles.filter((needle) => text.includes(needle)).length;
}

const pcApp = findPcApp();
if (!pcApp) {
  console.error('[glasscaps-dark-liquid] Could not detect PC app root from', cwd);
  process.exit(1);
}

const appDir = exists(path.join(pcApp, 'app')) ? path.join(pcApp, 'app') : path.join(pcApp, 'src', 'app');
const appRouteDir = path.join(appDir, 'referencia-visual', 'liquid-glass-capsules');
const legacyRouteDir = path.join(pcApp, 'referencia-visual', 'liquid-glass-capsules');
const appPage = path.join(appRouteDir, 'page.tsx');
const appCss = path.join(appRouteDir, 'liquid-glass-capsules.module.css');
const legacyPage = path.join(legacyRouteDir, 'page.tsx');
const legacyCss = path.join(legacyRouteDir, 'liquid-glass-capsules.module.css');
const component = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx');
const componentCss = path.join(pcApp, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css');
const doc = path.join(pcApp, 'docs', 'design', 'PRISMA_DARK_LIQUID_GLASS_BENCH_0306.md');

const requiredFiles = [appPage, appCss, legacyPage, legacyCss, component, componentCss, doc];
const missing = requiredFiles.filter((file) => !exists(file));
if (missing.length) {
  console.error('[glasscaps-dark-liquid] Missing files:');
  for (const file of missing) console.error(' -', file);
  process.exit(1);
}

const appPageText = read(appPage);
const appCssText = read(appCss);
const legacyPageText = read(legacyPage);
const legacyCssText = read(legacyCss);
const componentText = read(component);
const componentCssText = read(componentCss);
const docText = read(doc);
const blur = cssNumber(componentCssText, '--pgc-blur');

const shapes = ['geoCircleCyan', 'geoRectViolet', 'geoTriangleAmber', 'geoSquareBlue', 'geoCapsuleEmerald', 'geoDiamondRose', 'geoBlockLime', 'geoCircleMagenta'];
const backTexts = ['backTextPrisma', 'backTextGlass', 'backTextThinking', 'backTextStatic'];
const darkColors = ['#05070d', '#00d5ff', '#6436ff', '#ffb000', '#155dff', '#00c087', '#ff3d91', '#c6ea27', '#c02cff'];

const checks = [
  ['app route exists and is dark benchmark', appPageText.includes('Dark Liquid Glass Bench') && appPageText.includes('Dark glass over fixed shapes and text')],
  ['legacy route mirrors dark benchmark', legacyPageText.includes('Dark Liquid Glass Bench') && legacyPageText.includes('Dark glass over fixed shapes and text')],
  ['route background is dark only', appCssText.includes('background: #05070d;') && legacyCssText.includes('background: #05070d;')],
  ['old light bench background removed from active route css', !appCssText.includes('#efe7db') && !legacyCssText.includes('#efe7db')],
  ['fixed backplate preserved', hasAll(appCssText, ['.motionBackplate', 'position: fixed;', 'pointer-events: none;'])],
  ['all 8 dark solid shapes exist in app page', countNeedles(appPageText, shapes) === shapes.length],
  ['all 8 dark solid shapes exist in css', countNeedles(appCssText, shapes) === shapes.length],
  ['all fixed background texts exist in app page', countNeedles(appPageText, backTexts) === backTexts.length],
  ['all fixed background texts exist in css', countNeedles(appCssText, backTexts) === backTexts.length],
  ['dark solid shape colors exist', countNeedles(appCssText, darkColors) === darkColors.length],
  ['component keeps optical DOM layers separate', hasAll(componentText, ['styles.refraction', 'styles.underGlow', 'styles.specular', 'styles.liquidSheen', 'styles.content'])],
  ['root shell still has no backdrop blur', hasAll(componentCssText, ['.root {', '-webkit-backdrop-filter: none;', 'backdrop-filter: none;'])],
  ['central lens is only controlled backdrop-filter zone', componentCssText.includes('.refraction {') && componentCssText.includes('blur(var(--pgc-blur))')],
  ['central lens blur remains 1.5px', blur === 1.5],
  ['central lens blur remains under hard max 3px', Number.isFinite(blur) && blur <= 3],
  ['heavy 26px blur not present', !componentCssText.includes('--pgc-blur: 26px') && !componentCssText.includes('blur(26px)')],
  ['dark optics use stronger saturation/contrast', componentCssText.includes('--pgc-saturate: 1.18') && componentCssText.includes('--pgc-contrast: 1.16')],
  ['outer frame z-index and mask preserved', hasAll(componentCssText, ['.root::before', 'z-index: 2', 'mask-composite: exclude', '-webkit-mask-composite: xor'])],
  ['inner frame gap and z-index preserved', hasAll(componentCssText, ['--pgc-frame-gap: 3px', 'inset: var(--pgc-frame-gap)', 'z-index: 3'])],
  ['underglow changed from bar to full local caustic field', hasAll(componentCssText, ['.underGlow', 'inset: 5px 9px 4px 9px;', 'height: auto;', 'filter: blur(11px)', 'mix-blend-mode: screen'])],
  ['specular edge strengthened', componentCssText.includes('opacity: .84') && componentCssText.includes('rgba(255,255,255,.42)')],
  ['content remains above optical layers', componentCssText.includes('.content') && componentCssText.includes('z-index: 10')],
  ['status pill matches 184px preset', componentCssText.includes('.statusPill { min-width: 184px; }')],
  ['circle pill matches 52px preset', componentCssText.includes('--pgc-height: 52px') && componentCssText.includes('--pgc-min-width: 52px')],
  ['prefers-reduced-motion preserved', componentCssText.includes('prefers-reduced-motion') && appCssText.includes('prefers-reduced-motion')],
  ['prefers-contrast fallback added', componentCssText.includes('prefers-contrast: more') && appCssText.includes('prefers-contrast: more')],
  ['design note documents dark-only benchmark', docText.includes('Dark Liquid Glass') && docText.includes('dark-only')],
];

const failed = checks.filter(([, ok]) => !ok);
for (const [label, ok] of checks) console.log(`${ok ? 'OK' : 'FAIL'} ${label}`);
console.log('[glasscaps-dark-liquid] measured central blur:', Number.isFinite(blur) ? `${blur}px` : 'not found');
if (failed.length) {
  console.error(`[glasscaps-dark-liquid] ${failed.length} checks failed.`);
  process.exit(1);
}
console.log('[glasscaps-dark-liquid] PASS', JSON.stringify({ pcApp, appRouteDir, legacyRouteDir, blurPx: blur }, null, 2));
