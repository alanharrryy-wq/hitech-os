const fs = require("fs");
const path = require("path");

function asBool(value, defaultValue = false) {
  if (value === undefined || value === null || value === "") return defaultValue;
  const raw = String(value).trim().toLowerCase();
  if (["1", "true", "yes", "y", "si", "s", "on"].includes(raw)) return true;
  if (["0", "false", "no", "n", "off"].includes(raw)) return false;
  return defaultValue;
}

function asInt(value, defaultValue, minValue = 0, maxValue = 100000) {
  const n = Number(value);
  if (!Number.isFinite(n)) return defaultValue;
  return Math.max(minValue, Math.min(maxValue, Math.floor(n)));
}

function safeName(value) {
  return String(value || "item")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9_.-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 120) || "item";
}

function uniqueSortedPositions(maxScroll, viewportLength, overlap, maxTiles) {
  const max = Math.max(0, Math.floor(maxScroll || 0));
  const view = Math.max(1, Math.floor(viewportLength || 1));
  const maxUsefulOverlap = Math.floor(view / 2);
  const ov = Math.max(0, Math.min(view - 1, maxUsefulOverlap, Math.floor(overlap || 0)));
  const step = Math.max(1, view - ov);
  const positions = [];
  for (let y = 0; y < max; y += step) positions.push(y);
  positions.push(max);
  const unique = Array.from(new Set(positions.map(n => Math.max(0, Math.min(max, Math.floor(n)))))).sort((a, b) => a - b);
  if (unique.length <= maxTiles) return { positions: unique, truncated: false, expected: unique.length };
  const limited = unique.slice(0, Math.max(1, maxTiles - 1));
  if (!limited.includes(max)) limited.push(max);
  return { positions: Array.from(new Set(limited)).sort((a, b) => a - b), truncated: true, expected: unique.length };
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function fileParts(legacyPath, fallbackBase, fallbackDir) {
  const dir = legacyPath ? path.dirname(legacyPath) : fallbackDir;
  ensureDir(dir);
  const ext = legacyPath ? path.extname(legacyPath) || ".png" : ".png";
  const base = legacyPath ? path.basename(legacyPath, ext) : safeName(fallbackBase || "capture");
  return { dir, ext, base };
}

function emitProgress(stage, payload = {}) {
  const event = {
    ts: new Date().toISOString(),
    stage,
    mode: process.env.PRISMA_SURF_MODE || "",
    surface: process.env.PRISMA_SURF_SURFACE || "",
    targetId: payload.targetId || (payload.targetMeta && payload.targetMeta.targetId) || "",
    macro: payload.macro || (payload.targetMeta && payload.targetMeta.macro) || "",
    route: payload.route || (payload.targetMeta && payload.targetMeta.route) || "",
    label: payload.label || (payload.targetMeta && payload.targetMeta.label) || "",
    index: payload.index || null,
    total: payload.total || null,
    y: payload.y === undefined ? null : payload.y,
    message: payload.message || ""
  };
  const line = `[MAM-PROGRESS] ${event.surface || event.macro}|${event.mode}|${event.targetId}|${stage}|${event.index || ""}/${event.total || ""}|${event.message}`;
  try { console.log(line); } catch (_) {}
  const progressPath = process.env.PRISMA_SURF_PROGRESS_JSONL;
  if (progressPath) {
    try { fs.appendFileSync(progressPath, JSON.stringify(event) + "\n"); } catch (_) {}
  }
}

function formatShotError(error) {
  return error && error.message ? String(error.message) : String(error);
}

function isNavigationLikeError(error) {
  const message = formatShotError(error);
  return /Execution context was destroyed|navigation to finish|frame was detached|Target page, context or browser has been closed|Cannot find context with specified id|most likely because of a navigation/i.test(message);
}

class CaptureInterruptedError extends Error {
  constructor(kind, message, details = {}) {
    super(message);
    this.name = "CaptureInterruptedError";
    this.kind = kind;
    this.details = details;
  }
}

function createNavigationTracker(page) {
  const mainFrame = page.mainFrame();
  let epoch = 0;
  const events = [];
  const listener = frame => {
    if (frame !== mainFrame) return;
    epoch += 1;
    events.push({ ts: new Date().toISOString(), epoch, url: frame.url() });
  };
  page.on("framenavigated", listener);
  return {
    snapshot: () => epoch,
    changedSince: value => epoch !== value,
    events,
    dispose: () => {
      try { page.off("framenavigated", listener); } catch (_) {}
    }
  };
}

function deadlineState(startedAt, budgetMs) {
  const elapsedMs = Date.now() - startedAt;
  return { elapsedMs, remainingMs: Math.max(0, budgetMs - elapsedMs), expired: elapsedMs >= budgetMs };
}

function assertBudget(startedAt, budgetMs, stage) {
  const state = deadlineState(startedAt, budgetMs);
  if (state.expired) {
    throw new CaptureInterruptedError("budget", `Deep capture budget exhausted at ${stage}`, { stage, ...state });
  }
  return state;
}

async function quietDocument(page, tracker, quietWindowMs, quietMaxMs) {
  const started = Date.now();
  let lastEpoch = tracker.snapshot();
  let quietSince = Date.now();
  while (Date.now() - started < quietMaxMs) {
    if (page.isClosed()) return false;
    await page.waitForTimeout(Math.min(125, Math.max(50, quietWindowMs))).catch(() => {});
    const currentEpoch = tracker.snapshot();
    if (currentEpoch !== lastEpoch) {
      lastEpoch = currentEpoch;
      quietSince = Date.now();
      continue;
    }
    if (Date.now() - quietSince >= quietWindowMs) return true;
  }
  return false;
}

async function maybeScreenshot(task, coverage, bucket, stage) {
  try {
    const out = await task();
    if (bucket && out) bucket.push(out);
    return out;
  } catch (error) {
    coverage.errors.push({ stage: stage || coverage.currentStage || "screenshot", message: formatShotError(error) });
    return null;
  }
}

async function getDocumentMetrics(page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const body = document.body;
    const scrollWidth = Math.max(
      doc ? doc.scrollWidth : 0,
      body ? body.scrollWidth : 0,
      doc ? doc.clientWidth : 0,
      window.innerWidth || 0
    );
    const scrollHeight = Math.max(
      doc ? doc.scrollHeight : 0,
      body ? body.scrollHeight : 0,
      doc ? doc.clientHeight : 0,
      window.innerHeight || 0
    );
    return {
      scrollX: window.scrollX || 0,
      scrollY: window.scrollY || 0,
      viewportWidth: window.innerWidth || (doc ? doc.clientWidth : 0) || 0,
      viewportHeight: window.innerHeight || (doc ? doc.clientHeight : 0) || 0,
      scrollWidth,
      scrollHeight,
      devicePixelRatio: window.devicePixelRatio || 1,
      readyState: document.readyState,
      url: document.location ? document.location.href : ""
    };
  });
}

async function discoverScrollContainers(page, maxContainers, sessionId) {
  return page.evaluate(({ maxContainers, sessionId }) => {
    function classText(el) {
      const raw = el && el.getAttribute ? el.getAttribute("class") : "";
      return typeof raw === "string" ? raw : "";
    }
    function quoteCss(value) {
      return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
    }
    function selectorInfo(el) {
      if (!el || !el.tagName) return { selector: "", index: 0 };
      const tag = el.tagName.toLowerCase();
      const candidates = ["data-testid", "data-test", "data-prisma-route", "aria-label", "role"];
      let selector = "";
      if (el.id) {
        selector = `#${CSS.escape(el.id)}`;
      } else {
        for (const attrName of candidates) {
          const attrValue = el.getAttribute(attrName);
          if (attrValue && attrValue.length < 120) {
            selector = `${tag}[${attrName}="${quoteCss(attrValue)}"]`;
            break;
          }
        }
      }
      if (!selector) {
        const classes = classText(el).split(/\s+/).filter(Boolean).slice(0, 3).map(v => CSS.escape(v));
        selector = classes.length ? `${tag}.${classes.join(".")}` : tag;
      }
      let index = 0;
      try {
        const matches = Array.from(document.querySelectorAll(selector));
        const found = matches.indexOf(el);
        index = found >= 0 ? found : 0;
      } catch (_) {
        selector = tag;
        const matches = Array.from(document.querySelectorAll(selector));
        const found = matches.indexOf(el);
        index = found >= 0 ? found : 0;
      }
      return { selector, index };
    }
    function visible(el, rect, cs) {
      return rect.width >= 64 && rect.height >= 64 && cs.display !== "none" && cs.visibility !== "hidden" && Number.parseFloat(cs.opacity || "1") > 0.01;
    }
    const all = Array.from(document.querySelectorAll("body *"));
    const candidates = [];
    let serial = 0;
    for (const el of all) {
      if (!el || el === document.body || el === document.documentElement) continue;
      const cs = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const deltaY = Math.max(0, (el.scrollHeight || 0) - (el.clientHeight || 0));
      const deltaX = Math.max(0, (el.scrollWidth || 0) - (el.clientWidth || 0));
      const canScrollY = deltaY > 32 && /(auto|scroll|overlay|hidden|clip)/i.test(`${cs.overflowY} ${cs.overflow}`);
      const canScrollX = deltaX > 48 && /(auto|scroll|overlay|hidden|clip)/i.test(`${cs.overflowX} ${cs.overflow}`);
      if (!visible(el, rect, cs) || (!canScrollY && !canScrollX)) continue;
      const area = Math.round(rect.width * rect.height);
      const nameBlob = `${el.id || ""} ${classText(el)} ${el.getAttribute("role") || ""} ${el.getAttribute("aria-label") || ""}`;
      const namedBonus = /(main|content|scroll|panel|surface|viewport|screen|page|shell|table|list|grid|drawer|modal|dialog)/i.test(nameBlob) ? 250000 : 0;
      const score = deltaY * 10 + deltaX * 4 + Math.min(area, 500000) + namedBonus;
      const id = `${sessionId}-${serial++}`;
      const stable = selectorInfo(el);
      el.setAttribute("data-prisma-scroll-capture-id", id);
      candidates.push({
        id,
        selector: `[data-prisma-scroll-capture-id="${id}"]`,
        selectorGuess: stable.selector,
        selectorIndex: stable.index,
        tag: el.tagName.toLowerCase(),
        elementId: el.id || "",
        className: classText(el),
        role: el.getAttribute("role") || "",
        ariaLabel: el.getAttribute("aria-label") || "",
        overflowX: cs.overflowX,
        overflowY: cs.overflowY,
        rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
        clientWidth: el.clientWidth || 0,
        clientHeight: el.clientHeight || 0,
        scrollWidth: el.scrollWidth || 0,
        scrollHeight: el.scrollHeight || 0,
        scrollTop: el.scrollTop || 0,
        scrollLeft: el.scrollLeft || 0,
        deltaY,
        deltaX,
        score
      });
    }
    return candidates.sort((a, b) => b.score - a.score).slice(0, maxContainers);
  }, { maxContainers, sessionId });
}

async function resolveAndScrollContainer(page, container, y) {
  return page.evaluate(({ container, y }) => {
    function stableLookup() {
      if (!container.selectorGuess) return null;
      try {
        const matches = document.querySelectorAll(container.selectorGuess);
        return matches[container.selectorIndex] || matches[0] || null;
      } catch (_) {
        return null;
      }
    }
    let el = document.querySelector(container.selector);
    let resolvedBy = "capture-id";
    if (!el) {
      el = stableLookup();
      resolvedBy = "stable-selector";
    }
    if (!el || !el.isConnected) return { ok: false, reason: "container-detached" };
    el.setAttribute("data-prisma-scroll-capture-id", container.id);
    el.scrollTop = y;
    return {
      ok: true,
      resolvedBy,
      scrollTop: el.scrollTop,
      scrollLeft: el.scrollLeft,
      scrollHeight: el.scrollHeight,
      scrollWidth: el.scrollWidth,
      clientHeight: el.clientHeight,
      clientWidth: el.clientWidth
    };
  }, { container, y });
}

async function restoreScrollState(page, initialMetrics, containers) {
  await page.evaluate(({ initialMetrics, containers }) => {
    window.scrollTo(initialMetrics.scrollX || 0, initialMetrics.scrollY || 0);
    for (const c of containers || []) {
      let el = document.querySelector(c.selector);
      if (!el && c.selectorGuess) {
        try {
          const matches = document.querySelectorAll(c.selectorGuess);
          el = matches[c.selectorIndex] || matches[0] || null;
        } catch (_) {}
      }
      if (el) {
        el.scrollTop = c.scrollTop || 0;
        el.scrollLeft = c.scrollLeft || 0;
      }
    }
  }, { initialMetrics, containers }).catch(() => {});
}

async function cleanupCaptureAttributes(page, containers) {
  const ids = (containers || []).map(c => c.id).filter(Boolean);
  if (!ids.length) return;
  await page.evaluate(idsToRemove => {
    for (const id of idsToRemove) {
      const selector = `[data-prisma-scroll-capture-id="${String(id).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"]`;
      let el = null;
      try { el = document.querySelector(selector); } catch (_) {}
      if (el && el.getAttribute("data-prisma-scroll-capture-id") === id) {
        el.removeAttribute("data-prisma-scroll-capture-id");
      }
    }
  }, ids).catch(() => {});
}

function removeAttemptArtifacts(dir, base) {
  try {
    for (const name of fs.readdirSync(dir)) {
      if (name.startsWith(`${base}.page-tile-`) && name.endsWith(".png")) {
        try { fs.rmSync(path.join(dir, name), { force: true }); } catch (_) {}
      }
    }
  } catch (_) {}
  try { fs.rmSync(path.join(dir, `${base}.containers`), { recursive: true, force: true }); } catch (_) {}
}

async function capturePrimaryScreenshot(page, options) {
  const { path: shotPath, fullPage, timeout, coverage, stage, tracker, quietWindowMs, quietMaxMs, navigationRetries, targetMeta } = options;
  let lastError = null;
  for (let attempt = 0; attempt <= navigationRetries; attempt += 1) {
    const quiet = await quietDocument(page, tracker, quietWindowMs, quietMaxMs);
    if (!quiet) {
      lastError = new Error(`Document did not remain quiet before ${stage}`);
    } else {
      const epoch = tracker.snapshot();
      try {
        await page.screenshot({ path: shotPath, fullPage, timeout });
        if (tracker.changedSince(epoch)) {
          throw new CaptureInterruptedError("navigation", `Navigation occurred during ${stage}`, { stage });
        }
        if (attempt > 0) coverage.recoveries.push({ stage, attempt, reason: "navigation-retry-succeeded" });
        return shotPath;
      } catch (error) {
        lastError = error;
        if (!isNavigationLikeError(error) && !(error instanceof CaptureInterruptedError)) break;
      }
    }
    if (attempt < navigationRetries) {
      coverage.recoveries.push({ stage, attempt: attempt + 1, reason: "navigation-retry" });
      emitProgress("capture-retry", { targetMeta, index: attempt + 1, total: navigationRetries, message: `${stage}: navigation recovery` });
      await page.waitForTimeout(250 * (attempt + 1)).catch(() => {});
    }
  }
  coverage.errors.push({ stage, message: formatShotError(lastError || new Error(`${stage} failed`)) });
  return null;
}

async function captureDeepAttempt(page, context) {
  const {
    coverage, targetMeta, dir, base, tracker, startedAt, captureBudgetMs,
    maxPageTiles, maxScrollContainers, maxContainerTiles, tileOverlap,
    tileSettleMs, containerOperationTimeoutMs, maxConsecutiveContainerErrors,
    attempt
  } = context;

  assertBudget(startedAt, captureBudgetMs, `attempt-${attempt}-start`);
  const quiet = await quietDocument(page, tracker, context.quietWindowMs, context.quietMaxMs);
  if (!quiet) throw new CaptureInterruptedError("navigation", "Document did not reach a quiet navigation window", { attempt });
  const attemptEpoch = tracker.snapshot();
  const ensureStable = stage => {
    assertBudget(startedAt, captureBudgetMs, stage);
    if (page.isClosed()) throw new CaptureInterruptedError("navigation", `Page closed during ${stage}`, { stage, attempt });
    if (tracker.changedSince(attemptEpoch)) throw new CaptureInterruptedError("navigation", `Main frame navigated during ${stage}`, { stage, attempt });
  };

  removeAttemptArtifacts(dir, base);
  coverage.pageTiles = [];
  coverage.scrollContainers = [];
  coverage.pageTilePlan = null;
  coverage.scrollContainerDiscovery = null;

  ensureStable("page-metrics");
  const metrics = await getDocumentMetrics(page).catch(error => {
    if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "page-metrics", attempt });
    throw error;
  });
  ensureStable("page-metrics-after");
  const pageMaxY = Math.max(0, (metrics.scrollHeight || 0) - (metrics.viewportHeight || 0));
  const plan = uniqueSortedPositions(pageMaxY, metrics.viewportHeight || 1, tileOverlap, maxPageTiles);
  coverage.pageTilePlan = {
    expected: plan.expected,
    produced: plan.positions.length,
    truncated: plan.truncated,
    maxScrollY: pageMaxY,
    viewportHeight: metrics.viewportHeight || 0,
    documentHeight: metrics.scrollHeight || 0,
    attempt
  };
  if (plan.truncated) coverage.partial = true;

  coverage.currentStage = "page-tiles";
  let idx = 0;
  for (const y of plan.positions) {
    idx += 1;
    ensureStable(`page-tile-${idx}-before`);
    emitProgress("page-tile", { targetMeta, index: idx, total: plan.positions.length, y, message: `${base} page tile ${idx}/${plan.positions.length}` });
    const shotPath = path.join(dir, `${base}.page-tile-${String(idx).padStart(3, "0")}-y${String(y).padStart(5, "0")}.png`);
    try {
      await page.evaluate(scrollY => window.scrollTo(0, scrollY), y);
    } catch (error) {
      if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "page-scroll", y, attempt });
      throw error;
    }
    await page.waitForTimeout(tileSettleMs).catch(() => {});
    ensureStable(`page-tile-${idx}-screenshot`);
    try {
      await page.screenshot({ path: shotPath, fullPage: false, timeout: containerOperationTimeoutMs });
      coverage.pageTiles.push({ index: idx, y, path: shotPath, attempt });
    } catch (error) {
      if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "page-screenshot", y, attempt });
      coverage.errors.push({ stage: "page-screenshot", y, message: formatShotError(error) });
      coverage.partial = true;
    }
    ensureStable(`page-tile-${idx}-after`);
  }

  coverage.currentStage = "container-discovery";
  emitProgress("container-discovery", { targetMeta, message: base });
  const sessionId = `prisma-scroll-${Date.now()}-${Math.random().toString(36).slice(2, 10)}-a${attempt}`;
  let containers;
  try {
    containers = await discoverScrollContainers(page, maxScrollContainers, sessionId);
  } catch (error) {
    if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "container-discovery", attempt });
    throw error;
  }
  ensureStable("container-discovery-after");
  coverage.scrollContainerDiscovery = { selected: containers.length, maxScrollContainers, attempt };

  let containerIndex = 0;
  for (const c of containers) {
    containerIndex += 1;
    ensureStable(`container-${containerIndex}-start`);
    const containerBase = `${base}.container-${String(containerIndex).padStart(2, "0")}-${safeName(c.selectorGuess || c.id)}`;
    const containerDir = path.join(dir, `${base}.containers`);
    ensureDir(containerDir);
    const maxY = Math.max(0, (c.scrollHeight || 0) - (c.clientHeight || 0));
    const cPlan = uniqueSortedPositions(maxY, c.clientHeight || c.rect.height || 1, tileOverlap, maxContainerTiles);
    const cRecord = {
      index: containerIndex,
      id: c.id,
      selector: c.selector,
      selectorGuess: c.selectorGuess,
      selectorIndex: c.selectorIndex,
      tag: c.tag,
      elementId: c.elementId,
      className: c.className,
      role: c.role,
      ariaLabel: c.ariaLabel,
      overflowX: c.overflowX,
      overflowY: c.overflowY,
      rect: c.rect,
      clientWidth: c.clientWidth,
      clientHeight: c.clientHeight,
      scrollWidth: c.scrollWidth,
      scrollHeight: c.scrollHeight,
      deltaY: c.deltaY,
      deltaX: c.deltaX,
      tilePlan: { expected: cPlan.expected, produced: cPlan.positions.length, truncated: cPlan.truncated },
      tiles: [],
      errors: [],
      attempt
    };
    if (cPlan.truncated) coverage.partial = true;
    let tileIndex = 0;
    let consecutiveErrors = 0;
    for (const y of cPlan.positions) {
      tileIndex += 1;
      ensureStable(`container-${containerIndex}-tile-${tileIndex}-before`);
      coverage.currentStage = `container-${containerIndex}-tile-${tileIndex}`;
      emitProgress("container-tile", { targetMeta, index: tileIndex, total: cPlan.positions.length, y, message: `${base} container ${containerIndex}/${containers.length} tile ${tileIndex}/${cPlan.positions.length} ${c.selectorGuess || c.id}` });
      const shotPath = path.join(containerDir, `${containerBase}-tile-${String(tileIndex).padStart(3, "0")}-y${String(y).padStart(5, "0")}.png`);
      let scrolled;
      try {
        scrolled = await resolveAndScrollContainer(page, c, y);
      } catch (error) {
        if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "container-scroll", y, attempt });
        throw error;
      }
      if (!scrolled || !scrolled.ok) {
        throw new CaptureInterruptedError("dom-changed", `Scroll container disappeared: ${c.selectorGuess || c.selector}`, { stage: "container-scroll", y, attempt, container: c.selectorGuess || c.selector });
      }
      await page.waitForTimeout(tileSettleMs).catch(() => {});
      ensureStable(`container-${containerIndex}-tile-${tileIndex}-handle`);
      let handle = null;
      try {
        handle = await page.$(c.selector);
        if (!handle) throw new CaptureInterruptedError("dom-changed", `Scroll container handle disappeared: ${c.selectorGuess || c.selector}`, { stage: "container-handle", y, attempt });
        await handle.scrollIntoViewIfNeeded({ timeout: containerOperationTimeoutMs }).catch(error => {
          if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "container-scroll-into-view", y, attempt });
        });
        ensureStable(`container-${containerIndex}-tile-${tileIndex}-screenshot`);
        await handle.screenshot({ path: shotPath, timeout: containerOperationTimeoutMs });
        ensureStable(`container-${containerIndex}-tile-${tileIndex}-after`);
        cRecord.tiles.push({ index: tileIndex, y, actualScrollTop: scrolled.scrollTop, path: shotPath, resolvedBy: scrolled.resolvedBy, attempt });
        consecutiveErrors = 0;
      } catch (error) {
        if (error instanceof CaptureInterruptedError) throw error;
        if (isNavigationLikeError(error)) throw new CaptureInterruptedError("navigation", formatShotError(error), { stage: "container-screenshot", y, attempt });
        const message = formatShotError(error);
        cRecord.errors.push({ stage: "container-screenshot", y, message });
        coverage.errors.push({ stage: "container-screenshot", selector: c.selectorGuess || c.selector, y, message });
        coverage.partial = true;
        consecutiveErrors += 1;
        if (consecutiveErrors >= maxConsecutiveContainerErrors) break;
      } finally {
        if (handle) await handle.dispose().catch(() => {});
      }
    }
    coverage.scrollContainers.push(cRecord);
  }

  return containers;
}

async function captureDeepScreenshots(page, options) {
  const captureScreenshots = options.captureScreenshots !== false;
  const timeout = asInt(options.timeout, 15000, 1000, 180000);
  const deepScroll = Boolean(options.deepScroll);
  const fullPage = Boolean(options.fullPage || deepScroll);
  const maxPageTiles = asInt(options.maxPageTiles, 180, 1, 1000);
  const maxScrollContainers = asInt(options.maxScrollContainers, 36, 0, 300);
  const maxContainerTiles = asInt(options.maxContainerTiles, 120, 1, 1000);
  const tileOverlap = asInt(options.tileOverlap, 80, 0, 1000);
  const settleMs = asInt(options.settleMs, 120, 0, 5000);
  const tileSettleMs = asInt(options.tileSettleMs, Math.min(settleMs, 250), 0, 5000);
  const captureBudgetMs = asInt(options.captureBudgetMs, 240000, 15000, 3600000);
  const containerOperationTimeoutMs = asInt(options.containerOperationTimeoutMs, Math.min(timeout, 5000), 500, 60000);
  const navigationRetries = asInt(options.navigationRetries, 3, 0, 10);
  const quietWindowMs = asInt(options.quietWindowMs, Math.max(750, Math.min(1500, settleMs + 300)), 100, 10000);
  const quietMaxMs = asInt(options.quietMaxMs, 10000, 500, 60000);
  const maxConsecutiveContainerErrors = asInt(options.maxConsecutiveContainerErrors, 2, 1, 20);
  const targetMeta = options.targetMeta || {};
  const startedAt = Date.now();
  emitProgress("capture-start", { targetMeta, message: options.fileBase || "capture" });
  const fallbackDir = options.outDir || process.cwd();
  const { dir, base } = fileParts(options.legacyPath, options.fileBase, fallbackDir);

  const coverage = {
    version: "deep-capture-v2-navigation-safe",
    enabled: captureScreenshots,
    deepScroll,
    fullPage,
    status: captureScreenshots ? "running" : "disabled",
    partial: false,
    currentStage: "init",
    legacyScreenshot: null,
    viewportScreenshot: null,
    fullPageScreenshot: null,
    pageTiles: [],
    scrollContainers: [],
    errors: [],
    warnings: [],
    recoveries: [],
    navigationEvents: [],
    limits: {
      maxPageTiles,
      maxScrollContainers,
      maxContainerTiles,
      tileOverlap,
      captureBudgetMs,
      containerOperationTimeoutMs,
      navigationRetries,
      quietWindowMs,
      quietMaxMs,
      settleMs,
      tileSettleMs,
      maxConsecutiveContainerErrors
    },
    metricsBefore: null,
    metricsAfter: null,
    capturedAt: new Date().toISOString()
  };

  if (!captureScreenshots) {
    delete coverage.currentStage;
    coverage.timings = { elapsedMs: Date.now() - startedAt, captureBudgetMs };
    return coverage;
  }

  const tracker = createNavigationTracker(page);
  let initialMetrics = { scrollX: 0, scrollY: 0, viewportWidth: 0, viewportHeight: 0, scrollWidth: 0, scrollHeight: 0 };
  let containers = [];
  try {
    initialMetrics = await getDocumentMetrics(page).catch(error => {
      coverage.errors.push({ stage: "metrics-before", message: formatShotError(error) });
      return initialMetrics;
    });
    coverage.metricsBefore = initialMetrics;

    const legacyPath = options.legacyPath || path.join(dir, `${base}.png`);
    const viewportPath = path.join(dir, `${base}.viewport.png`);
    const fullPagePath = path.join(dir, `${base}.fullpage.png`);

    coverage.currentStage = "legacy";
    emitProgress("screenshot-legacy", { targetMeta, message: base });
    coverage.legacyScreenshot = await capturePrimaryScreenshot(page, {
      path: legacyPath,
      fullPage,
      timeout,
      coverage,
      stage: "legacy",
      tracker,
      quietWindowMs,
      quietMaxMs,
      navigationRetries,
      targetMeta
    });

    coverage.currentStage = "viewport";
    emitProgress("screenshot-viewport", { targetMeta, message: base });
    await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
    await page.waitForTimeout(settleMs).catch(() => {});
    coverage.viewportScreenshot = await capturePrimaryScreenshot(page, {
      path: viewportPath,
      fullPage: false,
      timeout,
      coverage,
      stage: "viewport",
      tracker,
      quietWindowMs,
      quietMaxMs,
      navigationRetries,
      targetMeta
    });

    if (fullPage) {
      coverage.currentStage = "fullpage";
      emitProgress("screenshot-fullpage", { targetMeta, message: base });
      if (coverage.legacyScreenshot && fullPage) {
        try {
          fs.copyFileSync(coverage.legacyScreenshot, fullPagePath);
          coverage.fullPageScreenshot = fullPagePath;
          coverage.warnings.push({ stage: "fullpage", message: "Reused the identical legacy full-page capture to avoid duplicate browser work." });
        } catch (error) {
          coverage.fullPageScreenshot = await capturePrimaryScreenshot(page, {
            path: fullPagePath,
            fullPage: true,
            timeout,
            coverage,
            stage: "fullpage",
            tracker,
            quietWindowMs,
            quietMaxMs,
            navigationRetries,
            targetMeta
          });
        }
      } else {
        coverage.fullPageScreenshot = await capturePrimaryScreenshot(page, {
          path: fullPagePath,
          fullPage: true,
          timeout,
          coverage,
          stage: "fullpage",
          tracker,
          quietWindowMs,
          quietMaxMs,
          navigationRetries,
          targetMeta
        });
      }
    }

    if (deepScroll) {
      let completed = false;
      let lastInterruption = null;
      for (let attempt = 1; attempt <= navigationRetries + 1; attempt += 1) {
        try {
          containers = await captureDeepAttempt(page, {
            coverage,
            targetMeta,
            dir,
            base,
            tracker,
            startedAt,
            captureBudgetMs,
            maxPageTiles,
            maxScrollContainers,
            maxContainerTiles,
            tileOverlap,
            settleMs,
            tileSettleMs,
            containerOperationTimeoutMs,
            navigationRetries,
            quietWindowMs,
            quietMaxMs,
            maxConsecutiveContainerErrors,
            attempt
          });
          completed = true;
          if (attempt > 1) coverage.recoveries.push({ stage: "deep-scroll", attempt, reason: "deep-capture-retry-succeeded" });
          break;
        } catch (error) {
          lastInterruption = error;
          const retryable = error instanceof CaptureInterruptedError && ["navigation", "dom-changed"].includes(error.kind);
          if (retryable && attempt <= navigationRetries && !deadlineState(startedAt, captureBudgetMs).expired) {
            coverage.recoveries.push({ stage: "deep-scroll", attempt, reason: error.kind, message: formatShotError(error), details: error.details || null });
            emitProgress("capture-retry", { targetMeta, index: attempt, total: navigationRetries, message: `${error.kind}: restarting deep capture from a clean DOM` });
            await cleanupCaptureAttributes(page, containers);
            containers = [];
            removeAttemptArtifacts(dir, base);
            await page.waitForTimeout(300 * attempt).catch(() => {});
            continue;
          }
          break;
        }
      }
      if (!completed) {
        coverage.partial = true;
        const kind = lastInterruption instanceof CaptureInterruptedError ? lastInterruption.kind : "deep-capture";
        coverage.errors.push({
          stage: "deep-capture",
          kind,
          message: formatShotError(lastInterruption || new Error("Deep capture did not complete")),
          details: lastInterruption && lastInterruption.details ? lastInterruption.details : null
        });
      }
    }
  } catch (error) {
    coverage.partial = true;
    coverage.errors.push({ stage: "capture-unhandled", message: formatShotError(error) });
  } finally {
    await restoreScrollState(page, initialMetrics, containers);
    await cleanupCaptureAttributes(page, containers);
    coverage.metricsAfter = await getDocumentMetrics(page).catch(() => null);
    coverage.navigationEvents = tracker.events.slice();
    tracker.dispose();
  }

  delete coverage.currentStage;
  const hardErrors = coverage.errors.filter(error => !error.recovered);
  if (hardErrors.length > 0 && !coverage.legacyScreenshot && !coverage.viewportScreenshot && !coverage.fullPageScreenshot) {
    coverage.status = "failed";
  } else if (coverage.partial || hardErrors.length > 0) {
    coverage.status = "partial";
  } else {
    coverage.status = "complete";
  }
  coverage.counts = {
    legacy: coverage.legacyScreenshot ? 1 : 0,
    viewport: coverage.viewportScreenshot ? 1 : 0,
    fullPage: coverage.fullPageScreenshot ? 1 : 0,
    pageTiles: coverage.pageTiles.length,
    scrollContainers: coverage.scrollContainers.length,
    containerTiles: coverage.scrollContainers.reduce((sum, c) => sum + (Array.isArray(c.tiles) ? c.tiles.length : 0), 0),
    errors: coverage.errors.length,
    warnings: coverage.warnings.length,
    recoveries: coverage.recoveries.length,
    navigationEvents: coverage.navigationEvents.length
  };
  coverage.timings = { elapsedMs: Date.now() - startedAt, captureBudgetMs };
  emitProgress("capture-done", { targetMeta, message: `${base} status=${coverage.status} recoveries=${coverage.recoveries.length}` });
  return coverage;
}

function envDeepCaptureOptions(overrides = {}) {
  const mode = String(process.env.PRISMA_SURF_DEEP_SCROLL || "1").trim().toLowerCase();
  return {
    deepScroll: mode !== "0" && mode !== "off" && mode !== "false" && mode !== "no",
    fullPage: asBool(process.env.PRISMA_SURF_FULLPAGE, true),
    maxPageTiles: asInt(process.env.PRISMA_SURF_MAX_PAGE_TILES, 180, 1, 1000),
    maxScrollContainers: asInt(process.env.PRISMA_SURF_MAX_SCROLL_CONTAINERS, 36, 0, 300),
    maxContainerTiles: asInt(process.env.PRISMA_SURF_MAX_CONTAINER_TILES, 120, 1, 1000),
    tileOverlap: asInt(process.env.PRISMA_SURF_TILE_OVERLAP_PX, 80, 0, 1000),
    captureBudgetMs: asInt(process.env.PRISMA_SURF_CAPTURE_BUDGET_MS, 240000, 15000, 3600000),
    containerOperationTimeoutMs: asInt(process.env.PRISMA_SURF_CONTAINER_OPERATION_TIMEOUT_MS, 5000, 500, 60000),
    navigationRetries: asInt(process.env.PRISMA_SURF_NAVIGATION_RETRIES, 3, 0, 10),
    quietWindowMs: asInt(process.env.PRISMA_SURF_NAVIGATION_QUIET_MS, 1000, 100, 10000),
    quietMaxMs: asInt(process.env.PRISMA_SURF_NAVIGATION_QUIET_MAX_MS, 10000, 500, 60000),
    tileSettleMs: asInt(process.env.PRISMA_SURF_TILE_SETTLE_MS, 220, 0, 5000),
    maxConsecutiveContainerErrors: asInt(process.env.PRISMA_SURF_MAX_CONTAINER_ERRORS, 2, 1, 20),
    ...overrides,
  };
}

module.exports = {
  captureDeepScreenshots,
  envDeepCaptureOptions,
  safeName,
  uniqueSortedPositions,
  emitProgress,
  isNavigationLikeError
};
