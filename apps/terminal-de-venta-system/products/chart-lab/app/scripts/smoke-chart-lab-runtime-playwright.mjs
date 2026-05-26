// PRISMA_CHART_LAB_RUNTIME_PLAYWRIGHT_SMOKE_V1
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const timestamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "_");
const evidenceRoot = "F:\\descargasf";
const forbiddenRuntimeText = [
  "Hydration failed",
  "Recoverable Error",
  "Text content did not match",
  "server rendered",
  "client rendered",
  "Unhandled Runtime Error",
  "TypeError",
  "ReferenceError",
  "Failed to lookup task type",
  "panicked at"
];

function argValue(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] ?? fallback : fallback;
}

function loadPlaywright() {
  const roots = [process.cwd(), path.resolve(process.cwd(), "apps/keystone"), path.resolve(process.cwd(), "..")];
  for (const root of roots) {
    try {
      const requireFromRoot = createRequire(path.join(root, "package.json"));
      return requireFromRoot("playwright");
    } catch {
      try {
        const requireFromRoot = createRequire(path.join(root, "package.json"));
        return requireFromRoot("@playwright/test");
      } catch {
        // Try the next workspace root.
      }
    }
  }
  throw new Error("Playwright is not resolvable. Run through an existing workspace with @playwright/test, for example pnpm -C apps/keystone exec node <script>.");
}

const label = argValue("--label", "local");
const url = argValue("--url", "http://127.0.0.1:3000/");
const timeoutMs = Number(argValue("--timeout-ms", "90000"));
const reportPath = argValue("--out", path.join(evidenceRoot, `chart_lab_${label}_runtime_smoke_${timestamp}.json`));
const screenshotDir = argValue("--screenshot-dir", path.join(evidenceRoot, `chart_lab_${label}_runtime_smoke_${timestamp}_screenshots`));

fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.mkdirSync(screenshotDir, { recursive: true });

function fail(assertions, message, details = {}) {
  assertions.push({ status: "FAIL", message, details });
}

function pass(assertions, message, details = {}) {
  assertions.push({ status: "PASS", message, details });
}

function containsForbidden(text) {
  return forbiddenRuntimeText.find((needle) => text.includes(needle));
}

async function checkViewport(page, viewport, assertions, screenshots) {
  await page.setViewportSize({ width: viewport.width, height: viewport.height });
  await page.waitForTimeout(250);
  const screenshotPath = path.join(screenshotDir, `${label}-${viewport.name}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  screenshots.push(screenshotPath);

  const metrics = await page.evaluate(async () => {
    const root = document.documentElement;
    const body = document.body;
    const maxScrollWidth = Math.max(root.scrollWidth, body.scrollWidth);
    const viewportWidth = window.innerWidth;
    const scrollHeight = Math.max(root.scrollHeight, body.scrollHeight);
    const viewportHeight = window.innerHeight;
    const scroller = document.scrollingElement ?? document.documentElement;
    const before = scroller.scrollTop;
    scroller.scrollTo({ top: before + 260, behavior: "instant" });
    await new Promise((resolve) => setTimeout(resolve, 120));
    const afterProgrammatic = scroller.scrollTop;
    scroller.scrollTo({ top: before, behavior: "instant" });
    await new Promise((resolve) => setTimeout(resolve, 40));
    const blockingOverlays = [...document.querySelectorAll(".lab-echart__visibility-warning, .studio-mobile-actions__panel, .clipboard-fallback-panel")]
      .map((node) => {
        const style = window.getComputedStyle(node);
        const rect = node.getBoundingClientRect();
        return {
          className: node instanceof HTMLElement ? node.className : "",
          pointerEvents: style.pointerEvents,
          visible: rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden"
        };
      })
      .filter((item) => item.visible && item.pointerEvents !== "none");
    return {
      maxScrollWidth,
      viewportWidth,
      scrollHeight,
      viewportHeight,
      canScrollVertically: scrollHeight <= viewportHeight + 2 || afterProgrammatic > before,
      blockingOverlays
    };
  });

  if (metrics.maxScrollWidth <= metrics.viewportWidth + 2) {
    pass(assertions, `${viewport.name}: no global horizontal overflow`, metrics);
  } else {
    fail(assertions, `${viewport.name}: global horizontal overflow`, metrics);
  }

  if (metrics.canScrollVertically) {
    pass(assertions, `${viewport.name}: vertical scroll remains usable`, metrics);
  } else {
    fail(assertions, `${viewport.name}: vertical scroll is trapped`, metrics);
  }

  if (!metrics.blockingOverlays.length) {
    pass(assertions, `${viewport.name}: overlays do not block scroll`, metrics);
  } else {
    fail(assertions, `${viewport.name}: overlay can block scroll`, metrics);
  }
}

async function main() {
  const assertions = [];
  const screenshots = [];
  const consoleMessages = [];
  const pageErrors = [];
  const forbiddenMessages = [];
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });

  page.on("console", (message) => {
    const entry = { type: message.type(), text: message.text() };
    consoleMessages.push(entry);
    const forbidden = containsForbidden(entry.text);
    if (forbidden || entry.type === "error") forbiddenMessages.push({ ...entry, forbidden });
  });
  page.on("pageerror", (error) => {
    const text = error instanceof Error ? error.stack ?? error.message : String(error);
    pageErrors.push(text);
    forbiddenMessages.push({ type: "pageerror", text, forbidden: containsForbidden(text) ?? "pageerror" });
  });

  try {
    const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
    if (response?.status() === 200) pass(assertions, "HTTP 200", { status: response.status() });
    else fail(assertions, "HTTP 200", { status: response?.status() ?? null });

    await page.waitForSelector('main[data-power-studio="true"]', { timeout: timeoutMs });
    await page.waitForSelector('main[data-hydration-safe="true"]', { timeout: timeoutMs });
    await page.waitForSelector(".lab-echart__canvas", { timeout: timeoutMs });
    await page.waitForFunction(() => (document.body.textContent ?? "").includes("PRISMA Chart Lab"), null, { timeout: timeoutMs });
    await page.waitForFunction(() => Boolean(document.querySelector(".lab-echart__canvas canvas, .lab-echart__canvas svg")), null, { timeout: timeoutMs });

    pass(assertions, 'main[data-power-studio="true"] exists');
    pass(assertions, 'main[data-hydration-safe="true"] exists');
    pass(assertions, ".lab-echart__canvas exists");
    pass(assertions, "canvas or svg exists inside chart area");
    pass(assertions, 'body contains "PRISMA Chart Lab"');

    const dom = await page.evaluate((forbiddenText) => {
      const bodyText = document.body.textContent ?? "";
      const wrapper = document.querySelector("[data-chart-suspected-blank]");
      const suspectedBlank = wrapper?.getAttribute("data-chart-suspected-blank") === "true";
      const visibilityWarning = Boolean(document.querySelector(".lab-echart__visibility-warning"));
      const emptyState = /empty|no data|missing data|sin datos/i.test(bodyText);
      const canvas = document.querySelector(".lab-echart__canvas canvas");
      let pixelSignal = null;
      if (canvas instanceof HTMLCanvasElement && canvas.width > 0 && canvas.height > 0) {
        try {
          const context = canvas.getContext("2d");
          const width = Math.min(canvas.width, 220);
          const height = Math.min(canvas.height, 160);
          const image = context?.getImageData(0, 0, width, height);
          if (image) {
            let colored = 0;
            let transparent = 0;
            for (let index = 0; index < image.data.length; index += 16) {
              const r = image.data[index];
              const g = image.data[index + 1];
              const b = image.data[index + 2];
              const a = image.data[index + 3];
              if (a < 8) transparent += 1;
              if (a > 8 && (Math.abs(r - g) > 6 || Math.abs(g - b) > 6 || Math.abs(r - b) > 6)) colored += 1;
            }
            pixelSignal = { colored, transparent, samples: Math.floor(image.data.length / 16) };
          }
        } catch (error) {
          pixelSignal = { error: error instanceof Error ? error.message : String(error) };
        }
      }
      return {
        forbiddenBodyText: forbiddenText.filter((needle) => bodyText.includes(needle)),
        suspectedBlank,
        visibilityWarning,
        emptyState,
        pixelSignal
      };
    }, forbiddenRuntimeText);

    if (!dom.forbiddenBodyText.length) pass(assertions, "body does not contain hydration/runtime overlay text", dom);
    else fail(assertions, "body contains hydration/runtime overlay text", dom);

    const hasPixelSignal = Boolean(dom.pixelSignal && "colored" in dom.pixelSignal && dom.pixelSignal.colored > 10);
    if (!dom.suspectedBlank || dom.visibilityWarning || dom.emptyState || hasPixelSignal) {
      pass(assertions, "chart is not a silent gray blank", dom);
    } else {
      fail(assertions, "chart appears to be a silent gray blank", dom);
    }

    for (const viewport of [
      { name: "desktop", width: 1366, height: 900 },
      { name: "tablet", width: 768, height: 1024 },
      { name: "mobile", width: 390, height: 844 }
    ]) {
      await checkViewport(page, viewport, assertions, screenshots);
    }

    if (!forbiddenMessages.length) pass(assertions, "no forbidden console/page errors");
    else fail(assertions, "forbidden console/page errors", { forbiddenMessages });
  } catch (error) {
    fail(assertions, "Playwright smoke execution failed", { error: error instanceof Error ? error.stack ?? error.message : String(error) });
  } finally {
    await browser.close();
  }

  const failed = assertions.filter((assertion) => assertion.status === "FAIL");
  const report = {
    status: failed.length ? "FAIL" : "PASS",
    label,
    url,
    reportPath,
    screenshotDir,
    screenshots,
    assertions,
    consoleMessages,
    pageErrors,
    forbiddenMessages,
    completedAt: new Date().toISOString()
  };
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), "utf8");
  if (failed.length) {
    console.error(`FAIL chart-lab-runtime-playwright-smoke ${label}: ${failed.length} issue(s)`);
    console.error(`Report: ${reportPath}`);
    process.exit(1);
  }
  console.log(`PASS chart-lab-runtime-playwright-smoke ${label}`);
  console.log(`Report: ${reportPath}`);
  console.log(`Screenshots: ${screenshotDir}`);
}

main();
