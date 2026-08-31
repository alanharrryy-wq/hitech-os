import fs from 'node:fs';
import path from 'node:path';

const base = process.env.RUNTIME_URL || 'http://127.0.0.1:3120';
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9224);
const out = path.resolve(process.env.EVIDENCE_DIR || 'evidence/tablet-inventory-primary-exact');
const phase = process.env.EVIDENCE_PHASE || 'UNKNOWN';
const shots = path.join(out, 'screenshots');
fs.mkdirSync(shots, { recursive: true });

const runtimeErrors = [];
const consoleErrors = [];
const networkErrors = [];
const requests = [];
const forbiddenMutationRequests = [];
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const b64 = value => Buffer.from(JSON.stringify(value)).toString('base64');

const products = [
  { id:'prod-coca-600', businessId:'biz_inventory_visual', sku:'COCA600', name:'Coca-Cola Original 600 ml', category:'Bebidas', barcode:'7501055300075', barcodes:['7501055300075'], priceCents:2200, stockOnHand:24, lowStockThreshold:6, isActive:true },
  { id:'prod-sabritas', businessId:'biz_inventory_visual', sku:'SABR45', name:'Sabritas Original 45 g', category:'Botanas', barcode:'7501011110076', barcodes:['7501011110076'], priceCents:1900, stockOnHand:18, lowStockThreshold:5, isActive:true }
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
  async close() {
    if (!this.ws || this.ws.readyState === WebSocket.CLOSED) return;
    await new Promise(resolve => {
      const timer = setTimeout(resolve, 1500);
      this.ws.addEventListener('close', () => { clearTimeout(timer); resolve(); }, { once: true });
      this.ws.close();
    });
  }
}

let target;
for (let i = 0; i < 40 && !target; i++) {
  try {
    const response = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent('about:blank')}`, { method: 'PUT' });
    if (response.ok) target = await response.json();
  } catch {}
  if (!target) await sleep(250);
}
if (!target) throw new Error('CHROME_DEBUG_TARGET_UNAVAILABLE');

const cdp = new Cdp(target.webSocketDebuggerUrl);
await cdp.connect();
for (const method of ['Page.enable', 'Runtime.enable', 'Log.enable', 'Network.enable']) await cdp.send(method);
await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1365, height: 1000, deviceScaleFactor: 1, mobile: false });
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
  if (entry.level === 'error' && !text.toLowerCase().includes('favicon') && !url.endsWith('/favicon.ico')) consoleErrors.push(`log:${text}${url ? ` @ ${url}` : ''}`);
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
  const method = String(params.request.method || 'GET').toUpperCase();
  requests.push(`${method} ${url.pathname}${url.search}`);
  if (url.pathname === '/api/pos/inventory/operations' && method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
    forbiddenMutationRequests.push(`${method} ${url.pathname}`);
    await cdp.send('Fetch.failRequest', { requestId: params.requestId, errorReason: 'BlockedByClient' });
    return;
  }
  let payload = null;
  if (url.pathname === '/api/license/status') {
    payload = { ok:true, data:{ status:{ state:'active', plan:'Tablet + PC Managed', assignmentState:'assigned', operationalDecision:'allow' } }, meta:{} };
  } else if (url.pathname === '/api/pos/sync/health/pc') {
    payload = { ok:true, enabled:true, status:'online', url:'http://pc.fixture', error:null };
  } else if (url.pathname === '/api/pos/products/search') {
    payload = { ok:true, data:{ products, count:products.length }, meta:{} };
  } else if (url.pathname === '/api/pos/products/resolve') {
    payload = { ok:true, data:{ product:products[0] }, meta:{} };
  } else if (url.pathname === '/api/pos/sync/panel') {
    payload = { ok:true, data:{ summary:{ total:0,pending:0,failed:0,sent:0,acked:0,conflict:0,risk:'ok',headline:'Todo enviado',operatorMessage:'Sin pendientes.',offlineVisible:false,lastCheckedAt:'2026-08-31T15:00:00.000Z' }, items:[], diagnostics:[] } };
  } else if (url.pathname === '/api/pos/sync/pull') {
    payload = { ok:true, data:{ stream:'catalog', targetBusinessId:'biz_inventory_visual', terminalId:'term_inventory_visual', pc:{ enabled:true, origin:'http://pc.fixture', exportPath:'/api/catalog/export' }, checkpoint:null, tableCounts:{ Product:products.length, PriceListItem:products.length } } };
  } else if (url.pathname === '/api/pos/inventory/operations' && method === 'GET') {
    payload = { ok:true, data:{ purchaseOrders:[], recentCounts:[] }, meta:{} };
  }
  if (payload !== null) {
    await cdp.send('Fetch.fulfillRequest', { requestId: params.requestId, responseCode: 200, responseHeaders:[{name:'content-type',value:'application/json; charset=utf-8'},{name:'cache-control',value:'no-store'}], body:b64(payload) });
  } else {
    await cdp.send('Fetch.continueRequest', { requestId: params.requestId });
  }
});

async function evalv(expression) {
  const result = await cdp.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(`EVAL_EXCEPTION:${result.exceptionDetails.text || 'unknown'}`);
  return result.result?.value;
}

const url = `${base}/inventory?inventoryPrimaryEvidence=${Date.now()}`;
await cdp.send('Page.navigate', { url });
const started = Date.now();
let body = '';
while (Date.now() - started < 45000) {
  body = String(await evalv("document.body ? document.body.innerText : ''") || '');
  const ready = await evalv("document.readyState === 'complete'");
  const lower = body.toLowerCase();
  if (ready && lower.includes('control de existencias') && lower.includes('abrir operaciones') && lower.includes('coca-cola original 600 ml')) break;
  await sleep(250);
}
if (!body.toLowerCase().includes('abrir operaciones')) throw new Error(`INVENTORY_NOT_READY:${body.slice(0,1600)}`);

const opened = await evalv(`(() => {
  const button=[...document.querySelectorAll('button')].find(el => (el.textContent||'').trim()==='Abrir operaciones');
  if (!button) return false;
  button.click();
  return true;
})()`);
if (!opened) throw new Error('OPEN_OPERATIONS_BUTTON_MISSING');

const openStarted = Date.now();
while (Date.now() - openStarted < 15000) {
  body = String(await evalv("document.body ? document.body.innerText : ''") || '');
  if (body.includes('Confirmar ajuste') && body.includes('Existencia final') && body.includes('Motivo')) break;
  await sleep(180);
}
if (!body.includes('Confirmar ajuste')) throw new Error('OPERATIONS_NOT_REVEALED');

const prepared = await evalv(`(() => {
  const section=[...document.querySelectorAll('section')].find(el => el.getAttribute('aria-label')==='Operaciones de inventario');
  if (!section) return {ok:false,reason:'section'};
  const labels=[...section.querySelectorAll('label')];
  const qtyLabel=labels.find(x => (x.textContent||'').includes('Existencia final'));
  const reasonLabel=labels.find(x => (x.textContent||'').includes('Motivo'));
  const qty=qtyLabel?.querySelector('input');
  const reason=reasonLabel?.querySelector('input');
  if (!qty || !reason) return {ok:false,reason:'inputs'};
  const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
  setter.call(qty,'1'); qty.dispatchEvent(new Event('input',{bubbles:true})); qty.dispatchEvent(new Event('change',{bubbles:true}));
  setter.call(reason,'Visual QA'); reason.dispatchEvent(new Event('input',{bubbles:true})); reason.dispatchEvent(new Event('change',{bubbles:true}));
  return {ok:true};
})()`);
if (!prepared?.ok) throw new Error(`STATE_PREP_FAILED:${JSON.stringify(prepared)}`);

let targetMeta;
const stateStarted = Date.now();
while (Date.now() - stateStarted < 8000) {
  targetMeta = await evalv(`(() => {
    const section=[...document.querySelectorAll('section')].find(el => el.getAttribute('aria-label')==='Operaciones de inventario');
    const form=section?.querySelector('[class*="operationForm"]');
    const buttons=form ? [...form.querySelectorAll(':scope > button')] : [];
    const target=buttons.find(el => (el.textContent||'').trim()==='Confirmar ajuste');
    if (!target) return null;
    const cs=getComputedStyle(target), r=target.getBoundingClientRect();
    return {
      text:(target.textContent||'').trim(), disabled:Boolean(target.disabled),
      rect:{x:r.x,y:r.y,width:r.width,height:r.height,left:r.left,top:r.top,right:r.right,bottom:r.bottom},
      computed:{
        background:cs.background, backgroundColor:cs.backgroundColor, backgroundImage:cs.backgroundImage,
        border:cs.border, borderColor:cs.borderColor, borderRadius:cs.borderRadius,
        boxShadow:cs.boxShadow, color:cs.color, opacity:cs.opacity, filter:cs.filter,
        outline:cs.outline, transform:cs.transform, transition:cs.transition, minHeight:cs.minHeight
      },
      className:target.className
    };
  })()`);
  if (targetMeta && targetMeta.disabled === false) break;
  await sleep(150);
}
if (!targetMeta) throw new Error('EXACT_FINAL_BUTTON_MISSING');
if (targetMeta.disabled) throw new Error('EXACT_FINAL_BUTTON_NOT_ENABLED');

const meta = await evalv(`(() => {
  const b=document.body,e=document.documentElement;
  const routeRoot=document.querySelector('[data-prisma-panel="tablet.inventory.route"][data-prisma-surface="tablet"][data-prisma-route="/inventory"]');
  const section=[...document.querySelectorAll('section')].find(el => el.getAttribute('aria-label')==='Operaciones de inventario');
  const directFinal=section?.querySelector('[class*="operationForm"] > button');
  const tabPrimaries=section ? [...section.querySelectorAll('[role="tab"]')].filter(x => x.className===directFinal?.className).length : -1;
  return {
    title:document.title,url:location.href,bodyLength:(b?.innerText||'').trim().length,
    clientWidth:e?.clientWidth||0,scrollWidth:Math.max(e?.scrollWidth||0,b?.scrollWidth||0),
    scrollHeight:Math.max(e?.scrollHeight||0,b?.scrollHeight||0),
    routeAnchors:routeRoot ? {panel:routeRoot.getAttribute('data-prisma-panel'),surface:routeRoot.getAttribute('data-prisma-surface'),route:routeRoot.getAttribute('data-prisma-route')} : null,
    operationsPresent:Boolean(section),directFinalButtonPresent:Boolean(directFinal),tabPrimaryClassReuseCount:tabPrimaries
  };
})()`);
if (!meta.routeAnchors || meta.routeAnchors.panel!=='tablet.inventory.route' || meta.routeAnchors.surface!=='tablet' || meta.routeAnchors.route!=='/inventory') throw new Error(`ROUTE_ANCHOR_DRIFT:${JSON.stringify(meta.routeAnchors)}`);
if (!meta.operationsPresent || !meta.directFinalButtonPresent) throw new Error('EXACT_TARGET_STRUCTURE_MISSING');
if ((meta.scrollWidth || 0) > (meta.clientWidth || 0) + 4) throw new Error(`HORIZONTAL_OVERFLOW:${meta.scrollWidth}>${meta.clientWidth}`);
if (forbiddenMutationRequests.length) throw new Error(`FORBIDDEN_INVENTORY_MUTATION:${JSON.stringify(forbiddenMutationRequests)}`);
if (runtimeErrors.length || consoleErrors.length || networkErrors.length) throw new Error(`RUNTIME_ANOMALY:${JSON.stringify({runtimeErrors,consoleErrors,networkErrors})}`);

const rect = targetMeta.rect;
const targetShot = await cdp.send('Page.captureScreenshot', { format:'png', captureBeyondViewport:true, fromSurface:true, clip:{x:Math.max(0,rect.left-18),y:Math.max(0,rect.top-18),width:Math.max(1,rect.width+36),height:Math.max(1,rect.height+36),scale:1} });
fs.writeFileSync(path.join(shots, `${phase.toLowerCase()}-target.png`), Buffer.from(targetShot.data, 'base64'));
const viewportShot = await cdp.send('Page.captureScreenshot', { format:'png', captureBeyondViewport:false, fromSurface:true });
fs.writeFileSync(path.join(shots, `${phase.toLowerCase()}-viewport.png`), Buffer.from(viewportShot.data, 'base64'));
const metrics = await cdp.send('Page.getLayoutMetrics');
const size = metrics.cssContentSize || metrics.contentSize || { width:1365, height:1000 };
const fullWidth = Math.max(1365, Math.min(Math.ceil(size.width || 1365), 1800));
const fullHeight = Math.max(1000, Math.min(Math.ceil(size.height || 1000), 8000));
const fullShot = await cdp.send('Page.captureScreenshot', { format:'png', captureBeyondViewport:true, fromSurface:true, clip:{x:0,y:0,width:fullWidth,height:fullHeight,scale:1} });
fs.writeFileSync(path.join(shots, `${phase.toLowerCase()}-full.png`), Buffer.from(fullShot.data, 'base64'));

const report = {
  schemaVersion:'tablet.inventory.primary.exact.runtime-evidence.v1', phase,
  commit:process.env.PRISMA_EVIDENCE_SHA || null, route:'/inventory', viewport:{width:1365,height:1000},
  state:{operationsOpen:true,mode:'adjust',quantity:'1',reason:'Visual QA',operationSubmitted:false},
  fixture:{kind:'runner-local-network-get-fixture',products:products.length,productionData:false,databaseUsed:false,prismaGenerate:false},
  meta,target:targetMeta,runtimeErrors,consoleErrors,networkErrors,requests,forbiddenMutationRequests,
  screenshots:[`${phase.toLowerCase()}-target.png`,`${phase.toLowerCase()}-viewport.png`,`${phase.toLowerCase()}-full.png`]
};
fs.writeFileSync(path.join(out,`${phase.toLowerCase()}-results.json`), JSON.stringify(report,null,2)+'\n');
await cdp.close();
console.log(`PASS_TABLET_INVENTORY_PRIMARY_${phase}_RUNTIME_EVIDENCE`);
