#!/usr/bin/env node
// Static guard for V03 files and package script wiring.
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
const args = new Map();
for (let i = 2; i < process.argv.length; i += 1) {
  const a = process.argv[i];
  if (a.startsWith('--')) {
    const k = a.slice(2);
    const v = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[++i] : 'true';
    args.set(k, v);
  }
}
const root = path.resolve(args.get('root') || path.join(process.cwd(), '../../..'));
const pcApp = path.join(root, 'products', 'pc', 'app');
const checks = [];
function check(id, pass, detail) { checks.push({ id, pass, detail }); }
function exists(rel) { return fs.existsSync(path.join(pcApp, rel)); }
check('visual-runner-exists', exists('tools/visual/verify_pc_uiux_visual_gate_v03.mjs'), 'tools/visual/verify_pc_uiux_visual_gate_v03.mjs');
check('visual-routes-exists', exists('tools/visual/pc-uiux-visual-routes.v03.json'), 'tools/visual/pc-uiux-visual-routes.v03.json');
const pkgPath = path.join(pcApp, 'package.json');
let pkg = {};
try { pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8')); check('package-json-readable', true, pkgPath); }
catch (err) { check('package-json-readable', false, String(err.message || err)); }
const scripts = pkg.scripts || {};
check('script-visual', typeof scripts['verify:pc-uiux-visual'] === 'string' && scripts['verify:pc-uiux-visual'].includes('verify_pc_uiux_visual_gate_v03.mjs'), scripts['verify:pc-uiux-visual'] || 'missing');
check('script-visual-static', typeof scripts['verify:pc-uiux-visual:static'] === 'string' && scripts['verify:pc-uiux-visual:static'].includes('verify_pc_uiux_visual_gate_v03_static.mjs'), scripts['verify:pc-uiux-visual:static'] || 'missing');
let routes = [];
try {
  const cfg = JSON.parse(fs.readFileSync(path.join(pcApp, 'tools/visual/pc-uiux-visual-routes.v03.json'), 'utf8'));
  routes = cfg.routes || [];
  check('routes-readable', true, `${routes.length} routes`);
  check('viewport-1920x1080', cfg.viewport?.width === 1920 && cfg.viewport?.height === 1080, JSON.stringify(cfg.viewport));
} catch (err) { check('routes-readable', false, String(err.message || err)); }
check('routes-core-count', routes.length >= 10, `${routes.length} routes`);
const required = ['/dashboard','/sales-control','/catalog','/purchasing','/proveedores','/sync','/exportables','/prisma-insights','/devices','/settings'];
for (const route of required) check(`route-${route}`, routes.some(r => r.route === route), route);
const failed = checks.filter(c => !c.pass);
const result = { status: failed.length ? 'FAIL' : 'PASS', pass: checks.length - failed.length, fail: failed.length, checks };
console.log(`[PRISMA PC UIUX V03 STATIC] ${result.status}: ${result.pass} passed, ${result.fail} failed.`);
for (const c of checks) console.log(`${c.pass ? 'PASS' : 'FAIL'} ${c.id} :: ${c.detail}`);
process.exit(failed.length ? 1 : 0);
