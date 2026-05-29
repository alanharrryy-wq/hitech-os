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

const dashboardPage = rel('products','pc','app','app','dashboard','page.tsx');
const dashboardCss = rel('products','pc','app','app','dashboard','prisma-surface-dashboard.module.css');
const publicRoot = rel('products','pc','app','public','surface-visual-governor','dashboard');
const pilotRoot = path.join(publicRoot, 'pilot-04');
const latestRoot = path.join(publicRoot, 'latest');
const indexPath = path.join(latestRoot, 'index.json');
const budgetPath = path.join(latestRoot, 'route-budget.pc-dashboard.pilot-04.json');
const twinPath = path.join(latestRoot, 'surface-twin.pc-dashboard.json');
const compatPath = path.join(latestRoot, 'surface.compatibility.dashboard.json');

ok('dashboard page exists', fs.existsSync(dashboardPage));
ok('dashboard css module exists', fs.existsSync(dashboardCss));
ok('pilot public root exists', fs.existsSync(pilotRoot));
ok('latest public root exists', fs.existsSync(latestRoot));

const page = read(dashboardPage);
const css = read(dashboardCss);
ok('page contains pilot marker', page.includes('data-prisma-surface-governor="pilot-04"'));
ok('page imports css module', page.includes('prisma-surface-dashboard.module.css'));
ok('page protects POS marker', page.includes('data-pos-protected="true"'));
ok('css uses real atmosphere asset', css.includes('storm-cloud-operations-real.jpg'));
ok('css includes reduced motion', css.includes('prefers-reduced-motion'));
ok('css has no external imports', !css.includes('@import') && !css.includes('http://') && !css.includes('https://'));

const index = readJson(indexPath);
const budget = readJson(budgetPath);
const twin = readJson(twinPath);
const compat = readJson(compatPath);
ok('index declares pilot 04', index?.pilot === '04_pc_dashboard_governed_hoy');
ok('index declares dashboard route', index?.route === '/dashboard');
ok('route budget is high but governed', budget?.visual_budget?.background === 'high' && budget?.visual_budget?.glow_strong_max === 1);
ok('surface twin declares pc_dashboard', twin?.surface === 'pc_dashboard');
ok('compat forbids POS application', compat?.surfaces?.pos?.allowed === false);
ok('compat allows pc dashboard', compat?.surfaces?.pc_dashboard?.allowed === true);
ok('tablet light-first note preserved', compat?.surfaces?.tablet?.policy === 'light_first_preserved_no_tablet_write');

const assets = walk(path.join(latestRoot, 'atmosphere-assets','backgrounds'));
ok('at least 3 atmosphere assets copied', assets.length >= 3, `${assets.length} assets`);
ok('storm real jpg copied', assets.some((p) => path.basename(p) === 'storm-cloud-operations-real.jpg'));

const publicFiles = walk(publicRoot);
const leakPattern = /(<LOCAL_PATH>|<LOCAL_PATH>|tablet-pos\.db|\.sqlite|\.db\b|databasePaths|<LOCAL_PATH>|<LOCAL_PATH>)/i;
const leaks = [];
for (const f of publicFiles) {
  if (fs.statSync(f).size > 5_000_000) continue;
  if (/\.(png|jpg|jpeg|webp)$/i.test(f)) continue;
  const txt = read(f);
  if (leakPattern.test(txt)) leaks.push(path.relative(root, f));
}
ok('public dashboard no local path/db leaks', leaks.length === 0, leaks.join(', '));
ok('no database files under dashboard public', publicFiles.every((f) => !/\.(db|sqlite|sqlite3)$/i.test(f)));

const protectedTokens = [
  'products/tablet/app/app/pos',
  'products/tablet/app/app/checkout',
  'products/tablet/app/components/pos',
  'products/pc/app/app/pos',
  'products/pc/app/app/checkout',
];
ok('page does not reference protected implementation paths', protectedTokens.every((t) => !page.includes(t)));

const result = {
  pilot: '04_pc_dashboard_governed_hoy',
  status: fail.length ? 'FAIL' : 'PASS',
  pass,
  fail,
  files_checked: publicFiles.length + 2,
  sha256: fs.existsSync(dashboardPage) ? crypto.createHash('sha256').update(fs.readFileSync(dashboardPage)).digest('hex') : null,
};
console.log(JSON.stringify(result, null, 2));
if (fail.length) process.exit(1);
