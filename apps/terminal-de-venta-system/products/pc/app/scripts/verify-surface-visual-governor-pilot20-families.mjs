import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
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

const cssPath = path.join(root, 'products/pc/app/app/prisma-liquid-glass.module.css');
const pagePath = path.join(root, 'products/pc/app/app/referencia-visual/liquid-glass/page.tsx');
const latestIndexPath = path.join(root, 'products/pc/app/public/surface-visual-governor/liquid-glass/latest/index.json');
const latestBudgetPath = path.join(root, 'products/pc/app/public/surface-visual-governor/liquid-glass/latest/route-budget.liquid-glass.pilot-20.json');
const latestCompatPath = path.join(root, 'products/pc/app/public/surface-visual-governor/liquid-glass/latest/surface.compatibility.liquid-glass.json');

const css = read(cssPath);
const page = read(pagePath);
const index = readJson(latestIndexPath);
const budget = readJson(latestBudgetPath);
const compat = readJson(latestCompatPath);

const expected = ['alpine-crystal', 'ocean-vapor', 'fog-forest', 'aurora-night'];

ok('family marker in page', page.includes('data-family-pack="unsplash-governed-4"'));
ok('page renders family list', page.includes('families.map'));
ok('css has family public base', css.includes('/surface-visual-governor/liquid-glass/families/'));
ok('css has jpg extension', css.includes('.jpg'));
ok('css keeps backdrop filter', css.includes('backdrop-filter') && css.includes('-webkit-backdrop-filter'));
ok('css keeps refraction filter id', css.includes('prisma-liquid-refraction'));
ok('css keeps reduced motion', css.includes('prefers-reduced-motion'));

for (const id of expected) {
  ok(`page family:${id}`, page.includes(id));
  ok(`css family:${id}`, css.includes(id));
  const file = path.join(root, 'products/pc/app/public/surface-visual-governor/liquid-glass/families', id, `${id}.jpg`);
  ok(`family asset exists:${id}`, fs.existsSync(file), file);
}

const families = index?.family_pack?.families || [];
ok('manifest family count 4', families.length === 4);
ok('manifest family pack id', index?.family_pack?.id === 'unsplash-governed-4');
ok('budget family count 4', budget?.visual_budget?.background_family_count === 4);
ok('compat family pack id', compat?.family_pack?.id === 'unsplash-governed-4');
ok('pos remains blocked', compat?.surfaces?.pos?.allowed === false);
ok('checkout remains blocked', compat?.surfaces?.checkout?.allowed === false);
ok('tablet remains blocked', compat?.surfaces?.tablet?.allowed === false);
ok('db untouched', compat?.db?.touched === false);
ok('deploy untouched', compat?.deploy?.performed === false);

const result = {
  pilot: '20_liquid_glass_reference_room',
  check: '4_family_background_pack',
  status: fail.length ? 'FAIL' : 'PASS',
  pass,
  fail,
};

console.log(JSON.stringify(result, null, 2));
if (fail.length) process.exit(1);
