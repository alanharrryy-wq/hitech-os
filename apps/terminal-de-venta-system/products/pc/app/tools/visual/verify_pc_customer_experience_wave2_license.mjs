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
const consoleErrors = [];
const pageErrors = [];
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push({ url: page.url(), text: message.text() });
});
page.on("pageerror", (error) => pageErrors.push({ url: page.url(), text: error.message }));

async function payload(response) {
  const text = await response.text();
  try { return JSON.parse(text); } catch { return { raw: text }; }
}

const devicesResponse = await context.request.get(`${baseUrl}/api/backoffice/devices`);
const syncResponse = await context.request.get(`${baseUrl}/api/backoffice/sync`);
const featuresResponse = await context.request.get(`${baseUrl}/api/license/features`);
const devicesBody = await payload(devicesResponse);
const syncBody = await payload(syncResponse);
const featuresBody = await payload(featuresResponse);

const pageResponse = await page.goto(`${baseUrl}/catalog`, { waitUntil: "domcontentloaded", timeout: 45_000 });
await page.waitForFunction(() => document.readyState === "complete", undefined, { timeout: 10_000 }).catch(() => null);
await page.waitForTimeout(350);

const primaryHrefs = await page.locator('[data-prisma-component="PrimaryHumanNavigation"] a[href]').evaluateAll((anchors) => anchors.map((anchor) => anchor.getAttribute("href")).filter(Boolean));
const secondaryHrefs = await page.locator('[data-prisma-component="SurfaceContextStrip"] a[href]').evaluateAll((anchors) => anchors.map((anchor) => anchor.getAttribute("href")).filter(Boolean)).catch(() => []);
const deniedGateCount = await page.locator('[data-prisma-component="PcLicenseNavigationGate"][data-license-navigation="denied"]').count();
const bodyNavigationState = await page.locator("body").getAttribute("data-prisma-pc-navigation");
const bodyText = await page.locator("body").innerText();
await page.screenshot({ path: path.join(outDir, "restricted-license-catalog-1440x900.png"), fullPage: true, caret: "initial" });

const featureRows = Array.isArray(featuresBody?.data?.features) ? featuresBody.data.features : [];
const pcOpen = featureRows.find((row) => row?.key === "pc.open");
const checks = [
  { id: "api.devices.denied", pass: devicesResponse.status() === 403 && devicesBody?.code === "LICENSE_FEATURE_DENIED", detail: `status=${devicesResponse.status()} code=${devicesBody?.code ?? "missing"}` },
  { id: "api.sync.denied", pass: syncResponse.status() === 403 && syncBody?.code === "LICENSE_FEATURE_DENIED", detail: `status=${syncResponse.status()} code=${syncBody?.code ?? "missing"}` },
  { id: "license.features.http", pass: featuresResponse.status() === 200, detail: `status=${featuresResponse.status()}` },
  { id: "license.pcOpen.denied", pass: pcOpen?.allowed === false, detail: `pc.open.allowed=${pcOpen?.allowed ?? "missing"}` },
  { id: "page.catalog.http", pass: pageResponse?.status() === 200, detail: `status=${pageResponse?.status() ?? 0}` },
  { id: "navigation.primary.absent", pass: primaryHrefs.length === 0, detail: `primary hrefs=${primaryHrefs.length}` },
  { id: "navigation.secondary.absent", pass: secondaryHrefs.length === 0, detail: `secondary hrefs=${secondaryHrefs.length}` },
  { id: "navigation.deniedGate.present", pass: deniedGateCount === 1, detail: `denied gate count=${deniedGateCount}` },
  { id: "navigation.bodyState.denied", pass: bodyNavigationState === "denied", detail: `body state=${bodyNavigationState ?? "missing"}` },
  { id: "navigation.customerCopy", pass: /Navegación PC no disponible para esta licencia\./i.test(bodyText), detail: "restricted navigation has customer-safe explanation" },
  { id: "runtime.consoleErrors", pass: consoleErrors.length === 0, detail: `consoleErrors=${consoleErrors.length}` },
  { id: "runtime.pageErrors", pass: pageErrors.length === 0, detail: `pageErrors=${pageErrors.length}` }
];
const failures = checks.filter((check) => !check.pass);

const report = {
  verifier: "PC_CUSTOMER_EXPERIENCE_WAVE2_RESTRICTED_LICENSE_GATE_V2",
  verdict: failures.length ? "FAIL_RESTRICTED_LICENSE_PROJECTION" : "PASS_RESTRICTED_NAV_FAIL_CLOSED",
  baseUrl,
  api: {
    devices: { status: devicesResponse.status(), code: devicesBody?.code ?? null },
    sync: { status: syncResponse.status(), code: syncBody?.code ?? null },
    pcOpen: pcOpen ?? null
  },
  page: {
    route: "/catalog",
    status: pageResponse?.status() ?? 0,
    primaryHrefs,
    secondaryHrefs,
    deniedGateCount,
    bodyNavigationState
  },
  consoleErrors,
  pageErrors,
  checks,
  failures,
  claimCeiling: "Certifies TABLET_SOLO fail-closed PC navigation plus inspected Devices/Sync API denial. It does not certify every role/permission combination or hosted licensing production readiness."
};

fs.writeFileSync(path.join(outDir, "PC_CUSTOMER_EXPERIENCE_WAVE2_LICENSE_RESULT.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
await browser.close();
if (failures.length) process.exit(1);
