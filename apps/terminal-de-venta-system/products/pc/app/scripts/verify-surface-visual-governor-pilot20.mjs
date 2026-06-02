
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const rel = (...parts) => path.join(root, ...parts);
const fail = [];
const pass = [];

function ok(name, condition, detail = '') {
  if (condition) pass.push({ name, detail });
  else fail.push({ name, detail });
}

function read(file) {
  return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '';
}

function readJson(file) {
  try { return JSON.parse(read(file)); }
  catch (err) { fail.push({ name: `json:${path.relative(root, file)}`, detail: err.message }); return null; }
}

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

const pagePath = rel('products','pc','app','app','referencia-visual','liquid-glass','page.tsx');
const cssPath = rel('products','pc','app','app','prisma-liquid-glass.module.css');
const refPagePath = rel('products','pc','app','app','referencia-visual','page.tsx');
const latestRoot = rel('products','pc','app','public','surface-visual-governor','liquid-glass','latest');
const pilotRoot = rel('products','pc','app','public','surface-visual-governor','liquid-glass','pilot-20');
const indexPath = path.join(latestRoot, 'index.json');
const budgetPath = path.join(latestRoot, 'route-budget.liquid-glass.pilot-20.json');
const compatPath = path.join(latestRoot, 'surface.compatibility.liquid-glass.json');
const docPath = rel('products','pc','app','docs','surface-visual-governor','pilot-20-liquid-glass-reference-room.md');

for (const p of [pagePath, cssPath, refPagePath, indexPath, budgetPath, compatPath, docPath]) {
  ok(`exists:${path.relative(root, p)}`, fs.existsSync(p));
}
ok('pilot public root exists', fs.existsSync(pilotRoot));
ok('latest public root exists', fs.existsSync(latestRoot));

const page = read(pagePath);
const css = read(cssPath);
const refPage = read(refPagePath);
const index = readJson(indexPath);
const budget = readJson(budgetPath);
const compat = readJson(compatPath);

ok('page has pilot marker', page.includes('data-prisma-liquid-glass-pilot="20"'));
ok('page route marker', page.includes('/referencia-visual/liquid-glass'));
ok('page imports css module', page.includes('../../prisma-liquid-glass.module.css'));
ok('page includes SVG turbulence', page.includes('feTurbulence'));
ok('page includes SVG displacement', page.includes('feDisplacementMap'));
ok('reference visual page links to lab', refPage.includes('/referencia-visual/liquid-glass'));

for (const token of ['backdrop-filter', '-webkit-backdrop-filter', 'saturate(', 'brightness(', 'mask-composite', 'prefers-reduced-motion', 'prisma-liquid-refraction']) {
  ok(`css token:${token}`, css.includes(token));
}
ok('css has no external http imports', !css.includes('@import') && !css.includes('http://') && !css.includes('https://'));
ok('css references governed family assets', css.includes('/surface-visual-governor/liquid-glass/families/') && (css.includes('.jpg') || css.includes('.png') || css.includes('.webp')));

ok('index pilot id', index?.pilot === '20_liquid_glass_reference_room');
ok('index route', index?.route === '/referencia-visual/liquid-glass');
ok('index pos blocked', index?.gates?.pos?.allowed === false);
ok('index checkout blocked', index?.gates?.checkout?.allowed === false);
ok('index tablet blocked and light preserved', index?.gates?.tablet?.allowed === false && index?.gates?.tablet?.light_first_preserved === true);
ok('index db untouched', index?.gates?.db?.touched === false);
ok('index deploy untouched', index?.gates?.deploy?.performed === false);
ok('index dependencies not modified by pilot', index?.gates?.dependencies?.installed_by_this_pilot === false);

ok('budget route', budget?.route === '/referencia-visual/liquid-glass');
ok('budget webgl off', budget?.visual_budget?.webgl === 0);
ok('budget dense safe cap', budget?.visual_budget?.dense_safe_blur_max_px === 8);
ok('compat pos false', compat?.surfaces?.pos?.allowed === false);
ok('compat checkout false', compat?.surfaces?.checkout?.allowed === false);
ok('compat pc reference true', compat?.surfaces?.pc_reference_visual?.allowed === true);

const protectedTokens = [
  'products/tablet/app/app/pos',
  'products/tablet/app/app/checkout',
  'products/tablet/app/components/pos',
  'products/pc/app/app/pos',
  'products/pc/app/app/checkout',
];
ok('page does not reference protected implementation paths', protectedTokens.every((token) => !page.includes(token)));

const packageJsonPath = rel('package.json');
const packageJson = readJson(packageJsonPath);
const allDeps = { ...(packageJson?.dependencies || {}), ...(packageJson?.devDependencies || {}) };
for (const lib of ['motion', 'gsap', '@gsap/react', 'class-variance-authority', 'clsx', 'tailwind-merge', '@radix-ui/react-dialog', '@vanilla-extract/css', 'ogl']) {
  ok(`workspace dependency present:${lib}`, Boolean(allDeps[lib]));
}

const result = {
  pilot: '20_liquid_glass_reference_room',
  status: fail.length ? 'FAIL' : 'PASS',
  pass,
  fail,
  sha256: {
    page: fs.existsSync(pagePath) ? sha256(pagePath) : null,
    css: fs.existsSync(cssPath) ? sha256(cssPath) : null,
    index: fs.existsSync(indexPath) ? sha256(indexPath) : null,
  },
};
console.log(JSON.stringify(result, null, 2));
if (fail.length) process.exit(1);
