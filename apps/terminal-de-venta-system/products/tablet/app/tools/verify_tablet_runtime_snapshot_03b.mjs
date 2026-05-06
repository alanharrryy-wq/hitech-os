#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const fail = (message) => {
  console.error(`FAIL ${message}`);
  process.exitCode = 1;
};
const ok = (message) => console.log(`OK ${message}`);
const read = (rel) => fs.readFileSync(path.join(root, rel), "utf8");
const exists = (rel) => fs.existsSync(path.join(root, rel));

const required = [
  "components/tablet-shell/tablet-nav.ts",
  "components/tablet-shell/prisma-tablet-shell.tsx",
  "components/tablet-shell/prisma-tablet-shell.module.css",
  "components/tablet-runtime/tablet-runtime-status-strip.tsx",
  "components/tablet-runtime/tablet-runtime-panel.tsx",
  "components/tablet-home/tablet-home-screen.tsx",
  "components/tablet-home/tablet-home.module.css",
  "src/lib/tablet-runtime-snapshot/shell-contract.ts",
  "src/lib/tablet-runtime-snapshot/view-model.ts",
  "src/lib/tablet-runtime-snapshot/visible-copy.ts",
  "src/lib/tablet-home/home-view-model.ts",
  "src/lib/tablet-home/operational-priority.ts",
  "src/server/tablet-runtime-snapshot/index.ts",
  "src/server/tablet-runtime-snapshot/build.ts",
  "src/server/tablet-runtime-snapshot/queries.prisma.ts",
  "src/server/tablet-runtime-snapshot/env.ts",
  "app/api/tablet/runtime/snapshot/route.ts",
  "app/page.tsx",
  "app/inventory/page.tsx",
  "app/existencias/page.tsx",
  "app/runtime-snapshot-preview/page.tsx",
  "docs/ux/PRISMA_TABLET_RUNTIME_SNAPSHOT_03B.md",
  "docs/ux/PRISMA_TABLET_HOME_SCREEN_03C.md",
  "docs/qa/PRISMA_TABLET_RUNTIME_SNAPSHOT_03B_QA.md",
  "docs/architecture/PRISMA_TABLET_RUNTIME_HOME_03B_03C_CONTRACT.md",
  "tools/fixtures/tablet_runtime_snapshot_03b_scenarios.json",
  "tools/fixtures/tablet_home_03c_acceptance.json",
  "tools/verify_tablet_runtime_home_03b_03c_deep.mjs",
  "tools/fixtures/tablet_operational_priorities_03c_cases.json",
  "tools/verify_tablet_operational_priorities_03c_cases.mjs"
];
for (const rel of required) exists(rel) ? ok(`exists ${rel}`) : fail(`missing ${rel}`);

const nav = read("components/tablet-shell/tablet-nav.ts");
const navArrayMatch = nav.match(/export const TABLET_NAV_ITEMS:[\s\S]*?= \[([\s\S]*?)\];/);
if (!navArrayMatch) fail("TABLET_NAV_ITEMS not found");
const navArray = navArrayMatch?.[1] ?? "";
const mainItems = [...navArray.matchAll(/href:\s*"([^"]+)",[\s\S]*?label:\s*"([^"]+)"/g)].map((match) => ({ href: match[1], label: match[2] }));
const expectedLabels = ["Inicio", "Vender", "Ventas de hoy", "Catalogo", "Existencias", "Turno"];
const expectedHrefs = ["/", "/pos", "/sales/today", "/catalog", "/stock", "/shift"];
if (mainItems.length !== 6) fail(`expected 6 main nav items, got ${mainItems.length}`); else ok("main nav has exactly 6 visible entries");
expectedLabels.forEach((label, index) => {
  if (mainItems[index]?.label !== label) fail(`nav label ${index} expected ${label}, got ${mainItems[index]?.label}`); else ok(`nav label ${label}`);
});
expectedHrefs.forEach((href, index) => {
  if (mainItems[index]?.href !== href) fail(`nav href ${index} expected ${href}, got ${mainItems[index]?.href}`); else ok(`nav href ${href}`);
});

const forbiddenMain = ["Cobro", "Devoluciones", "Sincronizacion", "Exportar"];
for (const word of forbiddenMain) {
  const inMain = mainItems.some((item) => item.label === word);
  if (inMain) fail(`${word} appears in main navigation`); else ok(`${word} not in main navigation`);
}
if (!navArray.includes('primary: true')) fail("Vender does not declare primary weight"); else ok("Vender declares primary visual weight");
if (!nav.includes('/inventory') || !nav.includes('/existencias')) fail("stock aliases are not declared"); else ok("stock aliases declared");

const shell = read("components/tablet-shell/prisma-tablet-shell.tsx");
["TabletRuntimeStatusStrip", "DEFAULT_TABLET_RUNTIME_SNAPSHOT", "runtimeSnapshot", "Venta autonoma"].forEach((needle) => {
  if (!shell.includes(needle)) fail(`shell missing ${needle}`); else ok(`shell includes ${needle}`);
});
if (shell.includes('href="/checkout"') || shell.includes('href="/returns"') || shell.includes('href="/settings/export"')) fail("shell exposes secondary routes as primary actions"); else ok("shell keeps secondary routes out of primary action chrome");

const route = read("app/api/tablet/runtime/snapshot/route.ts");
["getTabletRuntimeSnapshotFromRequest", "schemaVersion", "localSalesAllowed", "pcRequiredForBasicSale"].forEach((needle) => {
  if (!route.includes(needle)) fail(`runtime API route missing ${needle}`); else ok(`runtime API route includes ${needle}`);
});

const build = read("src/server/tablet-runtime-snapshot/build.ts");
["buildTabletRuntimeSnapshot", "TABLET_RUNTIME_VISIBLE_COPY.connection", "TABLET_RUNTIME_VISIBLE_COPY.catalog", "TABLET_RUNTIME_VISIBLE_COPY.shift", "pcRequiredForBasicSale: false"].forEach((needle) => {
  if (!build.includes(needle)) fail(`snapshot builder missing ${needle}`); else ok(`snapshot builder includes ${needle}`);
});

const homePage = read("app/page.tsx");
["getTabletRuntimeSnapshot", "readRuntimeSnapshotInput", "TabletHomeScreen", "runtimeSnapshot={snapshot}"].forEach((needle) => {
  if (!homePage.includes(needle)) fail(`home page missing ${needle}`); else ok(`home page includes ${needle}`);
});
const homeVm = read("src/lib/tablet-home/home-view-model.ts");
const prioritySource = read("src/lib/tablet-home/operational-priority.ts");
["buildTabletHomeViewModel", "buildTabletOperationalPriorities(snapshot)", "Abrir turno", "Ir a vender"].forEach((needle) => {
  if (!homeVm.includes(needle)) fail(`home view-model missing ${needle}`); else ok(`home view-model includes ${needle}`);
});
["Pendientes por enviar", "Existencias con presion", "reasonSignals", "weight:"].forEach((needle) => {
  if (!prioritySource.includes(needle)) fail(`priority source missing ${needle}`); else ok(`priority source includes ${needle}`);
});
const homeUi = read("components/tablet-home/tablet-home-screen.tsx");
["Inicio operativo", "Metricas rapidas", "Alertas que", "TabletRuntimePanel"].forEach((needle) => {
  if (!homeUi.includes(needle)) fail(`home screen missing ${needle}`); else ok(`home screen includes ${needle}`);
});

const visibleFiles = [
  "components/tablet-shell/tablet-nav.ts",
  "components/tablet-shell/prisma-tablet-shell.tsx",
  "components/tablet-runtime/tablet-runtime-status-strip.tsx",
  "components/tablet-home/tablet-home-screen.tsx",
  "src/lib/tablet-home/home-view-model.ts",
  "src/lib/tablet-runtime-snapshot/visible-copy.ts"
];
const forbiddenVisible = ["outbox", "payload", "schema", "mutation", "lookup", "amountCents", "businessId", "terminalId", "undefined", "null", "NaN", "fatal"];
for (const rel of visibleFiles) {
  const text = read(rel);
  for (const term of forbiddenVisible) {
    const visibleStringPattern = new RegExp(`>[^
<]*${term}[^
<]*<|label:\\s*\"[^\"]*${term}[^\"]*\"`, "i");
    if (visibleStringPattern.test(text)) fail(`${rel} exposes technical term ${term}`);
  }
  ok(`${rel} passes visible technical-copy scan`);
}

const fixtures = JSON.parse(read("tools/fixtures/tablet_runtime_snapshot_03b_scenarios.json"));
if (!Array.isArray(fixtures.cases) || fixtures.cases.length < 6) fail("runtime scenario fixtures are incomplete"); else ok(`runtime scenario fixtures ${fixtures.cases.length} cases`);
for (const scenario of fixtures.cases) {
  for (const key of ["shift", "connection", "catalog"]) {
    if (!scenario.expected?.[key]) fail(`scenario ${scenario.name} missing expected ${key}`);
  }
  ok(`scenario contract ${scenario.name}`);
}
const homeFixtures = JSON.parse(read("tools/fixtures/tablet_home_03c_acceptance.json"));
if (!Array.isArray(homeFixtures.cases) || homeFixtures.cases.length < 8) fail("home acceptance fixtures are incomplete"); else ok(`home acceptance fixtures ${homeFixtures.cases.length} cases`);
for (const scenario of homeFixtures.cases) {
  if (!scenario.expected?.primaryAction) fail(`home scenario ${scenario.name} missing primary action`);
  ok(`home scenario contract ${scenario.name}`);
}

const installManifestGate = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_installation_manifest_03b_03c_03d.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (installManifestGate.stdout) process.stdout.write(installManifestGate.stdout);
if (installManifestGate.stderr) process.stderr.write(installManifestGate.stderr);
if (installManifestGate.status !== 0) fail(`installation manifest gate failed with status ${installManifestGate.status}`); else ok("installation manifest gate passed");

const routeGate = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_route_contract_03b.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (routeGate.stdout) process.stdout.write(routeGate.stdout);
if (routeGate.stderr) process.stderr.write(routeGate.stderr);
if (routeGate.status !== 0) fail(`route gate failed with status ${routeGate.status}`); else ok("route gate passed");

const qualityGate = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_no_filler_gate_03b_03c_03d.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (qualityGate.stdout) process.stdout.write(qualityGate.stdout);
if (qualityGate.stderr) process.stderr.write(qualityGate.stderr);
if (qualityGate.status !== 0) fail(`quality gate failed with status ${qualityGate.status}`); else ok("quality gate passed");

const runtimeMatrix = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_runtime_builder_03b_cases.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (runtimeMatrix.stdout) process.stdout.write(runtimeMatrix.stdout);
if (runtimeMatrix.stderr) process.stderr.write(runtimeMatrix.stderr);
if (runtimeMatrix.status !== 0) fail(`runtime matrix verifier failed with status ${runtimeMatrix.status}`); else ok("runtime matrix verifier passed");

const homeMatrix = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_home_view_model_03c_cases.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (homeMatrix.stdout) process.stdout.write(homeMatrix.stdout);
if (homeMatrix.stderr) process.stderr.write(homeMatrix.stderr);
if (homeMatrix.status !== 0) fail(`home matrix verifier failed with status ${homeMatrix.status}`); else ok("home matrix verifier passed");

const priorityMatrix = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_operational_priorities_03c_cases.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (priorityMatrix.stdout) process.stdout.write(priorityMatrix.stdout);
if (priorityMatrix.stderr) process.stderr.write(priorityMatrix.stderr);
if (priorityMatrix.status !== 0) fail(`priority matrix verifier failed with status ${priorityMatrix.status}`); else ok("priority matrix verifier passed");

const cartCases = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_cart_engine_03d_cases.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (cartCases.stdout) process.stdout.write(cartCases.stdout);
if (cartCases.stderr) process.stderr.write(cartCases.stderr);
if (cartCases.status !== 0) fail(`cart cases verifier failed with status ${cartCases.status}`); else ok("cart cases verifier passed");

const cart = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_sell_cart_03d.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (cart.stdout) process.stdout.write(cart.stdout);
if (cart.stderr) process.stderr.write(cart.stderr);
if (cart.status !== 0) fail(`cart verifier failed with status ${cart.status}`); else ok("cart verifier passed");

const deep = spawnSync(process.execPath, [path.join(root, "tools", "verify_tablet_runtime_home_03b_03c_deep.mjs")], {
  cwd: root,
  encoding: "utf8"
});
if (deep.stdout) process.stdout.write(deep.stdout);
if (deep.stderr) process.stderr.write(deep.stderr);
if (deep.status !== 0) fail(`deep verifier failed with status ${deep.status}`); else ok("deep verifier passed");

if (process.exitCode) {
  process.exit(process.exitCode);
}
ok("PRISMA_TABLET_RUNTIME_SNAPSHOT_HOME_03B_03C verify complete");
