#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function argValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const root = path.resolve(argValue("--root", process.cwd()));
const outDir = path.resolve(argValue("--out", path.join(root, ".prisma_pc_uiux_v02_result")));
fs.mkdirSync(outDir, { recursive: true });

const pcApp = path.join(root, "products", "pc", "app");
const appDir = path.join(pcApp, "app");
const checks = [];
const rows = [];
const techDebtRows = [];

function exists(rel) { return fs.existsSync(path.join(root, rel)); }
function readRel(rel) { return fs.readFileSync(path.join(root, rel), "utf8"); }
function add(id, point, status, detail, severity = "P2") {
  checks.push({ id, point, status, detail, severity });
}
function pass(id, point, detail = "OK", severity = "P2") { add(id, point, "PASS", detail, severity); }
function warn(id, point, detail = "WARN") { add(id, point, "WARN", detail, "P3"); }
function fail(id, point, detail = "FAIL", severity = "P1") { add(id, point, "FAIL", detail, severity); }
function walk(dir, predicate, found = []) {
  if (!fs.existsSync(dir)) return found;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(p, predicate, found);
    else if (predicate(p)) found.push(p);
  }
  return found;
}
function routeFromPage(file) {
  const rel = path.relative(appDir, path.dirname(file)).replaceAll(path.sep, "/");
  return rel === "" ? "/" : `/${rel}`;
}
function parseRoutesFromTs(text) {
  return [...text.matchAll(/"?route"?:\s*"([^"]+)"/g)].map((m) => m[1]);
}
function parsePrimaryNavTitles(text) {
  const arraySlice = text.match(/PC_PRIMARY_NAVIGATION[\s\S]*?=\s*\[([\s\S]*?)\];/);
  if (!arraySlice) return [];
  return [...arraySlice[1].matchAll(/title:\s*"([^"]+)"/g)].map((m) => m[1]);
}
function csvEscape(value) { return `"${String(value ?? "").replaceAll('"', '""')}"`; }
function writeCsv(name, data, headers) {
  const csv = [headers.map(csvEscape).join(","), ...data.map((row) => headers.map((h) => csvEscape(row[h])).join(","))].join("\n");
  fs.writeFileSync(path.join(outDir, name), csv, "utf8");
}

const requiredFiles = [
  ["products/pc/app/src/uiux/copy-dictionary.ts", "Diccionario humano"],
  ["products/pc/app/src/uiux/status-translator.ts", "Traductor de estados"],
  ["products/pc/app/src/uiux/page-contracts.ts", "Contratos por ruta"],
  ["products/pc/app/src/uiux/route-map.ts", "Mapa de rutas"],
  ["products/pc/app/src/uiux/decision-model.ts", "Modelo de decisión"],
  ["products/pc/app/src/uiux/technical-route-map.ts", "Reubicación de términos técnicos"],
  ["products/pc/app/components/uiux/decision-screen.tsx", "DecisionScreen universal"],
  ["products/pc/app/components/uiux/pc-module-shell.tsx", "PcModuleShell"],
  ["products/pc/app/components/uiux/pc-subnav.tsx", "PcSubnav estándar"],
  ["products/pc/app/components/uiux/pc-route-contract-provider.tsx", "PcRouteContractProvider"],
  ["products/pc/app/tools/verify_pc_uiux_route_adoption_gate_v02.mjs", "Verificador V02"],
  ["products/pc/app/app/dashboard/page.tsx", "Adopción en Hoy"]
];

for (const [rel, point] of requiredFiles) {
  exists(rel) ? pass(`file:${rel}`, point, "Archivo presente", "P1") : fail(`file:${rel}`, point, "Archivo faltante", "P1");
}

const pageFiles = walk(appDir, (p) => p.endsWith("page.tsx"));
const pageRoutes = pageFiles.map(routeFromPage).sort();
const contractsText = exists("products/pc/app/src/uiux/page-contracts.ts") ? readRel("products/pc/app/src/uiux/page-contracts.ts") : "";
const routeMapText = exists("products/pc/app/src/uiux/route-map.ts") ? readRel("products/pc/app/src/uiux/route-map.ts") : "";
const contractRoutes = new Set(parseRoutesFromTs(contractsText));
const routeMapRoutes = new Set(parseRoutesFromTs(routeMapText));

for (const route of pageRoutes) {
  const hasContract = contractRoutes.has(route);
  const hasRouteMap = routeMapRoutes.has(route);
  rows.push({ route, hasContract: hasContract ? "YES" : "NO", hasRouteMap: hasRouteMap ? "YES" : "NO" });
}
const missingContracts = pageRoutes.filter((route) => !contractRoutes.has(route));
const missingRouteMap = pageRoutes.filter((route) => !routeMapRoutes.has(route));
missingContracts.length ? fail("route-contract-coverage", "Contratos para todas las rutas PC", `Faltan: ${missingContracts.join(", ")}`, "P1") : pass("route-contract-coverage", "Contratos para todas las rutas PC", `${pageRoutes.length} rutas cubiertas`, "P1");
missingRouteMap.length ? fail("route-map-coverage", "Route-map para todas las rutas PC", `Faltan: ${missingRouteMap.join(", ")}`, "P1") : pass("route-map-coverage", "Route-map para todas las rutas PC", `${pageRoutes.length} rutas cubiertas`, "P1");

const navigationText = exists("products/pc/app/src/composition/navigation.ts") ? readRel("products/pc/app/src/composition/navigation.ts") : "";
const primaryTitles = parsePrimaryNavTitles(navigationText);
const allowedPrimary = ["Hoy", "Ventas y caja", "Inventario", "Compras", "Proveedores", "Sincronización", "Reportes", "Análisis", "Sistema", "Configuración"];
const badPrimary = primaryTitles.filter((title) => !allowedPrimary.includes(title));
const technicalTerms = ["Runtime", "Data Quality", "License Runtime", "Tablet Communication", "Devices", "Audit", "Counts", "Movements"];
const technicalPrimary = primaryTitles.filter((title) => technicalTerms.some((term) => title.toLowerCase().includes(term.toLowerCase())));
if (badPrimary.length || technicalPrimary.length) fail("human-primary-navigation", "Navegación principal sólo humana", `No permitidos: ${[...badPrimary, ...technicalPrimary].join(", ")}`, "P1");
else pass("human-primary-navigation", "Navegación principal sólo humana", primaryTitles.join(" | "), "P1");

const appShellText = exists("products/pc/app/components/layout/app-shell.tsx") ? readRel("products/pc/app/components/layout/app-shell.tsx") : "";
appShellText.includes("getPrimaryRouteActions") && appShellText.includes("data-route-contract-resolved") ? pass("appshell-contract-actions", "AppShell resuelve título/acción desde contrato", "AppShell usa route model", "P1") : fail("appshell-contract-actions", "AppShell resuelve título/acción desde contrato", "No se detectó getPrimaryRouteActions/data-route-contract-resolved", "P1");
appShellText.includes("RouteIntentStrip") && appShellText.includes("PcSubnav") ? pass("appshell-intent-subnav", "AppShell muestra pregunta y subnav estándar", "RouteIntentStrip + PcSubnav", "P1") : fail("appshell-intent-subnav", "AppShell muestra pregunta y subnav estándar", "No se detectó RouteIntentStrip/PcSubnav", "P1");

const dashboardText = exists("products/pc/app/app/dashboard/page.tsx") ? readRel("products/pc/app/app/dashboard/page.tsx") : "";
dashboardText.includes("DecisionScreen") ? pass("dashboard-decision-screen", "DecisionScreen integrado en Hoy", "Dashboard importa/renderiza DecisionScreen", "P1") : fail("dashboard-decision-screen", "DecisionScreen integrado en Hoy", "Dashboard no usa DecisionScreen", "P1");
dashboardText.includes("buildEvidenceDrawerItems") ? pass("dashboard-evidence", "EvidenceDrawer real por pantalla", "Dashboard alimenta evidencia desde contrato", "P1") : fail("dashboard-evidence", "EvidenceDrawer real por pantalla", "Dashboard no alimenta evidencia", "P1");

const decisionModelText = exists("products/pc/app/src/uiux/decision-model.ts") ? readRel("products/pc/app/src/uiux/decision-model.ts") : "";
[
  ["normalizePcPathname", "Normalización de rutas"],
  ["getPcRouteContract", "Resolución de contrato por ruta"],
  ["buildEvidenceDrawerItems", "Builder de evidencia"],
  ["PC_STANDARD_SUBNAV", "Subnav estándar"],
  ["getPrimaryRouteActions", "Acciones por contrato"],
  ["getRouteEmptyState", "Empty states por contrato"],
  ["getRouteErrorState", "Error states por contrato"]
].forEach(([needle, point]) => decisionModelText.includes(needle) ? pass(`decision-model:${needle}`, point, "Presente") : fail(`decision-model:${needle}`, point, "Faltante", "P1"));

const evidenceText = exists("products/pc/app/components/uiux/evidence-drawer.tsx") ? readRel("products/pc/app/components/uiux/evidence-drawer.tsx") : "";
evidenceText.includes("<details") && evidenceText.includes("data-evidence-default=\"closed\"") ? pass("evidence-closed", "Evidencia técnica cerrada por defecto", "details + data-evidence-default", "P1") : fail("evidence-closed", "Evidencia técnica cerrada por defecto", "No se detectó details cerrado", "P1");
evidenceText.includes("operational") && evidenceText.includes("technical") ? pass("evidence-separated", "Evidencia operativa separada de técnica", "Kinds separados", "P2") : fail("evidence-separated", "Evidencia operativa separada de técnica", "No hay separación", "P2");

const statusBadgeText = exists("products/pc/app/components/uiux/human-status-badge.tsx") ? readRel("products/pc/app/components/uiux/human-status-badge.tsx") : "";
statusBadgeText.includes("humanizePcStatus") ? pass("status-translator-used", "Status translator usado por badges", "HumanStatusBadge importa humanizePcStatus", "P1") : fail("status-translator-used", "Status translator usado por badges", "No se detectó humanizePcStatus", "P1");

const statusTranslatorText = exists("products/pc/app/src/uiux/status-translator.ts") ? readRel("products/pc/app/src/uiux/status-translator.ts") : "";
statusTranslatorText.includes("humanizePcConfidence") && statusTranslatorText.includes("humanizePcFreshness") ? pass("confidence-freshness-translated", "Confidence/freshness traducidos", "Funciones presentes", "P2") : fail("confidence-freshness-translated", "Confidence/freshness traducidos", "Faltan traductores", "P2");

const tableText = exists("products/pc/app/components/uiux/actionable-table.tsx") ? readRel("products/pc/app/components/uiux/actionable-table.tsx") : "";
tableText.includes("Qué hacer") && tableText.includes("data-action-column") ? pass("actionable-table-enforces-action", "Tabla accionable exige Qué hacer", "Columna obligatoria/autogenerada", "P2") : fail("actionable-table-enforces-action", "Tabla accionable exige Qué hacer", "No se detectó columna de acción", "P2");

const confirmText = exists("products/pc/app/components/uiux/confirm-real-action-dialog.tsx") ? readRel("products/pc/app/components/uiux/confirm-real-action-dialog.tsx") : "";
confirmText.includes("Entiendo la consecuencia") ? pass("confirm-real-action", "Confirmación para acciones reales", "Checkbox de consecuencia presente", "P2") : warn("confirm-real-action", "Confirmación para acciones reales", "No se detectó texto esperado");

const technicalMapText = exists("products/pc/app/src/uiux/technical-route-map.ts") ? readRel("products/pc/app/src/uiux/technical-route-map.ts") : "";
for (const term of technicalTerms) {
  if (technicalMapText.toLowerCase().includes(term.toLowerCase())) pass(`technical-relocation:${term}`, `Reubicación de ${term}`, "Mapeado", "P2");
  else warn(`technical-relocation:${term}`, `Reubicación de ${term}`, "No mapeado");
}

const pkgText = exists("products/pc/app/package.json") ? readRel("products/pc/app/package.json") : "{}";
let pkg = {};
try { pkg = JSON.parse(pkgText); } catch {}
const scripts = pkg.scripts || {};
if (scripts["verify:pc-uiux-route-adoption"]) pass("package-script-v02", "Script de verificación V02 en package.json", scripts["verify:pc-uiux-route-adoption"], "P1");
else fail("package-script-v02", "Script de verificación V02 en package.json", "Falta script", "P1");
if (scripts.typecheck || scripts.build) pass("package-smoke-declared", "Smoke typecheck/build declarado", `typecheck=${Boolean(scripts.typecheck)} build=${Boolean(scripts.build)}`, "P2");
else warn("package-smoke-declared", "Smoke typecheck/build declarado", "No hay scripts typecheck/build");

const fakeGreen = checks.filter((check) => check.status === "PASS" && /falta|missing|no se detect/i.test(check.detail));
fakeGreen.length ? fail("no-fake-green", "No fake green en verificador", `PASS sospechosos: ${fakeGreen.map((c) => c.id).join(", ")}`, "P1") : pass("no-fake-green", "No fake green en verificador", "No hay PASS con detalle contradictorio", "P1");

for (const route of pageRoutes) {
  const pageText = fs.readFileSync(pageFiles.find((p) => routeFromPage(p) === route), "utf8");
  const usesDecision = pageText.includes("DecisionScreen");
  const usesAppShell = pageText.includes("AppShell");
  const usesEvidence = pageText.includes("EvidenceDrawer") || pageText.includes("buildEvidenceDrawerItems") || pageText.includes("Ver evidencia técnica");
  const hasHumanContract = contractRoutes.has(route);
  rows.find((r) => r.route === route).usesDecisionScreen = usesDecision ? "YES" : "NO";
  rows.find((r) => r.route === route).usesAppShell = usesAppShell ? "YES" : "NO";
  rows.find((r) => r.route === route).usesEvidence = usesEvidence ? "YES" : "NO";
  rows.find((r) => r.route === route).hasHumanContract = hasHumanContract ? "YES" : "NO";
}

for (const title of primaryTitles) {
  for (const term of technicalTerms) {
    if (title.toLowerCase().includes(term.toLowerCase())) {
      techDebtRows.push({ location: "primary-nav", term, current: title, target: "Sistema/Sincronización/Inventario/Evidencia" });
    }
  }
}

const passCount = checks.filter((c) => c.status === "PASS").length;
const warnCount = checks.filter((c) => c.status === "WARN").length;
const failCount = checks.filter((c) => c.status === "FAIL").length;
const blockingFails = checks.filter((c) => c.status === "FAIL" && ["P0", "P1"].includes(c.severity));

writeCsv("ROUTE_ADOPTION_MATRIX.csv", rows, ["route", "hasContract", "hasRouteMap", "usesDecisionScreen", "usesAppShell", "usesEvidence", "hasHumanContract"]);
writeCsv("TECHNICAL_NAV_DEBT.csv", techDebtRows, ["location", "term", "current", "target"]);
writeCsv("CHECKS.csv", checks, ["id", "point", "status", "severity", "detail"]);

const checklist = [
  `# PRISMA PC UIUX V02 Checklist`,
  "",
  `**PASS:** ${passCount}`,
  `**WARN:** ${warnCount}`,
  `**FAIL:** ${failCount}`,
  "",
  ...checks.map((c) => `${c.status === "PASS" ? "✅" : c.status === "WARN" ? "⚠️" : "❌"} ${c.point} — ${c.detail}`)
].join("\n");
fs.writeFileSync(path.join(outDir, "V02_CHECKLIST.md"), checklist, "utf8");

const nextActions = [
  "# NEXT ACTIONS ORDERED",
  "",
  blockingFails.length ? "## Primero corrige bloqueos P0/P1" : "## Siguiente paso recomendado",
  blockingFails.length ? blockingFails.map((c, i) => `${i+1}. ${c.point}: ${c.detail}`).join("\n") : "1. V03: Playwright 1920x1080 para capturas, overflow, jerarquía visual y navegación visible.",
  "2. Adoptar DecisionScreen en Inventario, Compras, Proveedores y Sincronización.",
  "3. Medir dependencia visual real por interfaz antes de instalar librerías nuevas.",
  "4. Convertir deuda restante en gates por módulo."
].join("\n");
fs.writeFileSync(path.join(outDir, "NEXT_ACTIONS_ORDERED.md"), nextActions, "utf8");

fs.writeFileSync(path.join(outDir, "VERIFY_RESULT.json"), JSON.stringify({ status: blockingFails.length ? "FAIL" : "PASS", passCount, warnCount, failCount, blockingFailCount: blockingFails.length, root, checkedAt: new Date().toISOString(), checks }, null, 2), "utf8");

console.log(`[PRISMA PC UIUX V02] ${blockingFails.length ? "FAIL" : "PASS"}: ${passCount} passed, ${warnCount} warnings, ${failCount} failures.`);
process.exit(blockingFails.length ? 1 : 0);
