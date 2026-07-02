import fs from 'node:fs';
import path from 'node:path';

const repo = process.cwd();
const appRoot = path.join(repo, 'apps', 'terminal-de-venta-system');
const targets = [
  'docs/product/surface-cleanup/PRISMA_SURFACE_CLEANUP_3006.md',
  'docs/product/surface-cleanup/surface-cleanup.navigation-manifest.json',
  'products/tablet/app/src/navigation/tablet-page-contracts.ts',
  'products/tablet/app/src/navigation/tablet-product-navigation.manifest.json',
  'products/pc/app/src/uiux/pc-product-navigation.ts',
  'products/pc/app/src/uiux/pc-product-navigation.manifest.json',
];

const fail = (message) => {
  console.error(`[surfcln-verify] FAIL: ${message}`);
  process.exit(1);
};

const read = (relativePath) => {
  const absolutePath = path.join(appRoot, relativePath);
  if (!fs.existsSync(absolutePath)) fail(`missing ${relativePath}`);
  return fs.readFileSync(absolutePath, 'utf8');
};

for (const relativePath of targets) {
  const content = read(relativePath);
  const cssPriorityToken = '!' + 'important';
  if (content.includes(cssPriorityToken)) fail(`CSS priority token found in ${relativePath}`);
}

const tablet = JSON.parse(read('products/tablet/app/src/navigation/tablet-product-navigation.manifest.json'));
const pc = JSON.parse(read('products/pc/app/src/uiux/pc-product-navigation.manifest.json'));
const combined = JSON.parse(read('docs/product/surface-cleanup/surface-cleanup.navigation-manifest.json'));

if (!tablet.authority.excludedSurfaces.includes('mobile')) fail('tablet manifest must exclude mobile');
if (!tablet.authority.excludedSurfaces.includes('shared_ui')) fail('tablet manifest must exclude shared_ui');
if (!pc.authority.excludedSurfaces.includes('mobile')) fail('pc manifest must exclude mobile');
if (!pc.authority.excludedSurfaces.includes('shared_ui')) fail('pc manifest must exclude shared_ui');

const forbiddenTabletFinal = new Set([
  '/prisma-dark-pos-reference',
  '/prisma-visual-catalog',
  '/referencia-visual',
  '/release-gate',
  '/screen-standard-preview',
  '/visual-os',
  '/visual-os/detached',
  '/visual-os/materiality-catalog',
  '/visual-os/pro',
  '/visual-os/realtime',
  '/visual-os/tablet-background-gallery',
  '/visual-os/tablet-codex-gallery',
  '/inventory',
  '/sales',
  '/settings/data',
  '/events/outbox',
]);

for (const route of tablet.tablet.finalMenuRoutes) {
  if (forbiddenTabletFinal.has(route)) fail(`tablet forbidden final route: ${route}`);
}

const forbiddenPcFinal = new Set(pc.pc.hiddenFromFinalUser);
for (const route of pc.pc.finalMenuRoutes) {
  if (forbiddenPcFinal.has(route)) fail(`pc forbidden final route: ${route}`);
}

const targetText = JSON.stringify(combined.outputs);
if (targetText.includes('products/mobile/') || targetText.includes('shared/')) {
  fail('manifest outputs must not target mobile or shared code');
}

console.log('[surfcln-verify] PASS: final navigation contracts separate product routes from lab/internal/reference routes.');
