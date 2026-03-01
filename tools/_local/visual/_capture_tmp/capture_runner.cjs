
const fs = require("fs");
const path = require("path");

async function run() {
  const configPath = process.argv[2];
  if (!configPath) {
    throw new Error("missing config path");
  }
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const { chromium } = require("playwright");
  const browser = await chromium.launch({ headless: true });
  const report = [];
  try {
    for (const target of config.targets) {
      for (const viewport of config.viewports) {
        const context = await browser.newContext({
          viewport: { width: viewport.width, height: viewport.height },
          deviceScaleFactor: 1,
          locale: "en-US",
          timezoneId: "UTC",
          colorScheme: "light"
        });
        const page = await context.newPage();
        await page.addInitScript(() => {
          const style = document.createElement("style");
          style.innerHTML = `*, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }`;
          document.head.appendChild(style);
          const fixed = Date.parse("2026-01-01T00:00:00.000Z");
          // eslint-disable-next-line no-global-assign
          Date.now = () => fixed;
        });
        const targetUrl = config.baseUrl.replace(/\/$/, "") + target.path;
        await page.goto(targetUrl, { waitUntil: "networkidle", timeout: config.timeoutMs });
        await page.waitForTimeout(config.settleMs);
        const outputPath = path.join(
          config.outputDir,
          `${target.name}__${viewport.name}.png`
        );
        await page.screenshot({ path: outputPath, fullPage: true });
        report.push({ target: target.name, viewport: viewport.name, file: outputPath, url: targetUrl });
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify({ ok: true, captures: report }, null, 2));
}

run().catch((error) => {
  const payload = {
    ok: false,
    error: String(error && error.stack ? error.stack : error)
  };
  process.stderr.write(JSON.stringify(payload, null, 2));
  process.exit(1);
});
