import fs from 'node:fs';
import path from 'node:path';

const base = process.env.RUNTIME_URL || 'http://127.0.0.1:3120';
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9224);
const out = path.resolve(process.env.EVIDENCE_DIR || 'evidence/tablet-final-screensqa');
const shots = path.join(out, 'screenshots');
fs.mkdirSync(shots, { recursive: true });

const runtimeErrors = [];
const consoleErrors = [];
const networkErrors = [];
const requests = [];
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const b64 = value => Buffer.from(JSON.stringify(value)).toString('base64');

class Cdp {
  constructor(url) { this.url = url; this.id = 1; this.pending = new Map(); this.handlers = new Map(); }
  async connect() {
    this.ws = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('CDP_CONNECT_TIMEOUT')), 10000);
      this.ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once: true });
      this.ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('CDP_CONNECT_ERROR')); }, { once: true });
    });
    this.ws.addEventListener('message', async event => {
      const raw = typeof event.data === 'string' ? event.data : Buffer.from(await event.data.arrayBuffer()).toString();
      const message = JSON.parse(raw);
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        message.error ? pending.reject(new Error(`${pending.method}:${JSON.stringify(message.error)}`)) : pending.resolve(message.result || {});
        return;
      }
      for (const handler of this.handlers.get(message.method) || []) {
        Promise.resolve(handler(message.params || {})).catch(error => runtimeErrors.push(`handler:${message.method}:${error.stack || error}`));
      }
    });
  }
  on(method, handler) { this.handlers.set(method, [...(this.handlers.get(method) || []), handler]); }
  send(method, params = {}) {
    const id = this.id++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
}

let target;
for (let i = 0; i < 40 && !target; i++) {
  try {
    const response = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(base + '/')}`, { method: 'PUT' });
    if (response.ok) target = await response.json();
  } catch {}
  if (!target) await sleep(250);
}
if (!target) throw new Error('CHROME_DEBUG_TARGET_UNAVAILABLE');

const cdp = new Cdp(target.webSocketDebuggerUrl);
await cdp.connect();
for (const method of ['Page.enable', 'Runtime.enable', 'Log.enable', 'Network.enable']) await cdp.send(method);
await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1365, height: 900, deviceScaleFactor: 1, mobile: false });
await cdp.send('Fetch.enable', { patterns: [{ urlPattern: `${base}/api/*`, requestStage: 'Request' }] });

cdp.on('Runtime.exceptionThrown', params => runtimeErrors.push(`exception:${params.exceptionDetails?.text || 'unknown'}`));
cdp.on('Runtime.consoleAPICalled', params => {
  if (params.type !== 'error') return;
  const text = (params.args || []).map(item => item.value ?? item.description ?? '').join(' ') || 'console.error';
  if (!text.toLowerCase().includes('favicon')) consoleErrors.push(text);
});
cdp.on('Log.entryAdded', params => {
  const entry = params.entry || {};
  const text = String(entry.text || '');
  const url = String(entry.url || '');
  const accessory404 = text === 'Failed to load resource: the server responded with a status of 404 (Not Found)' && !url;
  if (entry.level === 'error' && !text.toLowerCase().includes('favicon') && !url.endsWith('/favicon.ico') && !accessory404) {
    consoleErrors.push(`log:${text}${url ? ` @ ${url}` : ''}`);
  }
});
cdp.on('Network.responseReceived', params => {
  const response = params.response || {};
  const status = Number(response.status || 0);
  const url = String(response.url || '');
  const type = String(params.type || '');
  if (status >= 400 && type !== 'Image' && type !== 'Other' && !url.endsWith('/favicon.ico')) networkErrors.push(`${status}:${type || 'Unknown'}:${url}`);
});
cdp.on('Fetch.requestPaused', async params => {
  const url = new URL(params.request.url);
  requests.push(`${params.request.method} ${url.pathname}${url.search}`);
  let payload = null;
  if (url.pathname === '/api/license/status') {
    payload = { ok: true, data: { status: { state: 'active', plan: 'PRISMA Operación', assignmentState: 'assigned', operationalDecision: 'allow' } } };
  } else if (url.pathname === '/api/pos/sync/health/pc') {
    payload = { ok: true, enabled: true, status: 'online', url: 'http://pc.local', error: null };
  }
  if (payload !== null) {
    await cdp.send('Fetch.fulfillRequest', {
      requestId: params.requestId,
      responseCode: 200,
      responseHeaders: [{ name: 'content-type', value: 'application/json; charset=utf-8' }, { name: 'cache-control', value: 'no-store' }],
      body: b64(payload)
    });
  } else {
    await cdp.send('Fetch.continueRequest', { requestId: params.requestId });
  }
});

async function evalv(expression) {
  const result = await cdp.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  return result.result?.value;
}

const url = `${base}/?screensqaPilot=${Date.now()}`;
await cdp.send('Page.navigate', { url });
const started = Date.now();
let body = '';
while (Date.now() - started < 35000) {
  body = String(await evalv("document.body ? document.body.innerText : ''") || '');
  const ready = await evalv("document.readyState === 'complete'");
  if (ready && body.includes('Inicio operativo')) break;
  await sleep(200);
}
if (!body.includes('Inicio operativo')) throw new Error(`PILOT_HOME_NOT_READY:${body.slice(0, 1200)}`);
await sleep(900);

const meta = await evalv(`(() => {
  const b = document.body, e = document.documentElement;
  return {
    title: document.title,
    url: location.href,
    headings: [...document.querySelectorAll('h1,h2')].slice(0, 5).map(x => x.textContent.trim()).filter(Boolean),
    bodyLength: (b?.innerText || '').trim().length,
    clientWidth: e?.clientWidth || 0,
    scrollWidth: Math.max(e?.scrollWidth || 0, b?.scrollWidth || 0),
    scrollHeight: Math.max(e?.scrollHeight || 0, b?.scrollHeight || 0),
    tabletMarkers: [...document.querySelectorAll('[data-surface="tablet"]')].length
  };
})()`);

if ((meta.bodyLength || 0) < 20) throw new Error('PILOT_BODY_TOO_SMALL');
if ((meta.scrollWidth || 0) > (meta.clientWidth || 0) + 4) throw new Error(`PILOT_HORIZONTAL_OVERFLOW:${meta.scrollWidth}>${meta.clientWidth}`);
if (runtimeErrors.length || consoleErrors.length || networkErrors.length) {
  throw new Error(`PILOT_RUNTIME_ANOMALY:${JSON.stringify({ runtimeErrors, consoleErrors, networkErrors })}`);
}

const metrics = await cdp.send('Page.getLayoutMetrics');
const size = metrics.cssContentSize || metrics.contentSize || { width: 1365, height: 900 };
const width = Math.max(1365, Math.min(Math.ceil(size.width || 1365), 1800));
const height = Math.max(900, Math.min(Math.ceil(size.height || 900), 8000));
const screenshot = await cdp.send('Page.captureScreenshot', {
  format: 'png', captureBeyondViewport: true, fromSurface: true,
  clip: { x: 0, y: 0, width, height, scale: 1 }
});
const screenshotName = '01-home-pilot.png';
fs.writeFileSync(path.join(shots, screenshotName), Buffer.from(screenshot.data, 'base64'));

const report = {
  schemaVersion: 'tablet.final.screensqa.pilot.v1',
  productTarget: process.env.PRODUCT_TARGET || null,
  route: '/',
  screenshot: screenshotName,
  viewport: { width: 1365, height: 900 },
  capture: { width, height },
  meta,
  runtimeErrors,
  consoleErrors,
  networkErrors,
  requests
};
fs.writeFileSync(path.join(out, 'pilot-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log('PASS_TABLET_FINAL_SCREENSQA_PILOT_HOME_1_1');
