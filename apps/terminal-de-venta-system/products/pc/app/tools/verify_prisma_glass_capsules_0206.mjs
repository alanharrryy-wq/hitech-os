import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();

function hasPackageJson(p) {
  return fs.existsSync(path.join(p, 'package.json'));
}

function resolveAppRoot() {
  const candidates = [
    root,
    path.join(root, 'products', 'pc', 'app'),
    path.join(root, 'apps', 'terminal-de-venta-system', 'products', 'pc', 'app'),
  ].map((p) => path.resolve(p));

  return candidates.find((p) => hasPackageJson(p) && fs.existsSync(path.join(p, 'components')))
    ?? candidates.find((p) => fs.existsSync(path.join(p, 'components')))
    ?? candidates.find((p) => hasPackageJson(p));
}

const appRoot = resolveAppRoot();

if (!appRoot) {
  console.error('[glasscaps] No PC app root found');
  console.error('[glasscaps] cwd=' + root);
  process.exit(1);
}

const appDirCandidates = [
  path.join(appRoot, 'app'),
  path.join(appRoot, 'src', 'app'),
];

const appDir = appDirCandidates.find((p) => fs.existsSync(p));
if (!appDir) {
  console.error('[glasscaps] No Next app directory found under appRoot=' + appRoot);
  process.exit(1);
}

const defaultRealRouteDir = path.join(appDir, 'referencia-visual', 'liquid-glass-capsules');
const legacyRouteDir = path.join(appRoot, 'referencia-visual', 'liquid-glass-capsules');

function routePathToDir(routePath) {
  return path.join(appDir, ...routePath.split('/').filter(Boolean));
}

function resolveRealDemoRouteDir(routeDir) {
  const pagePath = path.join(routeDir, 'page.tsx');
  if (!fs.existsSync(pagePath)) {
    return routeDir;
  }

  const source = fs.readFileSync(pagePath, 'utf8');
  const redirectMatch = source.match(/redirect\(["']([^"']+)["']\)/);
  if (!redirectMatch || !redirectMatch[1].startsWith('/')) {
    return routeDir;
  }

  const candidate = routePathToDir(redirectMatch[1]);
  if (fs.existsSync(path.join(candidate, 'page.tsx'))) {
    return candidate;
  }

  return routeDir;
}

const realRouteDir = resolveRealDemoRouteDir(defaultRealRouteDir);

const files = [
  path.join(appRoot, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx'),
  path.join(appRoot, 'components', 'prisma-glass-capsule', 'prisma-glass-capsule.module.css'),
  path.join(appRoot, 'components', 'prisma-glass-capsule', 'index.ts'),
  path.join(realRouteDir, 'page.tsx'),
  path.join(realRouteDir, 'liquid-glass-capsules.module.css'),
  path.join(appRoot, 'docs', 'design', 'PRISMA_LIQUID_GLASS_CAPSULES_0206.md'),
  path.join(appRoot, 'tools', 'verify_prisma_glass_capsules_0206.mjs'),
];

const missing = files.filter((p) => !fs.existsSync(p));
if (missing.length) {
  console.error('[glasscaps] Missing files:');
  console.error(missing.map((p) => `- ${p}`).join('\n'));
  console.error('[glasscaps] cwd=' + root);
  console.error('[glasscaps] appRoot=' + appRoot);
  console.error('[glasscaps] appDir=' + appDir);
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
  ['real demo imports top dock', /PrismaGlassTopDock/.test(page)],
  ['real demo route imports component from project root', /from\s+['"](?:\.\.\/)+components\/prisma-glass-capsule['"]/.test(page)],
  ['real demo has scroll proof', /scrollProof/.test(page) && /scrollProof/.test(routeCss)],
  ['docs mention acceptance criteria', /Criterios de aceptación/i.test(docs) || /Criterios visuales mínimos/i.test(docs) || /Acceptance/i.test(docs)],
];

if (fs.existsSync(legacyRouteDir)) {
  const legacyPage = path.join(legacyRouteDir, 'page.tsx');
  if (fs.existsSync(legacyPage)) {
    const legacy = fs.readFileSync(legacyPage, 'utf8');
    checks.push(['legacy demo still imports component from legacy depth', /\.\.\/\.\.\/components\/prisma-glass-capsule/.test(legacy)]);
  }
}

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  console.error('[glasscaps] Failed checks:');
  console.error(failed.map(([name]) => `- ${name}`).join('\n'));
  console.error(`[glasscaps] cwd=${root}`);
  console.error(`[glasscaps] appRoot=${appRoot}`);
  console.error(`[glasscaps] appDir=${appDir}`);
  process.exit(1);
}

console.log('[glasscaps] VERIFY OK');
console.log(`[glasscaps] cwd=${root}`);
console.log(`[glasscaps] appRoot=${appRoot}`);
console.log(`[glasscaps] appDir=${appDir}`);
console.log(`[glasscaps] realRouteDir=${realRouteDir}`);
