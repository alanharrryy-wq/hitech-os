#!/usr/bin/env node
// PRISMA PC UIUX V03 Playwright Visual Gate.
// Captures 1920x1080 screenshots and checks visual-shell basics without needing Playwright Test config.
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const args = new Map();
for (let i = 2; i < process.argv.length; i += 1) {
  const a = process.argv[i];
  if (a.startsWith('--')) {
    const k = a.slice(2);
    const v = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[++i] : 'true';
    args.set(k, v);
  }
}
const root = path.resolve(args.get('root') || path.join(process.cwd(), '../../..'));
const pcApp = path.join(root, 'products', 'pc', 'app');
const urlBase = String(args.get('url') || process.env.PRISMA_PC_VISUAL_URL || 'http://127.0.0.1:3130').replace(/\/$/, '');
const outDir = path.resolve(args.get('out') || path.join(process.cwd(), 'visual-gate-results'));
const routesFile = path.resolve(args.get('routes') || path.join(pcApp, 'tools', 'visual', 'pc-uiux-visual-routes.v03.json'));
const timeoutMs = Number(args.get('timeout-ms') || 30000);
const strict = args.get('strict') === 'true';

function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
function slug(s) { return s.replace(/^\//, '').replace(/[^a-zA-Z0-9_-]+/g, '_') || 'root'; }
function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }
function writeJson(p, v) { fs.writeFileSync(p, JSON.stringify(v, null, 2), 'utf8'); }
function csvEscape(v) { const s = String(v ?? ''); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; }

ensureDir(outDir);
ensureDir(path.join(outDir, 'screenshots'));
ensureDir(path.join(outDir, 'html'));

let playwright;
try {
  playwright = await import('playwright');
} catch (first) {
  try {
    playwright = await import('@playwright/test');
  } catch (second) {
    const missing = {
      status: 'MISSING_PLAYWRIGHT',
      message: 'Playwright is not installed or not resolvable from the PC app. Run pnpm -C products/pc/app add -D @playwright/test && pnpm -C products/pc/app exec playwright install chromium, or use the V03 PowerShell runner with -InstallDeps.',
      first_error: String(first?.message || first),
      second_error: String(second?.message || second),
      root, pcApp, urlBase, outDir,
    };
    writeJson(path.join(outDir, 'VISUAL_GATE_RESULT.json'), missing);
    fs.writeFileSync(path.join(outDir, 'VISUAL_GATE_SUMMARY.md'), `# PRISMA PC UIUX V03 Visual Gate\n\n❌ **MISSING_PLAYWRIGHT**\n\n${missing.message}\n`, 'utf8');
    process.exit(2);
  }
}
const { chromium } = playwright;
if (!chromium) {
  writeJson(path.join(outDir, 'VISUAL_GATE_RESULT.json'), { status: 'MISSING_CHROMIUM_EXPORT', root, pcApp });
  process.exit(2);
}

const config = readJson(routesFile);
const viewport = config.viewport || { width: 1920, height: 1080 };
const routes = config.routes || [];
const forbiddenFirstLevel = [
  'Runtime', 'Data Quality', 'Tablet Communication', 'License Runtime', 'Movements', 'Counts', 'Devices', 'Audit',
  'canonical DB', 'feature gate', 'ingest', 'dispatcher', 'ack', 'payload', 'sqlite-runtime', 'databasePaths'
];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport,
  deviceScaleFactor: 1,
  colorScheme: 'dark',
  reducedMotion: 'reduce',
});
const results = [];

for (const entry of routes) {
  const route = entry.route;
  const page = await context.newPage();
  const consoleMessages = [];
  const pageErrors = [];
  page.on('console', msg => {
    const type = msg.type();
    if (['error','warning'].includes(type)) consoleMessages.push({ type, text: msg.text().slice(0, 900) });
  });
  page.on('pageerror', err => pageErrors.push(String(err?.message || err).slice(0, 1200)));
  const fullUrl = urlBase + route;
  const started = Date.now();
  let status = 'PASS';
  const checks = [];
  let screenshot = '';
  let htmlPath = '';
  try {
    const response = await page.goto(fullUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    await page.waitForLoadState('networkidle', { timeout: Math.min(timeoutMs, 15000) }).catch(() => {});
    await page.waitForTimeout(450);
    const responseStatus = response ? response.status() : 0;
    checks.push({ id: 'http-status', pass: responseStatus >= 200 && responseStatus < 500, detail: String(responseStatus) });

    const metrics = await page.evaluate((forbidden) => {
      const text = document.body?.innerText || '';
      const navText = Array.from(document.querySelectorAll('nav, aside, header, [role="navigation"], a, button')).map(el => el.textContent || '').join('\n');
      const de = document.documentElement;
      const body = document.body;
      const firstLevelHits = forbidden.filter(term => new RegExp(`(^|\\b)${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\b|$)`, 'i').test(navText));
      const h1 = Array.from(document.querySelectorAll('h1')).map(el => el.textContent?.trim()).filter(Boolean);
      return {
        title: document.title,
        textLength: text.trim().length,
        bodyTextSample: text.trim().slice(0, 5000),
        navTextSample: navText.trim().slice(0, 4000),
        h1,
        firstLevelHits,
        scrollWidth: Math.max(de.scrollWidth, body?.scrollWidth || 0),
        clientWidth: de.clientWidth,
        scrollHeight: Math.max(de.scrollHeight, body?.scrollHeight || 0),
        clientHeight: de.clientHeight,
        hasHorizontalOverflow: Math.max(de.scrollWidth, body?.scrollWidth || 0) > de.clientWidth + 8,
        hasMain: Boolean(document.querySelector('main')),
        hasNav: Boolean(document.querySelector('nav, [role="navigation"], aside')),
        hasButtons: document.querySelectorAll('button, a[href]').length,
      };
    }, forbiddenFirstLevel);

    checks.push({ id: 'page-has-text', pass: metrics.textLength > 80, detail: `${metrics.textLength} chars` });
    checks.push({ id: 'has-main-shell', pass: metrics.hasMain, detail: metrics.hasMain ? 'main found' : 'main missing' });
    checks.push({ id: 'has-navigation-or-actions', pass: metrics.hasNav || metrics.hasButtons >= 2, detail: `hasNav=${metrics.hasNav} buttonsLinks=${metrics.hasButtons}` });
    checks.push({ id: 'no-horizontal-overflow-1920', pass: !metrics.hasHorizontalOverflow, detail: `scrollWidth=${metrics.scrollWidth} clientWidth=${metrics.clientWidth}` });
    checks.push({ id: 'no-forbidden-first-level-terms', pass: metrics.firstLevelHits.length === 0, detail: metrics.firstLevelHits.join(', ') || 'clean' });
    const expected = entry.expected || [entry.name];
    const matchedExpected = expected.filter(token => metrics.bodyTextSample.toLowerCase().includes(String(token).toLowerCase()));
    checks.push({ id: 'expected-human-copy-visible', pass: matchedExpected.length > 0, detail: matchedExpected.join(', ') || `missing any of: ${expected.join(', ')}` });
    checks.push({ id: 'no-page-errors', pass: pageErrors.length === 0, detail: pageErrors.join(' | ') || 'none' });

    const routeSlug = slug(route);
    screenshot = path.join(outDir, 'screenshots', `${routeSlug}.png`);
    htmlPath = path.join(outDir, 'html', `${routeSlug}.html`);
    await page.screenshot({ path: screenshot, fullPage: true });
    fs.writeFileSync(htmlPath, await page.content(), 'utf8');

    const failedChecks = checks.filter(c => !c.pass);
    if (failedChecks.length) status = entry.critical || strict ? 'FAIL' : 'WARN';
    results.push({ route, name: entry.name, status, url: fullUrl, duration_ms: Date.now() - started, checks, metrics, consoleMessages, pageErrors, screenshot, htmlPath });
  } catch (err) {
    status = entry.critical || strict ? 'FAIL' : 'WARN';
    results.push({ route, name: entry.name, status, url: fullUrl, duration_ms: Date.now() - started, checks, error: String(err?.stack || err), consoleMessages, pageErrors, screenshot, htmlPath });
  } finally {
    await page.close().catch(() => {});
  }
}
await browser.close();

const fail = results.filter(r => r.status === 'FAIL').length;
const warn = results.filter(r => r.status === 'WARN').length;
const pass = results.filter(r => r.status === 'PASS').length;
const finalStatus = fail ? 'FAIL' : warn ? 'WARN' : 'PASS';
const summary = { status: finalStatus, pass, warn, fail, total: results.length, root, pcApp, urlBase, viewport, created_at: new Date().toISOString(), results };
writeJson(path.join(outDir, 'VISUAL_GATE_RESULT.json'), summary);

const csv = ['route,name,status,failed_checks,screenshot'];
for (const r of results) {
  const failed = (r.checks || []).filter(c => !c.pass).map(c => `${c.id}:${c.detail}`).join(' | ');
  csv.push([r.route, r.name, r.status, failed, r.screenshot].map(csvEscape).join(','));
}
fs.writeFileSync(path.join(outDir, 'VISUAL_ROUTE_MATRIX.csv'), csv.join('\n') + '\n', 'utf8');

const lines = [];
lines.push('# PRISMA PC UIUX V03 Playwright Visual Gate');
lines.push('');
lines.push(`**Status:** ${finalStatus}`);
lines.push(`**Routes:** ${results.length}`);
lines.push(`**Pass/Warn/Fail:** ${pass}/${warn}/${fail}`);
lines.push(`**Viewport:** ${viewport.width}x${viewport.height}`);
lines.push(`**URL base:** ${urlBase}`);
lines.push('');
lines.push('## Checklist');
lines.push('');
for (const r of results) {
  const mark = r.status === 'PASS' ? '✅' : r.status === 'WARN' ? '⚠️' : '❌';
  lines.push(`${mark} ${r.name} \`${r.route}\` — ${r.status}`);
  for (const c of (r.checks || [])) {
    lines.push(`  - ${c.pass ? '✅' : '❌'} ${c.id}: ${c.detail}`);
  }
  if (r.error) lines.push(`  - ❌ error: ${r.error.split('\n')[0]}`);
}
lines.push('');
lines.push('## Archivos clave');
lines.push('');
lines.push('- `screenshots/*.png`');
lines.push('- `html/*.html`');
lines.push('- `VISUAL_ROUTE_MATRIX.csv`');
lines.push('- `VISUAL_GATE_RESULT.json`');
fs.writeFileSync(path.join(outDir, 'VISUAL_GATE_SUMMARY.md'), lines.join('\n') + '\n', 'utf8');

process.exit(fail ? 1 : 0);
