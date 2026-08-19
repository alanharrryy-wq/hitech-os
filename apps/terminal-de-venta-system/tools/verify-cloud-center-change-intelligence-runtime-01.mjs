#!/usr/bin/env node
import fs from 'node:fs/promises';
import process from 'node:process';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const playwrightRoot = process.env.PCI_PLAYWRIGHT_ROOT || 'playwright';
const { chromium } = require(playwrightRoot);

const baseUrl = process.env.PCI_BASE_URL || 'http://127.0.0.1:8316';
const evidenceDir = process.env.PCI_EVIDENCE_DIR || 'pci-runtime-evidence';
const repoRoot = process.env.PCI_REPO_ROOT || process.cwd();
const expectedRepository = process.env.PCI_EXPECTED_REPOSITORY || 'prismahitech/hitech-os';
const target = `${baseUrl}/internal/web/change_intelligence_center.html`;
const expectedHealthUrl = `${baseUrl}/api/health`;
const runtimeUrl = `${baseUrl}/api/command-center/change-intelligence/repository`;
const expectedViews = ['overview','repositories','runs','discover','guard','control','authority','evidence','roi','entitlements'];
const expectedHead = String(process.env.PCI_EXPECTED_HEAD || execFileSync('git', ['-C', repoRoot, 'rev-parse', 'HEAD'], { encoding: 'utf8' })).trim().toLowerCase();
const expectedTree = String(process.env.PCI_EXPECTED_TREE || execFileSync('git', ['-C', repoRoot, 'rev-parse', 'HEAD^{tree}'], { encoding: 'utf8' })).trim().toLowerCase();

await fs.mkdir(evidenceDir, { recursive: true });

const result = {
  schemaVersion: 'prisma.change_intelligence.cloud_center.runtime.verify.v2',
  target,
  repositoryRuntimeUrl: runtimeUrl,
  expectedRepository,
  expectedHead,
  expectedTree,
  result: 'FAIL_CHANGE_INTELLIGENCE_CLOUD_CENTER_RUNTIME',
  runtimeVerified: false,
  productionCertified: false,
  certifiable: false,
  viewCount: expectedViews.length,
  profiles: [],
  fallback: null,
  errors: [],
};

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function collectForbidden(value, path = '$', out = []) {
  const forbiddenKey = /(repoRoot|outputRoot|resultRoot|localPath|cloneUrl|sshUrl|credential|authorization|token|secret|password|privateKey|sourceContent|sourceCode)/i;
  const absolutePath = /(?:^[A-Za-z]:[\\/]|^\/(?:home|Users|mnt|tmp|var|private)\/)/;
  if (Array.isArray(value)) {
    value.forEach((item, index) => collectForbidden(item, `${path}[${index}]`, out));
    return out;
  }
  if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (forbiddenKey.test(key)) out.push(`${path}.${key}:FORBIDDEN_KEY`);
      collectForbidden(item, `${path}.${key}`, out);
    }
    return out;
  }
  if (typeof value === 'string' && absolutePath.test(value)) out.push(`${path}:ABSOLUTE_LOCAL_PATH`);
  return out;
}

function verifyRuntimeEnvelope(runtime, name) {
  assert(runtime?.schemaVersion === 'prisma.change_intelligence.repository_runtime.v1', `${name}: runtime schema mismatch`);
  assert(runtime?.ok === true, `${name}: runtime not ok (${runtime?.status || runtime?.errorCode || 'UNKNOWN'})`);
  assert(runtime?.status === 'RUNTIME_SOURCE_READ_ONLY', `${name}: unexpected runtime status ${runtime?.status}`);
  assert(runtime?.readOnly === true, `${name}: runtime readOnly drift`);
  assert(runtime?.productionCertified === false, `${name}: runtime productionCertified drift`);
  assert(runtime?.certifiable === false, `${name}: runtime certifiable drift`);
  assert(runtime?.repository?.identity === expectedRepository, `${name}: repository identity mismatch ${runtime?.repository?.identity}`);
  assert(String(runtime?.repository?.head || '').toLowerCase() === expectedHead, `${name}: HEAD mismatch ${runtime?.repository?.head}`);
  assert(String(runtime?.repository?.tree || '').toLowerCase() === expectedTree, `${name}: tree mismatch ${runtime?.repository?.tree}`);
  assert(runtime?.freshness?.status === 'LIVE_SCAN', `${name}: freshness is not LIVE_SCAN`);
  assert(runtime?.provenance?.source === 'code_atlas.intelligence.resolve_intelligence_context', `${name}: wrong provenance source`);
  assert(runtime?.provenance?.runtimeEnvelope === true, `${name}: runtimeEnvelope marker missing`);
  assert(runtime?.provenance?.rawContextExposed === false, `${name}: raw context exposure marker drift`);
  assert(runtime?.readiness?.sourceFactsAvailable === true, `${name}: source facts unavailable`);
  const forbidden = collectForbidden(runtime);
  assert(forbidden.length === 0, `${name}: forbidden runtime fields leaked: ${forbidden.join(', ')}`);
  return forbidden;
}

const browser = await chromium.launch({ headless: true });

async function verifyProfile(name, viewport) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const badResponses = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      const location = msg.location();
      consoleErrors.push({ text: msg.text(), url: String(location?.url || ''), lineNumber: location?.lineNumber ?? null, columnNumber: location?.columnNumber ?? null });
    }
  });
  page.on('pageerror', err => pageErrors.push(String(err)));
  page.on('response', response => {
    const url = response.url();
    if (url.startsWith(baseUrl) && response.status() >= 400) badResponses.push({ url, status: response.status() });
  });

  const response = await page.goto(target, { waitUntil: 'networkidle', timeout: 120000 });
  assert(response && response.ok(), `${name}: document HTTP ${response?.status() ?? 'NO_RESPONSE'}`);
  await page.waitForSelector('body.pci-surface', { timeout: 10000 });
  await page.waitForSelector('style[data-pci-style="v1"]', { state: 'attached', timeout: 10000 });
  await page.waitForFunction(() => document.documentElement.dataset.pciState && document.documentElement.dataset.pciState !== 'booting');
  await page.waitForFunction(() => document.documentElement.dataset.pciRepositoryRuntime === 'received', null, { timeout: 120000 });

  const configResponse = await page.request.get(`${baseUrl}/internal/config/change_intelligence_cloud.json`);
  assert(configResponse.ok(), `${name}: governed config HTTP ${configResponse.status()}`);
  const config = await configResponse.json();
  assert(config?.maturity?.engineStatus === 'LOCAL_VERIFIED', `${name}: unexpected engineStatus ${config?.maturity?.engineStatus}`);
  assert(config?.maturity?.productionCertified === false && config?.maturity?.certifiable === false, `${name}: maturity claim ceiling drift`);
  assert(config?.controlPlane?.analysisRuns?.status === 'NOT_CONNECTED', `${name}: P2 analysisRuns must remain NOT_CONNECTED`);
  assert(config?.controlPlane?.authorityPacks?.status === 'NOT_CONNECTED', `${name}: P3 authorityPacks must remain NOT_CONNECTED`);
  assert(config?.controlPlane?.evidenceReferences?.status === 'NOT_CONNECTED', `${name}: P3 evidenceReferences must remain NOT_CONNECTED`);

  const runtimeResponse = await page.request.get(runtimeUrl, { timeout: 120000 });
  assert(runtimeResponse.ok(), `${name}: runtime endpoint HTTP ${runtimeResponse.status()}`);
  const runtime = await runtimeResponse.json();
  const forbiddenRuntimeFields = verifyRuntimeEnvelope(runtime, name);

  const navViews = await page.locator('[data-pci-view]').evaluateAll(nodes => nodes.map(n => n.getAttribute('data-pci-view')));
  const missingViews = expectedViews.filter(view => !navViews.includes(view));
  assert(missingViews.length === 0, `${name}: missing views ${missingViews.join(',')}`);

  for (const view of expectedViews) {
    await page.locator(`[data-pci-view="${view}"]`).click();
    await page.waitForTimeout(40);
    const hash = await page.evaluate(() => location.hash.replace(/^#/, ''));
    assert(hash === view, `${name}: navigation ${view} resolved ${hash}`);
  }

  await page.locator('[data-pci-view="repositories"]').click();
  const repositoryText = await page.locator('#pciContent').innerText();
  assert(repositoryText.includes('RUNTIME_SOURCE_READ_ONLY'), `${name}: browser did not render runtime status`);
  assert(repositoryText.includes(expectedHead.slice(0, 12)), `${name}: browser did not render runtime HEAD prefix`);
  assert(repositoryText.includes(expectedRepository), `${name}: browser did not render expected repository identity`);

  const forbiddenGreen = await page.locator('body').evaluate(body => /production\s+certified|paid\s+pilot\s+ready/i.test(body.innerText));
  assert(!forbiddenGreen, `${name}: forbidden maturity claim rendered`);
  const semanticText = await page.locator('body').innerText();
  assert(/UNKNOWN|NOT_CONNECTED|BLOCKED/i.test(semanticText), `${name}: fail-closed state vocabulary not rendered`);

  const hostChipText = (await page.locator('#pciRuntimeChip').innerText()).trim();
  assert(/Cloud Center host\s*·\s*reachable/i.test(hostChipText), `${name}: real Cloud Center host is not reachable (${hostChipText})`);
  assert(consoleErrors.length === 0, `${name}: console errors ${JSON.stringify(consoleErrors)}`);
  assert(pageErrors.length === 0, `${name}: page errors ${JSON.stringify(pageErrors)}`);
  assert(badResponses.length === 0, `${name}: bad HTTP responses ${JSON.stringify(badResponses)}`);

  const screenshot = `${evidenceDir}/change-intelligence-${name}.png`;
  await page.screenshot({ path: screenshot, fullPage: true });
  result.profiles.push({
    name,
    viewport,
    documentStatus: response.status(),
    pciState: await page.evaluate(() => document.documentElement.dataset.pciState),
    repositoryRuntimeState: await page.evaluate(() => document.documentElement.dataset.pciRepositoryRuntime),
    navViews,
    hostChipText,
    runtime: {
      status: runtime.status,
      repository: runtime.repository,
      freshness: runtime.freshness,
      coverage: runtime.coverage,
      readiness: runtime.readiness,
      provenance: runtime.provenance,
      readOnly: runtime.readOnly,
      certifiable: runtime.certifiable,
      productionCertified: runtime.productionCertified,
      forbiddenRuntimeFields,
    },
    consoleErrors,
    pageErrors,
    badResponses,
    screenshot,
  });
  await context.close();
}

async function verifyFallback() {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.route(runtimeUrl, route => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ ok: false, status: 'BLOCKED', errorCode: 'TEST_FAIL_CLOSED' }) }));
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', err => pageErrors.push(String(err)));
  const response = await page.goto(`${target}#repositories`, { waitUntil: 'networkidle', timeout: 30000 });
  assert(response && response.ok(), `fallback: document HTTP ${response?.status() ?? 'NO_RESPONSE'}`);
  await page.waitForFunction(() => document.documentElement.dataset.pciRepositoryRuntime === 'snapshot-fallback', null, { timeout: 15000 });
  const text = await page.locator('#pciContent').innerText();
  assert(text.includes('SNAPSHOT_FALLBACK'), 'fallback: snapshot fallback status not rendered');
  assert(!text.includes('RUNTIME_SOURCE_READ_ONLY'), 'fallback: stale runtime green survived failed endpoint');
  assert(pageErrors.length === 0, `fallback: page errors ${JSON.stringify(pageErrors)}`);
  const screenshot = `${evidenceDir}/change-intelligence-fallback.png`;
  await page.screenshot({ path: screenshot, fullPage: true });
  result.fallback = {
    state: await page.evaluate(() => document.documentElement.dataset.pciRepositoryRuntime),
    statusRendered: 'SNAPSHOT_FALLBACK',
    staleRuntimeGreenRendered: false,
    screenshot,
  };
  await context.close();
}

try {
  await verifyProfile('desktop', { width: 1440, height: 1000 });
  await verifyProfile('mobile', { width: 390, height: 844 });
  await verifyFallback();
  result.result = 'PASS_CHANGE_INTELLIGENCE_CLOUD_CENTER_RUNTIME';
  result.runtimeVerified = true;
} catch (error) {
  result.errors.push(String(error?.stack || error));
} finally {
  await browser.close();
  await fs.writeFile(`${evidenceDir}/runtime-report.json`, JSON.stringify(result, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify(result, null, 2));
}

process.exit(result.runtimeVerified ? 0 : 1);
