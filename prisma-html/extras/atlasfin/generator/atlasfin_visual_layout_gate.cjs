#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

function arg(name, fallback = '') {
  const index = process.argv.indexOf(name);
  return index >= 0 && index + 1 < process.argv.length ? process.argv[index + 1] : fallback;
}

function mkdirp(dir) { fs.mkdirSync(dir, { recursive: true }); }

function loadPlaywright() {
  const attempts = [];
  for (const candidate of ['@playwright/test', 'playwright']) {
    try {
      const loaded = require(candidate);
      if (loaded.chromium) return { chromium: loaded.chromium, moduleName: candidate };
    } catch (error) {
      attempts.push(`${candidate}: ${error.message}`);
    }
  }
  const explicit = process.env.PRISMA_PLAYWRIGHT_MODULE;
  if (explicit) {
    try {
      const loaded = require(path.resolve(explicit));
      if (loaded.chromium) return { chromium: loaded.chromium, moduleName: 'explicit-module' };
    } catch (error) {
      attempts.push(`explicit-module: ${error.message}`);
    }
  }
  throw new Error(`Playwright unavailable. ${attempts.join(' | ')}`);
}

async function launchBrowser(chromium) {
  try {
    return { browser: await chromium.launch({ headless: true }), launchMode: 'bundled-chromium' };
  } catch (error) {
    if (!String(error.message || error).includes("Executable doesn't exist")) throw error;
    return { browser: await chromium.launch({ headless: true, channel: 'msedge' }), launchMode: 'system-msedge' };
  }
}

const defaultViewports = [
  { width: 1365, height: 768 },
  { width: 1024, height: 768 },
  { width: 900, height: 768 },
  { width: 640, height: 900 }
];
const defaultPages = [
  'index.html',
  'i-paneles-cards.html',
  'k-estados-feedback.html',
  'l-carga-progreso.html',
  'x-sistema-diagnostico.html',
  'y-i18n-impresion-offline.html',
  'z-gobierno.html'
];
function parsePages() {
  const raw = arg('--pages', '').trim();
  return raw ? raw.split(',').map(value => value.trim()).filter(Boolean) : defaultPages;
}
function parseViewports() {
  const raw = arg('--viewports', '').trim();
  if (!raw) return defaultViewports;
  return raw.split(',').map(value => {
    const match = value.trim().match(/^(\d+)x(\d+)$/i);
    if (!match) throw new Error(`Invalid viewport: ${value}`);
    return { width: Number(match[1]), height: Number(match[2]) };
  });
}
const pages = parsePages();
const viewports = parseViewports();
const cardSelector = [
  '.atlas-card', '.atlas-component-card', '.atlas-rich-card', '.atlas-entity-card',
  '.atlas-mini-state', '.atlas-status-tile', '.atlas-demo-panel', '.atlas-state-stage',
  '.atlas-kpi-mini', '.atlas-copy-card', '.atlas-queue-item'
].join(',');
const stressSelector = [
  '.atlas-status', '.atlas-component-card__id', '.atlas-status-tile small',
  '.atlas-mini-state p', '.atlas-rowline > span', '.atlas-offline-demo small'
].join(',');

async function inspectPage(page, pageName, viewport, screenshotDir) {
  const blockedNetwork = [];
  await page.route('**/*', async route => {
    const protocol = new URL(route.request().url()).protocol;
    if (protocol === 'file:' || protocol === 'data:' || protocol === 'blob:') return route.continue();
    blockedNetwork.push({ protocol, resourceType: route.request().resourceType() });
    return route.abort('blockedbyclient');
  });
  await page.goto(pathToFileURL(path.join(arg('--atlas-root'), pageName)).href, { waitUntil: 'load' });
  await page.addStyleTag({ content: '.atlas-ny-section{content-visibility:visible;contain-intrinsic-size:none}' });
  await page.locator(stressSelector).evaluateAll(elements => {
    const stress = ' ESTADO_OPERATIVO_EXTENSO_SIN_CORTE_CONFIRMADO';
    for (const element of elements) {
      element.append(document.createTextNode(stress));
      element.setAttribute('data-layout-gate-stress', 'true');
    }
  });
  await page.evaluate(async () => {
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });

  const measurement = await page.evaluate(({ cardSelector: cardsQuery, stressSelector: stressQuery }) => {
    const tolerance = 1.25;
    const rectOf = element => {
      const rect = element.getBoundingClientRect();
      return { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom, width: rect.width, height: rect.height };
    };
    const labelOf = element => {
      const id = element.id ? `#${element.id}` : '';
      const classes = String(element.className || '').trim().split(/\s+/).filter(Boolean).slice(0, 3).map(value => `.${value}`).join('');
      return `${element.tagName.toLowerCase()}${id}${classes}`;
    };
    const pathOf = element => {
      const parts = [];
      let current = element;
      for (let depth = 0; current && current !== document.body && depth < 6; depth += 1) {
        parts.unshift(labelOf(current));
        current = current.parentElement;
      }
      return parts.join(' > ');
    };
    const visible = element => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) !== 0 && rect.width > 0 && rect.height > 0;
    };
    const cards = Array.from(document.querySelectorAll(cardsQuery)).filter(visible);
    const collisions = [];
    for (let leftIndex = 0; leftIndex < cards.length; leftIndex++) {
      for (let rightIndex = leftIndex + 1; rightIndex < cards.length; rightIndex++) {
        const left = cards[leftIndex];
        const right = cards[rightIndex];
        if (left.parentElement !== right.parentElement) continue;
        const a = rectOf(left);
        const b = rectOf(right);
        const overlapX = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const overlapY = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (overlapX > tolerance && overlapY > tolerance) {
          collisions.push({ left: labelOf(left), right: labelOf(right), overlapX, overlapY });
        }
      }
    }

    const elementOverflow = [];
    const parentEscapes = [];
    const targets = Array.from(new Set([...cards, ...document.querySelectorAll(stressQuery)])).filter(visible);
    for (const element of targets) {
      const deltaX = element.scrollWidth - element.clientWidth;
      const deltaY = element.scrollHeight - element.clientHeight;
      if (deltaX > tolerance || deltaY > tolerance) {
        elementOverflow.push({
          element: labelOf(element),
          clientWidth: element.clientWidth,
          scrollWidth: element.scrollWidth,
          clientHeight: element.clientHeight,
          scrollHeight: element.scrollHeight,
          horizontalOverflow: deltaX,
          verticalOverflow: deltaY
        });
      }
      const parent = element.parentElement;
      if (!parent || !visible(parent)) continue;
      const style = getComputedStyle(element);
      if (['absolute', 'fixed', 'sticky'].includes(style.position)) continue;
      const childRect = rectOf(element);
      const parentRect = rectOf(parent);
      const escape = {
        left: parentRect.left - childRect.left,
        top: parentRect.top - childRect.top,
        right: childRect.right - parentRect.right,
        bottom: childRect.bottom - parentRect.bottom
      };
      if (Object.values(escape).some(value => value > tolerance)) {
        parentEscapes.push({ element: labelOf(element), parent: labelOf(parent), escape });
      }
    }
    const root = document.documentElement;
    const body = document.body;
    const viewportWidth = root.clientWidth;
    const documentWidth = () => Math.max(root.scrollWidth, body.scrollWidth);
    const baselineDocumentWidth = documentWidth();
    const isolationCandidates = [];
    if (baselineDocumentWidth - viewportWidth > tolerance) {
      const all = Array.from(document.body.querySelectorAll('*')).filter(visible);
      for (let index = 0; index < all.length; index += 1) {
        const element = all[index];
        if (['SCRIPT', 'STYLE', 'LINK', 'META'].includes(element.tagName)) continue;
        const previous = element.style.getPropertyValue('display');
        const priority = element.style.getPropertyPriority('display');
        element.style.setProperty('display', 'none', 'important');
        const widthWithout = documentWidth();
        if (previous) element.style.setProperty('display', previous, priority);
        else element.style.removeProperty('display');
        if (widthWithout + tolerance < baselineDocumentWidth) {
          const rect = rectOf(element);
          const style = getComputedStyle(element);
          isolationCandidates.push({
            element: labelOf(element),
            selectorPath: pathOf(element),
            widthWithout,
            reduction: baselineDocumentWidth - widthWithout,
            rect,
            display: style.display,
            position: style.position,
            minWidth: style.minWidth,
            width: style.width,
            maxWidth: style.maxWidth,
            gridTemplateColumns: style.gridTemplateColumns,
            overflowX: style.overflowX,
            textSample: String(element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 220)
          });
        }
      }
      isolationCandidates.sort((a, b) => b.reduction - a.reduction || a.selectorPath.length - b.selectorPath.length);
    }
    const overflowContributors = Array.from(document.querySelectorAll('body *'))
      .filter(visible)
      .map(element => {
        const rect = rectOf(element);
        const style = getComputedStyle(element);
        const rightOverflow = rect.right - viewportWidth;
        const leftOverflow = 0 - rect.left;
        return {
          element: labelOf(element),
          selectorPath: pathOf(element),
          textSample: String(element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 180),
          rect,
          rightOverflow,
          leftOverflow,
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          display: style.display,
          position: style.position,
          gridTemplateColumns: style.gridTemplateColumns,
          overflowX: style.overflowX,
          minWidth: style.minWidth,
          maxWidth: style.maxWidth
        };
      })
      .filter(item => item.rightOverflow > tolerance || item.leftOverflow > tolerance)
      .sort((a, b) => Math.max(b.rightOverflow, b.leftOverflow) - Math.max(a.rightOverflow, a.leftOverflow))
      .slice(0, 24);
    return {
      document: {
        clientWidth: root.clientWidth,
        scrollWidth: Math.max(root.scrollWidth, body.scrollWidth),
        clientHeight: root.clientHeight,
        scrollHeight: Math.max(root.scrollHeight, body.scrollHeight),
        horizontalOverflow: Math.max(root.scrollWidth, body.scrollWidth) - root.clientWidth,
        verticalOverflow: Math.max(root.scrollHeight, body.scrollHeight) - root.clientHeight
      },
      counts: { cards: cards.length, stressTargets: document.querySelectorAll(stressQuery).length },
      collisions,
      elementOverflow,
      parentEscapes,
      overflowContributors,
      isolationCandidates: isolationCandidates.slice(0, 40)
    };
  }, { cardSelector, stressSelector });

  const failures = [];
  if (measurement.document.horizontalOverflow > 1.25) failures.push({ type: 'DOCUMENT_HORIZONTAL_OVERFLOW', value: measurement.document.horizontalOverflow });
  for (const collision of measurement.collisions) failures.push({ type: 'CARD_COLLISION', ...collision });
  for (const overflow of measurement.elementOverflow) failures.push({ type: 'ELEMENT_OVERFLOW', ...overflow });
  for (const escape of measurement.parentEscapes) failures.push({ type: 'ELEMENT_OUTSIDE_PARENT', ...escape });
  for (const request of blockedNetwork) failures.push({ type: 'EXTERNAL_REQUEST_BLOCKED', ...request });

  let screenshot = null;
  if (pageName === 'x-sistema-diagnostico.html' || failures.length) {
    screenshot = `${path.parse(pageName).name}-${viewport.width}x${viewport.height}.png`;
    await page.screenshot({ path: path.join(screenshotDir, screenshot), fullPage: true });
  }
  return { page: pageName, viewport, status: failures.length ? 'FAIL' : 'PASS', screenshot, measurement, failures };
}

(async () => {
  const atlasRoot = path.resolve(arg('--atlas-root', path.resolve(__dirname, '..')));
  const outDir = path.resolve(arg('--out-dir', path.join(atlasRoot, 'reports', 'visual-layout-gate')));
  const reportPath = path.join(outDir, 'ATLASFIN_VISUAL_LAYOUT_GATE.json');
  const screenshotDir = path.join(outDir, 'screens');
  mkdirp(screenshotDir);
  const startedAt = new Date().toISOString();
  let browser;
  try {
    const resolved = loadPlaywright();
    const launched = await launchBrowser(resolved.chromium);
    browser = launched.browser;
    const records = [];
    for (const viewport of viewports) {
      const context = await browser.newContext({ viewport });
      const page = await context.newPage();
      for (const pageName of pages) records.push(await inspectPage(page, pageName, viewport, screenshotDir));
      await context.close();
    }
    const failures = records.flatMap(record => record.failures.map(failure => ({ page: record.page, viewport: record.viewport, ...failure })));
    const report = {
      schema: 'prisma.atlasfin.visual-layout-gate.v2',
      taskId: 'ATLASFIN_COBRAR_VISUAL_EVIDENCE_HARDENING_FINAL_V1',
      status: failures.length ? 'FAIL_CLOSED_VISUAL_LAYOUT' : 'PASS_COLLISION_OVERFLOW_CONTAINMENT',
      browser: { moduleName: resolved.moduleName, launchMode: launched.launchMode },
      viewports,
      pages,
      stressMode: 'LONG_STATUS_TEXT_DOM_ONLY',
      records,
      failures,
      startedAt,
      finishedAt: new Date().toISOString()
    };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    if (failures.length) {
      console.error(`FAIL_CLOSED_VISUAL_LAYOUT failures=${failures.length}`);
      process.exitCode = 2;
    } else {
      console.log(`PASS_COLLISION_OVERFLOW_CONTAINMENT records=${records.length}`);
    }
  } catch (error) {
    const report = {
      schema: 'prisma.atlasfin.visual-layout-gate.v2',
      taskId: 'ATLASFIN_COBRAR_VISUAL_EVIDENCE_HARDENING_FINAL_V1',
      status: 'FAIL_CLOSED_GATE_ERROR',
      error: { name: error.name, message: String(error.message || error) },
      startedAt,
      finishedAt: new Date().toISOString()
    };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.error(error.stack || String(error));
    process.exitCode = 2;
  } finally {
    if (browser) await browser.close();
  }
})();
