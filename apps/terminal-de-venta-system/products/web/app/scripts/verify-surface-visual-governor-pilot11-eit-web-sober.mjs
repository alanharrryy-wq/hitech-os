#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const appRoot = process.env.PRISMA_EIT_APP_ROOT || process.cwd();
const routeDir = path.join(appRoot, 'app', 'surface-governor-public-sober');
const page = path.join(routeDir, 'page.tsx');
const css = path.join(routeDir, 'prisma-eit-public-sober-shell.module.css');
const pub = path.join(appRoot, 'public', 'surface-visual-governor', 'eit-web-public-sober-shell', 'latest', 'index.json');
const errors = [];

function mustExist(file) {
  if (!fs.existsSync(file)) errors.push(`Missing ${file}`);
}

mustExist(page);
mustExist(css);
mustExist(pub);

if (fs.existsSync(page)) {
  const txt = fs.readFileSync(page, 'utf8');
  for (const token of ['data-prisma-surface="eit-web"', 'data-prisma-pilot="11_eit_web_public_sober_shell"', 'Public Sober Shell']) {
    if (!txt.includes(token)) errors.push(`page missing token ${token}`);
  }
}

if (fs.existsSync(css)) {
  const txt = fs.readFileSync(css, 'utf8').toLowerCase();
  for (const forbidden of ['webgl', 'pixi', 'storm-cloud-operations-real.jpg', 'obsidian-cloud-motion.svg', 'backdrop-filter', 'blur(']) {
    if (txt.includes(forbidden)) errors.push(`css contains forbidden active token ${forbidden}`);
  }
}

if (fs.existsSync(pub)) {
  try {
    const manifest = JSON.parse(fs.readFileSync(pub, 'utf8'));
    const surface = String(manifest.surface || manifest.surface_id || manifest.target || '').toLowerCase();
    const serialized = JSON.stringify(manifest).toLowerCase();
    if (!serialized.includes('eit') && !serialized.includes('web')) {
      errors.push('public manifest does not identify eit/web surface');
    }
  } catch (err) {
    errors.push(`public manifest is not valid JSON: ${err.message}`);
  }
}

if (errors.length) {
  console.error('[PILOT 11] FAIL');
  for (const err of errors) console.error(' - ' + err);
  process.exit(1);
}
console.log('[PILOT 11] PASS: EIT/Web public sober shell verified');
