#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
let failed = false;
function ok(message){ console.log(`OK ${message}`); }
function fail(message){ console.error(`FAIL ${message}`); failed = true; }
function read(rel){ const file=path.join(root,rel); if(!fs.existsSync(file)){ fail(`missing ${rel}`); return "";} return fs.readFileSync(file,"utf8"); }

const nav = read("components/tablet-shell/tablet-nav.ts");
const shell = read("components/tablet-shell/prisma-tablet-shell.tsx");
const home = read("app/page.tsx");
const inventory = read("app/inventory/page.tsx");
const existencias = read("app/existencias/page.tsx");
const routeRules = [
  { route: "/", owner: "Inicio", visible: true, expectedInNav: true },
  { route: "/pos", owner: "Vender", visible: true, expectedInNav: true },
  { route: "/sales/today", owner: "Ventas de hoy", visible: true, expectedInNav: true },
  { route: "/catalog", owner: "Catalogo", visible: true, expectedInNav: true },
  { route: "/stock", owner: "Existencias", visible: true, expectedInNav: true },
  { route: "/shift", owner: "Turno", visible: true, expectedInNav: true },
  { route: "/checkout", owner: "Cobro", visible: false, expectedInNav: false },
  { route: "/returns", owner: "Devolucion", visible: false, expectedInNav: false },
  { route: "/sync", owner: "Sincronizacion", visible: false, expectedInNav: false },
  { route: "/settings/export", owner: "Exportar", visible: false, expectedInNav: false },
  { route: "/events/outbox", owner: "Pendientes por enviar", visible: false, expectedInNav: false },
  { route: "/inventory", owner: "Alias Existencias", visible: false, expectedInNav: false, aliasTo: "/stock" },
  { route: "/existencias", owner: "Alias Existencias", visible: false, expectedInNav: false, aliasTo: "/stock" }
];
for (const rule of routeRules) {
  const navContains = nav.includes(`href: "${rule.route}"`);
  if (rule.expectedInNav && !navContains) fail(`${rule.route} should be in main nav`);
  if (!rule.expectedInNav && navContains && nav.indexOf("TABLET_SECONDARY_ROUTES") > nav.indexOf(`href: "${rule.route}"`)) {
    fail(`${rule.route} appears before secondary route registry`);
  }
  ok(`route rule checked ${rule.route}`);
}
if (!inventory.includes('redirect("/stock")')) fail('/inventory does not redirect to /stock'); else ok('/inventory redirects to /stock');
if (!existencias.includes('redirect("/stock")')) fail('/existencias does not redirect to /stock'); else ok('/existencias redirects to /stock');
if (!home.includes('currentPath="/"')) fail('home does not declare currentPath=/'); else ok('home currentPath ok');
if (!shell.includes('aria-label="Navegacion principal de Tablet"')) fail('shell navigation aria label missing'); else ok('shell navigation aria label ok');
const secondary = nav.slice(nav.indexOf('TABLET_SECONDARY_ROUTES'));
for (const route of ['/checkout','/returns','/sync','/settings/export','/events/outbox','/inventory','/existencias']) {
  if (!secondary.includes(route)) fail(`secondary registry missing ${route}`); else ok(`secondary registry contains ${route}`);
}
if (failed) process.exit(1);
ok('route contract gate passed');
