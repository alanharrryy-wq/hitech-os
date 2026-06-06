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

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}

const tabletPage = rel('products','tablet','app','app','page.tsx');
const tabletCss = rel('products','tablet','app','app','prisma-tablet-light-shell.module.css');
const publicRoot = rel('products','tablet','app','public','surface-visual-governor','tablet-light-shell');
const pilotRoot = path.join(publicRoot, 'pilot-05');
const latestRoot = path.join(publicRoot, 'latest');
const indexPath = path.join(latestRoot, 'index.json');
const budgetPath = path.join(latestRoot, 'route-budget.tablet-light-shell.pilot-05.json');
const twinPath = path.join(latestRoot, 'surface-twin.tablet-light-shell.json');
const compatPath = path.join(latestRoot, 'surface.compatibility.tablet-light-shell.json');
const tokensPath = path.join(latestRoot, 'tablet-light-shell.tokens.json');

ok('tablet home page exists', fs.existsSync(tabletPage));
ok('tablet light shell css module exists', fs.existsSync(tabletCss));
ok('pilot public root exists', fs.existsSync(pilotRoot));
ok('latest public root exists', fs.existsSync(latestRoot));

const page = read(tabletPage);
const css = read(tabletCss);
ok('page contains pilot marker', page.includes('data-prisma-surface-governor="pilot-05"'));
ok('page imports css module', page.includes('prisma-tablet-light-shell.module.css'));
ok('page declares light-first', page.includes('data-tablet-light-first="true"'));
ok('page protects POS marker', page.includes('data-pos-protected="true"'));
ok('page declares fuji background', page.includes('tablet-fuji-cloudglass'));
ok('page has no /pos link', !/href=["']\/pos["']/.test(page));
ok('page has no /checkout link', !/href=["']\/checkout["']/.test(page));
ok('css keeps tablet light base', css.includes('--prisma-tablet-bg: #f4f7fb'));
ok('css uses fuji cloudglass atmosphere asset', css.includes('tablet-fuji-cloudglass.jpg'));
ok('css preserves glass panels', css.includes('backdrop-filter') && css.includes('blur('));
ok('css includes reduced motion', css.includes('prefers-reduced-motion'));
ok('css includes reduced transparency', css.includes('prefers-reduced-transparency'));
ok('css avoids dark storm asset as active background', !css.includes('storm-cloud-operations-real.jpg') && !css.includes('obsidian-cloud-motion.svg'));
ok('css has no external imports', !css.includes('@import') && !css.includes('http://') && !css.includes('https://'));
ok('css avoids WebGL/Pixi terms', !/webgl|pixi|three\/fiber|@react-three/i.test(css));

const index = readJson(indexPath);
const budget = readJson(budgetPath);
const twin = readJson(twinPath);
const compat = readJson(compatPath);
const tokens = readJson(tokensPath);
ok('index declares pilot 05', index?.pilot === '05_tablet_light_shell');
ok('index declares tablet root route', index?.route === '/');
ok('index declares active fuji preset', index?.activePresetId === 'tablet-fuji-cloudglass');
ok('route budget is light-first and no webgl', budget?.visual_budget?.background === 'light_photo_medium' && budget?.visual_budget?.webgl === 'forbidden');
ok('surface twin declares tablet_light_shell', twin?.surface === 'tablet_light_shell');
ok('compat forbids POS application', compat?.surfaces?.pos?.allowed === false);
ok('compat allows tablet shell only', compat?.surfaces?.tablet_light_shell?.allowed === true);
ok('tokens declare glass panel token', Boolean(tokens?.tokens?.['--tablet-glass-panel']));

for (const rootDir of [latestRoot, pilotRoot]) {
  const assets = walk(path.join(rootDir, 'atmosphere-assets','backgrounds'));
  ok(`${path.basename(rootDir)} fuji jpg copied`, assets.some((p) => path.basename(p) === 'tablet-fuji-cloudglass.jpg'));
  ok(`${path.basename(rootDir)} soft-gray compatibility alias copied`, assets.some((p) => path.basename(p) === 'tablet-soft-gray-clouds.svg'));
}

const publicFiles = walk(publicRoot);
const leakPattern = /(<LOCAL_PATH>|<OUTPUT_DIR>|<REPO_ROOT>|<HOME_PATH>|tablet-pos\.db|\.sqlite|\.db\b|databasePaths)/i;
const leaks = [];
for (const f of publicFiles) {
  if (fs.statSync(f).size > 5_000_000) continue;
  if (/\.(png|jpg|jpeg|webp)$/i.test(f)) continue;
  const txt = read(f);
  if (leakPattern.test(txt)) leaks.push(path.relative(root, f));
}
ok('public tablet no local path/db leaks', leaks.length === 0, leaks.join(', '));
ok('no database files under tablet shell public', publicFiles.every((f) => !/\.(db|sqlite|sqlite3)$/i.test(f)));

const protectedTokens = [
  'products/tablet/app/app/pos',
  'products/tablet/app/app/checkout',
  'products/tablet/app/components/pos',
  'products/pc/app/app/pos',
  'products/pc/app/app/checkout',
];
ok('page does not reference protected implementation paths', protectedTokens.every((t) => !page.includes(t)));

const result = {
  pilot: '05_tablet_light_shell',
  background: 'tablet-fuji-cloudglass',
  status: fail.length ? 'FAIL' : 'PASS',
  pass,
  fail,
  files_checked: publicFiles.length + 2,
  sha256: fs.existsSync(tabletPage) ? crypto.createHash('sha256').update(fs.readFileSync(tabletPage)).digest('hex') : null,
};
console.log(JSON.stringify(result, null, 2));
if (fail.length) process.exit(1);
