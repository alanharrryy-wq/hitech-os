import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const pcRoot = path.resolve(here, "..");

const results = [];
const failures = [];

const WAVE1_FROZEN_ROUTES = [
  "/dashboard", "/sales-control", "/cash-sessions", "/metricas-dia", "/purchasing", "/ordenes-compra",
  "/receiving", "/recepcion-proveedor", "/incidencias-recepcion", "/replenishment", "/senal-reabasto",
  "/exportables", "/prisma-insights", "/audit", "/settings/license", "/outbox-operativo", "/tablas-operativas",
  "/detalle-registros", "/estados-operativos", "/glosario", "/forecast-basico", "/acciones-masivas",
  "/contratos-reporte", "/scorecards-negocio", "/tablero-kpi", "/vistas-ejecutivas", "/filtros-avanzados",
  "/filtros-fecha"
];

const WAVE2_CUSTOMER_ROUTES = [
  "/catalog", "/proveedores", "/clientes", "/sync", "/devices", "/settings",
  "/stock", "/movements", "/counts", "/auditoria-inventario", "/salud-barcodes"
];

const WAVE2_INTERNALIZED_ROUTES = [
  "/ajustes-inventario", "/alertas-ejecutivas", "/alertas-operativas", "/catalogo-activo", "/conteos-operativos",
  "/data-quality", "/integridad-barcodes", "/license-runtime", "/politica-precios", "/sync-operativo",
  "/tablet-communication", "/validacion-catalogo"
];

function rel(...parts) {
  return path.join(pcRoot, ...parts);
}

function read(...parts) {
  return fs.readFileSync(rel(...parts), "utf8");
}

function record(id, pass, detail, classification = pass ? "PASS" : "FAIL") {
  const status = pass ? "PASS" : "FAIL";
  results.push({ id, status, classification, detail });
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

function gitBlobSha(source) {
  const payload = Buffer.from(source, "utf8");
  return crypto.createHash("sha1").update(Buffer.from(`blob ${payload.length}\0`, "utf8")).update(payload).digest("hex");
}

function frozenBlob(id, parts, expectedSha) {
  const source = read(...parts);
  const actual = gitBlobSha(source);
  record(id, actual === expectedSha, `${parts.join("/")} blob=${actual} expected=${expectedSha}`, actual === expectedSha ? "WAVE1_FROZEN" : "WAVE1_DRIFT");
}

function routeStatus(routeMapSource, route) {
  const escaped = route.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = routeMapSource.match(new RegExp(`"route"\\s*:\\s*"${escaped}"[\\s\\S]{0,180}?"status"\\s*:\\s*"(primary|secondary|internal|lab)"`));
  return match?.[1] ?? null;
}

for (const route of WAVE2_CUSTOMER_ROUTES) {
  const routeParts = route.slice(1).split("/");
  exists(`route.${route}.page`, "app", ...routeParts, "page.tsx");
  exists(`route.${route}.loading`, "app", ...routeParts, "loading.tsx");
  exists(`route.${route}.error`, "app", ...routeParts, "error.tsx");
  const errorSource = fs.existsSync(rel("app", ...routeParts, "error.tsx")) ? read("app", ...routeParts, "error.tsx") : "";
  excludes(`route.${route}.error.rawMessage`, errorSource, "error.message", `${route} error boundary does not render raw exception text`);
}

frozenBlob("wave1.freeze.navigation", ["src", "composition", "navigation.ts"], "a38b2e64abe65c0bdca66d7227d4f2e338078bc7");
frozenBlob("wave1.freeze.settingsLicensePage", ["app", "settings", "license", "page.tsx"], "b3a4e75808edbbfe0913ed61f677259b2d01ab99");
frozenBlob("wave1.freeze.licensePresentation", ["components", "license", "license-status-card.tsx"], "a7874b94979c2a9f9807808f3e9e668549bc074a");
frozenBlob("wave1.freeze.dashboardTasks", ["src", "server", "services", "operational-task.service.ts"], "080f47eedc5065fc7b51ec434551c43a4eea7fd8");

const navigation = read("src", "composition", "navigation.ts");
for (const route of ["/catalog", "/proveedores", "/clientes", "/sync", "/devices", "/settings"]) {
  includes(`nav.primary.${route}`, navigation, `"${route}"`, `primary navigation contains ${route}`);
}

const routeMap = read("src", "uiux", "route-map.ts");
for (const route of WAVE2_INTERNALIZED_ROUTES) {
  const status = routeStatus(routeMap, route);
  record(`routeMap.internalized.${route}`, status === "internal", `${route} status=${status ?? "missing"}`, status === "internal" ? "INTERNALIZED" : "VISIBILITY_DRIFT");
}
for (const route of WAVE2_CUSTOMER_ROUTES) {
  const status = routeStatus(routeMap, route);
  record(`routeMap.customer.${route}`, status === "primary" || status === "secondary", `${route} status=${status ?? "missing"}`);
}

const customerService = read("src", "server", "services", "customer.service.ts");
const catalogService = read("src", "server", "services", "catalog.service.ts");
const mediaService = read("src", "server", "services", "product-media.service.ts");
const variantService = read("src", "server", "services", "product-variant.service.ts");
for (const [name, source] of [["customers", customerService], ["catalog", catalogService], ["productMedia", mediaService], ["productVariants", variantService]]) {
  excludes(`copy.${name}.rawErrorMessage`, source, "error instanceof Error ? error.message", `${name} does not project raw exception text into its customer workspace`);
  excludes(`copy.${name}.migrationInstruction`, source, "Verifica la migración canónica", `${name} does not instruct customers about migrations`);
}

const apiResponse = read("src", "lib", "backoffice", "api-response.ts");
includes("api.customerSafe.optIn", apiResponse, "options.customerSafe", "customer-safe API failure is explicit opt-in");
includes("api.wave1.defaultPreserved", apiResponse, "const message = error instanceof Error ? error.message", "legacy default remains available for frozen Wave 1 callers");

const catalog = read("components", "catalog", "catalog-dashboard.tsx");
const previewCount = (catalog.match(/className=\{mediaStyles\.preview\}/g) ?? []).length;
record("catalog.singlePreview", previewCount === 1, `image preview count=${previewCount}`);
for (const phrase of ["Sin dock de selectores como aduana", "La tabla manda", "Estado honesto", "Editar bloqueado hasta auditoría", "Abrir validación", "Preparar ajuste"]) {
  excludes(`catalog.visiblePhrase.${phrase}`, catalog, phrase, `catalog excludes legacy customer-facing phrase: ${phrase}`);
}
includes("catalog.canonicalIssueLink", catalog, "href=\"/catalog?issue=problem\"", "catalog quality CTA stays on canonical catalog owner");

const inventory = read("components", "inventory", "inventory-workspace.tsx");
for (const phrase of ["ledger físico", "On hand ", "endpoint auditable", "before/after", "rollback de negocio", "/ajustes-inventario", "Buscar SKU, producto o barcode"]) {
  excludes(`inventory.visiblePhrase.${phrase}`, inventory, phrase, `inventory customer surfaces exclude legacy/internal phrase: ${phrase}`);
}
includes("inventory.honestBlockedAdjustment", inventory, "Ajuste directo no disponible", "stock write stays honestly unavailable where no governed write action exists");

const customerWorkspace = read("components", "customers", "customer-workspace.tsx");
for (const phrase of ["fuente canónica", "pendiente de migración", "proyección local de Tablet", "alta canónica", "Versión {selected.version}"]) {
  excludes(`customers.visiblePhrase.${phrase}`, customerWorkspace, phrase, `customers excludes internal phrase: ${phrase}`);
}
includes("customers.action.create", customerWorkspace, "fetch(\"/api/backoffice/customers\"", "customer create action remains wired");
includes("customers.action.update", customerWorkspace, "method: \"PATCH\"", "customer update action remains wired");

const commandCenter = read("components", "control", "pc-command-center-page.tsx");
includes("wave2.commandCenter.scope", commandCenter, "model.currentPath === \"/sync\" || model.currentPath === \"/devices\"", "customer-safe command-center projection is isolated to Sync and Devices");
includes("wave2.commandCenter.placeholderProjection", commandCenter, ".replace(/Prisma Original Customer/gi, \"tu negocio\")", "placeholder customer identity is projected to neutral customer text on Wave 2 routes");
includes("wave2.commandCenter.tableProjection", commandCenter, "wave2CustomerTable", "Sync/Devices tables pass through customer projection");
includes("wave2.commandCenter.actionSafe", commandCenter, "customerSafe={wave2CustomerSurface}", "Sync/Devices actions use customer-safe failures");
includes("wave2.commandCenter.noApiLinks", commandCenter, "!action.href.startsWith(\"/api/\")", "customer surface hides direct GET API links");
includes("wave2.commandCenter.stripDetails", commandCenter, "const projected: CommandTableRow = {}", "customer tables rebuild visible cells instead of forwarding diagnostic row metadata");

const commandActions = read("components", "control", "pc-command-actions.tsx");
includes("wave2.actions.genericFailure", commandActions, "No pudimos completar la acción", "customer-safe POST failure is generic");
includes("wave2.actions.optIn", commandActions, "customerSafe = false", "Wave 1 keeps previous action behavior unless Wave 2 opts in");

const syncPanel = read("components", "sync", "pc-sync-chart-promotion-panel.tsx");
for (const phrase of ["payload.message", "quality.sourceLabel", "quality.confidence.level", "quality.fallbackReason", "charts promovidos", "timeline de comandos"]) {
  excludes(`sync.visiblePhrase.${phrase}`, syncPanel, phrase, `sync customer view excludes ${phrase}`);
}
includes("sync.copy.safeFailure", syncPanel, "No pudimos cargar el estado de sincronización. Intenta de nuevo.", "sync failure is customer-safe");
includes("sync.copy.entityLabels", syncPanel, "function entityLabel", "sync entity names are projected to customer labels");

const moduleOverview = read("components", "backoffice", "module-overview-page.tsx");
includes("overview.wave1FreezeSet", moduleOverview, "FROZEN_WAVE1_ROUTES", "shared overview preserves Wave 1 routes explicitly");
includes("overview.wave2CustomerProjection", moduleOverview, "CustomerOverview", "non-Wave1 module overviews use customer projection");

const supplierView = read("components", "operations", "operation-workspace.tsx");
includes("suppliers.scopeIsolation", supplierView, "resolvedPath === \"/proveedores\"", "supplier customer copy is isolated from frozen purchasing/receiving/replenishment routes");

const barcodeHealth = read("app", "salud-barcodes", "page.tsx");
for (const phrase of ["owner durable", "endpoint auditable", "Carga canónica", "mutación"]) {
  excludes(`barcodeHealth.visiblePhrase.${phrase}`, barcodeHealth, phrase, `barcode health excludes internal phrase: ${phrase}`);
}

const guardedApis = [
  ["customers", "app/api/backoffice/customers/route.ts"],
  ["customer-detail", "app/api/backoffice/customers/[customerId]/route.ts"],
  ["product-media", "app/api/backoffice/product-media/route.ts"],
  ["product-variants", "app/api/backoffice/product-variants/route.ts"],
  ["product-variant-detail", "app/api/backoffice/product-variants/[variantId]/route.ts"],
  ["sync", "app/api/backoffice/sync/route.ts"],
  ["devices", "app/api/backoffice/devices/route.ts"]
];
for (const [name, file] of guardedApis) {
  const source = read(...file.split("/"));
  record(`license.apiGuard.${name}`, source.includes("guardPcFeatureForApi"), `${file} uses guardPcFeatureForApi`);
  record(`api.customerSafe.${name}`, source.includes("customerSafe: true"), `${file} fails customer-safe for unexpected errors`);
}

const hypotheses = [
  { id: "P0.filesystem-enoent", classification: "FIXED_WAVE2", evidence: "Catalog/media workspaces no longer project raw exception text or filesystem guidance." },
  { id: "P0.prisma-sql-migration", classification: "FIXED_WAVE2_AND_WAVE1_FROZEN", evidence: "Wave 2 workspaces fail customer-safe; Dashboard task wording remains frozen under Wave 1 and is not reopened here." },
  { id: "P0.orm-endpoint-owner-vocabulary", classification: "FIXED_OR_INTERNALIZED_WAVE2", evidence: "Visible Wave 2 surfaces were humanized; unproductized technical projections are internal in the canonical route map." },
  { id: "P0.license-internal-ids", classification: "CONFIRMED_WAVE1_FROZEN", evidence: "/settings/license belongs to Wave 1; its certified projection is not rewritten by Wave 2." },
  { id: "P0.machine-sync-runtime-ids", classification: "FIXED_WAVE2", evidence: "Sync/Devices rebuild customer rows and do not forward diagnostic row metadata or direct API links." },
  { id: "P0.placeholder-identity", classification: "FIXED_WAVE2", evidence: "Sync/Devices project 'Prisma Original Customer' to neutral customer text." },
  { id: "P0.contradictory-state-semantics", classification: "EVIDENCE_GAP_RUNTIME", evidence: "Requires populated runtime visual/state evidence; source scan alone cannot certify semantic consistency." },
  { id: "P0.clientes-focused-evidence", classification: "SOURCE_READY_RUNTIME_EVIDENCE_GAP", evidence: "CRUD wiring, fail-closed data service, loading/error boundaries and customer copy are source-verified; E2E runtime remains required." },
  { id: "P1.receiving-purpose-overlap", classification: "DONE_WAVE1_FROZEN", evidence: "Both relevant receiving routes are in the certified Wave 1 route set; no re-audit without drift." },
  { id: "P1.replenishment-purpose-overlap", classification: "DONE_WAVE1_FROZEN", evidence: "Both relevant replenishment routes are in the certified Wave 1 route set; no re-audit without drift." },
  { id: "P1.duplicate-data-quality", classification: "FIXED_OR_INTERNALIZED_WAVE2", evidence: "Legacy validation/integrity/data-quality projections are internal in the canonical route map; catalog and barcode health remain customer owners." },
  { id: "P1.hidden-filter-404", classification: "DONE_WAVE1_FROZEN", evidence: "Hidden filter routes were certified by Wave 1 and are not reopened without drift." },
  { id: "P1.generic-empty-states", classification: "FIXED_WAVE2_SOURCE", evidence: "All 11 customer Wave 2 routes have page/loading/error boundaries; visible workspaces expose honest empty/unavailable states." },
  { id: "P1.progressive-disclosure", classification: "PASS_SOURCE_RUNTIME_VISUAL_PENDING", evidence: "Catalog and inventory use master/detail or row details; customer-safe command center strips diagnostic expansion metadata." },
  { id: "P1.populated-responsive-readiness", classification: "EVIDENCE_GAP_RUNTIME_VISUAL", evidence: "Requires screenshots at 1440x900 and 1366x768 with populated states." },
  { id: "P1.role-license-navigation-visibility", classification: "EVIDENCE_GAP_RUNTIME_SHARED_NAV", evidence: "Wave 2 read/write APIs inspected here are guarded, but AppShell primary/secondary navigation is not yet proven against concrete role/license states. No PASS is claimed." }
];

const evidenceGaps = hypotheses.filter((item) => item.classification.includes("EVIDENCE_GAP"));

const report = {
  verifier: "PC_CUSTOMER_EXPERIENCE_CLOSURE_WAVE2_SOURCE_GATE_V3",
  verdict: failures.length ? "FAIL" : "PASS_SOURCE_GATE_RUNTIME_PENDING",
  wave1: {
    status: "FROZEN_DO_NOT_REBUILD",
    routes: WAVE1_FROZEN_ROUTES
  },
  wave2: {
    customerRoutes: WAVE2_CUSTOMER_ROUTES,
    internalizedRoutes: WAVE2_INTERNALIZED_ROUTES
  },
  counts: {
    pass: results.filter((result) => result.status === "PASS").length,
    fail: failures.length,
    total: results.length,
    evidenceGaps: evidenceGaps.length
  },
  results,
  hypotheses,
  evidenceGaps,
  limitations: [
    "This gate is source-level. It does not claim runtime, screenshot, console, server-log or full customer-journey certification.",
    "Role/license customer navigation visibility remains unproven for concrete entitlements and must not be converted into PASS by absence of a detected source defect.",
    "Wave 1 remains frozen; known Wave 1 projections are not rewritten by Wave 2 without direct post-merge drift and task-exact authorization."
  ],
  certification: failures.length || evidenceGaps.length ? "NOT_YET_PC_CUSTOMER_EXPERIENCE_CLOSURE_CERTIFIED" : "PC_CUSTOMER_EXPERIENCE_CLOSURE_CERTIFIED"
};

console.log(JSON.stringify(report, null, 2));
if (failures.length) process.exit(1);
