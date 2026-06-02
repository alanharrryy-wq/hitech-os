import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();

function hasPackageJson(p) {
  return fs.existsSync(path.join(p, 'package.json'));
}

function hasGlassFiles(p) {
  return fs.existsSync(path.join(p, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx'))
    && fs.existsSync(path.join(p, 'referencia-visual', 'liquid-glass-capsules', 'page.tsx'));
}

const candidates = [
  root,
  path.join(root, 'products', 'pc', 'app'),
  path.join(root, 'apps', 'terminal-de-venta-system', 'products', 'pc', 'app'),
  path.join(root, 'app'),
].map((p) => path.resolve(p));

const appRoot = candidates.find((p) => hasPackageJson(p) && hasGlassFiles(p))
  ?? candidates.find((p) => hasGlassFiles(p))
  ?? candidates.find((p) => hasPackageJson(p) && fs.existsSync(path.join(p, 'components')));

if (!appRoot) {
  console.error('[glasscaps] No app root found');
  console.error('[glasscaps] cwd=' + root);
  console.error('[glasscaps] tried:\n' + candidates.map((p) => `- ${p}`).join('\n'));
  process.exit(1);
}

const files = [
  path.join(appRoot, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx'),
  path.join(appRoot, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css'),
  path.join(appRoot, 'components', 'prisma-glass-capsule', 'index.ts'),
  path.join(appRoot, 'referencia-visual', 'liquid-glass-capsules', 'page.tsx'),
  path.join(appRoot, 'referencia-visual', 'liquid-glass-capsules', 'liquid-glass-capsules.module.css'),
  path.join(appRoot, 'docs', 'design', 'PRISMA_LIQUID_GLASS_CAPSULES_0206.md'),
];

const missing = files.filter((p) => !fs.existsSync(p));
if (missing.length) {
  console.error('[glasscaps] Missing files:');
  console.error(missing.map((p) => `- ${p}`).join('\n'));
  console.error('[glasscaps] cwd=' + root);
  console.error('[glasscaps] appRoot=' + appRoot);
  process.exit(1);
}

const component = fs.readFileSync(files[0], 'utf8');
const css = fs.readFileSync(files[1], 'utf8');
const page = fs.readFileSync(files[3], 'utf8');
const routeCss = fs.readFileSync(files[4], 'utf8');
const docs = fs.readFileSync(files[5], 'utf8');

const checks = [
  ['exports PrismaGlassCapsule', /export function PrismaGlassCapsule/.test(component)],
  ['exports PrismaGlassTopDock', /export function PrismaGlassTopDock/.test(component)],
  ['component exposes role status', /role="status"/.test(component)],
  ['component exposes aria-live', /aria-live="polite"/.test(component)],
  ['component has action group', /actionGroup/.test(component)],
  ['CSS uses backdrop-filter', /backdrop-filter/.test(css)],
  ['CSS includes webkit backdrop filter', /-webkit-backdrop-filter/.test(css)],
  ['CSS has specular layer', /specular/.test(css)],
  ['CSS has refraction layer', /refraction/.test(css)],
  ['CSS has liquid sheen layer', /liquidSheen/.test(css)],
  ['CSS has reduced motion fallback', /prefers-reduced-motion/.test(css)],
  ['CSS has unsupported backdrop fallback', /@supports not/.test(css)],
  ['CSS has thinking shimmer', /prismaGlassSweep/.test(css)],
  ['CSS has density tokens', /data-density/.test(css)],
  ['CSS has tone rose', /data-tone="rose"/.test(css)],
  ['CSS has tone blue', /data-tone="blue"/.test(css)],
  ['demo imports top dock', /PrismaGlassTopDock/.test(page)],
  ['demo route imports component', /prisma-glass-capsule/.test(page)],
  ['demo has scroll proof', /scrollProof/.test(page) && /scrollProof/.test(routeCss)],
  ['docs mention acceptance criteria', /Criterios de aceptación/i.test(docs) || /Criterios visuales mínimos/i.test(docs) || /Acceptance/i.test(docs)],
];

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  console.error('[glasscaps] Failed checks:');
  console.error(failed.map(([name]) => `- ${name}`).join('\n'));
  console.error(`[glasscaps] cwd=${root}`);
  console.error(`[glasscaps] appRoot=${appRoot}`);
  process.exit(1);
}

console.log('[glasscaps] VERIFY OK');
console.log(`[glasscaps] cwd=${root}`);
console.log(`[glasscaps] appRoot=${appRoot}`);
