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
const results = [];
let currentTarget = 'bootstrap';

const fixtureTicket = {
  saleId: 'fixture-sale-01', folio: 'V-000123', canonicalTicketId: 'ticket-fixture-01', lookupAliases: ['V-000123'], resolvedBy: 'saleId',
  businessId: 'biz_hitech_default', businessName: 'HITECH Demo', storeId: 'store-centro', storeName: 'Centro', terminalId: 'terminal-tablet-01', terminalName: 'Tablet Caja 01',
  cashSessionId: 'shift-fixture-01', clientRequestId: 'req-fixture-01', cashier: 'Ana Caja', status: 'closed', createdAt: '2026-08-26T10:05:00.000Z', completedAt: '2026-08-26T10:07:00.000Z',
  subtotalCents: 12500, discountCents: 0, paymentMethod: 'cash', cashReceivedCents: 15000, changeCents: 2500, totalCents: 12500, lineCount: 2, unitsSold: 3,
  lines: [
    { id: 'line-01', productId: 'prod-01', sku: 'SKU-001', productName: 'Producto demostración A', qty: 2, priceCents: 4000, totalCents: 8000, returnedQty: 0, returnAvailableQty: 2, returnedCents: 0, returnStatus: 'available' },
    { id: 'line-02', productId: 'prod-02', sku: 'SKU-002', productName: 'Producto demostración B', qty: 1, priceCents: 4500, totalCents: 4500, returnedQty: 0, returnAvailableQty: 1, returnedCents: 0, returnStatus: 'available' }
  ],
  paymentTenders: [{ id: 'tender-01', tenderType: 'cash', amountCents: 12500, recordedAt: '2026-08-26T10:07:00.000Z', source: 'tablet' }],
  returns: [], returnSummary: null,
  evidence: { contract: 'fixture-read-only', local: true, outboxEvents: [{ id: 'evt-fixture-01', topic: 'sale.closed', status: 'acked', createdAt: '2026-08-26T10:07:00.000Z' }], auditEvents: [], evidenceEventIds: ['evt-fixture-01'], evidenceTopics: ['sale.closed'] }
};
const fixtureSummary = {
  businessId: 'biz_hitech_default', terminalId: 'terminal-tablet-01', date: '2026-08-26', salesCount: 1, ticketsClosed: 1, totalCents: 12500, averageTicketCents: 12500, unitsSold: 3,
  topProducts: [{ productId: 'prod-01', sku: 'SKU-001', name: 'Producto demostración A', qty: 2, totalCents: 8000 }, { productId: 'prod-02', sku: 'SKU-002', name: 'Producto demostración B', qty: 1, totalCents: 4500 }],
  tickets: [fixtureTicket]
};

const targets = [
  ['home','/','direct'],['pos','/pos','direct'],['checkout','/checkout','direct'],['shift','/shift','direct'],['stock','/stock','direct'],['catalog','/catalog','direct'],['existencias','/existencias','direct'],['inventory-low-stock','/inventory/low-stock','direct'],
  ['sales-today','/sales/today','direct'],['sales-history','/sales/history','direct'],['returns','/returns','direct'],['sync','/sync','direct'],['offline','/offline','direct'],['settings-license','/settings/license','direct'],['settings-export','/settings/export','direct'],['settings-data','/settings/data','direct'],['setup','/setup','direct'],
  ['inventory-alias','/inventory','alias'],['sales-alias','/sales','alias'],
  ['sales-today-detail','/sales/today/fixture-sale-01?businessId=biz_hitech_default','dynamic-fixture'],['sales-history-detail','/sales/history/fixture-sale-01?businessId=biz_hitech_default','dynamic-fixture'],['return-from-ticket','/sales/today/fixture-sale-01/return?businessId=biz_hitech_default','dynamic-fixture']
];

const b64 = value => Buffer.from(JSON.stringify(value)).toString('base64');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
class Cdp {
  constructor(url){this.url=url;this.id=1;this.pending=new Map;this.handlers=new Map}
  async connect(){this.ws=new WebSocket(this.url);await new Promise((ok,no)=>{const t=setTimeout(()=>no(new Error('CDP_CONNECT_TIMEOUT')),10000);this.ws.addEventListener('open',()=>{clearTimeout(t);ok()},{once:true});this.ws.addEventListener('error',()=>{clearTimeout(t);no(new Error('CDP_CONNECT_ERROR'))},{once:true})});this.ws.addEventListener('message',async e=>{const raw=typeof e.data==='string'?e.data:Buffer.from(await e.data.arrayBuffer()).toString();const m=JSON.parse(raw);if(m.id){const p=this.pending.get(m.id);if(!p)return;this.pending.delete(m.id);m.error?p.no(new Error(`${p.method}:${JSON.stringify(m.error)}`)):p.ok(m.result||{});return}for(const fn of this.handlers.get(m.method)||[])Promise.resolve(fn(m.params||{})).catch(x=>runtimeErrors.push(`${currentTarget}:handler:${m.method}:${x.stack||x}`))})}
  on(m,f){this.handlers.set(m,[...(this.handlers.get(m)||[]),f])}
  send(method,params={}){const id=this.id++;return new Promise((ok,no)=>{this.pending.set(id,{ok,no,method});this.ws.send(JSON.stringify({id,method,params}))})}
}

let target;
for(let i=0;i<40&&!target;i++){try{const r=await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(base+'/')}`,{method:'PUT'});if(r.ok)target=await r.json()}catch{}if(!target)await sleep(250)}
if(!target)throw new Error('CHROME_DEBUG_TARGET_UNAVAILABLE');
const cdp=new Cdp(target.webSocketDebuggerUrl);await cdp.connect();
for(const m of ['Page.enable','Runtime.enable','Log.enable','Network.enable'])await cdp.send(m);
await cdp.send('Emulation.setDeviceMetricsOverride',{width:1365,height:900,deviceScaleFactor:1,mobile:false});
await cdp.send('Fetch.enable',{patterns:[{urlPattern:`${base}/api/*`,requestStage:'Request'}]});

cdp.on('Runtime.exceptionThrown',p=>runtimeErrors.push(`${currentTarget}:exception:${p.exceptionDetails?.text||'unknown'}`));
cdp.on('Runtime.consoleAPICalled',p=>{if(p.type==='error'){const t=(p.args||[]).map(x=>x.value??x.description??'').join(' ')||'console.error';if(!t.toLowerCase().includes('favicon'))consoleErrors.push(`${currentTarget}:${t}`)}});
cdp.on('Log.entryAdded',p=>{const e=p.entry||{},t=String(e.text||''),u=String(e.url||'');const accessory=t==='Failed to load resource: the server responded with a status of 404 (Not Found)'&&!u;if(e.level==='error'&&!t.toLowerCase().includes('favicon')&&!u.endsWith('/favicon.ico')&&!accessory)consoleErrors.push(`${currentTarget}:log:${t}${u?` @ ${u}`:''}`)});
cdp.on('Network.responseReceived',p=>{const r=p.response||{},s=Number(r.status||0),u=String(r.url||''),type=String(p.type||'');if(s>=400&&type!=='Image'&&type!=='Other'&&!u.endsWith('/favicon.ico'))networkErrors.push(`${currentTarget}:${s}:${type||'Unknown'}:${u}`)});
cdp.on('Fetch.requestPaused',async p=>{
  const u=new URL(p.request.url);requests.push(`${currentTarget} ${p.request.method} ${u.pathname}${u.search}`);let payload=null;
  if(u.pathname==='/api/pos/sales/detail')payload={ok:true,data:{ticket:fixtureTicket}};
  else if(u.pathname==='/api/pos/sales/today'||u.pathname==='/api/pos/sales/history')payload={ok:true,data:{summary:fixtureSummary}};
  else if(u.pathname==='/api/license/status')payload={ok:true,data:{status:{state:'active',plan:'PRISMA Operación',assignmentState:'assigned',operationalDecision:'allow'}}};
  else if(u.pathname==='/api/pos/sync/health/pc')payload={ok:true,enabled:true,status:'online',url:'http://pc.local',error:null};
  else if(u.pathname==='/api/pos/sync/panel')payload={ok:true,data:{summary:{total:0,pending:0,failed:0,sent:0,acked:0,conflict:0,risk:'ok',headline:'Todo enviado',operatorMessage:'Sin pendientes.',offlineVisible:false,lastCheckedAt:'2026-08-26T10:00:00.000Z'},items:[],diagnostics:['Venta local disponible','No hay pendientes visibles']}};
  else if(u.pathname==='/api/pos/sync/pull')payload={ok:true,data:{stream:'catalog',targetBusinessId:'biz_hitech_default',terminalId:'terminal-tablet-01',pc:{enabled:true,origin:'http://pc.local',exportPath:'/api/catalog/export'},checkpoint:null,tableCounts:{Product:2,PriceListItem:2}}};
  if(payload!==null)await cdp.send('Fetch.fulfillRequest',{requestId:p.requestId,responseCode:200,responseHeaders:[{name:'content-type',value:'application/json; charset=utf-8'},{name:'cache-control',value:'no-store'}],body:b64(payload)});else await cdp.send('Fetch.continueRequest',{requestId:p.requestId});
});

async function evalv(expression){const r=await cdp.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});return r.result?.value}
async function bodyText(){return String(await evalv("document.body ? document.body.innerText : ''")||'')}
async function waitReady(label,ms=35000){const start=Date.now();while(Date.now()-start<ms){if(await evalv("document.readyState === 'complete' && document.body && document.body.innerText.trim().length > 20"))return;await sleep(200)}throw new Error(`WAIT_READY_TIMEOUT:${label}`)}
async function snapshotMeta(){return await evalv(`(()=>{const b=document.body,e=document.documentElement;return{title:document.title,url:location.href,headings:[...document.querySelectorAll('h1,h2')].slice(0,4).map(x=>x.textContent.trim()).filter(Boolean),bodyLength:(b?.innerText||'').trim().length,bodyPreview:(b?.innerText||'').trim().slice(0,1200),clientWidth:e?.clientWidth||0,scrollWidth:Math.max(e?.scrollWidth||0,b?.scrollWidth||0),scrollHeight:Math.max(e?.scrollHeight||0,b?.scrollHeight||0),routeMarkers:[...document.querySelectorAll('[data-surface="tablet"]')].length}})()`)}
async function shot(name){const m=await cdp.send('Page.getLayoutMetrics');const cs=m.cssContentSize||m.contentSize||{width:1365,height:900};const width=Math.max(1365,Math.min(Math.ceil(cs.width||1365),1800)),height=Math.max(900,Math.min(Math.ceil(cs.height||900),8000));const r=await cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,fromSurface:true,clip:{x:0,y:0,width,height,scale:1}});fs.writeFileSync(path.join(shots,name),Buffer.from(r.data,'base64'));return{width,height}}
const fatalText=[/Internal Server Error/i,/Application error/i,/Unhandled Runtime Error/i,/This page could not be found/i,/404: This page could not be found/i];

for(const [id,route,kind] of targets){currentTarget=id;const re=runtimeErrors.length,ce=consoleErrors.length,ne=networkErrors.length;const url=`${base}${route}${route.includes('?')?'&':'?'}screensqa=${Date.now()}`;await cdp.send('Page.navigate',{url});let status='captured',error=null,meta=null,dimensions=null;try{await waitReady(id);await sleep(900);meta=await snapshotMeta();const text=String(meta?.bodyPreview||'')+'\n'+await bodyText();const fatal=fatalText.find(rx=>rx.test(text));if(fatal)throw new Error(`FATAL_TEXT:${fatal}`);if((meta?.bodyLength||0)<20)throw new Error('BODY_TOO_SMALL');if((meta?.scrollWidth||0)>(meta?.clientWidth||0)+4)throw new Error(`HORIZONTAL_OVERFLOW:${meta.scrollWidth}>${meta.clientWidth}`);dimensions=await shot(`${String(results.length+1).padStart(2,'0')}-${id}.png`)}catch(e){status='failed';error=String(e?.stack||e);try{meta=meta||await snapshotMeta();dimensions=await shot(`${String(results.length+1).padStart(2,'0')}-${id}-FAILED.png`)}catch{}}
  const rr=runtimeErrors.slice(re),cc=consoleErrors.slice(ce),nn=networkErrors.slice(ne);if(rr.length||cc.length||nn.length)status='failed';results.push({id,route,kind,status,error,meta,dimensions,runtimeErrors:rr,consoleErrors:cc,networkErrors:nn});
}
const report={schemaVersion:'tablet.final.screensqa.runtime.v1',productTarget:process.env.PRODUCT_TARGET||null,evidenceBase:process.env.EVIDENCE_BASE||null,viewport:{width:1365,height:900},targetCount:targets.length,capturedCount:results.filter(x=>x.status==='captured').length,failedCount:results.filter(x=>x.status==='failed').length,results,runtimeErrors,consoleErrors,networkErrors,requests};
fs.writeFileSync(path.join(out,'screensqa-results.json'),JSON.stringify(report,null,2)+'\n');fs.writeFileSync(path.join(out,'browser-runtime-errors.json'),JSON.stringify({runtimeErrors,consoleErrors,networkErrors},null,2)+'\n');fs.writeFileSync(path.join(out,'requests.log'),requests.join('\n')+'\n');
const passed=report.capturedCount,failed=report.failedCount;console.log(`TABLET_FINAL_SCREENSQA_BROWSER ${passed}/${results.length} PASS, ${failed} FAIL`);for(const r of results)console.log(`${r.status==='captured'?'PASS':'FAIL'} ${r.id} ${r.route}${r.error?` :: ${r.error.split('\n')[0]}`:''}`);if(failed)process.exit(2);console.log('PASS_TABLET_FINAL_SCREENSQA_BROWSER_22_22');
