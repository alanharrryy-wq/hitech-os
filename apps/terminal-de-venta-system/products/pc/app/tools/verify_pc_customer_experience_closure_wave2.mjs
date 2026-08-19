import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const pcRoot = path.resolve(here, "..");

const results = [];
const failures = [];

function rel(...parts) {
  return path.join(pcRoot, ...parts);
}

function read(...parts) {
  return fs.readFileSync(rel(...parts), "utf8");
}

function record(id, pass, detail) {
  const status = pass ? "PASS" : "FAIL";
  results.push({ id, status, detail });
  if (!pass) failures.push({ id, detail });
}

function exists(id, ...parts) {
  const target = rel(...parts);
  record(id, fs.existsSync(target), path.relative(pcRoot, target).replaceAll("\\", "/"));
}

function includes(id, source, token, detail = token) {
  record(id, source.includes(token), detail);
}

function excludes(id, source, token, detail = token) {
  record(id, !source.includes(token), detail);
}

const wave2Routes = ["catalog", "proveedores", "clientes", "sync", "devices", "settings"];
for (const route of wave2Routes) {
  exists(`route.${route}.page`, "app", route, "page.tsx");
  exists(`route.${route}.loading`, "app", route, "loading.tsx");
  exists(`route.${route}.error`, "app", route, "error.tsx");
}

const navigation = read("src", "composition", "navigation.ts");
for (const route of ["/catalog", "/proveedores", "/clientes", "/sync", "/devices", "/settings"]) {
  includes(`nav.primary.${route}`, navigation, `"${route}"`, `primary navigation contains ${route}`);
}

const customerService = read("src", "server", "services", "customer.service.ts");
const taskService = read("src", "server", "services", "operational-task.service.ts");
const mediaService = read("src", "server", "services", "product-media.service.ts");
const variantService = read("src", "server", "services", "product-variant.service.ts");
const apiResponse = read("src", "lib", "backoffice", "api-response.ts");

for (const [name, source] of [
  ["customers", customerService],
  ["operationalTasks", taskService],
  ["productMedia", mediaService],
  ["productVariants", variantService]
]) {
  excludes(`copy.${name}.rawErrorMessage`, source, "error instanceof Error ? error.message", `${name} does not project raw error.message`);
  excludes(`copy.${name}.migrationInstruction`, source, "Verifica la migración canónica", `${name} does not instruct customers about migrations`);
}
excludes("api.backoffice.rawDetails", apiResponse, "details: { message }", "backoffice 500 does not return raw exception text");
excludes("api.backoffice.rawException", apiResponse, "const message = error instanceof Error", "backoffice 500 does not derive a customer payload from exception.message");

const catalog = read("components", "catalog", "catalog-dashboard.tsx");
const previewCount = (catalog.match(/className=\{mediaStyles\.preview\}/g) ?? []).length;
record("catalog.singlePreview", previewCount === 1, `image preview count=${previewCount}`);
for (const token of ["Sin dock de selectores como aduana", "La tabla manda", "Estado honesto", "Editar bloqueado hasta auditoría", "Barcode"] ) {
  excludes(`catalog.copy.${token}`, catalog, token, `catalog excludes customer-facing technical copy: ${token}`);
}

const customerWorkspace = read("components", "customers", "customer-workspace.tsx");
for (const token of ["fuente canónica", "pendiente de migración", "proyección local de Tablet", "alta canónica", "Versión {selected.version}"]) {
  excludes(`customers.copy.${token}`, customerWorkspace, token, `customers excludes internal copy: ${token}`);
}
includes("customers.action.create", customerWorkspace, "fetch(\"/api/backoffice/customers\"", "customer create action remains wired");
includes("customers.action.update", customerWorkspace, "method: \"PATCH\"", "customer update action remains wired");

const license = read("components", "license", "license-status-card.tsx");
for (const token of ["status.customerId", "status.businessId", "status.source", "readiness.handoff", "readiness.deviceScope.note", "<strong>{feature.key}</strong>"]) {
  excludes(`license.visible.${token}`, license, token, `license projection excludes ${token}`);
}
includes("license.featureLabels", license, "function featureLabel", "license maps capability keys to customer labels");

const commandCenter = read("components", "control", "pc-command-center-page.tsx");
includes("wave2.commandCenter.scope", commandCenter, "model.currentPath === \"/sync\" || model.currentPath === \"/devices\"", "customer-safe projection is isolated to Sync and Devices");
includes("wave2.commandCenter.tableProjection", commandCenter, "wave2CustomerTable", "Sync/Devices tables pass through customer projection");
includes("wave2.commandCenter.actionSafe", commandCenter, "customerSafe={wave2CustomerSurface}", "Sync/Devices actions use customer-safe failures");
includes("wave2.commandCenter.noApiLinks", commandCenter, "!action.href.startsWith(\"/api/\")", "customer surface hides direct GET API links");
includes("wave2.commandCenter.stripDetails", commandCenter, "const projected: CommandTableRow = {}", "customer table is rebuilt from visible columns instead of forwarding technical detail metadata");

const commandActions = read("components", "control", "pc-command-actions.tsx");
includes("wave2.actions.genericFailure", commandActions, "No pudimos completar la acción", "customer-safe POST failure is generic");
includes("wave2.actions.optIn", commandActions, "customerSafe = false", "Wave 1 keeps previous action behavior unless Wave 2 opts in");

const syncPanel = read("components", "sync", "pc-sync-chart-promotion-panel.tsx");
for (const token of ["payload.message", "cursor:", "quality.sourceLabel", "quality.confidence.level", "quality.fallbackReason", "charts promovidos", "timeline de comandos"] ) {
  excludes(`sync.copy.${token}`, syncPanel, token, `sync customer view excludes ${token}`);
}
includes("sync.copy.safeFailure", syncPanel, "No pudimos cargar el estado de sincronización. Intenta de nuevo.", "sync chart failure is customer-safe");
includes("sync.copy.entityLabels", syncPanel, "function entityLabel", "sync entity names are projected to customer labels");

const overview = read("components", "backoffice", "module-overview-page.tsx");
includes("settings.customerProjection", overview, "overview.route === \"/settings\"", "settings has route-scoped customer projection");
includes("settings.customerTitle", overview, "Usuarios y roles", "settings uses customer-facing title");

const operation = read("components", "operations", "operation-workspace.tsx");
for (const token of ["PurchaseOrder", "ReplenishmentSignal", "Sale + SaleReturn", "Nada de NaN", "no chisme con icono rojo", "Ruta" ]) {
  excludes(`suppliers.copy.${token}`, operation, token, `supplier/procurement view excludes ${token}`);
}

const guardedApis = [
  ["customers", "app/api/backoffice/customers/route.ts"],
  ["product-media", "app/api/backoffice/product-media/route.ts"],
  ["product-variants", "app/api/backoffice/product-variants/route.ts"],
  ["sync", "app/api/backoffice/sync/route.ts"],
  ["devices", "app/api/backoffice/devices/route.ts"]
];
for (const [name, file] of guardedApis) {
  const source = fs.existsSync(rel(...file.split("/"))) ? read(...file.split("/")) : "";
  record(`license.apiGuard.${name}`, source.includes("guardPcFeatureForApi"), `${file} uses guardPcFeatureForApi`);
}

const directRouteStates = wave2Routes.map((route) => ({
  route: `/${route}`,
  page: fs.existsSync(rel("app", route, "page.tsx")),
  loading: fs.existsSync(rel("app", route, "loading.tsx")),
  error: fs.existsSync(rel("app", route, "error.tsx"))
}));

const report = {
  verifier: "PC_CUSTOMER_EXPERIENCE_CLOSURE_WAVE2_SOURCE_GATE_V1",
  verdict: failures.length ? "FAIL" : "PASS_SOURCE_GATE",
  scope: {
    wave1: "FROZEN_DO_NOT_REBUILD",
    wave2Routes: wave2Routes.map((route) => `/${route}`)
  },
  counts: {
    pass: results.filter((result) => result.status === "PASS").length,
    fail: failures.length,
    total: results.length
  },
  routeStates: directRouteStates,
  results,
  limitations: [
    "This gate is source-level and does not claim runtime, screenshot, console, server-log or end-to-end journey certification.",
    "Role/license navigation visibility requires runtime evidence for concrete license/role states; API guards are verified here, but absence of runtime role evidence is not converted into PASS.",
    "Wave 1 remains frozen and must be checked separately for direct drift before merge."
  ]
};

console.log(JSON.stringify(report, null, 2));
if (failures.length) process.exit(1);
