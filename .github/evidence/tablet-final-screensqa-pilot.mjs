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

const products = [
  { id:'prod-coca-600', businessId:'biz_78b3c840796a4a4dad', sku:'COCA600', name:'Coca-Cola Original 600 ml', category:'Bebidas', barcode:'7501055300075', barcodes:['7501055300075'], priceCents:2200, stockOnHand:24, lowStockThreshold:6, isActive:true },
  { id:'prod-sabritas', businessId:'biz_78b3c840796a4a4dad', sku:'SABR45', name:'Sabritas Original 45 g', category:'Botanas', barcode:'7501011110076', barcodes:['7501011110076'], priceCents:1900, stockOnHand:18, lowStockThreshold:5, isActive:true },
  { id:'prod-lala', businessId:'biz_78b3c840796a4a4dad', sku:'LALA1L', name:'Leche Lala Entera 1 L', category:'Lácteos', barcode:'7501020511116', barcodes:['7501020511116'], priceCents:3100, stockOnHand:13, lowStockThreshold:4, isActive:true },
  { id:'prod-bimbo', businessId:'biz_78b3c840796a4a4dad', sku:'BIMBO620', name:'Pan Blanco Bimbo 620 g', category:'Panadería', barcode:'7501000110421', barcodes:['7501000110421'], priceCents:4800, stockOnHand:9, lowStockThreshold:3, isActive:true },
  { id:'prod-ciel', businessId:'biz_78b3c840796a4a4dad', sku:'CIEL1L', name:'Agua Ciel 1 L', category:'Bebidas', barcode:'7501055310883', barcodes:['7501055310883'], priceCents:1600, stockOnHand:32, lowStockThreshold:8, isActive:true },
  { id:'prod-nescafe', businessId:'biz_78b3c840796a4a4dad', sku:'NESCAFE120', name:'Nescafé Clásico 120 g', category:'Abarrotes', barcode:'7501058610553', barcodes:['7501058610553'], priceCents:8900, stockOnHand:7, lowStockThreshold:2, isActive:true }
];
const cart = [
  { product: products[0], qty: 2 },
  { product: products[1], qty: 1 }
];

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
    const response = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(base + '/pos')}`, { method: 'PUT' });
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
  const incidental404 = text === 'Failed to load resource: the server responded with a status of 404 (Not Found)' && !url;
  if (entry.level === 'error' && !text.toLowerCase().includes('favicon') && !url.endsWith('/favicon.ico') && !incidental404) {
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
    payload = { ok:true, data:{ status:{ state:'active', plan:'Tablet + PC Managed', assignmentState:'assigned', operationalDecision:'allow' } }, meta:{} };
  } else if (url.pathname === '/api/pos/sync/health/pc') {
    payload = { ok:true, enabled:true, status:'online', url:'http://pc.local', error:null };
  } else if (url.pathname === '/api/pos/products/search') {
    payload = { ok:true, data:{ products, count:products.length }, meta:{} };
  } else if (url.pathname === '/api/pos/products/resolve') {
    const code = url.searchParams.get('code') || '';
    const product = products.find(p => p.barcode === code || p.sku === code) || products[0];
    payload = { ok:true, data:{ product }, meta:{} };
  } else if (url.pathname === '/api/pos/sync/panel') {
    payload = { ok:true, data:{ summary:{ total:0,pending:0,failed:0,sent:0,acked:0,conflict:0,risk:'ok',headline:'Todo enviado',operatorMessage:'Sin pendientes.',offlineVisible:false,lastCheckedAt:'2026-08-26T10:00:00.000Z' }, items:[], diagnostics:['Venta local disponible','No hay pendientes visibles'] } };
  } else if (url.pathname === '/api/pos/sync/pull') {
    payload = { ok:true, data:{ stream:'catalog', targetBusinessId:'biz_78b3c840796a4a4dad', terminalId:'term_49103c7382d84663a3', pc:{ enabled:true, origin:'http://pc.local', exportPath:'/api/catalog/export' }, checkpoint:null, tableCounts:{ Product:products.length, PriceListItem:products.length } } };
  }
  if (payload !== null) {
    await cdp.send('Fetch.fulfillRequest', {
      requestId: params.requestId,
      responseCode: 200,
      responseHeaders: [{ name:'content-type', value:'application/json; charset=utf-8' }, { name:'cache-control', value:'no-store' }],
      body: b64(payload)
    });
  } else {
    await cdp.send('Fetch.continueRequest', { requestId: params.requestId });
  }
});

const cartJson = JSON.stringify(cart);
await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
  source: `try { localStorage.setItem('prisma.tablet.pos.activeCart.v2', ${JSON.stringify(cartJson)}); } catch {}`
});

async function evalv(expression) {
  const result = await cdp.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  return result.result?.value;
}

const url = `${base}/pos?screensqaPilot=${Date.now()}`;
await cdp.send('Page.navigate', { url });
const started = Date.now();
let body = '';
while (Date.now() - started < 45000) {
  body = String(await evalv("document.body ? document.body.innerText : ''") || '');
  const ready = await evalv("document.readyState === 'complete'");
  if (ready && body.includes('Buscar producto o escanear código') && body.includes('Ticket') && body.includes('Coca-Cola Original 600 ml') && body.includes('Cobrar')) break;
  await sleep(250);
}
if (!(body.includes('Buscar producto o escanear código') && body.includes('Ticket') && body.includes('Coca-Cola Original 600 ml') && body.includes('Cobrar'))) {
  throw new Error(`PILOT_POS_NOT_READY:${body.slice(0, 1800)}`);
}
await sleep(1000);

const meta = await evalv(`(() => {
  const b=document.body,e=document.documentElement;
  const cobrar=document.querySelector('[data-prisma-component="CheckoutButton"]');
  return {
    title:document.title,
    url:location.href,
    headings:[...document.querySelectorAll('h1,h2')].slice(0,8).map(x=>x.textContent.trim()).filter(Boolean),
    bodyLength:(b?.innerText||'').trim().length,
    clientWidth:e?.clientWidth||0,
    scrollWidth:Math.max(e?.scrollWidth||0,b?.scrollWidth||0),
    scrollHeight:Math.max(e?.scrollHeight||0,b?.scrollHeight||0),
    tabletMarkers:[...document.querySelectorAll('[data-surface="tablet"]')].length,
    productCards:[...document.querySelectorAll('[data-prisma-component="ProductCard"]')].length,
    cobrarPresent:Boolean(cobrar),
    cobrarDisabled:Boolean(cobrar?.disabled),
    cobrarText:cobrar?.textContent?.replace(/\s+/g,' ').trim()||''
  };
})()`);

if ((meta.bodyLength || 0) < 100) throw new Error('PILOT_POS_BODY_TOO_SMALL');
if ((meta.scrollWidth || 0) > (meta.clientWidth || 0) + 4) throw new Error(`PILOT_POS_HORIZONTAL_OVERFLOW:${meta.scrollWidth}>${meta.clientWidth}`);
if (!meta.cobrarPresent) throw new Error('PILOT_POS_COBRAR_MISSING');
if (meta.cobrarDisabled) throw new Error(`PILOT_POS_COBRAR_DISABLED:${meta.cobrarText}`);
if (runtimeErrors.length || consoleErrors.length || networkErrors.length) {
  throw new Error(`PILOT_POS_RUNTIME_ANOMALY:${JSON.stringify({ runtimeErrors, consoleErrors, networkErrors })}`);
}

const metrics = await cdp.send('Page.getLayoutMetrics');
const size = metrics.cssContentSize || metrics.contentSize || { width:1365, height:900 };
const width = Math.max(1365, Math.min(Math.ceil(size.width || 1365), 1800));
const height = Math.max(900, Math.min(Math.ceil(size.height || 900), 8000));
const screenshot = await cdp.send('Page.captureScreenshot', {
  format:'png', captureBeyondViewport:true, fromSurface:true,
  clip:{ x:0, y:0, width, height, scale:1 }
});
const screenshotName = '01-pos-pilot.png';
fs.writeFileSync(path.join(shots, screenshotName), Buffer.from(screenshot.data, 'base64'));

const report = {
  schemaVersion:'tablet.final.screensqa.pos.pilot.v1',
  productTarget:process.env.PRODUCT_TARGET || null,
  route:'/pos',
  screenshot:screenshotName,
  viewport:{ width:1365, height:900 },
  capture:{ width, height },
  fixture:{ kind:'runner-local-deterministic', products:products.length, cartLines:cart.length, productionData:false },
  meta,
  runtimeErrors,
  consoleErrors,
  networkErrors,
  requests
};
fs.writeFileSync(path.join(out, 'pilot-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log('PASS_TABLET_FINAL_SCREENSQA_PILOT_POS_1_1');
