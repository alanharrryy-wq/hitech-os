#!/usr/bin/env node
/* PRISMA Surface Visual Governor · Pilot 02 verifier */
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const app = path.join(root, 'products', 'chart-lab', 'app');
const base = path.join(app, 'public', 'surface-visual-governor', 'recipe-export', 'latest');
const required = ['chart.recipe.json','visual.recipe.json','motion.recipe.json','background.recipe.json','surface.compatibility.json','index.json'];
let failures = [];
function readJson(file) {
  const raw = fs.readFileSync(file, 'utf8');
  if (/[A-Za-z]:\\/.test(raw)) failures.push(`local path leak in ${file}`);
  if (/tablet-pos\.db|databasePaths|CLOUDFLARE_API_TOKEN/i.test(raw)) failures.push(`sensitive token/db marker in ${file}`);
  return JSON.parse(raw);
}
for (const name of required) {
  const file = path.join(base, name);
  if (!fs.existsSync(file)) failures.push(`missing ${file}`);
  else {
    const data = readJson(file);
    if (data.pilot !== '02_chart_lab_recipe_export') failures.push(`bad pilot marker in ${file}`);
    if (data.public_safety?.cloudflare_deploy_performed !== false) failures.push(`deploy marker not false in ${file}`);
    if (data.public_safety?.database_touched !== false) failures.push(`db marker not false in ${file}`);
  }
}
const compatibility = readJson(path.join(base, 'surface.compatibility.json'));
if (compatibility.surfaces?.pos?.allowed !== false) failures.push('POS is not blocked in compatibility file');
if (compatibility.surfaces?.tablet?.budget !== 'light-first') failures.push('Tablet is not light-first');
const bg = readJson(path.join(base, 'background.recipe.json'));
if (!bg.atmosphere_engine?.real_images_are_first_class) failures.push('Atmosphere Engine real-image flag missing');
if (!Array.isArray(bg.atmosphere_engine?.assets) || bg.atmosphere_engine.assets.length < 1) failures.push('No atmosphere assets registered');
const ts = path.join(app, 'src', 'prisma-surface-governor', 'chart-lab-recipe-export.ts');
if (!fs.existsSync(ts)) failures.push(`missing ${ts}`);
if (failures.length) {
  console.error('[PRISMA Pilot 02] FAIL');
  for (const f of failures) console.error(' - ' + f);
  process.exit(1);
}
console.log('[PRISMA Pilot 02] PASS: Chart Lab Recipe Export public recipes and compatibility gates verified.');
