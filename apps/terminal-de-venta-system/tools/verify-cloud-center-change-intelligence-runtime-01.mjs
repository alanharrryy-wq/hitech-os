#!/usr/bin/env node
import fs from 'node:fs/promises';
import process from 'node:process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const playwrightRoot = process.env.PCI_PLAYWRIGHT_ROOT || 'playwright';
const { chromium } = require(playwrightRoot);

const baseUrl = process.env.PCI_BASE_URL || 'http://127.0.0.1:8316';
const evidenceDir = process.env.PCI_EVIDENCE_DIR || 'pci-runtime-evidence';
const target = `${baseUrl}/internal/web/change_intelligence_center.html`;
const expectedHealthUrl = `${baseUrl}/api/health`;
const expectedViews = ['overview','repositories','runs','discover','guard','control','authority','evidence','roi','entitlements'];
const expectedVisualContract = 'PRISMA_CLOUD_CENTER_STORMGLASS_LITE_V1';

await fs.mkdir(evidenceDir, { recursive: true });

const result = {
  schemaVersion: 'prisma.change_intelligence.cloud_center.runtime.verify.v1',
  target,
  result: 'FAIL_CHANGE_INTELLIGENCE_CLOUD_CENTER_RUNTIME',
  runtimeVerified: false,
  productionCertified: false,
  certifiable: false,
  visualContract: expectedVisualContract,
  viewCount: expectedViews.length,
  profiles: [],
  errors: [],
};

const browser = await chromium.launch({ headless: true });

function countGridTracks(value) {
  const text = String(value || '').trim();
  if (!text || text === 'none') return 0;
  return text.split(/\s+/).filter(Boolean).length;
}

async function verifyProfile(name, viewport) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const badResponses = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      const location = msg.location();
      consoleErrors.push({
        text: msg.text(),
        url: String(location?.url || ''),
        lineNumber: location?.lineNumber ?? null,
        columnNumber: location?.columnNumber ?? null,
      });
    }
  });
  page.on('pageerror', err => pageErrors.push(String(err)));
  page.on('response', response => {
    const url = response.url();
    if (url.startsWith(baseUrl) && response.status() >= 400) badResponses.push({ url, status: response.status() });
  });

  const response = await page.goto(target, { waitUntil: 'networkidle', timeout: 30000 });
  if (!response || !response.ok()) throw new Error(`${name}: document HTTP ${response?.status() ?? 'NO_RESPONSE'}`);

  await page.waitForSelector('body.pci-surface', { timeout: 10000 });
  await page.waitForSelector('style[data-pci-style="v1"]', { state: 'attached', timeout: 10000 });
  await page.waitForFunction(() => document.documentElement.dataset.pciState && document.documentElement.dataset.pciState !== 'booting');

  const configResponse = await page.request.get(`${baseUrl}/internal/config/change_intelligence_cloud.json`);
  if (!configResponse.ok()) throw new Error(`${name}: governed config HTTP ${configResponse.status()}`);
  const config = await configResponse.json();
  if (config?.maturity?.engineStatus !== 'LOCAL_VERIFIED') throw new Error(`${name}: unexpected engineStatus ${config?.maturity?.engineStatus}`);
  if (config?.maturity?.productionCertified !== false || config?.maturity?.certifiable !== false) throw new Error(`${name}: maturity claim ceiling drift`);

  const navViews = await page.locator('[data-pci-view]').evaluateAll(nodes => nodes.map(n => n.getAttribute('data-pci-view')));
  const missingViews = expectedViews.filter(view => !navViews.includes(view));
  if (missingViews.length) throw new Error(`${name}: missing views ${missingViews.join(',')}`);

  for (const view of expectedViews) {
    await page.locator(`[data-pci-view="${view}"]`).click();
    await page.waitForTimeout(40);
    const hash = await page.evaluate(() => location.hash.replace(/^#/, ''));
    if (hash !== view) throw new Error(`${name}: navigation ${view} resolved ${hash}`);
  }

  const forbiddenGreen = await page.locator('body').evaluate(body => /production\s+certified|paid\s+pilot\s+ready/i.test(body.innerText));
  if (forbiddenGreen) throw new Error(`${name}: forbidden maturity claim rendered`);

  const semanticText = await page.locator('body').innerText();
  if (!/UNKNOWN|NOT_CONNECTED|BLOCKED/i.test(semanticText)) throw new Error(`${name}: fail-closed state vocabulary not rendered`);

  const hostChipText = (await page.locator('#pciRuntimeChip').innerText()).trim();
  if (!/Cloud Center host\s*·\s*UNKNOWN/i.test(hostChipText)) {
    throw new Error(`${name}: disconnected host probe did not remain UNKNOWN (${hostChipText})`);
  }

  const visualContract = await page.evaluate(() => {
    const by = selector => document.querySelector(selector);
    const style = selector => {
      const node = by(selector);
      return node ? getComputedStyle(node) : null;
    };
    const html = document.documentElement;
    const topbar = style('.pci-topbar');
    const mark = style('.pci-brand-mark');
    const layout = style('.pci-layout');
    const nav = style('.pci-nav');
    const hero = style('.pci-hero');
    const card = style('.pci-card');
    const body = getComputedStyle(document.body);
    const canonicalLink = by('link[rel="stylesheet"][href*="cloud_command_center.css"]');
    return {
      declared: html.dataset.pciVisualContract || '',
      canonicalStylesheetHref: canonicalLink?.href || '',
      bodyBackgroundImage: body.backgroundImage,
      topbar: topbar ? {
        position: topbar.position,
        borderRadius: topbar.borderRadius,
        backdropFilter: topbar.backdropFilter || topbar.webkitBackdropFilter || '',
      } : null,
      brandMark: mark ? {
        borderTopWidth: mark.borderTopWidth,
        borderTopStyle: mark.borderTopStyle,
        backgroundColor: mark.backgroundColor,
        width: mark.width,
        height: mark.height,
      } : null,
      layout: layout ? {
        display: layout.display,
        gridTemplateColumns: layout.gridTemplateColumns,
      } : null,
      nav: nav ? {
        display: nav.display,
        flexWrap: nav.flexWrap,
        overflowX: nav.overflowX,
      } : null,
      hero: hero ? {
        display: hero.display,
        gridTemplateColumns: hero.gridTemplateColumns,
        borderRadius: hero.borderRadius,
        backdropFilter: hero.backdropFilter || hero.webkitBackdropFilter || '',
      } : null,
      card: card ? {
        borderRadius: card.borderRadius,
        backdropFilter: card.backdropFilter || card.webkitBackdropFilter || '',
      } : null,
    };
  });

  if (visualContract.declared !== expectedVisualContract) {
    throw new Error(`${name}: visual contract drift ${visualContract.declared}`);
  }
  if (!/cloud_command_center\.css/i.test(visualContract.canonicalStylesheetHref)) {
    throw new Error(`${name}: canonical Cloud Center stylesheet not loaded`);
  }
  if (!/simon-spring-zmMrlEHsFQY-unsplash\.jpg/i.test(visualContract.bodyBackgroundImage)) {
    throw new Error(`${name}: canonical Stormglass atmosphere photo not active`);
  }
  if (!visualContract.topbar || ['sticky','fixed'].includes(visualContract.topbar.position)) {
    throw new Error(`${name}: topbar must remain floating, not sticky/fixed`);
  }
  if (visualContract.topbar.borderRadius !== '28px') {
    throw new Error(`${name}: topbar radius drift ${visualContract.topbar.borderRadius}`);
  }
  if (!visualContract.brandMark || visualContract.brandMark.borderTopWidth !== '0px' || visualContract.brandMark.backgroundColor !== 'rgba(0, 0, 0, 0)') {
    throw new Error(`${name}: canonical unboxed crystal mark contract failed`);
  }
  if (!visualContract.nav || visualContract.nav.display !== 'flex') {
    throw new Error(`${name}: navigation is not the canonical horizontal flex family`);
  }
  if (!visualContract.layout || countGridTracks(visualContract.layout.gridTemplateColumns) !== 1) {
    throw new Error(`${name}: legacy sidebar layout still active (${visualContract.layout?.gridTemplateColumns})`);
  }
  if (!visualContract.hero || visualContract.hero.borderRadius !== '24px' || !/blur\(2px\)/.test(visualContract.hero.backdropFilter)) {
    throw new Error(`${name}: hero Stormglass Lite geometry/material drift`);
  }
  if (!visualContract.card || visualContract.card.borderRadius !== '24px' || !/blur\(2px\)/.test(visualContract.card.backdropFilter)) {
    throw new Error(`${name}: card Stormglass Lite geometry/material drift`);
  }

  const heroTracks = countGridTracks(visualContract.hero.gridTemplateColumns);
  if (name === 'desktop' && heroTracks < 2) {
    throw new Error(`${name}: desktop hero must preserve content + seal columns (${visualContract.hero.gridTemplateColumns})`);
  }
  if (name === 'mobile') {
    if (visualContract.nav.flexWrap !== 'nowrap' || !['auto','scroll'].includes(visualContract.nav.overflowX)) {
      throw new Error(`${name}: mobile navigation must remain horizontal scroll, got wrap=${visualContract.nav.flexWrap} overflowX=${visualContract.nav.overflowX}`);
    }
    if (heroTracks !== 1) {
      throw new Error(`${name}: mobile hero must collapse to one column (${visualContract.hero.gridTemplateColumns})`);
    }
  }

  const expectedHealthResponses = badResponses.filter(entry => entry.url === expectedHealthUrl && entry.status === 404);
  const unexpectedBadResponses = badResponses.filter(entry => !(entry.url === expectedHealthUrl && entry.status === 404));
  if (expectedHealthResponses.length !== 1) {
    throw new Error(`${name}: expected exactly one fail-closed /api/health 404, found ${expectedHealthResponses.length}`);
  }

  const failedResource404 = entry => /Failed to load resource/i.test(entry.text) && /\b404\b/.test(entry.text);
  const expectedHealthConsoleErrors = consoleErrors.length === 1 && failedResource404(consoleErrors[0])
    ? [consoleErrors[0]]
    : [];
  const unexpectedConsoleErrors = expectedHealthConsoleErrors.length === 1 ? [] : consoleErrors;
  if (expectedHealthConsoleErrors.length !== 1) {
    throw new Error(`${name}: expected one Chromium failed-resource console event correlated with /api/health 404, found ${consoleErrors.length}`);
  }

  const screenshot = `${evidenceDir}/change-intelligence-${name}.png`;
  await page.screenshot({ path: screenshot, fullPage: true });

  const profile = {
    name,
    viewport,
    documentStatus: response.status(),
    pciState: await page.evaluate(() => document.documentElement.dataset.pciState),
    navViews,
    hostChipText,
    visualContract,
    expectedHealthProbe: {
      url: expectedHealthUrl,
      expectedStatus: 404,
      responses: expectedHealthResponses,
      consoleErrors: expectedHealthConsoleErrors,
    },
    consoleErrors,
    pageErrors,
    badResponses,
    unexpectedConsoleErrors,
    unexpectedBadResponses,
    screenshot,
  };
  result.profiles.push(profile);

  if (unexpectedConsoleErrors.length || pageErrors.length || unexpectedBadResponses.length) {
    throw new Error(`${name}: unexpected runtime errors console=${unexpectedConsoleErrors.length} page=${pageErrors.length} http=${unexpectedBadResponses.length}`);
  }

  await context.close();
}

try {
  await verifyProfile('desktop', { width: 1440, height: 1000 });
  await verifyProfile('mobile', { width: 390, height: 844 });
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
