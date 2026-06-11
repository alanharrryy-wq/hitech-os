import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

function parseArgs(argv) {
  const args = {
    outDir: path.join('F:', 'descargasf', 'visualcat-visual-evidence'),
    routes: [],
    timeoutMs: 45000,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--out-dir') {
      args.outDir = argv[i + 1];
      i += 1;
    } else if (arg === '--route') {
      args.routes.push(argv[i + 1]);
      i += 1;
    } else if (arg === '--timeout-ms') {
      args.timeoutMs = Number(argv[i + 1]);
      i += 1;
    }
  }

  return args;
}

function routeSlug(route) {
  const label = `${route.surface}-${route.name}`;
  return label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function parseRoute(raw) {
  const [surface, name, url, viewportRaw = '1366x900'] = raw.split('|');
  const [width, height] = viewportRaw.split('x').map((part) => Number(part));
  if (!surface || !name || !url || !Number.isFinite(width) || !Number.isFinite(height)) {
    throw new Error(`Invalid --route value: ${raw}`);
  }
  return { surface, name, url, viewport: { width, height } };
}

async function captureRoute(browser, route, outDir, timeoutMs) {
  const slug = routeSlug(route);
  const page = await browser.newPage({ viewport: route.viewport });
  const startedAt = new Date().toISOString();
  const result = {
    ...route,
    slug,
    status: 'UNKNOWN',
    started_at: startedAt,
    finished_at: '',
    http_status: null,
    title: '',
    body_text_sample: '',
    screenshot: '',
    error: '',
  };

  try {
    const response = await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    result.http_status = response?.status() ?? null;
    await page.waitForLoadState('networkidle', { timeout: Math.min(timeoutMs, 15000) }).catch(() => {});
    result.title = await page.title();
    result.body_text_sample = (await page.locator('body').innerText({ timeout: 10000 })).replace(/\s+/g, ' ').slice(0, 500);
    const screenshotPath = path.join(outDir, 'screenshots', `${slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    result.screenshot = screenshotPath;
    result.status = result.http_status && result.http_status < 500 && result.body_text_sample.length > 0 ? 'PASS_VISUAL' : 'FAIL_VISUAL';
  } catch (error) {
    result.status = 'FAIL_VISUAL';
    result.error = error instanceof Error ? error.message : String(error);
  } finally {
    result.finished_at = new Date().toISOString();
    await page.close().catch(() => {});
  }

  return result;
}

function writeReports(outDir, routes, results) {
  const pass = results.filter((result) => result.status === 'PASS_VISUAL').length;
  const fail = results.filter((result) => result.status === 'FAIL_VISUAL').length;
  const skipped = routes.length - results.length;
  const classification = fail === 0 && pass > 0 ? 'PASS_VISUAL' : fail > 0 ? 'FAIL_VISUAL' : 'SKIPPED_NO_LIVE_SERVER';
  const report = {
    generated_at: new Date().toISOString(),
    classification,
    totals: { pass, fail, skipped },
    results,
  };

  const jsonPath = path.join(outDir, 'visualcat-visual-evidence.json');
  const mdPath = path.join(outDir, 'visualcat-visual-evidence.md');
  writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`);
  writeFileSync(
    mdPath,
    [
      '# VisualCat Visual Evidence',
      '',
      `- Classification: ${classification}`,
      `- PASS_VISUAL: ${pass}`,
      `- FAIL_VISUAL: ${fail}`,
      `- SKIPPED: ${skipped}`,
      '',
      '| Surface | Route | URL | Viewport | Status | HTTP | Screenshot |',
      '|---|---|---|---|---|---|---|',
      ...results.map((result) => `| ${result.surface} | ${result.name} | ${result.url} | ${result.viewport.width}x${result.viewport.height} | ${result.status} | ${result.http_status ?? ''} | ${result.screenshot} |`),
      '',
    ].join('\n'),
  );
  return { report, jsonPath, mdPath };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const routes = args.routes.map(parseRoute);
  mkdirSync(path.join(args.outDir, 'screenshots'), { recursive: true });

  if (routes.length === 0) {
    writeReports(args.outDir, [], []);
    return;
  }

  const requireFromCwd = createRequire(path.join(process.cwd(), 'package.json'));
  const { chromium } = (() => {
    try {
      return requireFromCwd('playwright');
    } catch {
      return requireFromCwd('@playwright/test');
    }
  })();
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const route of routes) {
      results.push(await captureRoute(browser, route, args.outDir, args.timeoutMs));
    }
  } finally {
    await browser.close();
  }

  const { report, jsonPath, mdPath } = writeReports(args.outDir, routes, results);
  console.log(JSON.stringify({ classification: report.classification, json: jsonPath, md: mdPath }, null, 2));
  if (report.classification === 'FAIL_VISUAL') process.exitCode = 1;
}

if (!existsSync(process.cwd())) {
  throw new Error('Working directory is not reachable.');
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
