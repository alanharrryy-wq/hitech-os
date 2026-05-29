import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const rel = (...parts) => path.join(root, ...parts);
const read = (p) => fs.readFileSync(rel(p), 'utf8');
const exists = (p) => fs.existsSync(rel(p));
const fail = (msg) => { console.error(`[PILOT03][FAIL] ${msg}`); process.exit(1); };
const pass = (msg) => console.log(`[PILOT03][PASS] ${msg}`);
const mustFile = (p) => { if (!exists(p)) fail(`Missing ${p}`); return rel(p); };
const parseJson = (p) => { try { return JSON.parse(read(p)); } catch (err) { fail(`Invalid JSON ${p}: ${err.message}`); } };
const sha256 = (p) => crypto.createHash('sha256').update(fs.readFileSync(rel(p))).digest('hex');

const pagePath = 'products/pc/app/app/referencia-visual/page.tsx';
const cssPath = 'products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/prisma-pc-reference-visual.css';
const indexPath = 'products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/index.json';
const routeManifestPath = 'products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/route.visual-reference.pilot-03.json';
const twinPath = 'products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/surface-twin.pc-reference.json';
const materialityPath = 'products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/materiality-catalog.registry.json';

mustFile(pagePath);
mustFile(cssPath);
mustFile(indexPath);
mustFile(routeManifestPath);
mustFile(twinPath);
mustFile(materialityPath);

const page = read(pagePath);
const css = read(cssPath);
for (const needle of ['PRISMA Surface Visual Governor · Pilot 03', 'Materiality Catalog', 'Atmosphere Engine', 'POS', '<LOCAL_PATH>']) {
  if (!page.includes(needle)) fail(`page.tsx missing required text: ${needle}`);
}
for (const needle of ['prefers-reduced-motion', 'storm-cloud-operations-real.jpg', 'prvSlowDrift', 'backdrop-filter']) {
  if (!css.includes(needle)) fail(`CSS missing required token: ${needle}`);
}

const index = parseJson(indexPath);
if (index.pilot !== '03_pc_referencia_visual') fail('index pilot id mismatch');
if (index.route !== '/referencia-visual') fail('index route mismatch');
if (index.gates?.pos?.allowed !== false) fail('POS gate must be false');
if (index.gates?.tablet?.light_first !== true) fail('Tablet light-first gate missing');
if (index.gates?.db?.touched !== false) fail('DB gate must be untouched');
if (index.gates?.deploy?.performed !== false) fail('deploy gate must be false');
if (index.gates?.dependencies?.installed !== false) fail('dependencies gate must be false');

const routeManifest = parseJson(routeManifestPath);
if (routeManifest.route !== '/referencia-visual') fail('route manifest route mismatch');
if (routeManifest.writes_limited_to_reference_route !== true) fail('route manifest write boundary missing');

const twin = parseJson(twinPath);
if (twin.surface !== 'pc') fail('surface twin must be pc');
if (twin.consumes?.materiality_catalog !== true) fail('surface twin must consume Materiality Catalog');
if (twin.consumes?.chart_lab_recipe_export !== true) fail('surface twin must consume Chart Lab recipes');

const materialitySize = fs.statSync(rel(materialityPath)).size;
if (materialitySize < 300000) fail(`Materiality registry too small: ${materialitySize}`);
pass(`Materiality registry mirror size ${materialitySize}`);

const recipeDir = 'products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/recipe-export';
for (const file of ['chart.recipe.json','visual.recipe.json','motion.recipe.json','background.recipe.json','surface.compatibility.json','ultra-codex.index.json','index.json']) {
  mustFile(path.join(recipeDir, file));
  parseJson(path.join(recipeDir, file));
}
const compat = parseJson(path.join(recipeDir, 'surface.compatibility.json'));
const compatText = JSON.stringify(compat).toLowerCase();
if (!compatText.includes('pos') || !compatText.includes('false')) fail('surface.compatibility.json does not visibly block POS');

const assetDir = rel('products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/atmosphere-assets/backgrounds');
if (!fs.existsSync(assetDir)) fail('missing atmosphere asset directory');
const assetFiles = fs.readdirSync(assetDir).filter((x) => /\.(svg|png|jpe?g|webp)$/i.test(x));
if (assetFiles.length < 3) fail(`expected at least 3 atmosphere assets, got ${assetFiles.length}`);
if (!assetFiles.includes('storm-cloud-operations-real.jpg')) fail('missing storm-cloud-operations-real.jpg');
pass(`Atmosphere assets mirrored: ${assetFiles.length}`);

for (const protectedRel of [
  'products/tablet/app/app/pos',
  'products/tablet/app/app/checkout',
  'products/tablet/app/components/pos'
]) {
  if (fs.existsSync(rel(protectedRel))) pass(`Protected path present and not required for Pilot 03 writes: ${protectedRel}`);
}

console.log(JSON.stringify({
  status: 'PASS',
  pilot: '03_pc_referencia_visual',
  pageSha256: sha256(pagePath),
  cssSha256: sha256(cssPath),
  materialityBytes: materialitySize,
  atmosphereAssets: assetFiles.length,
}, null, 2));
