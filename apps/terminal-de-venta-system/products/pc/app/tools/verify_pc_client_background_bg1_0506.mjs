#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const checks = [];
function ok(name, pass, detail = '') {
  checks.push({ name, pass, detail });
  const mark = pass ? 'PASS' : 'FAIL';
  console.log(`[${mark}] ${name}${detail ? ' :: ' + detail : ''}`);
}
function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}
const assetRel = 'public/backgrounds/prisma/pc-client-snow-mountains.png';
const cssRel = 'app/prisma-atmospheric-background.css';
const layoutRel = 'app/layout.tsx';
const componentRel = 'app/components/PrismaAtmosphericBackground.tsx';

const assetPath = path.join(root, assetRel);
ok('asset de fondo existe', fs.existsSync(assetPath), assetRel);
if (fs.existsSync(assetPath)) {
  const size = fs.statSync(assetPath).size;
  ok('asset no está vacío', size > 1024 * 100, `${size} bytes`);
}

const css = fs.existsSync(path.join(root, cssRel)) ? read(cssRel) : '';
ok('CSS atmosférico existe', !!css, cssRel);
ok('CSS contiene marcador bg1', css.includes('PRISMA PC CLIENT BACKGROUND BG1'), 'bloque gobernado');
ok('CSS usa imagen snow mountains', css.includes('/backgrounds/prisma/pc-client-snow-mountains.png'), 'url pública');
ok('CSS usa background-size cover', /background-size:\s*cover/i.test(css), 'cover');
ok('CSS mantiene selector pc-backoffice', css.includes('html[data-prisma-surface="pc-backoffice"]'), 'surface scoped');
ok('CSS conserva legibilidad con scrim', css.includes('prisma-bg-scrim') && css.includes('linear-gradient'), 'scrim/gradient');

const layout = fs.existsSync(path.join(root, layoutRel)) ? read(layoutRel) : '';
ok('layout existe', !!layout, layoutRel);
ok('layout importa CSS atmosférico', layout.includes('prisma-atmospheric-background.css'), 'import');
ok('layout renderiza PrismaAtmosphericBackground', layout.includes('<PrismaAtmosphericBackground />'), 'render');

const component = fs.existsSync(path.join(root, componentRel)) ? read(componentRel) : '';
ok('componente atmosférico existe', !!component, componentRel);
ok('componente conserva capas prisma-bg-base', component.includes('prisma-bg-base'), 'base layer');
ok('documentación bg1 existe', fs.existsSync(path.join(root, 'docs/pc-client-background-bg1-0506.md')), 'docs');

const failed = checks.filter((c) => !c.pass);
console.log(`\nPC background bg1 checks: ${checks.length - failed.length}/${checks.length} PASS`);
if (failed.length) process.exit(1);
