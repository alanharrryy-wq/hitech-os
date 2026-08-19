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
const outDir = path.resolve(arg("--out", "artifacts/pc-wave2-license"));
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ locale: "es-MX", viewport: { width: 1440, height: 900 } });
const page = await context.newPage();

async function payload(response) {
  const text = await response.text();
  try { return JSON.parse(text); } catch { return { raw: text }; }
}

const devicesResponse = await context.request.get(`${baseUrl}/api/backoffice/devices`);
const syncResponse = await context.request.get(`${baseUrl}/api/backoffice/sync`);
const devicesBody = await payload(devicesResponse);
const syncBody = await payload(syncResponse);

const pageResponse = await page.goto(`${baseUrl}/catalog`, { waitUntil: "domcontentloaded", timeout: 45_000 });
await page.waitForTimeout(300);
const primaryHrefs = await page.locator('[data-prisma-component="PrimaryHumanNavigation"] a[href]').evaluateAll((anchors) => anchors.map((anchor) => anchor.getAttribute("href")).filter(Boolean));
const secondaryHrefs = await page.locator('[data-prisma-component="SurfaceContextStrip"] a[href]').evaluateAll((anchors) => anchors.map((anchor) => anchor.getAttribute("href")).filter(Boolean)).catch(() => []);
const bodyText = await page.locator("body").innerText();
await page.screenshot({ path: path.join(outDir, "restricted-license-catalog-1440x900.png"), fullPage: true });

const pcApiBlocked = devicesResponse.status() >= 400 && syncResponse.status() >= 400;
const customerNavigationVisible = primaryHrefs.length > 0 || secondaryHrefs.length > 0;
const productVerdict = pcApiBlocked && customerNavigationVisible
  ? "BLOCKED_SHARED_DEPENDENCY"
  : pcApiBlocked && !customerNavigationVisible
    ? "PASS_RESTRICTED_NAV_FAIL_CLOSED"
    : "INCONCLUSIVE_LICENSE_FIXTURE";

const report = {
  verifier: "PC_CUSTOMER_EXPERIENCE_CLOSURE_WAVE2_RESTRICTED_LICENSE_EVIDENCE_V1",
  evidenceCollection: "PASS",
  productVerdict,
  certificationImpact: productVerdict === "PASS_RESTRICTED_NAV_FAIL_CLOSED" ? "NONE" : "BLOCKS_FINAL_CERTIFICATION",
  page: {
    route: "/catalog",
    status: pageResponse?.status() ?? 0,
    primaryHrefs,
    secondaryHrefs,
    containsBlockedCopy: /bloquead|restringid|licencia/i.test(bodyText)
  },
  api: {
    devices: { status: devicesResponse.status(), code: devicesBody?.code ?? null, message: devicesBody?.message ?? null },
    sync: { status: syncResponse.status(), code: syncBody?.code ?? null, message: syncBody?.message ?? null }
  },
  interpretation: pcApiBlocked && customerNavigationVisible
    ? "The restricted license blocks inspected PC APIs while the shared AppShell still renders customer navigation. This is a confirmed cross-route navigation gating gap. Do not hide it as PASS and do not rewrite frozen Wave 1 navigation in this Wave 2 lane."
    : pcApiBlocked && !customerNavigationVisible
      ? "Restricted PC access fails closed at both API and customer navigation boundaries."
      : "The restricted fixture did not prove the expected PC API denial; inspect the license fixture before drawing a product conclusion."
};

fs.writeFileSync(path.join(outDir, "PC_CUSTOMER_EXPERIENCE_WAVE2_LICENSE_RESULT.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
await browser.close();

// This verifier is an evidence collector, not a green product gate. A BLOCKED_SHARED_DEPENDENCY
// is a successful evidence collection with a blocking product classification.
if (productVerdict === "INCONCLUSIVE_LICENSE_FIXTURE") process.exit(1);
