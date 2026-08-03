#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

function arg(name, fallback = '') { const index = process.argv.indexOf(name); return index >= 0 && index + 1 < process.argv.length ? process.argv[index + 1] : fallback; }
function mkdirp(dir) { fs.mkdirSync(dir, { recursive: true }); }
function loadPlaywright() {
  for (const name of ['@playwright/test', 'playwright']) {
    try { const loaded = require(name); if (loaded.chromium) return { chromium: loaded.chromium, moduleName: name }; } catch {}
  }
  const explicit = process.env.PRISMA_PLAYWRIGHT_MODULE;
  if (explicit) { const loaded = require(path.resolve(explicit)); if (loaded.chromium) return { chromium: loaded.chromium, moduleName: 'explicit-module' }; }
  throw new Error('Playwright unavailable; set PRISMA_PLAYWRIGHT_MODULE to an existing module entry.');
}
async function launch(chromium) {
  try { return { browser: await chromium.launch({ headless: true }), mode: 'bundled-chromium' }; }
  catch (error) {
    if (!String(error.message || error).includes("Executable doesn't exist")) throw error;
    return { browser: await chromium.launch({ headless: true, channel: 'msedge' }), mode: 'system-msedge' };
  }
}
function durationMs(value) {
  return Math.max(...String(value || '0s').split(',').map(part => part.trim().endsWith('ms') ? Number.parseFloat(part) : Number.parseFloat(part) * 1000));
}

(async () => {
  const outDir = path.resolve(arg('--out-dir', path.join(process.cwd(), 'mamastrophic-cobrar-state-fixture')));
  const screensDir = path.join(outDir, 'screens');
  const reportPath = path.join(outDir, 'COBRAR_STATE_FIXTURE_EVIDENCE.json');
  mkdirp(screensDir);
  const startedAt = new Date().toISOString();
  let browser;
  try {
    const resolved = loadPlaywright();
    const launched = await launch(resolved.chromium);
    browser = launched.browser;
    const page = await browser.newPage({ viewport: { width: 1024, height: 900 } });
    const attemptedExternalRequests = [];
    page.on('request', request => {
      const protocol = new URL(request.url()).protocol;
      if (!['file:', 'data:', 'blob:'].includes(protocol)) attemptedExternalRequests.push({ protocol, resourceType: request.resourceType() });
    });
    const fixturePath = path.resolve(__dirname, '..', 'fixtures', 'cobrar-states.html');
    await page.goto(pathToFileURL(fixturePath).href, { waitUntil: 'load' });
    const safety = await page.evaluate(() => ({
      scripts: document.scripts.length,
      forms: document.forms.length,
      links: document.querySelectorAll('a[href]').length,
      inlineHandlers: document.querySelectorAll('[onclick],[onsubmit],[onchange]').length,
      buttons: document.querySelectorAll('button').length
    }));
    const failures = [];
    if (safety.scripts || safety.forms || safety.links || safety.inlineHandlers || safety.buttons !== 6) failures.push({ type: 'FIXTURE_SAFETY_CONTRACT', safety });

    const cases = {};
    const normal = page.locator('[data-case="enabled-normal"] button');
    cases.enabledNormal = await normal.evaluate(element => ({ disabled: element.disabled, state: element.dataset.prismaState, rect: element.getBoundingClientRect().toJSON() }));
    if (cases.enabledNormal.disabled || cases.enabledNormal.state !== 'ready') failures.push({ type: 'ENABLED_NORMAL_INVALID' });
    await normal.screenshot({ path: path.join(screensDir, 'enabled-normal.png') });

    const hover = page.locator('[data-case="enabled-hover"] button');
    const hoverBefore = await hover.evaluate(element => { const style = getComputedStyle(element); return { transform: style.transform, borderColor: style.borderColor, boxShadow: style.boxShadow }; });
    await hover.hover();
    const hoverAfter = await hover.evaluate(element => { const style = getComputedStyle(element); return { disabled: element.disabled, hovered: element.matches(':hover'), transform: style.transform, borderColor: style.borderColor, boxShadow: style.boxShadow }; });
    cases.enabledHover = { before: hoverBefore, after: hoverAfter };
    if (hoverAfter.disabled || !hoverAfter.hovered || JSON.stringify(hoverBefore) === JSON.stringify({ transform: hoverAfter.transform, borderColor: hoverAfter.borderColor, boxShadow: hoverAfter.boxShadow })) failures.push({ type: 'ENABLED_HOVER_INVALID' });
    await hover.screenshot({ path: path.join(screensDir, 'enabled-hover.png') });

    await page.mouse.move(0, 0);
    const focus = page.locator('[data-case="focus-visible"] button');
    await page.locator('body').focus();
    for (let index = 0; index < 8 && !(await focus.evaluate(element => element === document.activeElement)); index++) await page.keyboard.press('Tab');
    cases.focusVisible = await focus.evaluate(element => ({ active: element === document.activeElement, focusVisible: element.matches(':focus-visible'), outlineWidth: getComputedStyle(element).outlineWidth }));
    if (!cases.focusVisible.active || !cases.focusVisible.focusVisible || Number.parseFloat(cases.focusVisible.outlineWidth) < 2) failures.push({ type: 'FOCUS_VISIBLE_INVALID' });
    await focus.screenshot({ path: path.join(screensDir, 'focus-visible.png') });

    const loading = page.locator('[data-case="loading"] button');
    cases.loading = await loading.evaluate(element => ({ disabled: element.disabled, ariaBusy: element.getAttribute('aria-busy'), state: element.dataset.prismaState, spinnerAnimation: getComputedStyle(element.querySelector('.cobrarIcon'), '::after').animationName }));
    if (!cases.loading.disabled || cases.loading.ariaBusy !== 'true' || cases.loading.state !== 'loading' || cases.loading.spinnerAnimation === 'none') failures.push({ type: 'LOADING_INVALID' });
    await loading.screenshot({ path: path.join(screensDir, 'loading.png') });

    await page.emulateMedia({ reducedMotion: 'reduce' });
    const reduced = page.locator('[data-case="reduced-motion"] button');
    cases.reducedMotion = await reduced.evaluate(element => ({ transitionDuration: getComputedStyle(element).transitionDuration, animationDuration: getComputedStyle(element).animationDuration }));
    if (durationMs(cases.reducedMotion.transitionDuration) > 1 || durationMs(cases.reducedMotion.animationDuration) > 1) failures.push({ type: 'REDUCED_MOTION_INVALID', value: cases.reducedMotion });
    await reduced.screenshot({ path: path.join(screensDir, 'reduced-motion.png') });

    const disabled = page.locator('[data-case="disabled"] button');
    cases.disabled = await disabled.evaluate(element => ({ disabled: element.disabled, ariaDisabled: element.getAttribute('aria-disabled'), state: element.dataset.prismaState, cursor: getComputedStyle(element).cursor }));
    if (!cases.disabled.disabled || cases.disabled.ariaDisabled !== 'true' || cases.disabled.state !== 'disabled') failures.push({ type: 'DISABLED_INVALID' });
    await disabled.screenshot({ path: path.join(screensDir, 'disabled.png') });

    for (const request of attemptedExternalRequests) failures.push({ type: 'EXTERNAL_REQUEST', ...request });
    const report = {
      schema: 'prisma.mamastrophic.safe-cobrar-state-fixture.v1',
      taskId: 'ATLASFIN_COBRAR_VISUAL_EVIDENCE_HARDENING_FINAL_V1',
      status: failures.length ? 'FAIL_SAFE_ISOLATED_STATE_FIXTURE' : 'PASS_SAFE_ISOLATED_STATE_FIXTURE',
      fixtureSafety: { ...safety, externalRequestCount: attemptedExternalRequests.length, productHandlersExecuted: 0, salePaymentApiDbNavigationExecuted: false },
      browser: { moduleName: resolved.moduleName, launchMode: launched.mode },
      cases,
      failures,
      startedAt,
      finishedAt: new Date().toISOString()
    };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    if (failures.length) { console.error(`FAIL_SAFE_ISOLATED_STATE_FIXTURE failures=${failures.length}`); process.exitCode = 2; }
    else console.log('PASS_SAFE_ISOLATED_STATE_FIXTURE states=6');
  } catch (error) {
    fs.writeFileSync(reportPath, JSON.stringify({ schema: 'prisma.mamastrophic.safe-cobrar-state-fixture.v1', taskId: 'ATLASFIN_COBRAR_VISUAL_EVIDENCE_HARDENING_FINAL_V1', status: 'FAIL_CLOSED_FIXTURE_ERROR', error: { name: error.name, message: String(error.message || error) }, startedAt, finishedAt: new Date().toISOString() }, null, 2));
    console.error(error.stack || String(error));
    process.exitCode = 2;
  } finally {
    if (browser) await browser.close();
  }
})();
