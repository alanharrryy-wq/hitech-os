import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = await import("@playwright/test");
} catch (firstError) {
  const explicitModule = process.env.PRISMA_PLAYWRIGHT_TEST_MODULE;
  if (!explicitModule) throw firstError;
  playwright = require(explicitModule);
}
const chromium = playwright.chromium ?? playwright.default?.chromium;
if (!chromium) throw new Error("PLAYWRIGHT_CHROMIUM_EXPORT_MISSING");

function arg(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] ?? fallback : fallback;
}

const baseUrl = arg("--base-url", "http://127.0.0.1:3130").replace(/\/$/, "");
const outDir = path.resolve(arg("--out", "artifacts/pc-wave2-runtime"));
fs.mkdirSync(outDir, { recursive: true });

const routes = [
  "/catalog",
  "/proveedores",
  "/clientes",
  "/sync",
  "/devices",
  "/settings",
  "/stock",
  "/movements",
  "/counts",
  "/auditoria-inventario",
  "/salud-barcodes"
];
const businessReadEndpoints = [
  "/api/backoffice/catalog",
  "/api/backoffice/suppliers",
  "/api/backoffice/stock",
  "/api/backoffice/movements",
  "/api/backoffice/counts",
  "/api/backoffice/sync",
  "/api/backoffice/devices",
  "/api/license/features"
];
const viewports = [
  { width: 1440, height: 900, label: "1440x900" },
  { width: 1366, height: 768, label: "1366x768" }
];
const technicalLeakPatterns = [
  { name: "prisma-error", pattern: /PrismaClientKnownRequestError/i },
  { name: "sqlite-error", pattern: /SQLITE_(ERROR|CONSTRAINT|BUSY)/i },
  { name: "missing-table", pattern: /no such table/i },
  { name: "enoent", pattern: /ENOENT/i },
  { name: "runner-path", pattern: /\/home\/runner\/work\//i },
  { name: "windows-path", pattern: /[A-Z]:\\[^\s]+/i }
];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ locale: "es-MX" });
const request = context.request;
const results = [];
const failures = [];
const screenshots = [];
const consoleErrors = [];
const pageErrors = [];

function record(family, id, pass, detail, extra = {}) {
  const item = { family, id, status: pass ? "PASS" : "FAIL", detail, ...extra };
  results.push(item);
  if (!pass) failures.push(item);
}

async function jsonResponse(response) {
  const text = await response.text();
  try { return JSON.parse(text); } catch { return { __raw: text }; }
}

async function verifyBusinessReads() {
  for (const endpoint of businessReadEndpoints) {
    const response = await request.get(`${baseUrl}${endpoint}`);
    const body = await jsonResponse(response);
    record("businessReadContract", `${endpoint}.http`, response.status() === 200, `${endpoint} => ${response.status()}`);
    record("businessReadContract", `${endpoint}.envelope`, body?.ok === true, `${endpoint} returns customer-safe ok envelope`);
  }
}

async function customerJourney() {
  const stamp = Date.now();
  const createPayload = {
    displayName: `Cliente Wave2 CI ${stamp}`,
    phone: "5550102030",
    email: `wave2-${stamp}@example.test`,
    segment: "CI",
    fiscalProfile: { legalName: `Cliente Wave2 CI ${stamp}`, rfc: "XAXX010101000" }
  };

  const create = await request.post(`${baseUrl}/api/backoffice/customers`, { data: createPayload });
  const createBody = await jsonResponse(create);
  record("businessMutationE2E", "customers.create.http", create.status() === 201, `POST /api/backoffice/customers => ${create.status()}`);
  record("businessMutationE2E", "customers.create.durableId", Boolean(createBody?.ok && createBody?.data?.customer?.id), "created customer has durable ID");
  const customer = createBody?.data?.customer;
  if (!customer?.id) return null;

  const search = await request.get(`${baseUrl}/api/backoffice/customers?q=${encodeURIComponent(createPayload.displayName)}&includeInactive=true`);
  const searchBody = await jsonResponse(search);
  record("businessMutationE2E", "customers.search.http", search.status() === 200, `GET customer search => ${search.status()}`);
  record("businessMutationE2E", "customers.search.result", Boolean(searchBody?.data?.customers?.some((row) => row.id === customer.id)), "created customer is searchable");

  const detail = await request.get(`${baseUrl}/api/backoffice/customers/${encodeURIComponent(customer.id)}`);
  const detailBody = await jsonResponse(detail);
  const version = detailBody?.data?.customer?.version;
  record("businessMutationE2E", "customers.detail.http", detail.status() === 200, `GET customer detail => ${detail.status()}`);
  record("businessMutationE2E", "customers.detail.version", Number.isInteger(version) && version > 0, `customer version=${version ?? "missing"}`);

  const updatedName = `${createPayload.displayName} Actualizado`;
  const update = await request.patch(`${baseUrl}/api/backoffice/customers/${encodeURIComponent(customer.id)}`, {
    data: { displayName: updatedName, expectedVersion: version }
  });
  const updateBody = await jsonResponse(update);
  record("businessMutationE2E", "customers.update.http", update.status() === 200, `PATCH customer => ${update.status()}`);
  record("businessMutationE2E", "customers.update.readAfterWrite", updateBody?.data?.customer?.displayName === updatedName, "updated name returned after write");

  const reread = await request.get(`${baseUrl}/api/backoffice/customers/${encodeURIComponent(customer.id)}`);
  const rereadBody = await jsonResponse(reread);
  record("businessMutationE2E", "customers.reread.http", reread.status() === 200, `GET customer after update => ${reread.status()}`);
  record("businessMutationE2E", "customers.reread.persisted", rereadBody?.data?.customer?.displayName === updatedName, "updated customer persisted in isolated DB");

  return { id: customer.id, displayName: updatedName };
}

await verifyBusinessReads();
const createdCustomer = await customerJourney();

for (const viewport of viewports) {
  const page = await context.newPage();
  await page.setViewportSize({ width: viewport.width, height: viewport.height });
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push({ viewport: viewport.label, url: page.url(), text: message.text() });
  });
  page.on("pageerror", (error) => pageErrors.push({ viewport: viewport.label, url: page.url(), text: error.message }));

  for (const route of routes) {
    const response = await page.goto(`${baseUrl}${route}`, { waitUntil: "domcontentloaded", timeout: 45_000 });
    await page.waitForFunction(() => document.readyState === "complete", undefined, { timeout: 10_000 }).catch(() => null);
    await page.waitForTimeout(550);
    const status = response?.status() ?? 0;
    const routeKey = route === "/" ? "root" : route.slice(1).replaceAll("/", "-");
    record("presentationRuntime", `${viewport.label}.${route}.http`, status === 200, `${route} => ${status}`);

    const bodyText = await page.locator("body").innerText().catch(() => "");
    record("presentationRuntime", `${viewport.label}.${route}.body`, bodyText.trim().length > 0, `${route} has visible body text`);
    for (const leak of technicalLeakPatterns) {
      const match = bodyText.match(leak.pattern)?.[0] ?? null;
      record("runtimeSafety", `${viewport.label}.${route}.leak.${leak.name}`, !match, match ? `visible technical leak: ${match}` : "no visible technical leak");
    }

    const invalidMetric = await page.locator(".metric").allInnerTexts().then((values) => values.find((value) => /^(NaN|undefined|null)$/i.test(value.trim())) ?? null).catch(() => null);
    record("presentationRuntime", `${viewport.label}.${route}.metricValues`, !invalidMetric, invalidMetric ? `invalid metric value=${invalidMetric}` : "metric values are concrete or absent");

    const positiveContradiction = await page.locator(".status-pill.tone-ok").allInnerTexts().then((values) => values.find((value) => /(bloquead|restringid|no disponible|error|fall|cr[ií]tic|conflicto)/i.test(value)) ?? null).catch(() => null);
    record("presentationRuntime", `${viewport.label}.${route}.positiveSemantics`, !positiveContradiction, positiveContradiction ? `positive tone contradicts text=${positiveContradiction}` : "no positive-state contradiction");

    const negativeContradiction = await page.locator(".status-pill.tone-danger").allInnerTexts().then((values) => values.find((value) => /^(ok|activo|activa|saludable|confirmad[oa])$/i.test(value.trim())) ?? null).catch(() => null);
    record("presentationRuntime", `${viewport.label}.${route}.negativeSemantics`, !negativeContradiction, negativeContradiction ? `negative tone contradicts text=${negativeContradiction}` : "no negative-state contradiction");

    const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth }));
    record("visualUsability", `${viewport.label}.${route}.horizontalOverflow`, overflow.scrollWidth <= overflow.innerWidth + 2, `scrollWidth=${overflow.scrollWidth}, innerWidth=${overflow.innerWidth}`);

    if (route === "/catalog") {
      const primaryCount = await page.locator('[data-prisma-component="PrimaryHumanNavigation"] a[href]').count();
      record("licenseEnforcement", `${viewport.label}.entitledNavigationVisible`, primaryCount > 0, `entitled primary navigation links=${primaryCount}`);
    }

    if (route === "/clientes") {
      const panelSizes = await page.evaluate(() => {
        const search = document.querySelector('[data-prisma-customer-panel="search"]');
        const create = document.querySelector('[data-prisma-customer-panel="create"]');
        const size = (element) => element ? Math.round(element.getBoundingClientRect().width) : 0;
        return { search: size(search), create: size(create) };
      });
      record("visualUsability", `${viewport.label}.clientes.searchPanelWidth`, panelSizes.search >= 280, `search panel width=${panelSizes.search}px; minimum=280px`);
      record("visualUsability", `${viewport.label}.clientes.createPanelWidth`, panelSizes.create >= 520, `create panel width=${panelSizes.create}px; minimum=520px`);
      if (createdCustomer) {
        record("businessMutationE2E", `customers.${viewport.label}.visible`, bodyText.includes(createdCustomer.displayName), `updated customer visible on /clientes at ${viewport.label}`);
      }
    }

    const screenshotPath = path.join(outDir, `${viewport.label}-${routeKey}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true, caret: "initial" });
    screenshots.push(path.relative(outDir, screenshotPath).replaceAll("\\", "/"));
  }
  await page.close();
}

record("runtimeSafety", "consoleErrors", consoleErrors.length === 0, `consoleErrors=${consoleErrors.length}`, { errors: consoleErrors.slice(0, 20) });
record("runtimeSafety", "pageErrors", pageErrors.length === 0, `pageErrors=${pageErrors.length}`, { errors: pageErrors.slice(0, 20) });

const familyCounts = Object.fromEntries(
  [...new Set(results.map((item) => item.family))].sort().map((family) => {
    const items = results.filter((item) => item.family === family);
    return [family, {
      pass: items.filter((item) => item.status === "PASS").length,
      fail: items.filter((item) => item.status === "FAIL").length,
      total: items.length
    }];
  })
);

const report = {
  verifier: "PC_CUSTOMER_EXPERIENCE_WAVE2_RUNTIME_GATE_V2",
  verdict: failures.length ? "FAIL" : "PASS_BOUNDED_WAVE2_CERTIFICATION",
  baseUrl,
  routes,
  viewports,
  counts: {
    pass: results.filter((item) => item.status === "PASS").length,
    fail: failures.length,
    totalAssertions: results.length,
    screenshots: screenshots.length,
    consoleErrors: consoleErrors.length,
    pageErrors: pageErrors.length,
    byFamily: familyCounts
  },
  certifiedJourneys: [
    "Customers: create -> durable ID -> search -> detail/version -> update -> read-after-write -> reread persisted",
    "Read contracts: catalog, suppliers, stock, movements, counts, sync, devices and license features",
    "Presentation/runtime: 11 Wave 2 routes at 1440x900 and 1366x768",
    "Visual usability: /clientes search/create panel minimum widths and viewport overflow",
    "Entitled navigation: PrimaryHumanNavigation visible when canonical pc.open is allowed"
  ],
  notCertifiedJourneys: [
    "catalog create/update/delete mutation",
    "supplier create/update/delete mutation",
    "stock adjustment mutation",
    "inventory count lifecycle mutation",
    "sync dispatch/replay mutation",
    "device claim/revoke mutation",
    "settings write mutation",
    "production customer data or hosted production readiness"
  ],
  claimCeiling: "Assertion count is not functional coverage. Only certifiedJourneys above are certified by this gate; notCertifiedJourneys remain explicitly outside the claim.",
  customerJourney: createdCustomer,
  screenshots,
  results,
  failures
};

fs.writeFileSync(path.join(outDir, "PC_CUSTOMER_EXPERIENCE_WAVE2_RUNTIME_RESULT.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
await browser.close();
if (failures.length) process.exit(1);
