#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const rootArgIndex = args.indexOf("--root");
const outArgIndex = args.indexOf("--out");
const root = path.resolve(rootArgIndex >= 0 ? args[rootArgIndex + 1] : process.cwd());
const outDir = outArgIndex >= 0 ? path.resolve(args[outArgIndex + 1]) : root;
const pcApp = path.join(root, "products", "pc", "app");

const requiredFiles = [
  "docs/PC_UIUX_SIMPLIFICATION_DEBT.md",
  "src/uiux/copy-dictionary.ts",
  "src/uiux/page-contracts.ts",
  "src/uiux/pc-uiux-baseline.json",
  "src/uiux/route-map.ts",
  "src/uiux/status-translator.ts",
  "src/composition/navigation.ts",
  "components/layout/app-shell.tsx",
  "components/uiux/decision-types.ts",
  "components/uiux/decision-header.tsx",
  "components/uiux/attention-summary.tsx",
  "components/uiux/next-best-action.tsx",
  "components/uiux/evidence-drawer.tsx",
  "components/uiux/human-status-badge.tsx",
  "components/uiux/human-error-state.tsx",
  "components/uiux/empty-state-human.tsx",
  "components/uiux/actionable-table.tsx",
  "components/uiux/chart-insight-card.tsx",
  "components/uiux/confirm-real-action-dialog.tsx",
  "components/uiux/decision-screen.tsx",
  "components/uiux/index.ts",
  "tools/verify_pc_uiux_ansi_nav_gate.mjs",
  "package.json"
];

const primaryLabels = [
  "Hoy",
  "Ventas y caja",
  "Inventario",
  "Compras",
  "Proveedores",
  "Sincronización",
  "Reportes",
  "Análisis",
  "Sistema",
  "Configuración"
];

const bannedFirstLevelLabels = [
  "Runtime",
  "Data Quality",
  "Tablet Communication",
  "License Runtime",
  "Audit",
  "Devices",
  "Movements",
  "Counts"
];

function read(rel) {
  return fs.readFileSync(path.join(pcApp, rel), "utf8");
}

function exists(rel) {
  return fs.existsSync(path.join(pcApp, rel));
}

const checks = [];
function push(name, status, detail = "") {
  checks.push({ name, status, detail });
}

for (const file of requiredFiles) {
  push(`exists:${file}`, exists(file) ? "PASS" : "FAIL", exists(file) ? "" : "Archivo requerido ausente");
}

if (exists("src/composition/navigation.ts")) {
  const nav = read("src/composition/navigation.ts");
  for (const label of primaryLabels) {
    push(`primary-nav-label:${label}`, nav.includes(`title: \"${label}\"`) ? "PASS" : "FAIL", "Debe existir en PC_PRIMARY_NAVIGATION");
  }
  for (const label of bannedFirstLevelLabels) {
    push(`no-banned-first-level:${label}`, nav.includes(`title: \"${label}\"`) ? "FAIL" : "PASS", "No debe aparecer como title de navegación principal");
  }
  push("primary-nav-count", (nav.match(/title: "/g) || []).length >= 10 ? "PASS" : "FAIL", "Debe declarar al menos 10 títulos humanos");
}

if (exists("components/layout/app-shell.tsx")) {
  const shell = read("components/layout/app-shell.tsx");
  push("app-shell-human-first-gate", shell.includes('data-uiux-gate="human-first-nav"') ? "PASS" : "FAIL", "AppShell debe declarar gate humano");
  push("app-shell-uses-primary-navigation", shell.includes("getPrimaryNavigation") ? "PASS" : "FAIL", "AppShell debe usar navegación principal humana");
  push("app-shell-no-old-nav-groups", shell.includes("GROUP_ORDER") ? "FAIL" : "PASS", "Debe retirar GROUP_ORDER antiguo del primer nivel");
}

if (exists("src/uiux/route-map.ts")) {
  const map = read("src/uiux/route-map.ts");
  for (const group of ["hoy", "ventas-caja", "inventario", "compras", "proveedores", "sincronizacion", "reportes", "analisis", "sistema", "configuracion"]) {
    push(`route-map-group:${group}`, map.includes(`\"group\": \"${group}\"`) ? "PASS" : "FAIL", "Grupo esperado no encontrado en route-map");
  }
}

const components = [
  "DecisionHeader",
  "AttentionSummary",
  "NextBestAction",
  "EvidenceDrawer",
  "HumanStatusBadge",
  "HumanErrorState",
  "EmptyStateHuman",
  "ActionableTable",
  "ChartInsightCard",
  "ConfirmRealActionDialog"
];
const uiuxDir = path.join(pcApp, "components", "uiux");
let allUiux = "";
if (fs.existsSync(uiuxDir)) {
  for (const file of fs.readdirSync(uiuxDir)) {
    if (file.endsWith(".ts") || file.endsWith(".tsx")) {
      allUiux += "\n" + fs.readFileSync(path.join(uiuxDir, file), "utf8");
    }
  }
}
for (const component of components) {
  push(`component-export:${component}`, allUiux.includes(`function ${component}`) || allUiux.includes(`const ${component}`) ? "PASS" : "FAIL", "Componente/gate requerido");
  push(`component-marker:${component}`, allUiux.includes(`data-prisma-component=\"${component}\"`) ? "PASS" : "WARN", "Se recomienda marcador data-prisma-component");
}

if (exists("package.json")) {
  const pkg = JSON.parse(read("package.json"));
  push("package-script-verify", pkg.scripts && pkg.scripts["verify:pc-uiux-ansi-nav-gate"] ? "PASS" : "FAIL", "Falta script de verificación");
}

const failCount = checks.filter((check) => check.status === "FAIL").length;
const warnCount = checks.filter((check) => check.status === "WARN").length;
const passCount = checks.filter((check) => check.status === "PASS").length;
const report = {
  generatedAt: new Date().toISOString(),
  root,
  pcApp,
  passCount,
  warnCount,
  failCount,
  checks
};

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "verify_pc_uiux_ansi_nav_gate.json"), JSON.stringify(report, null, 2));
fs.writeFileSync(path.join(outDir, "verify_pc_uiux_ansi_nav_gate.md"), `# PRISMA PC UIUX ANSI Nav Gate Verifier\n\n- PASS: ${passCount}\n- WARN: ${warnCount}\n- FAIL: ${failCount}\n\n${checks.map((check) => `- ${check.status}: ${check.name}${check.detail ? ` — ${check.detail}` : ""}`).join("\n")}\n`);

if (failCount > 0) {
  console.error(`[PRISMA PC UIUX] FAIL: ${failCount} checks failed.`);
  process.exit(1);
}
console.log(`[PRISMA PC UIUX] PASS: ${passCount} checks passed, ${warnCount} warnings.`);
