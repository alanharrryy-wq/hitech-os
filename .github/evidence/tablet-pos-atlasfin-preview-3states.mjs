import fs from 'node:fs';
import path from 'node:path';

const base = process.env.RUNTIME_URL || 'http://127.0.0.1:3120';
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9224);
const out = path.resolve(process.env.EVIDENCE_DIR || 'evidence/tablet-pos-atlasfin-preview');
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
    const q = (url.searchParams.get('q') || '').trim().toLowerCase();
    const filtered = q ? products.filter(p => `${p.name} ${p.sku} ${p.category}`.toLowerCase().includes(q)) : products;
    payload = { ok:true, data:{ products:filtered, count:filtered.length }, meta:{} };
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

async function waitFor(predicate, label, timeout = 45000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evalv(predicate);
    if (value) return value;
    await sleep(250);
  }
  throw new Error(`PREVIEW_WAIT_TIMEOUT:${label}`);
}

async function capture(name) {
  const metrics = await cdp.send('Page.getLayoutMetrics');
  const size = metrics.cssContentSize || metrics.contentSize || { width:1365, height:900 };
  const width = Math.max(1365, Math.min(Math.ceil(size.width || 1365), 1800));
  const height = Math.max(900, Math.min(Math.ceil(size.height || 900), 8000));
  const screenshot = await cdp.send('Page.captureScreenshot', {
    format:'png', captureBeyondViewport:true, fromSurface:true,
    clip:{ x:0, y:0, width, height, scale:1 }
  });
  fs.writeFileSync(path.join(shots, name), Buffer.from(screenshot.data, 'base64'));
  const state = await evalv(`(() => ({
    url: location.href,
    body: (document.body?.innerText || '').slice(0,3000),
    productCards: document.querySelectorAll('[data-prisma-component="ProductCard"]').length,
    ticketRows: document.querySelectorAll('[data-prisma-component="CartItemRow"]').length,
    activeCategory: [...document.querySelectorAll('button')].map(x=>({t:(x.textContent||'').replace(/\\s+/g,' ').trim(), p:x.getAttribute('aria-pressed')})).find(x=>x.p==='true') || null,
    ticketOptionsOpen: [...document.querySelectorAll('details')].some(x => x.open && (x.textContent || '').includes('Opciones de ticket')),
    width: document.documentElement.clientWidth,
    scrollWidth: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0)
  }))()`);
  return { name, width, height, state };
}

await cdp.send('Page.navigate', { url: `${base}/pos?atlasfinPreview=${Date.now()}` });
await waitFor(`(() => {
  const t=document.body?.innerText||'';
  return document.readyState==='complete' && t.includes('Buscar producto o escanear código') && t.includes('Ticket') && t.includes('Coca-Cola Original 600 ml') && t.includes('Cobrar');
})()`, 'initial-pos');
await sleep(900);

const states = [];
states.push(await capture('01-pos-overview.png'));

const searchApplied = await evalv(`(() => {
  const input=[...document.querySelectorAll('input')].find(x => (x.placeholder||'').includes('Buscar producto'));
  if(!input) return false;
  const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
  if(!setter) return false;
  setter.call(input,'coca');
  input.dispatchEvent(new Event('input',{bubbles:true}));
  input.dispatchEvent(new Event('change',{bubbles:true}));
  return true;
})()`);
if (!searchApplied) throw new Error('PREVIEW_SEARCH_INPUT_NOT_FOUND');
await waitFor(`(() => {
  const t=document.body?.innerText||'';
  return t.includes('Coca-Cola Original 600 ml') && document.querySelectorAll('[data-prisma-component="ProductCard"]').length===1;
})()`, 'search-coca');
await sleep(650);
states.push(await capture('02-pos-search-coca.png'));

const categoryReady = await evalv(`(() => {
  const input=[...document.querySelectorAll('input')].find(x => (x.placeholder||'').includes('Buscar producto'));
  const setter=input && Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
  if(input && setter){ setter.call(input,''); input.dispatchEvent(new Event('input',{bubbles:true})); input.dispatchEvent(new Event('change',{bubbles:true})); }
  return true;
})()`);
if (!categoryReady) throw new Error('PREVIEW_CLEAR_SEARCH_FAILED');
await waitFor(`document.querySelectorAll('[data-prisma-component="ProductCard"]').length >= 6`, 'catalog-restored');
const clicked = await evalv(`(() => {
  const button=[...document.querySelectorAll('button')].find(x => (x.textContent||'').replace(/\\s+/g,' ').trim()==='Bebidas');
  if(!button) return false;
  button.click();
  const details=[...document.querySelectorAll('details')].find(x => (x.textContent||'').includes('Opciones de ticket'));
  if(details) details.open=true;
  return true;
})()`);
if (!clicked) throw new Error('PREVIEW_BEBIDAS_CATEGORY_NOT_FOUND');
await waitFor(`(() => {
  const t=document.body?.innerText||'';
  return t.includes('Coca-Cola Original 600 ml') && t.includes('Agua Ciel 1 L') && document.querySelectorAll('[data-prisma-component="ProductCard"]').length===2;
})()`, 'bebidas-filter');
await sleep(650);
states.push(await capture('03-pos-bebidas-ticket-options.png'));

for (const row of states) {
  if ((row.state.scrollWidth || 0) > (row.state.width || 0) + 4) throw new Error(`PREVIEW_HORIZONTAL_OVERFLOW:${row.name}:${row.state.scrollWidth}>${row.state.width}`);
}
if (runtimeErrors.length || consoleErrors.length || networkErrors.length) {
  throw new Error(`PREVIEW_RUNTIME_ANOMALY:${JSON.stringify({runtimeErrors,consoleErrors,networkErrors})}`);
}

const report = {
  schemaVersion:'tablet.pos.atlasfin.preview.3states.v1',
  route:'/pos',
  viewport:{ width:1365, height:900 },
  productionData:false,
  visualCertification:false,
  states,
  runtimeErrors,
  consoleErrors,
  networkErrors,
  requests
};
fs.writeFileSync(path.join(out, 'preview-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log('PASS_TABLET_POS_ATLASFIN_PREVIEW_3_STATES');
