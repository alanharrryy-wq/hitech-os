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
const viewports = [
  { width: 1440, height: 900, label: "1440x900" },
  { width: 1366, height: 768, label: "1366x768" }
];

const technicalLeakPatterns = [
  /PrismaClientKnownRequestError/i,
  /SQLITE_(ERROR|CONSTRAINT|BUSY)/i,
  /no such table/i,
  /ENOENT/i,
  /migration can[oó]nica/i,
  /Prisma Original Customer/i,
  /\b(owner|endpoint|payload|idempotenc(?:y|ia)|read-after-write|canonical_prisma|fallback_empty)\b/i,
  /\/home\/runner\/work\//i,
  /[A-Z]:\\[^\s]+/i
];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ locale: "es-MX" });
const request = context.request;
const results = [];
const failures = [];
const screenshots = [];
const consoleErrors = [];
const pageErrors = [];

function record(id, pass, detail, extra = {}) {
  const item = { id, status: pass ? "PASS" : "FAIL", detail, ...extra };
  results.push(item);
  if (!pass) failures.push(item);
}

async function jsonResponse(response) {
  const text = await response.text();
  try { return JSON.parse(text); } catch { return { __raw: text }; }
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
  record("journey.customers.create.http", create.status() === 201, `POST /api/backoffice/customers => ${create.status()}`);
  record("journey.customers.create.body", Boolean(createBody?.ok && createBody?.data?.customer?.id), "created customer has durable id");
  const customer = createBody?.data?.customer;
  if (!customer?.id) return null;

  const search = await request.get(`${baseUrl}/api/backoffice/customers?q=${encodeURIComponent(createPayload.displayName)}&includeInactive=true`);
  const searchBody = await jsonResponse(search);
  record("journey.customers.search.http", search.status() === 200, `GET customer search => ${search.status()}`);
  record("journey.customers.search.result", Boolean(searchBody?.data?.customers?.some((row) => row.id === customer.id)), "created customer is searchable");

  const detail = await request.get(`${baseUrl}/api/backoffice/customers/${encodeURIComponent(customer.id)}`);
  const detailBody = await jsonResponse(detail);
  record("journey.customers.detail.http", detail.status() === 200, `GET customer detail => ${detail.status()}`);
  const version = detailBody?.data?.customer?.version;
  record("journey.customers.detail.version", Number.isInteger(version) && version > 0, `customer version=${version ?? "missing"}`);

  const updatedName = `${createPayload.displayName} Actualizado`;
  const update = await request.patch(`${baseUrl}/api/backoffice/customers/${encodeURIComponent(customer.id)}`, {
    data: { displayName: updatedName, expectedVersion: version }
  });
  const updateBody = await jsonResponse(update);
  record("journey.customers.update.http", update.status() === 200, `PATCH customer => ${update.status()}`);
  record("journey.customers.update.readAfterWrite", updateBody?.data?.customer?.displayName === updatedName, "updated name returned after write");

  return { id: customer.id, displayName: updatedName };
}

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
    await page.waitForTimeout(650);
    const status = response?.status() ?? 0;
    const routeKey = route === "/" ? "root" : route.slice(1).replaceAll("/", "-");
    record(`route.${viewport.label}.${route}.http`, status === 200, `${route} => ${status}`);

    const bodyText = await page.locator("body").innerText().catch(() => "");
    record(`route.${viewport.label}.${route}.body`, bodyText.trim().length > 0, `${route} has visible body text`);

    for (const pattern of technicalLeakPatterns) {
      const match = bodyText.match(pattern)?.[0] ?? null;
      record(`route.${viewport.label}.${route}.leak.${pattern.source}`, !match, match ? `visible leak: ${match}` : "no visible technical leak");
    }

    const invalidMetric = await page.locator(".metric").allInnerTexts().then((values) => values.find((value) => /^(NaN|undefined|null)$/i.test(value.trim())) ?? null).catch(() => null);
    record(`route.${viewport.label}.${route}.metricValues`, !invalidMetric, invalidMetric ? `invalid metric value=${invalidMetric}` : "metric values are concrete or absent");

    const positiveContradiction = await page.locator(".status-pill.tone-ok").allInnerTexts().then((values) => values.find((value) => /(bloquead|restringid|no disponible|error|fall|cr[ií]tic|conflicto)/i.test(value)) ?? null).catch(() => null);
    record(`route.${viewport.label}.${route}.positiveSemantics`, !positiveContradiction, positiveContradiction ? `positive tone contradicts text=${positiveContradiction}` : "no positive-state contradiction");

    const negativeContradiction = await page.locator(".status-pill.tone-danger").allInnerTexts().then((values) => values.find((value) => /^(ok|activo|activa|saludable|confirmad[oa])$/i.test(value.trim())) ?? null).catch(() => null);
    record(`route.${viewport.label}.${route}.negativeSemantics`, !negativeContradiction, negativeContradiction ? `negative tone contradicts text=${negativeContradiction}` : "no negative-state contradiction");

    const overflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth }));
    record(`route.${viewport.label}.${route}.horizontalOverflow`, overflow.scrollWidth <= overflow.innerWidth + 2, `scrollWidth=${overflow.scrollWidth}, innerWidth=${overflow.innerWidth}`);

    if (route === "/clientes" && createdCustomer) {
      record(`journey.customers.${viewport.label}.visible`, bodyText.includes(createdCustomer.displayName), `updated customer visible on /clientes at ${viewport.label}`);
    }

    const screenshotPath = path.join(outDir, `${viewport.label}-${routeKey}.png`);
    // Playwright's default caret hiding temporarily mutates focused controls with
    // style="caret-color: transparent". During React hydration that mutation can
    // create a test-induced mismatch. Preserve the real DOM instead.
    await page.screenshot({ path: screenshotPath, fullPage: true, caret: "initial" });
    screenshots.push(path.relative(outDir, screenshotPath).replaceAll("\\", "/"));
  }

  await page.close();
}

record("runtime.consoleErrors", consoleErrors.length === 0, `consoleErrors=${consoleErrors.length}`, { errors: consoleErrors.slice(0, 20) });
record("runtime.pageErrors", pageErrors.length === 0, `pageErrors=${pageErrors.length}`, { errors: pageErrors.slice(0, 20) });

const report = {
  verifier: "PC_CUSTOMER_EXPERIENCE_CLOSURE_WAVE2_RUNTIME_GATE_V1",
  verdict: failures.length ? "FAIL" : "PASS_RUNTIME_VISUAL_JOURNEYS",
  baseUrl,
  routes,
  viewports,
  counts: {
    pass: results.filter((item) => item.status === "PASS").length,
    fail: failures.length,
    total: results.length,
    screenshots: screenshots.length,
    consoleErrors: consoleErrors.length,
    pageErrors: pageErrors.length
  },
  customerJourney: createdCustomer,
  screenshots,
  results,
  failures,
  certificationNote: failures.length
    ? "Runtime/customer journey gate failed. Do not certify."
    : "Runtime, populated customer journey, state semantics and responsive evidence passed for the 11 Wave 2 customer routes. Role/license navigation remains a separate evidence lane."
};

fs.writeFileSync(path.join(outDir, "PC_CUSTOMER_EXPERIENCE_WAVE2_RUNTIME_RESULT.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
await browser.close();
if (failures.length) process.exit(1);
