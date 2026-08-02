#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { legalEvidenceEnabled, applyLegalRedaction, sanitizeText, sanitizeUrl, sanitizeObject, sanitizeConsoleEntry, sanitizeNetworkEntry } = require('./surf8.legal-evidence.cjs');
const { createRequire } = require('module');

function arg(name, fallback = '') { const i = process.argv.indexOf(name); return (i >= 0 && i + 1 < process.argv.length) ? process.argv[i + 1] : fallback; }
function has(name) { return process.argv.includes(name); }
function mkdirp(p) { fs.mkdirSync(p, { recursive: true }); }
function writeJson(file, data) { mkdirp(path.dirname(file)); fs.writeFileSync(file, JSON.stringify(data, null, 2)); }
function safeName(value) { return String(value || 'item').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9_.-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 120) || 'item'; }
function uniq(arr) { const out = []; const seen = new Set(); for (const x of arr) { if (!x) continue; const r = path.resolve(String(x)); const k = r.toLowerCase(); if (!seen.has(k) && fs.existsSync(r)) { seen.add(k); out.push(r); } } return out; }
function ancestors(start) { const out = []; let p = path.resolve(start || process.cwd()); for (;;) { out.push(p); const next = path.dirname(p); if (next === p) break; p = next; } return out; }
function listPnpmCandidates(root) {
  const out = [];
  const pnpm = path.join(root, 'node_modules', '.pnpm');
  if (!fs.existsSync(pnpm)) return out;
  let names = [];
  try { names = fs.readdirSync(pnpm); } catch { return out; }
  for (const name of names) {
    if (name.startsWith('@playwright+test@')) out.push({ moduleName: '@playwright/test', file: path.join(pnpm, name, 'node_modules', '@playwright', 'test', 'index.js') });
    if (name.startsWith('playwright@')) out.push({ moduleName: 'playwright', file: path.join(pnpm, name, 'node_modules', 'playwright', 'index.js') });
  }
  return out;
}
function candidateRoots() {
  const envList = String(process.env.PRISMA_POINT_RESOLVE_ROOTS || '').split(';').filter(Boolean);
  const repo = process.env.PRISMA_REPO_ROOT || '';
  const app = process.env.PRISMA_APP_ROOT || '';
  const pc = process.env.PRISMA_PC_APP_ROOT || '';
  const tool = process.env.PRISMA_TOOL_ROOT || '';
  const derived = [];
  if (repo) derived.push(path.join(repo, 'apps', 'terminal-de-venta-system'));
  if (repo) derived.push(path.join(repo, 'apps', 'terminal-de-venta-system', 'products', 'pc', 'app'));
  return uniq([
    ...envList,
    app,
    pc,
    repo,
    tool,
    process.cwd(),
    ...derived,
    ...ancestors(__dirname),
    ...ancestors(process.cwd())
  ]);
}
function tryRequireFrom(root, name) {
  const base = fs.existsSync(path.join(root, 'package.json')) ? path.join(root, 'package.json') : path.join(root, 'noop.js');
  const req = createRequire(base);
  const resolved = req.resolve(name);
  return { mod: req(name), resolved, method: 'createRequire', root, moduleName: name };
}
function tryDirectFile(file, moduleName, root) {
  if (!fs.existsSync(file)) throw new Error('Direct candidate missing: ' + file);
  const req = createRequire(file);
  const mod = req(file);
  return { mod, resolved: file, method: 'direct-file', root, moduleName };
}
function resolvePlaywrightDetailed() {
  const roots = candidateRoots();
  const attempts = [];
  for (const root of roots) {
    for (const modName of ['@playwright/test', 'playwright']) {
      try {
        const hit = tryRequireFrom(root, modName);
        if (hit.mod && hit.mod.chromium) return { ok: true, chromium: hit.mod.chromium, moduleName: modName, root, resolved: hit.resolved, method: hit.method, attempts };
        attempts.push({ root, moduleName: modName, ok: false, error: 'module loaded but chromium export missing', resolved: hit.resolved, method: hit.method });
      } catch (e) {
        attempts.push({ root, moduleName: modName, ok: false, error: e && e.message ? e.message : String(e), method: 'createRequire' });
      }
    }
    const direct = [
      { moduleName: '@playwright/test', file: path.join(root, 'node_modules', '@playwright', 'test', 'index.js') },
      { moduleName: 'playwright', file: path.join(root, 'node_modules', 'playwright', 'index.js') },
      ...listPnpmCandidates(root)
    ];
    for (const cand of direct) {
      try {
        const hit = tryDirectFile(cand.file, cand.moduleName, root);
        if (hit.mod && hit.mod.chromium) return { ok: true, chromium: hit.mod.chromium, moduleName: cand.moduleName, root, resolved: cand.file, method: hit.method, attempts };
        attempts.push({ root, moduleName: cand.moduleName, ok: false, error: 'direct module loaded but chromium export missing', resolved: cand.file, method: 'direct-file' });
      } catch (e) {
        attempts.push({ root, moduleName: cand.moduleName, ok: false, error: e && e.message ? e.message : String(e), resolved: cand.file, method: 'direct-file' });
      }
    }
  }
  return { ok: false, roots, attempts };
}
function resolvePlaywright(reportsDir) {
  const r = resolvePlaywrightDetailed();
  if (reportsDir) writeJson(path.join(reportsDir, 'playwright-resolution.json'), { ...r, chromium: undefined });
  if (!r.ok) throw new Error('No pude resolver Playwright. Revisa playwright-resolution.json. Roots=' + (r.roots || []).join(' | '));
  return r;
}
function formatError(error) { return { name: error && error.name ? String(error.name) : typeof error, message: error && error.message ? String(error.message) : String(error), stack: error && error.stack ? String(error.stack) : null }; }

const selftestResolve = has('--selftest-resolve');
const surface = arg('--surface', 'tablet');
const port = Number(arg('--port', surface === 'tablet' ? '3120' : '3000'));
const route = arg('--route', surface === 'tablet' ? '/pos' : '/');
const exactSelector = arg('--selector', '');
const authoritySelector = arg('--authority-selector', exactSelector);
const componentUiId = arg('--component-ui-id', '');
const evidencePhase = arg('--evidence-phase', '');
const outDir = path.resolve(arg('--out-dir', path.join('F:\\descargasf', `mam point ${surface}`)));
const reportsDir = path.join(outDir, 'reports');
const screensDir = path.join(outDir, 'screens');
const domDir = path.join(outDir, 'dom');
mkdirp(reportsDir); mkdirp(screensDir); mkdirp(domDir);

if (selftestResolve) {
  try {
    const r = resolvePlaywright(reportsDir);
    writeJson(path.join(reportsDir, 'point-resolve-summary.json'), { status: 'PASS', moduleName: r.moduleName, root: r.root, resolved: r.resolved, method: r.method, createdAt: new Date().toISOString() });
    console.log(`PLAYWRIGHT_RESOLVED module=${r.moduleName} root=${r.root} method=${r.method} resolved=${r.resolved}`);
    process.exit(0);
  } catch (e) {
    writeJson(path.join(reportsDir, 'point-resolve-summary.json'), { status: 'FAIL', error: formatError(e), createdAt: new Date().toISOString() });
    console.error(e && e.stack ? e.stack : String(e));
    process.exit(2);
  }
}

const xArg = Number(arg('--x', '-1'));
const yArg = Number(arg('--y', '-1'));
const allowPartial = has('--allow-partial');
const viewportW = Number(process.env.PRISMA_POINT_VIEWPORT_W || '1365');
const viewportH = Number(process.env.PRISMA_POINT_VIEWPORT_H || '768');
const gotoTimeout = Number(process.env.PRISMA_POINT_GOTO_TIMEOUT_MS || '15000');
const gotoRetries = Number(process.env.PRISMA_POINT_GOTO_RETRIES || '1');
const settleMs = Number(process.env.PRISMA_POINT_SETTLE_MS || '700');
const noScreens = process.env.PRISMA_POINT_NO_SCREENSHOTS === '1';
const baseUrl = `http://127.0.0.1:${port}`;
const url = new URL(route || '/', baseUrl).toString();
const consoleMessages = [];
const networkFailures = [];
const httpErrors = [];

const exactComputedProperties = [
  'position','display','gridTemplateColumns','alignItems','gap','minHeight','padding','overflow',
  'border','borderColor','borderWidth','borderRadius','background','backgroundColor','backgroundImage',
  'boxShadow','color','cursor','font','textAlign','textShadow','transition','transform','filter','opacity'
];

async function computedSnapshot(locator, pseudo = null) {
  return locator.evaluate((el, args) => {
    const cs = getComputedStyle(el, args.pseudo);
    const computed = {};
    for (const property of args.properties) computed[property] = cs[property] || '';
    const rect = el.getBoundingClientRect();
    const attrs = {};
    for (const attr of Array.from(el.attributes || [])) {
      if (attr.name.startsWith('data-') || ['id','type','disabled','aria-disabled','aria-label'].includes(attr.name)) attrs[attr.name] = attr.value;
    }
    return {
      pseudo: args.pseudo,
      computed,
      rect: { x:rect.x, y:rect.y, left:rect.left, top:rect.top, right:rect.right, bottom:rect.bottom, width:rect.width, height:rect.height },
      attributes: attrs,
      disabled: Boolean(el.disabled),
      focusVisible: el.matches(':focus-visible'),
      text: String(el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 220),
      dom: `<${el.tagName.toLowerCase()} ${Array.from(el.attributes || []).filter(a => a.name.startsWith('data-') || ['id','type','disabled','aria-disabled','aria-label'].includes(a.name)).map(a => `${a.name}="${String(a.value).replace(/"/g, '&quot;')}"`).join(' ')}>`
    };
  }, { pseudo, properties: exactComputedProperties });
}

function defaultPoint(surfaceName, w, h) {
  if (surfaceName === 'tablet') return { x: Math.floor(w * 0.86), y: Math.floor(h * 0.55), reason: 'tablet-right-rail-default' };
  if (surfaceName === 'pc') return { x: Math.floor(w * 0.50), y: Math.floor(h * 0.50), reason: 'pc-center-default' };
  return { x: Math.floor(w * 0.50), y: Math.floor(h * 0.50), reason: 'center-default' };
}
const defPoint = defaultPoint(surface, viewportW, viewportH);
const point = { x: xArg >= 0 ? xArg : defPoint.x, y: yArg >= 0 ? yArg : defPoint.y, reason: (xArg >= 0 && yArg >= 0) ? 'explicit' : defPoint.reason };
async function gotoWithRetry(page) {
  let last = null;
  for (let i = 0; i <= gotoRetries; i++) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: gotoTimeout });
      await page.waitForLoadState('networkidle', { timeout: Math.min(7000, gotoTimeout) }).catch(() => {});
      await page.waitForTimeout(settleMs);
      return { ok: true, attempts: i + 1 };
    } catch (e) {
      last = e;
      if (i < gotoRetries) await page.waitForTimeout(650 * (i + 1));
    }
  }
  return { ok: false, error: formatError(last), attempts: gotoRetries + 1 };
}
function mdEscape(s) { return String(s || '').replace(/\|/g, '\\|').replace(/\n/g, ' '); }

(async () => {
  const startedAt = new Date().toISOString();
  let browser;
  try {
    const resolved = resolvePlaywright(reportsDir);
    const { chromium } = resolved;
    let browserLaunch = { mode: 'bundled-chromium' };
    try {
      browser = await chromium.launch({ headless: true });
    } catch (error) {
      const message = error && error.message ? String(error.message) : String(error);
      if (!message.includes("Executable doesn't exist")) throw error;
      browser = await chromium.launch({ headless: true, channel: 'msedge' });
      browserLaunch = { mode: 'system-channel', channel: 'msedge', fallbackReason: 'BUNDLED_CHROMIUM_EXECUTABLE_MISSING' };
    }
    const page = await browser.newPage({ viewport: { width: viewportW, height: viewportH } });
    page.on('console', msg => consoleMessages.push(sanitizeConsoleEntry({ type: msg.type(), text: msg.text().slice(0, 800) })));
    page.on('requestfailed', req => networkFailures.push(sanitizeNetworkEntry({ url: sanitizeUrl(req.url()), failure: req.failure() ? req.failure().errorText : 'unknown' })));
    page.on('response', response => {
      if (response.status() >= 400) httpErrors.push(sanitizeNetworkEntry({ url: sanitizeUrl(response.url()), status: response.status(), resourceType: response.request().resourceType() }));
    });
    const nav = await gotoWithRetry(page);
    if (!nav.ok && !allowPartial) throw new Error(`Navigation failed ${sanitizeUrl(url)}: ${nav.error ? sanitizeText(nav.error.message) : 'unknown'}`);
    const legalRedaction = await applyLegalRedaction(page).catch(error => ({ enabled: true, status: 'BLOCKED_UNREDACTED', error: sanitizeText(error && error.message ? error.message : String(error)) }));
    let exactEvidence = null;
    if (exactSelector) {
      const target = page.locator(exactSelector);
      const count = await target.count();
      if (count !== 1) throw new Error(`Exact target cardinality mismatch selector=${exactSelector} count=${count}`);
      const states = [];
      const base = await computedSnapshot(target);
      const beforePseudo = await computedSnapshot(target, '::before');
      states.push({ state: 'normal', status: 'PASS', snapshot: base, beforePseudo });
      states.push({ state: 'disabled', status: base.disabled ? 'PASS' : 'SKIPPED_STATE_NOT_REPRODUCIBLE_WITHOUT_PRODUCT_SIDE_EFFECT', snapshot: base });
      await target.hover({ timeout: gotoTimeout });
      await page.waitForTimeout(180);
      const hover = await computedSnapshot(target);
      states.push({ state: 'hover', status: 'PASS', snapshot: hover, beforePseudo: await computedSnapshot(target, '::before') });
      if (!noScreens) await target.screenshot({ path: path.join(screensDir, `${safeName(surface)}.${safeName(evidencePhase || 'capture')}.exact-target-hover.png`) });
      if (!base.disabled) {
        await page.keyboard.press('Tab');
        for (let i = 0; i < 80 && !(await target.evaluate(el => el === document.activeElement)); i++) await page.keyboard.press('Tab');
        const focus = await computedSnapshot(target);
        states.push({ state: 'focus-visible', status: focus.focusVisible ? 'PASS' : 'FAIL_FOCUS_VISIBLE_NOT_REACHED', snapshot: focus });
      } else {
        states.push({ state: 'focus-visible', status: 'SKIPPED_STATE_NOT_REPRODUCIBLE_WITHOUT_PRODUCT_SIDE_EFFECT', reason: 'Native disabled target is not focusable.' });
      }
      await page.emulateMedia({ reducedMotion: 'reduce' });
      states.push({ state: 'reduced-motion', status: 'PASS', snapshot: await computedSnapshot(target) });
      states.push({ state: 'loading', status: base.attributes['data-prisma-state'] === 'loading' ? 'PASS' : 'SKIPPED_STATE_NOT_REPRODUCIBLE_WITHOUT_PRODUCT_SIDE_EFFECT' });
      let targetScreenshot = null;
      if (!noScreens) {
        targetScreenshot = path.join(screensDir, `${safeName(surface)}.${safeName(evidencePhase || 'capture')}.exact-target.png`);
        await target.screenshot({ path: targetScreenshot });
      }
      exactEvidence = {
        schema: 'prisma.mamastrophic.exact-target-evidence.v1',
        taskId: 'ATLASFIN_COBRAR_FULL_GOVERNED_APPLICATION_V1',
        controlId: 'ATLASFIN.CONTROL.TABLET.POS.COBRAR.V1',
        componentUiId,
        phase: evidencePhase || 'UNSPECIFIED',
        status: states.some(row => String(row.status).startsWith('FAIL')) ? 'FAIL' : 'PASS',
        runtimeSelector: exactSelector,
        authoritySelector,
        route,
        viewport: { width: viewportW, height: viewportH, deviceScaleFactor: 1 },
        browserLaunch,
        targetScreenshot,
        states,
        console: consoleMessages,
        networkFailures,
        httpErrors,
        capturedAt: new Date().toISOString()
      };
      writeJson(path.join(reportsDir, 'exact-target-evidence.json'), exactEvidence);
      fs.writeFileSync(path.join(domDir, 'exact-target.dom.txt'), sanitizeText(base.dom), 'utf8');
    }
    let capture = await page.evaluate(({ point, surface, route, url }) => {
      function rectOf(el) { const r = el.getBoundingClientRect(); return { x:r.x,y:r.y,left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height }; }
      function dataAttrs(el) { const out={}; for (const a of Array.from(el.attributes || [])) if (a.name.startsWith('data-')) out[a.name]=a.value; return out; }
      function selectorGuess(el) {
        if (!el || !el.tagName) return '';
        const tag=el.tagName.toLowerCase();
        if (el.id) return `${tag}#${CSS.escape(el.id)}`;
        const cls=String(el.className || '').split(/\s+/).filter(Boolean).slice(0,4).map(c=>'.'+CSS.escape(c)).join('');
        const data=Array.from(el.attributes || []).find(a=>a.name.startsWith('data-') && a.value);
        if (data) return `${tag}[${data.name}="${String(data.value).replace(/"/g, '\\"')}"]${cls}`;
        return `${tag}${cls}`;
      }
      function computed(el) { const cs=getComputedStyle(el); const props=['position','zIndex','display','visibility','opacity','pointerEvents','background','backgroundColor','backgroundImage','backdropFilter','webkitBackdropFilter','filter','boxShadow','borderRadius','overflow','overflowX','overflowY','transform','mixBlendMode','isolation','contain','clipPath']; const out={}; for (const p of props) out[p]=cs[p] || ''; return out; }
      function textSample(el) { return String(el.innerText || el.textContent || '').replace(/\s+/g,' ').trim().slice(0,220); }
      function flags(el, cs, rect) { const bg=`${cs.background || ''} ${cs.backgroundColor || ''} ${cs.backgroundImage || ''}`.toLowerCase(); const z=Number.parseInt(cs.zIndex,10); return { containsPoint: rect.left<=point.x && rect.right>=point.x && rect.top<=point.y && rect.bottom>=point.y, hasNonTransparentBackground: (/rgba?\(/.test(bg) && !/rgba\([^)]*,\s*0\s*\)/.test(bg)) || (cs.backgroundImage && cs.backgroundImage !== 'none'), hasBackdropFilter: Boolean((cs.backdropFilter && cs.backdropFilter !== 'none') || (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== 'none')), hasFilter: Boolean(cs.filter && cs.filter !== 'none'), hasBoxShadow: Boolean(cs.boxShadow && cs.boxShadow !== 'none'), hasZIndex: !Number.isNaN(z), isFixedOrAbsolute: cs.position === 'fixed' || cs.position === 'absolute' || cs.position === 'sticky', mayObscure: (cs.opacity !== '0' && cs.visibility !== 'hidden' && cs.display !== 'none') }; }
      function pack(el, rank) { const r=rectOf(el); const cs=computed(el); return { rank, tag:el.tagName.toLowerCase(), id:el.id || '', className:String(el.className || ''), data:dataAttrs(el), selectorGuess:selectorGuess(el), textSample:textSample(el), rect:r, computed:cs, flags:flags(el,cs,r) }; }
      const stack = document.elementsFromPoint(point.x, point.y).map((el,i)=>pack(el,i+1));
      const allSuspicious = Array.from(document.querySelectorAll('body *')).map((el,i)=>pack(el,i+1)).filter(x => x.flags.mayObscure && (x.flags.hasNonTransparentBackground || x.flags.hasBackdropFilter || x.flags.hasFilter || x.flags.hasBoxShadow || x.flags.hasZIndex || x.flags.isFixedOrAbsolute)).slice(0, 500);
      return { surface, route, url, point, viewport:{ width:innerWidth, height:innerHeight, devicePixelRatio }, title:document.title, stack, suspiciousLayers:allSuspicious, capturedAt:new Date().toISOString() };
    }, { point, surface, route, url });
    capture.navigation = nav;
    capture.console = consoleMessages;
    capture.networkFailures = networkFailures;
    capture.httpErrors = httpErrors;
    capture.resolution = { moduleName: resolved.moduleName, root: resolved.root, resolved: resolved.resolved, method: resolved.method };
    capture.browserLaunch = browserLaunch;
    writeJson(path.join(reportsDir, 'point-stack.json'), capture);
    writeJson(path.join(domDir, `${safeName(surface)}.point-stack.dom.json`), capture);
    let screenshotPath = null;
    if (!noScreens) {
      await page.evaluate(({ point }) => {
        const old = document.getElementById('__mam_point_marker__');
        if (old) old.remove();
        const marker = document.createElement('div');
        marker.id = '__mam_point_marker__';
        marker.style.cssText = `position:fixed; left:${point.x-10}px; top:${point.y-10}px; width:20px; height:20px; border:3px solid red; border-radius:999px; z-index:2147483647; pointer-events:none; box-shadow:0 0 0 9999px rgba(255,0,0,0.06);`;
        document.body.appendChild(marker);
      }, { point });
      screenshotPath = path.join(screensDir, `${safeName(surface)}.${safeName(route)}.point.png`);
      await page.screenshot({ path: screenshotPath, fullPage: false });
    }
    const md = [];
    md.push(`# Point probe ${surface} ${route}`);
    md.push('');
    md.push(`- URL: ${sanitizeUrl(url)}`);
    md.push(`- Point: ${point.x}, ${point.y} (${point.reason})`);
    md.push(`- Playwright: ${resolved.moduleName} via ${resolved.method}`);
    md.push(`- Screenshot: ${screenshotPath || 'NoScreenshots'}`);
    md.push('');
    md.push('| Rank | Selector | Position | Z | Background | Rect | Text |');
    md.push('|---:|---|---|---|---|---|---|');
    for (const row of capture.stack) {
      const cs=row.computed, r=row.rect;
      md.push(`| ${row.rank} | ${mdEscape(row.selectorGuess)} | ${mdEscape(cs.position)} | ${mdEscape(cs.zIndex)} | ${mdEscape((cs.background || cs.backgroundColor || '').slice(0,90))} | ${Math.round(r.x)},${Math.round(r.y)} ${Math.round(r.width)}x${Math.round(r.height)} | ${mdEscape(row.textSample).slice(0,90)} |`);
    }
    fs.writeFileSync(path.join(reportsDir, 'point-stack.md'), md.join('\n'), 'utf8');
    writeJson(path.join(reportsDir, 'point-summary.json'), { status: exactEvidence && exactEvidence.status !== 'PASS' ? 'FAIL' : 'PASS', surface, route, url: sanitizeUrl(url), point, stackCount: capture.stack.length, suspiciousCount: capture.suspiciousLayers.length, screenshot: screenshotPath, exactEvidence, resolution: capture.resolution, legalRedaction, startedAt, finishedAt:new Date().toISOString() });
    console.log(`POINT_PROBE_PASS surface=${surface} route=${route} x=${point.x} y=${point.y}`);
    await browser.close();
    process.exit(0);
  } catch (e) {
    if (browser) await browser.close().catch(() => {});
    writeJson(path.join(reportsDir, 'point-summary.json'), { status: allowPartial ? 'PARTIAL' : 'FAIL', surface, route, url: sanitizeUrl(url), point, error: sanitizeObject(formatError(e)), console: consoleMessages, networkFailures, startedAt, finishedAt:new Date().toISOString() });
    console.error(e && e.stack ? e.stack : String(e));
    process.exit(allowPartial ? 0 : 2);
  }
})();
