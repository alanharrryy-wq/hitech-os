const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, "surf-fix6.targets.json"), "utf8"));
const outDir = path.join(process.cwd(), "test-results", "surf-fix6-internal-surfaces");
fs.mkdirSync(outDir, { recursive: true });

test.describe.configure({ mode: "parallel" });
test.use({ trace: "retain-on-failure", screenshot: "only-on-failure", video: "off" });
test.setTimeout(Number(process.env.PRISMA_SURF_TEST_TIMEOUT_MS || 18000));

const onlinePorts = new Set(String(process.env.PRISMA_SURF_ONLINE_PORTS || "").split(",").map(s => s.trim()).filter(Boolean));
const captureScreenshots = String(process.env.PRISMA_SURF_SCREENSHOTS || "1") !== "0";
const fullPage = String(process.env.PRISMA_SURF_FULLPAGE || "0") === "1";
const settleMs = Number(process.env.PRISMA_SURF_SETTLE_MS || 120);
const gotoTimeout = Number(process.env.PRISMA_SURF_GOTO_TIMEOUT_MS || 8000);
const clickTimeout = Number(process.env.PRISMA_SURF_CLICK_TIMEOUT_MS || 2500);

function safeName(value) { return String(value || "surface").normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-zA-Z0-9_.-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 96) || "surface"; }
function shouldSkipPort(target) { return onlinePorts.size > 0 && !onlinePorts.has(String(target.macro)); }
async function gotoBase(page, target, route = "/") { const url = new URL(route, target.baseUrl).toString(); await page.goto(url, { waitUntil: "domcontentloaded", timeout: gotoTimeout }); return url; }
async function capture(page, target, label, extra = {}) {
  const record = { targetId: target.id, macro: target.macro, name: target.name, label, url: page.url(), title: await page.title().catch(() => null), h1: await page.locator("h1").first().textContent({ timeout: 600 }).catch(() => null), ...extra };
  const fileBase = `${target.macro}-${safeName(target.id)}-${safeName(label)}`;
  if (captureScreenshots) await page.screenshot({ path: path.join(outDir, `${fileBase}.png`), fullPage }).catch(error => { record.screenshotError = error.message; });
  fs.writeFileSync(path.join(outDir, `${fileBase}.json`), JSON.stringify(record, null, 2));
}
async function clickTextTarget(page, target) {
  await gotoBase(page, target);
  const loc = page.getByText(target.label, { exact: true }).first();
  await expect(loc, `${target.name} should expose internal label ${target.label}`).toHaveCount(1, { timeout: 1800 });
  await loc.scrollIntoViewIfNeeded({ timeout: clickTimeout }).catch(() => {});
  await loc.click({ timeout: clickTimeout, force: true });
  await page.waitForTimeout(settleMs);
  await capture(page, target, target.label, { kind: "text-click", clicked: true });
}
async function captureRoute(page, target) { const url = await gotoBase(page, target, target.route); await page.waitForTimeout(settleMs); await capture(page, target, target.route, { kind: "route", visitedUrl: url }); }
async function selectorDiscovery(page, target) {
  await gotoBase(page, target); const records = [];
  for (const selector of target.selectors || []) {
    const loc = page.locator(selector); const count = Math.min(await loc.count().catch(() => 0), Number(target.limit || 20));
    for (let i = 0; i < count; i += 1) {
      const item = loc.nth(i);
      const label = await item.evaluate(el => el.getAttribute("data-prisma-interface-target") || el.getAttribute("data-prisma-chart-target") || el.getAttribute("data-chart-target") || el.getAttribute("aria-label") || el.textContent || el.tagName).catch(() => `${selector}-${i}`);
      const rec = { selector, index: i, label, clicked: false, error: null };
      try { await item.scrollIntoViewIfNeeded({ timeout: clickTimeout }).catch(() => {}); await item.click({ timeout: clickTimeout, force: true }); rec.clicked = true; await page.waitForTimeout(settleMs); await capture(page, target, `${selector}-${label}-${i}`, rec); } catch (error) { rec.error = error.message; }
      records.push(rec);
    }
  }
  fs.writeFileSync(path.join(outDir, `${target.macro}-${safeName(target.id)}-summary.json`), JSON.stringify({ target, records }, null, 2));
  if (target.kind === "control-center-real-tabs") expect(await page.locator("[data-prisma-interface-target]").count(), "Control Center must expose real data-prisma-interface-target tabs").toBeGreaterThan(0);
}
async function controlCenterLifecycle(page, target) {
  await gotoBase(page, target);
  const targets = page.locator("[data-prisma-interface-target]");
  await expect(targets, "Control Center must expose real data-prisma-interface-target tabs").not.toHaveCount(0, { timeout: 3000 });
  const lifecycleTarget = page.locator("[data-prisma-interface-target]").filter({ hasText: /lifecycle|ciclo|datos locales|data life/i }).first();
  const attrLifecycle = page.locator("[data-prisma-interface-target*='life' i], [data-prisma-interface-target*='ciclo' i], [data-prisma-interface-target*='datos' i]").first();
  if (await lifecycleTarget.count().catch(() => 0)) await lifecycleTarget.click({ timeout: clickTimeout, force: true });
  else if (await attrLifecycle.count().catch(() => 0)) await attrLifecycle.click({ timeout: clickTimeout, force: true });
  await page.waitForTimeout(Math.max(settleMs, 250));
  await expect(page.locator("#lifecycleSurface"), "Control Center Data Lifecycle must materialize #lifecycleSurface at runtime").toHaveCount(1, { timeout: 4000 });
  await capture(page, target, "lifecycleSurface", { kind: "control-center-lifecycle", lifecycleSurface: true });
}
for (const target of manifest.testTargets) {
  const tags = (target.tags || []).join(" ");
  test(`${target.macro} ${target.id} ${tags}`, async ({ page }) => {
    test.skip(shouldSkipPort(target), `${target.baseUrl} was offline in one-shot preflight`);
    if (target.kind === "text-click") return clickTextTarget(page, target);
    if (target.kind === "route") return captureRoute(page, target);
    if (target.kind === "selector-discovery" || target.kind === "control-center-real-tabs") return selectorDiscovery(page, target);
    if (target.kind === "control-center-lifecycle") return controlCenterLifecycle(page, target);
    throw new Error(`Unknown target kind: ${target.kind}`);
  });
}
