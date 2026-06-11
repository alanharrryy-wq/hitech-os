const fs = require("fs");
const path = require("path");
const { captureDeepScreenshots, envDeepCaptureOptions, emitProgress } = require("./surf8.deep-capture.cjs");

function registerSurf8Tests(test, expect) {
  const planPath = process.env.PRISMA_SURF_PLAN_JSON;
  if (!planPath) throw new Error("PRISMA_SURF_PLAN_JSON is required");
  const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
  const outDir = process.env.PRISMA_SURF_OUT_DIR || path.join(process.cwd(), "test-results", "surf8-surfaces");
  fs.mkdirSync(outDir, { recursive: true });

  const captureScreenshots = String(process.env.PRISMA_SURF_SCREENSHOTS || "1") !== "0";
  const fullPage = String(process.env.PRISMA_SURF_FULLPAGE || "1") === "1";
  const deepCaptureOptions = envDeepCaptureOptions({ fullPage });
  const settleMs = Number(process.env.PRISMA_SURF_SETTLE_MS || 180);
  const gotoTimeout = Number(process.env.PRISMA_SURF_GOTO_TIMEOUT_MS || 45000);
  const gotoRetries = Number(process.env.PRISMA_SURF_GOTO_RETRIES || 2);
  const clickTimeout = Number(process.env.PRISMA_SURF_CLICK_TIMEOUT_MS || 7000);
  const screenshotTimeout = Number(process.env.PRISMA_SURF_SCREENSHOT_TIMEOUT_MS || 15000);
  const probeTimeout = Number(process.env.PRISMA_SURF_PROBE_TIMEOUT_MS || 1400);
  const defaultTestTimeout = Math.max(
    150000,
    (gotoTimeout * (gotoRetries + 1)) + screenshotTimeout + (clickTimeout * 3) + 35000
  );
  const testTimeout = Number(process.env.PRISMA_SURF_TEST_TIMEOUT_MS || defaultTestTimeout);
  const onlinePorts = new Set(String(process.env.PRISMA_SURF_ONLINE_PORTS || "").split(",").map(s => s.trim()).filter(Boolean));
  const runMode = String(process.env.PRISMA_SURF_MODE || "surf8");
  const gpuMode = String(process.env.PRISMA_SURF_GPU_MODE || "off").toLowerCase();
  let gpuArgs = [];
  try {
    const parsedGpuArgs = JSON.parse(process.env.PRISMA_SURF_GPU_ARGS_JSON || "[]");
    if (Array.isArray(parsedGpuArgs)) gpuArgs = parsedGpuArgs.map(String).filter(Boolean);
  } catch (_) {
    gpuArgs = [];
  }
  const useGpuLaunchOptions = gpuMode !== "off" && gpuArgs.length > 0;
  const launchOptions = useGpuLaunchOptions ? { args: gpuArgs } : undefined;
  fs.writeFileSync(path.join(outDir, "gpu-runtime.json"), JSON.stringify({ gpuMode, chromiumArgs: gpuArgs, launchOptionsEnabled: useGpuLaunchOptions, capturedAt: new Date().toISOString() }, null, 2));

  test.describe.configure({ mode: "parallel" });
  test.use({ trace: "retain-on-failure", screenshot: "only-on-failure", video: "off", ...(launchOptions ? { launchOptions } : {}) });
  test.setTimeout(testTimeout);

  function safeName(value) {
    return String(value || "surface")
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-zA-Z0-9_.-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 120) || "surface";
  }
  function formatError(error) {
    return {
      type: error && error.name ? String(error.name) : typeof error,
      message: error && error.message ? String(error.message) : String(error),
      stack: error && error.stack ? String(error.stack) : null,
    };
  }
  function writeJsonRecord(fileBase, record) {
    fs.writeFileSync(path.join(outDir, `${fileBase}.json`), JSON.stringify(record, null, 2));
  }
  function targetUrl(target, route) {
    return new URL(route || target.route || "/", target.baseUrl).toString();
  }
  function isRetryableNavigationError(error) {
    const message = error && error.message ? String(error.message) : String(error);
    return /ERR_CONNECTION_REFUSED|ERR_CONNECTION_RESET|ERR_CONNECTION_CLOSED|Timeout/i.test(message);
  }
  function shouldSkipPort(target) {
    return onlinePorts.size > 0 && !onlinePorts.has(String(target.port || target.macro));
  }
  function bounded(promise, ms, fallback) {
    return Promise.race([
      Promise.resolve(promise).catch(() => fallback),
      new Promise(resolve => setTimeout(() => resolve(fallback), ms))
    ]);
  }
  function urlPathMatches(currentUrl, expectedUrl) {
    try {
      const current = new URL(currentUrl);
      const expected = new URL(expectedUrl);
      return current.origin === expected.origin && current.pathname === expected.pathname;
    } catch (_) {
      return false;
    }
  }
  async function softNavigationState(page, expectedUrl) {
    const currentUrl = page.url();
    const state = await bounded(page.evaluate(() => {
      const bodyText = document.body ? String(document.body.innerText || document.body.textContent || '') : '';
      return {
        readyState: document.readyState,
        hasBody: Boolean(document.body),
        bodyTextLength: bodyText.trim().length,
        h1: document.querySelector('h1') ? document.querySelector('h1').textContent : null
      };
    }), probeTimeout, null);
    return {
      currentUrl,
      expectedUrl,
      pathMatches: urlPathMatches(currentUrl, expectedUrl),
      readyState: state ? state.readyState : null,
      hasBody: state ? state.hasBody : false,
      bodyTextLength: state ? state.bodyTextLength : 0,
      h1: state ? state.h1 : null,
      softLanded: Boolean(state && urlPathMatches(currentUrl, expectedUrl) && state.hasBody && state.bodyTextLength > 0)
    };
  }
  async function capture(page, target, label, extra = {}) {
    const fileBase = `${safeName(target.macro)}-${safeName(target.id)}-${safeName(label)}`;
    const record = {
      status: extra.status || "captured",
      targetId: target.id,
      macro: target.macro,
      port: target.port,
      kind: target.kind,
      label,
      url: page.url(),
      title: await bounded(page.title(), probeTimeout, null),
      h1: await bounded(page.locator("h1").first().textContent({ timeout: 600 }), probeTimeout, null),
      capturedAt: new Date().toISOString(),
      gpuMode,
      chromiumArgs: gpuArgs,
      ...extra,
    };
    if (captureScreenshots) {
      const screenshotPath = path.join(outDir, `${fileBase}.png`);
      const scrollCoverage = await captureDeepScreenshots(page, {
        ...deepCaptureOptions,
        captureScreenshots,
        timeout: screenshotTimeout,
        settleMs,
        outDir,
        fileBase,
        legacyPath: screenshotPath,
        targetMeta: { targetId: target.id, macro: target.macro, kind: target.kind, label }
      });
      record.screenshot = scrollCoverage.fullPageScreenshot || scrollCoverage.legacyScreenshot || scrollCoverage.viewportScreenshot || null;
      record.screenshotLegacy = scrollCoverage.legacyScreenshot || null;
      record.screenshotViewport = scrollCoverage.viewportScreenshot || null;
      record.screenshotFullPage = scrollCoverage.fullPageScreenshot || null;
      record.scrollCoverage = scrollCoverage;
      if (scrollCoverage.errors && scrollCoverage.errors.length) record.screenshotErrors = scrollCoverage.errors;
    }
    writeJsonRecord(fileBase, record);
  }
  async function captureSkipped(page, target, reason, extra = {}) {
    const label = target.route || target.label || target.chartId || target.tab || target.frame || target.interfaceTarget || target.id;
    const fileBase = `${safeName(target.macro)}-${safeName(target.id)}-skipped`;
    writeJsonRecord(fileBase, {
      status: "skipped",
      targetId: target.id,
      macro: target.macro,
      port: target.port,
      kind: target.kind,
      label,
      route: target.route || null,
      expectedUrl: targetUrl(target, target.route || "/"),
      reason,
      reasonType: extra.reasonType || "skipped",
      capturedAt: new Date().toISOString(),
      gpuMode,
      chromiumArgs: gpuArgs,
    });
  }
  async function captureFailure(page, target, label, error, extra = {}) {
    const fileBase = `${safeName(target.macro)}-${safeName(target.id)}-${safeName(label || "failed")}-failed`;
    const record = {
      status: "failed",
      targetId: target.id,
      macro: target.macro,
      port: target.port,
      kind: target.kind,
      label: label || target.id,
      route: target.route || null,
      expectedUrl: targetUrl(target, target.route || "/"),
      url: page ? page.url() : null,
      title: page ? await bounded(page.title(), probeTimeout, null) : null,
      h1: page ? await bounded(page.locator("h1").first().textContent({ timeout: 600 }), probeTimeout, null) : null,
      capturedAt: new Date().toISOString(),
      gpuMode,
      chromiumArgs: gpuArgs,
      error: formatError(error),
      ...extra,
    };
    if (captureScreenshots && page) {
      const screenshotPath = path.join(outDir, `${fileBase}.png`);
      const scrollCoverage = await captureDeepScreenshots(page, {
        ...deepCaptureOptions,
        captureScreenshots,
        timeout: screenshotTimeout,
        settleMs,
        outDir,
        fileBase,
        legacyPath: screenshotPath,
        targetMeta: { targetId: target.id, macro: target.macro, kind: target.kind, label: label || target.id, failure: true }
      });
      record.screenshot = scrollCoverage.fullPageScreenshot || scrollCoverage.legacyScreenshot || scrollCoverage.viewportScreenshot || null;
      record.screenshotLegacy = scrollCoverage.legacyScreenshot || null;
      record.screenshotViewport = scrollCoverage.viewportScreenshot || null;
      record.screenshotFullPage = scrollCoverage.fullPageScreenshot || null;
      record.scrollCoverage = scrollCoverage;
      if (scrollCoverage.errors && scrollCoverage.errors.length) record.screenshotErrors = scrollCoverage.errors;
    }
    writeJsonRecord(fileBase, record);
  }
  async function gotoAndSettle(page, target, route) {
    const url = targetUrl(target, route);
    let lastError = null;
    for (let attempt = 0; attempt <= gotoRetries; attempt += 1) {
      try {
        await page.goto(url, { waitUntil: "domcontentloaded", timeout: gotoTimeout });
        lastError = null;
        break;
      } catch (error) {
        lastError = error;
        const softState = await softNavigationState(page, url).catch(() => null);
        if (softState && softState.softLanded) {
          await page.waitForTimeout(settleMs);
          return { url, softNavigation: true, softState, navigationWarning: formatError(error) };
        }
        if (attempt >= gotoRetries || !isRetryableNavigationError(error)) throw error;
        await page.waitForTimeout(850 * (attempt + 1));
      }
    }
    if (lastError) throw lastError;
    await page.waitForTimeout(settleMs);
    return { url, softNavigation: false };
  }
  async function captureRoute(page, target) {
    const nav = await gotoAndSettle(page, target, target.route || "/");
    await capture(page, target, target.route || "/", { route: target.route, navigation: nav });
  }
  async function captureTabletNav(page, target) {
    const nav = await gotoAndSettle(page, target, target.route || "/");
    const byHref = page.locator(`a[href="${target.route}"]`).first();
    const hrefVisible = await byHref.isVisible({ timeout: 800 }).catch(() => false);
    const labelVisible = await page.getByText(target.label, { exact: true }).first().isVisible({ timeout: 800 }).catch(() => false);
    await capture(page, target, target.label || target.route, { route: target.route, navLabel: target.label, hrefVisible, labelVisible, navigation: nav });
  }
  async function captureChart(page, target) {
    const nav = await gotoAndSettle(page, target, target.route || "/");
    const selected = await page.locator("[data-selected-chart], [data-chart-id]").first().evaluate(el => el.getAttribute("data-selected-chart") || el.getAttribute("data-chart-id") || el.textContent).catch(() => null);
    await capture(page, target, target.chartId || "chart", { chartId: target.chartId, selectedChart: selected, navigation: nav });
  }
  async function captureChartTab(page, target) {
    const nav = await gotoAndSettle(page, target, target.route || "/");
    const tabName = target.tab || "tab";
    const roleTab = page.getByRole("tab", { name: new RegExp(tabName, "i") }).first();
    const button = page.locator("button").filter({ hasText: new RegExp(tabName, "i") }).first();
    let clicked = false;
    if (await roleTab.count().catch(() => 0)) { await roleTab.click({ timeout: clickTimeout, force: true }).catch(() => {}); clicked = true; }
    else if (await button.count().catch(() => 0)) { await button.click({ timeout: clickTimeout, force: true }).catch(() => {}); clicked = true; }
    await page.waitForTimeout(settleMs);
    await capture(page, target, tabName, { tab: tabName, clicked, navigation: nav });
  }
  async function captureChartFrame(page, target) {
    const nav = await gotoAndSettle(page, target, target.route || "/");
    const frame = target.frame || "frame";
    const candidate = page.locator(`[data-target="${frame}"], [data-chart-target="${frame}"], button:has-text("${frame}")`).first();
    let clicked = false;
    if (await candidate.count().catch(() => 0)) { await candidate.click({ timeout: clickTimeout, force: true }).catch(() => {}); clicked = true; }
    await page.waitForTimeout(settleMs);
    await capture(page, target, frame, { frame, clicked, navigation: nav });
  }
  function controlCenterSurfaceSelector(interfaceTarget) {
    return {
      quality: "#qualityBaySurface, .qualityBaySurface",
      license: "#licenseOpsSurface, .licenseOpsSurface",
      lifecycle: "#lifecycleSurface, .lifecycleSurface",
      prismo: "#prismoConsoleSurface, .prismoConsoleSurface",
    }[interfaceTarget] || "";
  }
  async function getControlCenterState(page, interfaceTarget) {
    const selector = controlCenterSurfaceSelector(interfaceTarget);
    return page.evaluate(({ interfaceTarget, selector }) => {
      const button = document.querySelector(`[data-prisma-interface-target="${interfaceTarget}"]`);
      const surface = selector ? document.querySelector(selector) : null;
      const visible = surface ? getComputedStyle(surface).display !== "none" && !surface.hidden : false;
      return {
        active: document.body ? document.body.getAttribute("data-prisma-interface") : null,
        pressed: button ? button.getAttribute("aria-pressed") : null,
        surfaceFound: Boolean(surface),
        surfaceVisible: visible,
      };
    }, { interfaceTarget, selector }).catch(error => ({ error: error.message }));
  }
  async function selectControlCenterTarget(page, target, btn) {
    const interfaceTarget = target.interfaceTarget;
    let lastState = await getControlCenterState(page, interfaceTarget);
    if (lastState.active === interfaceTarget || lastState.pressed === "true" || lastState.surfaceVisible) return lastState;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      await btn.click({ timeout: clickTimeout, force: true, noWaitAfter: true });
      await page.waitForTimeout(Math.max(settleMs, 650 + attempt * 350));
      lastState = await getControlCenterState(page, interfaceTarget);
      if (lastState.active === interfaceTarget || lastState.pressed === "true" || lastState.surfaceVisible) return lastState;
    }
    throw new Error(`Control Center target ${interfaceTarget} did not become active after click retries. Last state: ${JSON.stringify(lastState)}`);
  }
  async function captureControlCenterTarget(page, target) {
    const nav = await gotoAndSettle(page, target, "/");
    const selector = `[data-prisma-interface-target="${target.interfaceTarget}"]`;
    const btn = page.locator(selector).first();
    await expect(btn, `Control Center real target ${target.interfaceTarget}`).toHaveCount(1, { timeout: 3500 });
    await btn.scrollIntoViewIfNeeded({ timeout: clickTimeout }).catch(() => {});
    const interfaceState = await selectControlCenterTarget(page, target, btn);
    await capture(page, target, target.interfaceTarget, { interfaceTarget: target.interfaceTarget, interfaceState, navigation: nav });
  }
  async function captureControlCenterLifecycle(page, target) {
    await captureControlCenterTarget(page, { ...target, kind: "control-center-target", interfaceTarget: target.interfaceTarget || "lifecycle" });
    const lifecycle = page.locator("#lifecycleSurface, .lifecycleSurface").first();
    await expect(lifecycle, "Control Center lifecycle surface must materialize").toHaveCount(1, { timeout: 12000 });
    await capture(page, target, "lifecycleSurface", { lifecycleSurface: true });
  }

  if (!Array.isArray(plan.targets) || plan.targets.length === 0) {
    throw new Error(`surf8 plan has zero targets: ${planPath}`);
  }

  for (const [targetIndex, target] of plan.targets.entries()) {
    const tags = Array.isArray(target.tags) ? target.tags.join(" ") : "";
    test(`${target.macro} ${target.id} ${tags}`, async ({ page }) => {
      emitProgress("target-start", { targetMeta: { targetId: target.id, macro: target.macro, kind: target.kind, route: target.route || null, label: target.label || target.id }, index: targetIndex + 1, total: plan.targets.length, message: `${runMode} ${target.macro} ${target.id}` });
      const label = target.route || target.label || target.chartId || target.tab || target.frame || target.interfaceTarget || target.id;
      if (shouldSkipPort(target)) {
        emitProgress("target-skipped-offline", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: `${target.baseUrl} offline` });
        await captureSkipped(page, target, `${target.baseUrl} was offline in surf8 preflight`, { reasonType: "offline_port" });
        return;
      }
      try {
        if (target.kind === "route") { const out = await captureRoute(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        if (target.kind === "tablet-nav") { const out = await captureTabletNav(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        if (target.kind === "chart-lab-chart") { const out = await captureChart(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        if (target.kind === "chart-lab-tab") { const out = await captureChartTab(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        if (target.kind === "chart-lab-frame") { const out = await captureChartFrame(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        if (target.kind === "control-center-target") { const out = await captureControlCenterTarget(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        if (target.kind === "control-center-lifecycle") { const out = await captureControlCenterLifecycle(page, target); emitProgress("target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured" }); return out; }
        throw new Error(`Unknown surf8 target kind: ${target.kind}`);
      } catch (error) {
        emitProgress("target-failed", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: error && error.message ? error.message : String(error) });
        await captureFailure(page, target, label, error);
        throw error;
      }
    });
  }
}

module.exports = { registerSurf8Tests };
