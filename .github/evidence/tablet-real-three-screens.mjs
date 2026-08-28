import fs from 'node:fs';
import path from 'node:path';

const base = process.env.RUNTIME_URL || 'http://127.0.0.1:3120';
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9224);
const out = path.resolve(process.env.EVIDENCE_DIR || 'evidence/tablet-real-three-screens');
const shots = path.join(out, 'screenshots');
fs.mkdirSync(shots, { recursive: true });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const b64json = (value) => Buffer.from(JSON.stringify(value)).toString('base64');
const runtimeErrors = [];
const consoleErrors = [];
const networkErrors = [];
const apiRequests = [];
const captures = [];

const businessId = 'biz_78b3c840796a4a4dad';
const terminalId = 'term_49103c7382d84663a3';
const storeId = 'store_00728649f3804a9e82';

const products = [
  { id:'prod-coca-600', businessId, sku:'COCA600', name:'Coca-Cola Original 600 ml', category:'Bebidas', barcode:'7501055300075', barcodes:['7501055300075'], priceCents:2200, costCents:1400, stockOnHand:24, lowStockThreshold:6, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-sabritas', businessId, sku:'SABR45', name:'Sabritas Original 45 g', category:'Botanas', barcode:'7501011110076', barcodes:['7501011110076'], priceCents:1900, costCents:1100, stockOnHand:3, lowStockThreshold:5, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-lala', businessId, sku:'LALA1L', name:'Leche Lala Entera 1 L', category:'Lácteos', barcode:'7501020511116', barcodes:['7501020511116'], priceCents:3100, costCents:2200, stockOnHand:13, lowStockThreshold:4, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-bimbo', businessId, sku:'BIMBO620', name:'Pan Blanco Bimbo 620 g', category:'Panadería', barcode:'7501000110421', barcodes:['7501000110421'], priceCents:4800, costCents:3300, stockOnHand:0, lowStockThreshold:3, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-ciel', businessId, sku:'CIEL1L', name:'Agua Ciel 1 L', category:'Bebidas', barcode:'7501055310883', barcodes:['7501055310883'], priceCents:1600, costCents:900, stockOnHand:32, lowStockThreshold:8, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-nescafe', businessId, sku:'NESCAFE120', name:'Nescafé Clásico 120 g', category:'Abarrotes', barcode:'7501058610553', barcodes:['7501058610553'], priceCents:8900, costCents:6200, stockOnHand:7, lowStockThreshold:8, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-trident', businessId, sku:'TRIDENT18', name:'Trident Menta 18 piezas', category:'Dulces', barcode:'7622201802558', barcodes:['7622201802558'], priceCents:2100, costCents:1300, stockOnHand:40, lowStockThreshold:10, isActive:true, updatedAt:'2026-08-28T06:00:00.000Z' },
  { id:'prod-inactive', businessId, sku:'JUGOOLD', name:'Jugo naranja 355 ml', category:'Bebidas', barcode:'7500000000001', barcodes:['7500000000001'], priceCents:2500, costCents:1500, stockOnHand:8, lowStockThreshold:4, isActive:false, updatedAt:'2026-08-28T06:00:00.000Z' }
];

const salesSummary = {
  businessId,
  terminalId,
  date:'2026-08-28',
  salesCount:5,
  ticketsClosed:5,
  totalCents:495900,
  averageTicketCents:99180,
  unitsSold:13,
  topProducts:[
    { productId:'prod-coca-600', sku:'COCA600', name:'Coca-Cola Original 600 ml', qty:5, totalCents:11000 },
    { productId:'prod-sabritas', sku:'SABR45', name:'Sabritas Original 45 g', qty:3, totalCents:5700 }
  ],
  tickets:[
    { saleId:'sale-001', folio:'TC-000156', businessId, terminalId, cashSessionId:'shift-real-shot', clientRequestId:'req-156', cashier:'Ana Caja', status:'COMPLETED', createdAt:'2026-08-28T19:25:00.000Z', completedAt:'2026-08-28T19:27:00.000Z', paymentMethod:'CARD', totalCents:78500, returnSummary:null, lineCount:2, unitsSold:3, lines:[{id:'sl-1',productId:'prod-coca-600',sku:'COCA600',productName:'Coca-Cola Original 600 ml',qty:2,priceCents:2200,totalCents:4400},{id:'sl-2',productId:'prod-lala',sku:'LALA1L',productName:'Leche Lala Entera 1 L',qty:1,priceCents:3100,totalCents:3100}] },
    { saleId:'sale-002', folio:'TC-000155', businessId, terminalId, cashSessionId:'shift-real-shot', clientRequestId:'req-155', cashier:'Carlos Ruiz', status:'COMPLETED', createdAt:'2026-08-28T19:10:00.000Z', completedAt:'2026-08-28T19:12:00.000Z', paymentMethod:'CASH', totalCents:32000, returnSummary:null, lineCount:2, unitsSold:2, lines:[{id:'sl-3',productId:'prod-sabritas',sku:'SABR45',productName:'Sabritas Original 45 g',qty:1,priceCents:1900,totalCents:1900},{id:'sl-4',productId:'prod-ciel',sku:'CIEL1L',productName:'Agua Ciel 1 L',qty:1,priceCents:1600,totalCents:1600}] },
    { saleId:'sale-003', folio:'TC-000154', businessId, terminalId, cashSessionId:'shift-real-shot', clientRequestId:'req-154', cashier:'María Hernández', status:'COMPLETED', createdAt:'2026-08-28T18:57:00.000Z', completedAt:'2026-08-28T18:58:00.000Z', paymentMethod:'CARD', totalCents:125000, returnSummary:null, lineCount:3, unitsSold:4, lines:[{id:'sl-5',productId:'prod-nescafe',sku:'NESCAFE120',productName:'Nescafé Clásico 120 g',qty:1,priceCents:8900,totalCents:8900}] },
    { saleId:'sale-004', folio:'TC-000153', businessId, terminalId, cashSessionId:'shift-real-shot', clientRequestId:'req-153', cashier:'Carlos Ruiz', status:'COMPLETED', createdAt:'2026-08-28T18:42:00.000Z', completedAt:'2026-08-28T18:45:00.000Z', paymentMethod:'TRANSFER', totalCents:295000, returnSummary:null, lineCount:2, unitsSold:2, lines:[{id:'sl-6',productId:'prod-bimbo',sku:'BIMBO620',productName:'Pan Blanco Bimbo 620 g',qty:1,priceCents:4800,totalCents:4800}] },
    { saleId:'sale-005', folio:'TC-000152', businessId, terminalId, cashSessionId:'shift-real-shot', clientRequestId:'req-152', cashier:'Ana Caja', status:'COMPLETED', createdAt:'2026-08-28T18:28:00.000Z', completedAt:'2026-08-28T18:29:00.000Z', paymentMethod:'CASH', totalCents:14500, returnSummary:null, lineCount:1, unitsSold:2, lines:[{id:'sl-7',productId:'prod-trident',sku:'TRIDENT18',productName:'Trident Menta 18 piezas',qty:2,priceCents:2100,totalCents:4200}] }
  ]
};

const shift = {
  id:'shift-real-shot', businessId, storeId, terminalId,
  cashierId:'cashier-ana', cashier:'Ana Caja', status:'OPEN',
  openedAt:'2026-08-28T14:00:00.000Z', closedAt:null,
  cashStartCents:500000, cashEndCents:null, expectedCashCents:845000,
  varianceCents:null, salesCount:28, salesTotalCents:2478050,
  movementCount:3, canSell:true, canClose:true,
  operatorMessage:'Turno abierto y listo para operar.'
};

class Cdp {
  constructor(url) { this.url = url; this.id = 1; this.pending = new Map(); this.handlers = new Map(); }
  async connect() {
    this.ws = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('CDP_CONNECT_TIMEOUT')), 10000);
      this.ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once:true });
      this.ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('CDP_CONNECT_ERROR')); }, { once:true });
    });
    this.ws.addEventListener('message', async (event) => {
      const raw = typeof event.data === 'string' ? event.data : Buffer.from(await event.data.arrayBuffer()).toString();
      const message = JSON.parse(raw);
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(`${pending.method}:${JSON.stringify(message.error)}`));
        else pending.resolve(message.result || {});
        return;
      }
      for (const handler of this.handlers.get(message.method) || []) {
        Promise.resolve(handler(message.params || {})).catch((error) => runtimeErrors.push(`handler:${message.method}:${error.stack || error}`));
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
for (let i = 0; i < 50 && !target; i++) {
  try {
    const response = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(base + '/stock')}`, { method:'PUT' });
    if (response.ok) target = await response.json();
  } catch {}
  if (!target) await sleep(250);
}
if (!target) throw new Error('CHROME_DEBUG_TARGET_UNAVAILABLE');

const cdp = new Cdp(target.webSocketDebuggerUrl);
await cdp.connect();
for (const method of ['Page.enable','Runtime.enable','Log.enable','Network.enable']) await cdp.send(method);
await cdp.send('Emulation.setDeviceMetricsOverride', { width:1365, height:900, deviceScaleFactor:1, mobile:false });
await cdp.send('Fetch.enable', { patterns:[{ urlPattern:`${base}/api/*`, requestStage:'Request' }] });

cdp.on('Runtime.exceptionThrown', (params) => runtimeErrors.push(`exception:${params.exceptionDetails?.text || 'unknown'}`));
cdp.on('Runtime.consoleAPICalled', (params) => {
  if (params.type !== 'error') return;
  const text = (params.args || []).map((item) => item.value ?? item.description ?? '').join(' ') || 'console.error';
  if (!text.toLowerCase().includes('favicon')) consoleErrors.push(text);
});
cdp.on('Log.entryAdded', (params) => {
  const entry = params.entry || {};
  const text = String(entry.text || '');
  const url = String(entry.url || '');
  if (entry.level === 'error' && !text.toLowerCase().includes('favicon') && !url.endsWith('/favicon.ico')) {
    const incidental = text.includes('404') && (url.endsWith('.png') || url.endsWith('.jpg') || url.endsWith('.webp'));
    if (!incidental) consoleErrors.push(`log:${text}${url ? ` @ ${url}` : ''}`);
  }
});
cdp.on('Network.responseReceived', (params) => {
  const response = params.response || {};
  const status = Number(response.status || 0);
  const url = String(response.url || '');
  const type = String(params.type || '');
  if (status >= 400 && ['XHR','Fetch','Document','Script','Stylesheet'].includes(type) && !url.endsWith('/favicon.ico')) {
    networkErrors.push(`${status}:${type}:${url}`);
  }
});

cdp.on('Fetch.requestPaused', async (params) => {
  const url = new URL(params.request.url);
  apiRequests.push(`${params.request.method} ${url.pathname}${url.search}`);
  let payload = null;
  if (url.pathname === '/api/pos/products/search') {
    const q = (url.searchParams.get('q') || '').trim().toLowerCase();
    const filtered = q ? products.filter((p) => `${p.name} ${p.sku} ${p.category}`.toLowerCase().includes(q)) : products;
    payload = { ok:true, data:{ products:filtered, count:filtered.length }, meta:{ source:'runner-local-screenshot-fixture' } };
  } else if (url.pathname === '/api/pos/products/resolve') {
    const code = url.searchParams.get('code') || '';
    const product = products.find((p) => p.barcode === code || p.sku === code) || products[0];
    payload = { ok:true, data:{ product }, meta:{ source:'runner-local-screenshot-fixture' } };
  } else if (url.pathname === '/api/pos/sales/today') {
    payload = { ok:true, data:{ summary:salesSummary }, meta:{ source:'runner-local-screenshot-fixture' } };
  } else if (url.pathname === '/api/pos/shift/current') {
    payload = { ok:true, data:{ shift }, meta:{ source:'runner-local-screenshot-fixture' } };
  } else if (url.pathname === '/api/license/status') {
    payload = { ok:true, data:{ status:{ state:'development', plan:'DEVELOPMENT', assignmentState:'assigned', operationalDecision:'allow' } }, meta:{} };
  } else if (url.pathname === '/api/pos/sync/health/pc') {
    payload = { ok:true, enabled:true, status:'online', url:'http://pc.local', error:null };
  }
  if (payload !== null) {
    await cdp.send('Fetch.fulfillRequest', {
      requestId:params.requestId,
      responseCode:200,
      responseHeaders:[{name:'content-type',value:'application/json; charset=utf-8'},{name:'cache-control',value:'no-store'}],
      body:b64json(payload)
    });
  } else {
    await cdp.send('Fetch.continueRequest', { requestId:params.requestId });
  }
});

async function evalv(expression) {
  const result = await cdp.send('Runtime.evaluate', { expression, returnByValue:true, awaitPromise:true });
  if (result.exceptionDetails) throw new Error(`EVAL_EXCEPTION:${result.exceptionDetails.text || 'unknown'}`);
  return result.result?.value;
}

async function waitFor(expression, label, timeout = 45000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    try {
      if (await evalv(expression)) return;
    } catch {}
    await sleep(250);
  }
  const state = await evalv(`(() => ({url:location.href,title:document.title,body:(document.body?.innerText||'').slice(0,5000),readyState:document.readyState}))()`);
  fs.writeFileSync(path.join(out, `diagnostic-${label}.json`), JSON.stringify(state, null, 2) + '\n');
  const png = await cdp.send('Page.captureScreenshot', { format:'png', fromSurface:true, captureBeyondViewport:false });
  fs.writeFileSync(path.join(shots, `00-diagnostic-${label}.png`), Buffer.from(png.data, 'base64'));
  throw new Error(`WAIT_TIMEOUT:${label}:${JSON.stringify(state)}`);
}

async function capture(route, fileName, readyExpression, label) {
  const beforeRuntime = runtimeErrors.length;
  const beforeConsole = consoleErrors.length;
  const beforeNetwork = networkErrors.length;
  await cdp.send('Page.navigate', { url:`${base}${route}?realScreens=${Date.now()}` });
  await waitFor(`document.readyState === 'complete' || document.readyState === 'interactive'`, `${label}-document`, 30000);
  await waitFor(readyExpression, label, 45000);
  await sleep(1200);
  await evalv(`window.scrollTo(0,0); true`);
  await sleep(250);
  const png = await cdp.send('Page.captureScreenshot', { format:'png', fromSurface:true, captureBeyondViewport:false });
  const filePath = path.join(shots, fileName);
  fs.writeFileSync(filePath, Buffer.from(png.data, 'base64'));
  const state = await evalv(`(() => ({
    route:location.pathname,
    title:document.title,
    body:(document.body?.innerText||'').slice(0,3500),
    width:document.documentElement.clientWidth,
    height:document.documentElement.clientHeight,
    scrollWidth:Math.max(document.documentElement.scrollWidth,document.body?.scrollWidth||0),
    scrollHeight:Math.max(document.documentElement.scrollHeight,document.body?.scrollHeight||0)
  }))()`);
  captures.push({
    route,
    fileName,
    bytes:fs.statSync(filePath).size,
    state,
    newRuntimeErrors:runtimeErrors.slice(beforeRuntime),
    newConsoleErrors:consoleErrors.slice(beforeConsole),
    newNetworkErrors:networkErrors.slice(beforeNetwork)
  });
}

await capture(
  '/stock',
  '01-inventario-real.png',
  `(() => { const t=document.body?.innerText||''; return t.includes('Existencias para vender') && t.includes('Coca-Cola Original 600 ml') && t.includes('Sabritas Original 45 g'); })()`,
  'inventario'
);

await capture(
  '/sales/today',
  '02-ventas-de-hoy-real.png',
  `(() => { const t=document.body?.innerText||''; return t.includes('Ventas de hoy') && t.includes('TC-000156') && t.includes('TC-000153'); })()`,
  'ventas-hoy'
);

await capture(
  '/shift',
  '03-turno-caja-real.png',
  `(() => { const t=document.body?.innerText||''; return t.includes('Turno abierto') && t.includes('Caja del dia') && t.includes('Contar y cerrar caja'); })()`,
  'turno-caja'
);

const unexpected = {
  runtimeErrors,
  consoleErrors:[...new Set(consoleErrors)],
  networkErrors:[...new Set(networkErrors)]
};
fs.writeFileSync(path.join(out, 'browser-results.json'), JSON.stringify({ captures, apiRequests:[...new Set(apiRequests)], unexpected }, null, 2) + '\n');

if (captures.length !== 3) throw new Error(`CAPTURE_COUNT:${captures.length}`);
if (captures.some((capture) => capture.bytes < 50000)) throw new Error('SCREENSHOT_TOO_SMALL');
if (runtimeErrors.length) throw new Error(`RUNTIME_ERRORS:${JSON.stringify(runtimeErrors)}`);
if (consoleErrors.length) throw new Error(`CONSOLE_ERRORS:${JSON.stringify([...new Set(consoleErrors)])}`);
if (networkErrors.length) throw new Error(`NETWORK_ERRORS:${JSON.stringify([...new Set(networkErrors)])}`);

console.log('PASS_TABLET_REAL_THREE_SCREENS');
