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
  const ov = Math.max(0, Math.min(view - 1, Math.floor(overlap || 0)));
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

async function maybeScreenshot(task, coverage, bucket) {
  try {
    const out = await task();
    if (bucket && out) bucket.push(out);
    return out;
  } catch (error) {
    coverage.errors.push({ stage: coverage.currentStage || "screenshot", message: formatShotError(error) });
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

async function discoverScrollContainers(page, maxContainers) {
  return page.evaluate(({ maxContainers }) => {
    function classText(el) {
      const raw = el && el.getAttribute ? el.getAttribute("class") : "";
      return typeof raw === "string" ? raw : "";
    }
    function selectorGuess(el) {
      if (!el || !el.tagName) return "";
      if (el.id) return `#${CSS.escape(el.id)}`;
      const attr = el.getAttribute("data-testid") || el.getAttribute("data-test") || el.getAttribute("data-prisma-route") || el.getAttribute("aria-label") || el.getAttribute("role");
      const tag = el.tagName.toLowerCase();
      if (attr) return `${tag}[${attr.length < 80 ? `*="${String(attr).replace(/"/g, "")}"` : ""}]`;
      const cls = classText(el).split(/\s+/).filter(Boolean).slice(0, 3).join(".");
      return cls ? `${tag}.${cls}` : tag;
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
      const id = `prisma-scroll-${Date.now()}-${serial++}`;
      el.setAttribute("data-prisma-scroll-capture-id", id);
      candidates.push({
        id,
        selector: `[data-prisma-scroll-capture-id="${id}"]`,
        selectorGuess: selectorGuess(el),
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
  }, { maxContainers });
}

async function restoreScrollState(page, initialMetrics, containers) {
  await page.evaluate(({ initialMetrics, containers }) => {
    window.scrollTo(initialMetrics.scrollX || 0, initialMetrics.scrollY || 0);
    for (const c of containers || []) {
      const el = document.querySelector(c.selector);
      if (el) {
        el.scrollTop = c.scrollTop || 0;
        el.scrollLeft = c.scrollLeft || 0;
      }
    }
  }, { initialMetrics, containers }).catch(() => {});
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
  const targetMeta = options.targetMeta || {};
  emitProgress("capture-start", { targetMeta, message: options.fileBase || "capture" });
  const fallbackDir = options.outDir || process.cwd();
  const { dir, base } = fileParts(options.legacyPath, options.fileBase, fallbackDir);

  const coverage = {
    version: "deep-capture-v1",
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
    limits: { maxPageTiles, maxScrollContainers, maxContainerTiles, tileOverlap },
    metricsBefore: null,
    metricsAfter: null,
    capturedAt: new Date().toISOString()
  };

  if (!captureScreenshots) {
    delete coverage.currentStage;
    return coverage;
  }

  const initialMetrics = await getDocumentMetrics(page).catch(error => {
    coverage.errors.push({ stage: "metrics-before", message: formatShotError(error) });
    return { scrollX: 0, scrollY: 0, viewportWidth: 0, viewportHeight: 0, scrollWidth: 0, scrollHeight: 0 };
  });
  coverage.metricsBefore = initialMetrics;

  const legacyPath = options.legacyPath || path.join(dir, `${base}.png`);
  const viewportPath = path.join(dir, `${base}.viewport.png`);
  const fullPagePath = path.join(dir, `${base}.fullpage.png`);

  coverage.currentStage = "legacy";
  emitProgress("screenshot-legacy", { targetMeta, message: base });
  await maybeScreenshot(async () => {
    await page.screenshot({ path: legacyPath, fullPage, timeout });
    coverage.legacyScreenshot = legacyPath;
    return legacyPath;
  }, coverage);

  coverage.currentStage = "viewport";
  emitProgress("screenshot-viewport", { targetMeta, message: base });
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
  await page.waitForTimeout(settleMs).catch(() => {});
  await maybeScreenshot(async () => {
    await page.screenshot({ path: viewportPath, fullPage: false, timeout });
    coverage.viewportScreenshot = viewportPath;
    return viewportPath;
  }, coverage);

  if (fullPage) {
    coverage.currentStage = "fullpage";
    emitProgress("screenshot-fullpage", { targetMeta, message: base });
    await maybeScreenshot(async () => {
      await page.screenshot({ path: fullPagePath, fullPage: true, timeout });
      coverage.fullPageScreenshot = fullPagePath;
      return fullPagePath;
    }, coverage);
  }

  let containers = [];
  if (deepScroll) {
    const metrics = await getDocumentMetrics(page).catch(() => initialMetrics);
    const pageMaxY = Math.max(0, (metrics.scrollHeight || 0) - (metrics.viewportHeight || 0));
    const plan = uniqueSortedPositions(pageMaxY, metrics.viewportHeight || 1, tileOverlap, maxPageTiles);
    coverage.pageTilePlan = {
      expected: plan.expected,
      produced: plan.positions.length,
      truncated: plan.truncated,
      maxScrollY: pageMaxY,
      viewportHeight: metrics.viewportHeight || 0,
      documentHeight: metrics.scrollHeight || 0
    };
    if (plan.truncated) coverage.partial = true;

    coverage.currentStage = "page-tiles";
    let idx = 0;
    for (const y of plan.positions) {
      idx += 1;
      emitProgress("page-tile", { targetMeta, index: idx, total: plan.positions.length, y, message: `${base} page tile ${idx}/${plan.positions.length}` });
      const shotPath = path.join(dir, `${base}.page-tile-${String(idx).padStart(3, "0")}-y${String(y).padStart(5, "0")}.png`);
      await page.evaluate(scrollY => window.scrollTo(0, scrollY), y).catch(error => {
        coverage.errors.push({ stage: "page-scroll", y, message: formatShotError(error) });
      });
      await page.waitForTimeout(settleMs).catch(() => {});
      await maybeScreenshot(async () => {
        await page.screenshot({ path: shotPath, fullPage: false, timeout });
        const entry = { index: idx, y, path: shotPath };
        coverage.pageTiles.push(entry);
        return entry;
      }, coverage);
    }

    coverage.currentStage = "container-discovery";
    emitProgress("container-discovery", { targetMeta, message: base });
    containers = await discoverScrollContainers(page, maxScrollContainers).catch(error => {
      coverage.errors.push({ stage: "container-discovery", message: formatShotError(error) });
      return [];
    });
    coverage.scrollContainerDiscovery = {
      selected: containers.length,
      maxScrollContainers
    };

    let containerIndex = 0;
    for (const c of containers) {
      containerIndex += 1;
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
        errors: []
      };
      if (cPlan.truncated) coverage.partial = true;
      let tileIndex = 0;
      for (const y of cPlan.positions) {
        tileIndex += 1;
        coverage.currentStage = `container-${containerIndex}-tile-${tileIndex}`;
        emitProgress("container-tile", { targetMeta, index: tileIndex, total: cPlan.positions.length, y, message: `${base} container ${containerIndex}/${containers.length} tile ${tileIndex}/${cPlan.positions.length} ${c.selectorGuess || c.id}` });
        const shotPath = path.join(containerDir, `${containerBase}-tile-${String(tileIndex).padStart(3, "0")}-y${String(y).padStart(5, "0")}.png`);
        const scrolled = await page.locator(c.selector).first().evaluate((el, yValue) => {
          el.scrollTop = yValue;
          return { scrollTop: el.scrollTop, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight };
        }, y).catch(error => {
          const msg = formatShotError(error);
          cRecord.errors.push({ stage: "container-scroll", y, message: msg });
          coverage.errors.push({ stage: "container-scroll", selector: c.selectorGuess || c.selector, y, message: msg });
          return null;
        });
        await page.locator(c.selector).first().scrollIntoViewIfNeeded({ timeout: Math.min(timeout, 5000) }).catch(() => {});
        await page.waitForTimeout(settleMs).catch(() => {});
        if (!scrolled) continue;
        try {
          await page.locator(c.selector).first().screenshot({ path: shotPath, timeout });
          const entry = { index: tileIndex, y, actualScrollTop: scrolled.scrollTop, path: shotPath };
          cRecord.tiles.push(entry);
        } catch (error) {
          const msg = formatShotError(error);
          cRecord.errors.push({ stage: "container-screenshot", y, message: msg });
          coverage.errors.push({ stage: "container-screenshot", selector: c.selectorGuess || c.selector, y, message: msg });
        }
      }
      coverage.scrollContainers.push(cRecord);
    }
  }

  await restoreScrollState(page, initialMetrics, containers);
  coverage.metricsAfter = await getDocumentMetrics(page).catch(() => null);
  emitProgress("capture-done", { targetMeta, message: `${base} status=${coverage.status || "unknown"}` });
  delete coverage.currentStage;

  const hardErrors = coverage.errors.filter(e => !/Timeout.*networkidle/i.test(String(e.message || "")));
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
    errors: coverage.errors.length
  };
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
    ...overrides,
  };
}

module.exports = { captureDeepScreenshots, envDeepCaptureOptions, safeName, uniqueSortedPositions, emitProgress };
