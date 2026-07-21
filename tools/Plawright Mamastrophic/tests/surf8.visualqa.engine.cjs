const fs = require("fs");
const path = require("path");
const { captureDeepScreenshots, envDeepCaptureOptions, emitProgress } = require("./surf8.deep-capture.cjs");
const { legalEvidenceEnabled, applyLegalRedaction, sanitizeText, sanitizeUrl, sanitizeObject, sanitizeConsoleEntry, sanitizeNetworkEntry } = require("./surf8.legal-evidence.cjs");

function registerSurf8VisualQaTests(test, expect) {
  const planPath = process.env.PRISMA_SURF_PLAN_JSON;
  if (!planPath) throw new Error("PRISMA_SURF_PLAN_JSON is required");

  const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
  const outDir = process.env.PRISMA_VISUALQA_OUT_DIR || process.env.PRISMA_SURF_OUT_DIR || path.join(process.cwd(), "test-results", "visualqa");
  const reportsDir = process.env.PRISMA_VISUALQA_REPORTS_DIR || path.join(outDir, "reports");
  const screensDir = process.env.PRISMA_VISUALQA_SCREENS_DIR || path.join(outDir, "screens");
  const domDir = process.env.PRISMA_VISUALQA_DOM_DIR || path.join(outDir, "dom");
  const captureScreenshots = String(process.env.PRISMA_SURF_SCREENSHOTS || "1") !== "0";
  const fullPage = String(process.env.PRISMA_SURF_FULLPAGE || "1") === "1";
  const deepCaptureOptions = envDeepCaptureOptions({ fullPage });
  const deepCaptureBudget = captureScreenshots ? Number(deepCaptureOptions.captureBudgetMs || 240000) : 0;
  const settleMs = Number(process.env.PRISMA_SURF_SETTLE_MS || 220);
  const gotoTimeout = Number(process.env.PRISMA_SURF_GOTO_TIMEOUT_MS || 45000);
  const gotoRetries = Number(process.env.PRISMA_SURF_GOTO_RETRIES || 2);
  const clickTimeout = Number(process.env.PRISMA_SURF_CLICK_TIMEOUT_MS || 7000);
  const screenshotTimeout = Number(process.env.PRISMA_SURF_SCREENSHOT_TIMEOUT_MS || 15000);
  const probeTimeout = Number(process.env.PRISMA_SURF_PROBE_TIMEOUT_MS || 1400);
  const defaultTestTimeout = Math.max(
    240000,
    (gotoTimeout * (gotoRetries + 1)) + deepCaptureBudget + (screenshotTimeout * 2) + (clickTimeout * 3) + 60000
  );
  const testTimeout = Number(process.env.PRISMA_SURF_TEST_TIMEOUT_MS || defaultTestTimeout);
  const onlinePorts = new Set(String(process.env.PRISMA_SURF_ONLINE_PORTS || "").split(",").map(s => s.trim()).filter(Boolean));
  const runMode = String(process.env.PRISMA_SURF_MODE || "visualqa");
  const gpuMode = String(process.env.PRISMA_SURF_GPU_MODE || "off").toLowerCase();
  const viewportWidth = Math.max(240, Number(process.env.PRISMA_SURF_VIEWPORT_WIDTH || 1365));
  const viewportHeight = Math.max(320, Number(process.env.PRISMA_SURF_VIEWPORT_HEIGHT || 768));
  const viewport = { width: viewportWidth, height: viewportHeight };

  let gpuArgs = [];
  try {
    const parsedGpuArgs = JSON.parse(process.env.PRISMA_SURF_GPU_ARGS_JSON || "[]");
    if (Array.isArray(parsedGpuArgs)) gpuArgs = parsedGpuArgs.map(String).filter(Boolean);
  } catch (_) {
    gpuArgs = [];
  }
  const useGpuLaunchOptions = gpuMode !== "off" && gpuArgs.length > 0;
  const launchOptions = useGpuLaunchOptions ? { args: gpuArgs } : undefined;

  for (const dir of [outDir, reportsDir, screensDir, domDir]) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(path.join(reportsDir, "gpu-runtime.json"), JSON.stringify({
    gpuMode,
    chromiumArgs: gpuArgs,
    launchOptionsEnabled: useGpuLaunchOptions,
    testTimeout,
    deepCaptureBudget,
    deepCaptureOptions,
    capturedAt: new Date().toISOString()
  }, null, 2));

  test.describe.configure({ mode: "parallel" });
  const legalMode = legalEvidenceEnabled();
  test.use({ viewport, trace: legalMode ? "off" : "retain-on-failure", screenshot: legalMode ? "off" : "only-on-failure", video: "off", ...(launchOptions ? { launchOptions } : {}) });
  test.setTimeout(testTimeout);

  function safeName(value) {
    return String(value || "route")
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-zA-Z0-9_.-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 140) || "route";
  }

  function routeSafeName(target) {
    const raw = target.route || target.label || target.chartId || target.tab || target.frame || target.interfaceTarget || target.id || "route";
    const routeName = raw === "/" ? "home" : safeName(String(raw).replace(/^\//, ""));
    return `${safeName(target.id || target.macro)}--${routeName}`;
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
    let timer = null;
    const timeoutPromise = new Promise(resolve => {
      timer = setTimeout(() => resolve(fallback), ms);
    });
    return Promise.race([
      Promise.resolve(promise).catch(() => fallback),
      timeoutPromise
    ]).finally(() => {
      if (timer) clearTimeout(timer);
    });
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

  function formatError(error) {
    return {
      type: error && error.name ? String(error.name) : typeof error,
      message: error && error.message ? String(error.message) : String(error),
      stack: error && error.stack ? String(error.stack) : null
    };
  }

  function writeJson(filePath, data) {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  }

  function targetPaths(target) {
    const base = routeSafeName(target);
    return {
      base,
      surfaceDir: safeName(target.macro || "surface"),
      screen: path.join(screensDir, safeName(target.macro || "surface"), `${base}.png`),
      dom: path.join(domDir, safeName(target.macro || "surface"), `${base}.dom.json`),
      computed: path.join(domDir, safeName(target.macro || "surface"), `${base}.computed.json`)
    };
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
    await page.waitForLoadState("networkidle", { timeout: Math.min(8000, gotoTimeout) }).catch(() => {});
    await page.waitForTimeout(settleMs);
    return { url, softNavigation: false };
  }

  async function prepareTarget(page, target) {
    if (target.kind === "chart-lab-tab" && target.tab) {
      const tabName = target.tab;
      const roleTab = page.getByRole("tab", { name: new RegExp(tabName, "i") }).first();
      const button = page.locator("button").filter({ hasText: new RegExp(tabName, "i") }).first();
      if (await roleTab.count().catch(() => 0)) await roleTab.click({ timeout: clickTimeout, force: true }).catch(() => {});
      else if (await button.count().catch(() => 0)) await button.click({ timeout: clickTimeout, force: true }).catch(() => {});
      await page.waitForTimeout(settleMs);
    }

    if (target.kind === "chart-lab-frame" && target.frame) {
      const frame = target.frame;
      const candidate = page.locator(`[data-target="${frame}"], [data-chart-target="${frame}"], button:has-text("${frame}")`).first();
      if (await candidate.count().catch(() => 0)) await candidate.click({ timeout: clickTimeout, force: true }).catch(() => {});
      await page.waitForTimeout(settleMs);
    }

    if ((target.kind === "control-center-target" || target.kind === "control-center-lifecycle") && target.interfaceTarget) {
      const selector = `[data-prisma-interface-target="${target.interfaceTarget}"]`;
      const btn = page.locator(selector).first();
      if (await btn.count().catch(() => 0)) {
        await btn.scrollIntoViewIfNeeded({ timeout: clickTimeout }).catch(() => {});
        await btn.click({ timeout: clickTimeout, force: true, noWaitAfter: true }).catch(() => {});
        await page.waitForTimeout(Math.max(settleMs, 800));
      }
    }
  }

  async function captureComputed(page, target, status, extra = {}) {
    const paths = targetPaths(target);
    const legalRedaction = await applyLegalRedaction(page).catch(error => ({ enabled: true, status: "BLOCKED_UNREDACTED", error: sanitizeText(error && error.message ? error.message : String(error)) }));
    extra = sanitizeObject(extra);
    const viewport = page.viewportSize() || { width: 0, height: 0 };
    const title = sanitizeText(await bounded(page.title(), probeTimeout, null));
    const url = sanitizeUrl(page.url());
    const capturedAt = new Date().toISOString();

    const visual = await page.evaluate(({ targetMeta }) => {
      const selectorContracts = [
        "html",
        "body",
        "main",
        "[data-prisma-shell]",
        "[data-prisma-background]",
        "[data-prisma-cloudglass]",
        "[data-prisma-route]",
        "[class*=\"shell\" i]",
        "[class*=\"page\" i]",
        "[class*=\"screen\" i]",
        "[class*=\"viewport\" i]",
        "[class*=\"content\" i]",
        "[class*=\"panel\" i]",
        "[class*=\"card\" i]",
        "[class*=\"surface\" i]",
        "[class*=\"overlay\" i]",
        "[class*=\"dialog\" i]",
        "[class*=\"modal\" i]",
        "[class*=\"sidebar\" i]",
        "[class*=\"header\" i]",
        "[class*=\"nav\" i]"
      ];

      function rgbaParts(value) {
        const raw = String(value || "").trim().toLowerCase();
        if (!raw || raw === "transparent") return [0, 0, 0, 0];
        let m = raw.match(/^rgba?\(([^)]+)\)$/);
        if (!m) return null;
        const parts = m[1].split(",").map(x => x.trim());
        const r = Number.parseFloat(parts[0]);
        const g = Number.parseFloat(parts[1]);
        const b = Number.parseFloat(parts[2]);
        const a = parts.length >= 4 ? Number.parseFloat(parts[3]) : 1;
        if ([r, g, b, a].some(x => Number.isNaN(x))) return null;
        return [r, g, b, a];
      }

      function isNonTransparent(value) {
        const rgba = rgbaParts(value);
        if (!rgba) return Boolean(value && value !== "transparent");
        return rgba[3] > 0.02;
      }

      function luminanceFromRgb(r, g, b) {
        const vals = [r, g, b].map(v => {
          const n = Math.max(0, Math.min(255, v)) / 255;
          return n <= 0.03928 ? n / 12.92 : Math.pow((n + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2];
      }

      function contrastRatio(fg, bg) {
        const f = rgbaParts(fg);
        const b = rgbaParts(bg);
        if (!f || !b || b[3] < 0.98 || f[3] < 0.2) return null;
        const l1 = luminanceFromRgb(f[0], f[1], f[2]);
        const l2 = luminanceFromRgb(b[0], b[1], b[2]);
        const high = Math.max(l1, l2);
        const low = Math.min(l1, l2);
        return Math.round(((high + 0.05) / (low + 0.05)) * 100) / 100;
      }

      function textSample(el) {
        return String(el.innerText || el.textContent || "")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 180);
      }

      function classText(el) {
        if (!el || !el.className) return "";
        if (typeof el.className === "string") return el.className;
        if (typeof el.className.baseVal === "string") return el.className.baseVal;
        return String(el.getAttribute("class") || "");
      }

      function selectorGuess(el) {
        if (!el || !el.tagName) return "";
        const tag = el.tagName.toLowerCase();
        const quoteCss = value => String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
        const dataAttrs = ["data-prisma-shell", "data-prisma-background", "data-prisma-cloudglass", "data-prisma-route", "data-testid", "data-test-id", "data-prisma-interface-target"];
        for (const attr of dataAttrs) {
          const val = el.getAttribute(attr);
          if (val !== null) return val === "" ? `${tag}[${attr}]` : `${tag}[${attr}="${quoteCss(String(val).slice(0, 80))}"]`;
        }
        if (el.id) return `${tag}#${CSS.escape(String(el.id).slice(0, 80))}`;
        const cls = classText(el).split(/\s+/).filter(Boolean).slice(0, 3).map(value => CSS.escape(value));
        if (cls.length) return `${tag}.${cls.join(".")}`;
        const parent = el.parentElement;
        if (!parent) return tag;
        const siblings = Array.from(parent.children).filter(x => x.tagName === el.tagName);
        const idx = siblings.indexOf(el) + 1;
        return `${tag}:nth-of-type(${idx || 1})`;
      }

      function isViewportUnit(value) {
        return /100(vh|dvh|svh|lvh)|calc\(.*100(vh|dvh|svh|lvh)/i.test(String(value || ""));
      }

      function summarizeDom(root, depth = 0) {
        if (!root || depth > 4) return null;
        const children = Array.from(root.children || []).slice(0, 24).map(child => summarizeDom(child, depth + 1)).filter(Boolean);
        return {
          tag: root.tagName ? root.tagName.toLowerCase() : "",
          id: root.id || "",
          className: classText(root).slice(0, 220),
          selectorGuess: selectorGuess(root),
          role: root.getAttribute ? (root.getAttribute("role") || "") : "",
          data: root.getAttribute ? {
            prismaShell: root.getAttribute("data-prisma-shell"),
            prismaBackground: root.getAttribute("data-prisma-background"),
            prismaCloudglass: root.getAttribute("data-prisma-cloudglass"),
            prismaRoute: root.getAttribute("data-prisma-route"),
            testid: root.getAttribute("data-testid") || root.getAttribute("data-test-id")
          } : {},
          textSample: textSample(root).slice(0, 100),
          childCount: root.children ? root.children.length : 0,
          children
        };
      }

      const picked = new Set();
      for (const sel of selectorContracts) {
        try {
          for (const el of document.querySelectorAll(sel)) picked.add(el);
        } catch (_) {}
      }

      const all = Array.from(document.querySelectorAll("*"));
      const viewportW = window.innerWidth || document.documentElement.clientWidth || 0;
      const viewportH = window.innerHeight || document.documentElement.clientHeight || 0;

      for (const el of all) {
        if (picked.size > 650) break;
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const classAndId = `${el.id || ""} ${classText(el)}`;
        const positionHit = /^(fixed|sticky|absolute)$/i.test(cs.position);
        const zHit = cs.zIndex && cs.zIndex !== "auto";
        const bgHit = isNonTransparent(cs.backgroundColor) || (cs.backgroundImage && cs.backgroundImage !== "none");
        const filterHit = (cs.backdropFilter && cs.backdropFilter !== "none") || (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== "none") || (cs.filter && cs.filter !== "none");
        const namedHit = /(overlay|dialog|modal|panel|card|shell|page|screen|viewport|surface|sidebar|header|nav|glass|background)/i.test(classAndId);
        const viewportHit = isViewportUnit(cs.minHeight) || isViewportUnit(cs.height) || ((cs.inset === "0px" || (cs.top === "0px" && cs.right === "0px" && cs.bottom === "0px" && cs.left === "0px")) && positionHit);
        const visibleSize = rect.width > 1 && rect.height > 1;
        if (visibleSize && (positionHit || zHit || bgHit || filterHit || namedHit || viewportHit)) picked.add(el);
      }

      const elements = Array.from(picked).slice(0, 650).map(el => {
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const cls = classText(el);
        const bbox = {
          x: Math.round(rect.x * 100) / 100,
          y: Math.round(rect.y * 100) / 100,
          width: Math.round(rect.width * 100) / 100,
          height: Math.round(rect.height * 100) / 100
        };
        const coversViewport = bbox.x <= 12 && bbox.y <= 12 && bbox.width >= viewportW * 0.88 && bbox.height >= viewportH * 0.88;
        const hasNonTransparentBackground = isNonTransparent(cs.backgroundColor) || Boolean(cs.backgroundImage && cs.backgroundImage !== "none");
        const isOverlay = /overlay|dialog|modal|popover|backdrop/i.test(`${el.id || ""} ${cls}`) || (/^(fixed|sticky|absolute)$/i.test(cs.position) && (coversViewport || (cs.inset === "0px")));
        const isPanelOrCard = /panel|card|surface|sheet|drawer|tile|cloudglass|glass/i.test(`${el.id || ""} ${cls}`);
        const isShellOrViewport = el === document.body || el === document.documentElement || /shell|page|screen|viewport|layout|root|app/i.test(`${el.id || ""} ${cls}`);
        const hasZIndex = cs.zIndex && cs.zIndex !== "auto";
        const hasBackdropFilter = Boolean((cs.backdropFilter && cs.backdropFilter !== "none") || (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== "none"));
        const mayObscureBackground = (coversViewport || isOverlay || isPanelOrCard || isShellOrViewport || hasZIndex) && hasNonTransparentBackground && Number.parseFloat(cs.opacity || "1") > 0.02;

        return {
          selectorGuess: selectorGuess(el),
          tag: el.tagName ? el.tagName.toLowerCase() : "",
          id: el.id || "",
          className: cls,
          textSample: textSample(el),
          bbox,
          computed: {
            position: cs.position,
            display: cs.display,
            visibility: cs.visibility,
            opacity: cs.opacity,
            zIndex: cs.zIndex,
            color: cs.color,
            fontSize: cs.fontSize,
            background: cs.background,
            backgroundColor: cs.backgroundColor,
            backgroundImage: cs.backgroundImage,
            backdropFilter: cs.backdropFilter || cs.webkitBackdropFilter || "none",
            filter: cs.filter,
            overflow: cs.overflow,
            overflowX: cs.overflowX,
            overflowY: cs.overflowY,
            isolation: cs.isolation,
            pointerEvents: cs.pointerEvents,
            minHeight: cs.minHeight,
            height: cs.height,
            inset: cs.inset,
            top: cs.top,
            right: cs.right,
            bottom: cs.bottom,
            left: cs.left
          },
          flags: {
            coversViewport,
            hasNonTransparentBackground,
            mayObscureBackground,
            isOverlay,
            isPanelOrCard,
            isShellOrViewport,
            hasZIndex,
            hasBackdropFilter,
            hasBackgroundImage: Boolean(cs.backgroundImage && cs.backgroundImage !== "none"),
            positionCandidate: /^(fixed|sticky|absolute)$/i.test(cs.position)
          },
          readability: {
            color: cs.color,
            backgroundColor: cs.backgroundColor,
            opacity: cs.opacity,
            fontSize: cs.fontSize,
            contrastApprox: contrastRatio(cs.color, cs.backgroundColor)
          }
        };
      });

      return {
        routeMeta: targetMeta,
        viewport: { width: viewportW, height: viewportH },
        scroll: { x: window.scrollX || 0, y: window.scrollY || 0 },
        document: {
          readyState: document.readyState,
          title: document.title,
          location: document.location.href,
          bodyClassName: document.body ? classText(document.body) : "",
          htmlClassName: document.documentElement ? classText(document.documentElement) : ""
        },
        domSnapshot: summarizeDom(document.documentElement),
        elements
      };
    }, { targetMeta: { id: target.id, macro: target.macro, kind: target.kind, route: target.route || null } });

    const record = {
      status,
      surface: target.macro,
      route: target.route || null,
      url,
      targetId: target.id,
      kind: target.kind,
      capturedAt,
      viewport,
      title,
      gpuMode,
      chromiumArgs: gpuArgs,
      console: extra.console || [],
      networkFailures: extra.networkFailures || [],
      elements: visual.elements || [],
      screenshot: null,
      error: extra.error || null
    };

    const domRecord = {
      status,
      surface: target.macro,
      route: target.route || null,
      url,
      targetId: target.id,
      capturedAt,
      title,
      viewport: visual.viewport || viewport,
      document: visual.document || {},
      domSnapshot: visual.domSnapshot || null,
      legalRedaction
    };

    if (captureScreenshots) {
      const scrollCoverage = await captureDeepScreenshots(page, {
        ...deepCaptureOptions,
        captureScreenshots,
        timeout: screenshotTimeout,
        settleMs,
        outDir: path.dirname(paths.screen),
        fileBase: path.basename(paths.screen, path.extname(paths.screen)),
        legacyPath: paths.screen,
        targetMeta: { targetId: target.id, macro: target.macro, kind: target.kind, route: target.route || null, visualqa: true }
      });
      record.screenshot = scrollCoverage.fullPageScreenshot || scrollCoverage.legacyScreenshot || scrollCoverage.viewportScreenshot || null;
      record.screenshotLegacy = scrollCoverage.legacyScreenshot || null;
      record.screenshotViewport = scrollCoverage.viewportScreenshot || null;
      record.screenshotFullPage = scrollCoverage.fullPageScreenshot || null;
      record.scrollCoverage = scrollCoverage;
      if (scrollCoverage.errors && scrollCoverage.errors.length) record.screenshotErrors = scrollCoverage.errors;
    }

    writeJson(paths.computed, record);
    writeJson(paths.dom, domRecord);
  }

  async function captureSkippedOffline(target) {
    const paths = targetPaths(target);
    const now = new Date().toISOString();
    const base = {
      status: "skipped_offline",
      surface: target.macro,
      route: target.route || null,
      url: targetUrl(target, target.route || "/"),
      expectedUrl: targetUrl(target, target.route || "/"),
      targetId: target.id,
      kind: target.kind,
      capturedAt: now,
      viewport: { width: 0, height: 0 },
      title: null,
      console: [],
      networkFailures: [],
      elements: [],
      error: null,
      reason: `${target.baseUrl} was offline in visualqa preflight`,
      reasonType: "offline_port"
    };
    writeJson(paths.computed, base);
    writeJson(paths.dom, {
      status: "skipped_offline",
      surface: target.macro,
      route: target.route || null,
      url: base.url,
      targetId: target.id,
      capturedAt: now,
      title: null,
      viewport: { width: 0, height: 0 },
      document: {},
      domSnapshot: null,
      reason: base.reason,
      reasonType: "offline_port"
    });
  }

  if (!Array.isArray(plan.targets) || plan.targets.length === 0) {
    throw new Error(`visualqa plan has zero targets: ${planPath}`);
  }

  for (const [targetIndex, target] of plan.targets.entries()) {
    const tags = Array.isArray(target.tags) ? target.tags.join(" ") : "";
    test(`visualqa ${target.macro} ${target.id} ${tags}`, async ({ page }) => {
      emitProgress("qa-target-start", { targetMeta: { targetId: target.id, macro: target.macro, kind: target.kind, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: `${runMode} ${target.macro} ${target.id}` });
      if (shouldSkipPort(target)) {
        emitProgress("qa-target-skipped-offline", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: `${target.baseUrl} offline` });
        await captureSkippedOffline(target);
        return;
      }

      const consoleEntries = [];
      const networkFailures = [];

      page.on("console", msg => {
        const type = msg.type();
        if (type === "error" || type === "warning" || type === "warn") {
          consoleEntries.push({
            type,
            text: sanitizeText(msg.text()),
            location: sanitizeObject(msg.location ? msg.location() : null)
          });
        }
      });
      page.on("pageerror", error => {
        consoleEntries.push(sanitizeConsoleEntry({ type: "pageerror", text: error && error.message ? error.message : String(error), location: null }));
      });
      page.on("requestfailed", request => {
        networkFailures.push({
          type: "requestfailed",
          url: sanitizeUrl(request.url()),
          method: request.method(),
          resourceType: request.resourceType(),
          failure: sanitizeObject(request.failure()),
        });
      });
      page.on("response", response => {
        const status = response.status();
        if (status >= 400) {
          networkFailures.push({
            type: "http_error",
            url: sanitizeUrl(response.url()),
            status,
            statusText: response.statusText(),
            requestMethod: response.request().method(),
            resourceType: response.request().resourceType(),
          });
        }
      });

      try {
        const navigation = await gotoAndSettle(page, target, target.route || "/");
        await prepareTarget(page, target);
        emitProgress("qa-computed", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "DOM/computed/render layers" });
        await captureComputed(page, target, "captured", { console: consoleEntries, networkFailures, navigation });
        emitProgress("qa-target-done", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: "captured + QA" });
      } catch (error) {
        emitProgress("qa-target-failed", { targetMeta: { targetId: target.id, macro: target.macro, route: target.route || null }, index: targetIndex + 1, total: plan.targets.length, message: error && error.message ? error.message : String(error) });
        await captureComputed(page, target, "failed", { console: consoleEntries, networkFailures, error: formatError(error) }).catch(() => {});
        throw error;
      }
    });
  }
}

module.exports = { registerSurf8VisualQaTests };

// MAMVIEW4_VIEWPORT_BRIDGE_0407: visualqa engine uses explicit Playwright viewport from PRISMA_SURF_VIEWPORT_WIDTH/HEIGHT.
