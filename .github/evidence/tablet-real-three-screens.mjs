import fs from 'node:fs';
import path from 'node:path';

const base = process.env.RUNTIME_URL || 'http://127.0.0.1:3120';
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9224);
const out = path.resolve(process.env.EVIDENCE_DIR || 'evidence/tablet-real-three-screens');
const shots = path.join(out, 'screenshots');
fs.mkdirSync(shots, { recursive: true });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64');
const businessId = 'biz_78b3c840796a4a4dad';
const storeId = 'store_00728649f3804a9e82';
const terminalId = 'term_49103c7382d84663a3';
const runtimeErrors = [];
const consoleErrors = [];
const networkErrors = [];
const apiRequests = [];
const captures = [];

const products = [
  { id:'p-coca', businessId, sku:'COCA600', name:'Coca-Cola Original 600 ml', category:'Bebidas', barcode:'7501055300075', barcodes:['7501055300075'], priceCents:2200, costCents:1400, stockOnHand:24, lowStockThreshold:6, isActive:true },
  { id:'p-sabritas', businessId, sku:'SABR45', name:'Sabritas Original 45 g', category:'Botanas', barcode:'7501011110076', barcodes:['7501011110076'], priceCents:1900, costCents:1100, stockOnHand:3, lowStockThreshold:5, isActive:true },
  { id:'p-lala', businessId, sku:'LALA1L', name:'Leche Lala Entera 1 L', category:'Lácteos', barcode:'7501020511116', barcodes:['7501020511116'], priceCents:3100, costCents:2200, stockOnHand:13, lowStockThreshold:4, isActive:true },
  { id:'p-bimbo', businessId, sku:'BIMBO620', name:'Pan Blanco Bimbo 620 g', category:'Panadería', barcode:'7501000110421', barcodes:['7501000110421'], priceCents:4800, costCents:3300, stockOnHand:0, lowStockThreshold:3, isActive:true },
  { id:'p-ciel', businessId, sku:'CIEL1L', name:'Agua Ciel 1 L', category:'Bebidas', barcode:'7501055310883', barcodes:['7501055310883'], priceCents:1600, costCents:900, stockOnHand:32, lowStockThreshold:8, isActive:true },
  { id:'p-nescafe', businessId, sku:'NESCAFE120', name:'Nescafé Clásico 120 g', category:'Abarrotes', barcode:'7501058610553', barcodes:['7501058610553'], priceCents:8900, costCents:6200, stockOnHand:7, lowStockThreshold:8, isActive:true },
  { id:'p-inactive', businessId, sku:'JUGOOLD', name:'Jugo naranja 355 ml', category:'Bebidas', barcode:'7500000000001', barcodes:['7500000000001'], priceCents:2500, costCents:1500, stockOnHand:8, lowStockThreshold:4, isActive:false }
];

const line = (id, product, qty = 1) => ({ id, productId:product.id, sku:product.sku, productName:product.name, qty, priceCents:product.priceCents, totalCents:product.priceCents * qty });
const ticket = (n, folio, cashier, method, totalCents, completedAt, lines) => ({
  saleId:`sale-${n}`, folio, businessId, terminalId, cashSessionId:'shift-real-shot', clientRequestId:`req-${n}`,
  cashier, status:'COMPLETED', createdAt:completedAt, completedAt, paymentMethod:method, totalCents,
  returnSummary:null, lineCount:lines.length, unitsSold:lines.reduce((sum,item)=>sum+item.qty,0), lines
});
const tickets = [
  ticket(156,'TC-000156','Ana Caja','CARD',78500,'2026-08-28T19:25:00.000Z',[line('l1',products[0],2),line('l2',products[2],1)]),
  ticket(155,'TC-000155','Carlos Ruiz','CASH',32000,'2026-08-28T19:10:00.000Z',[line('l3',products[1],1),line('l4',products[4],1)]),
  ticket(154,'TC-000154','María Hernández','CARD',125000,'2026-08-28T18:57:00.000Z',[line('l5',products[5],1)]),
  ticket(153,'TC-000153','Carlos Ruiz','TRANSFER',260400,'2026-08-28T18:42:00.000Z',[line('l6',products[0],3)])
];
const salesSummary = {
  businessId, terminalId, date:'2026-08-28', salesCount:tickets.length, ticketsClosed:tickets.length,
  totalCents:tickets.reduce((sum,t)=>sum+t.totalCents,0),
  averageTicketCents:Math.round(tickets.reduce((sum,t)=>sum+t.totalCents,0)/tickets.length),
  unitsSold:tickets.reduce((sum,t)=>sum+t.unitsSold,0),
  topProducts:[{productId:products[0].id,sku:products[0].sku,name:products[0].name,qty:5,totalCents:11000}],
  tickets
};
const shift = {
  id:'shift-real-shot', businessId, storeId, terminalId, cashierId:'cashier-ana', cashier:'Ana Caja', status:'OPEN',
  openedAt:'2026-08-28T14:00:00.000Z', closedAt:null, cashStartCents:500000, cashEndCents:null,
  expectedCashCents:845000, varianceCents:null, salesCount:28, salesTotalCents:2478050, movementCount:3,
  canSell:true, canClose:true, operatorMessage:'Turno abierto y listo para operar.'
};

class Cdp {
  constructor(url) { this.url=url; this.id=1; this.pending=new Map(); this.handlers=new Map(); }
  async connect() {
    this.ws=new WebSocket(this.url);
    await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error('CDP_CONNECT_TIMEOUT')),10000);
      this.ws.addEventListener('open',()=>{clearTimeout(timer);resolve();},{once:true});
      this.ws.addEventListener('error',()=>{clearTimeout(timer);reject(new Error('CDP_CONNECT_ERROR'));},{once:true});
    });
    this.ws.addEventListener('message',async(event)=>{
      const raw=typeof event.data==='string'?event.data:Buffer.from(await event.data.arrayBuffer()).toString();
      const msg=JSON.parse(raw);
      if(msg.id){const p=this.pending.get(msg.id);if(!p)return;this.pending.delete(msg.id);msg.error?p.reject(new Error(`${p.method}:${JSON.stringify(msg.error)}`)):p.resolve(msg.result||{});return;}
      for(const handler of this.handlers.get(msg.method)||[]) Promise.resolve(handler(msg.params||{})).catch((e)=>runtimeErrors.push(`handler:${msg.method}:${e.stack||e}`));
    });
  }
  on(method,handler){this.handlers.set(method,[...(this.handlers.get(method)||[]),handler]);}
  send(method,params={}){const id=this.id++;return new Promise((resolve,reject)=>{this.pending.set(id,{resolve,reject,method});this.ws.send(JSON.stringify({id,method,params}));});}
}

let target;
for(let i=0;i<50&&!target;i++){
  try{const r=await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(base+'/stock')}`,{method:'PUT'});if(r.ok)target=await r.json();}catch{}
  if(!target)await sleep(250);
}
if(!target)throw new Error('CHROME_DEBUG_TARGET_UNAVAILABLE');

const cdp=new Cdp(target.webSocketDebuggerUrl);
await cdp.connect();
for(const method of ['Page.enable','Runtime.enable','Log.enable','Network.enable'])await cdp.send(method);
await cdp.send('Emulation.setDeviceMetricsOverride',{width:1365,height:900,deviceScaleFactor:1,mobile:false});
await cdp.send('Fetch.enable',{patterns:[{urlPattern:`${base}/api/*`,requestStage:'Request'}]});

cdp.on('Runtime.exceptionThrown',(p)=>runtimeErrors.push(`exception:${p.exceptionDetails?.text||'unknown'}`));
cdp.on('Runtime.consoleAPICalled',(p)=>{if(p.type==='error'){const text=(p.args||[]).map(x=>x.value??x.description??'').join(' ');if(!text.toLowerCase().includes('favicon'))consoleErrors.push(text||'console.error');}});
cdp.on('Log.entryAdded',(p)=>{const e=p.entry||{};const text=String(e.text||'');const url=String(e.url||'');if(e.level==='error'&&!text.toLowerCase().includes('favicon')&&!url.endsWith('/favicon.ico')){const incidental=text.includes('404')&&/\.(png|jpg|webp)$/.test(url);if(!incidental)consoleErrors.push(`log:${text}${url?` @ ${url}`:''}`);}});
cdp.on('Network.responseReceived',(p)=>{const r=p.response||{};const status=Number(r.status||0);const type=String(p.type||'');const url=String(r.url||'');if(status>=400&&['XHR','Fetch','Document','Script','Stylesheet'].includes(type)&&!url.endsWith('/favicon.ico'))networkErrors.push(`${status}:${type}:${url}`);});

cdp.on('Fetch.requestPaused',async(p)=>{
  const url=new URL(p.request.url);apiRequests.push(`${p.request.method} ${url.pathname}${url.search}`);let payload=null;
  if(url.pathname==='/api/pos/products/search'){
    const q=(url.searchParams.get('q')||'').trim().toLowerCase();const filtered=q?products.filter(x=>`${x.name} ${x.sku} ${x.category}`.toLowerCase().includes(q)):products;
    payload={ok:true,data:{products:filtered,count:filtered.length},meta:{source:'runner-local-screenshot-fixture'}};
  }else if(url.pathname==='/api/pos/products/resolve'){
    const code=url.searchParams.get('code')||'';payload={ok:true,data:{product:products.find(x=>x.barcode===code||x.sku===code)||products[0]},meta:{}};
  }else if(url.pathname==='/api/pos/sales/today')payload={ok:true,data:{summary:salesSummary},meta:{source:'runner-local-screenshot-fixture'}};
  else if(url.pathname==='/api/pos/shift/current')payload={ok:true,data:{shift},meta:{source:'runner-local-screenshot-fixture'}};
  else if(url.pathname==='/api/license/status')payload={ok:true,data:{status:{state:'development',plan:'DEVELOPMENT',assignmentState:'assigned',operationalDecision:'allow'}},meta:{}};
  else if(url.pathname==='/api/pos/sync/health/pc')payload={ok:true,enabled:true,status:'online',url:'http://pc.local',error:null};
  if(payload!==null)await cdp.send('Fetch.fulfillRequest',{requestId:p.requestId,responseCode:200,responseHeaders:[{name:'content-type',value:'application/json; charset=utf-8'},{name:'cache-control',value:'no-store'}],body:encode(payload)});
  else await cdp.send('Fetch.continueRequest',{requestId:p.requestId});
});

async function evalv(expression){const r=await cdp.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(`EVAL_EXCEPTION:${r.exceptionDetails.text||'unknown'}`);return r.result?.value;}
async function waitFor(expression,label,timeout=45000){const start=Date.now();while(Date.now()-start<timeout){try{if(await evalv(expression))return;}catch{}await sleep(250);}const state=await evalv(`(()=>({url:location.href,title:document.title,body:(document.body?.innerText||'').slice(0,5000),readyState:document.readyState}))()`);fs.writeFileSync(path.join(out,`diagnostic-${label}.json`),JSON.stringify(state,null,2)+'\n');const png=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});fs.writeFileSync(path.join(shots,`00-diagnostic-${label}.png`),Buffer.from(png.data,'base64'));throw new Error(`WAIT_TIMEOUT:${label}:${JSON.stringify(state)}`);}
async function capture(route,fileName,ready,label){const er=runtimeErrors.length,ec=consoleErrors.length,en=networkErrors.length;await cdp.send('Page.navigate',{url:`${base}${route}?realScreens=${Date.now()}`});await waitFor(`document.readyState==='complete'||document.readyState==='interactive'`,`${label}-doc`,30000);await waitFor(ready,label,45000);await sleep(1000);await evalv(`window.scrollTo(0,0);true`);await sleep(250);const png=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});const fp=path.join(shots,fileName);fs.writeFileSync(fp,Buffer.from(png.data,'base64'));const state=await evalv(`(()=>({route:location.pathname,title:document.title,body:(document.body?.innerText||'').slice(0,2500),width:document.documentElement.clientWidth,height:document.documentElement.clientHeight,scrollHeight:Math.max(document.documentElement.scrollHeight,document.body?.scrollHeight||0)}))()`);captures.push({route,fileName,bytes:fs.statSync(fp).size,state,newRuntimeErrors:runtimeErrors.slice(er),newConsoleErrors:consoleErrors.slice(ec),newNetworkErrors:networkErrors.slice(en)});}

await capture('/stock','01-inventario-real.png',`(()=>{const t=document.body?.innerText||'';return t.includes('CONTROL DE EXISTENCIAS')&&t.includes('Coca-Cola Original 600 ml')&&t.includes('Sabritas Original 45 g');})()`,'inventario');
await capture('/sales/today','02-ventas-de-hoy-real.png',`(()=>{const t=document.body?.innerText||'';return t.includes('Ventas de hoy')&&t.includes('TC-000156')&&t.includes('TC-000153');})()`,'ventas-hoy');
await capture('/shift','03-turno-caja-real.png',`(()=>{const t=document.body?.innerText||'';return t.includes('Turno abierto')&&t.includes('Caja del dia')&&t.includes('Contar y cerrar caja');})()`,'turno-caja');

const unexpected={runtimeErrors,consoleErrors:[...new Set(consoleErrors)],networkErrors:[...new Set(networkErrors)]};
fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify({captures,apiRequests:[...new Set(apiRequests)],unexpected},null,2)+'\n');
if(captures.length!==3)throw new Error(`CAPTURE_COUNT:${captures.length}`);
if(captures.some(x=>x.bytes<50000))throw new Error('SCREENSHOT_TOO_SMALL');
if(runtimeErrors.length)throw new Error(`RUNTIME_ERRORS:${JSON.stringify(runtimeErrors)}`);
if(consoleErrors.length)throw new Error(`CONSOLE_ERRORS:${JSON.stringify([...new Set(consoleErrors)])}`);
if(networkErrors.length)throw new Error(`NETWORK_ERRORS:${JSON.stringify([...new Set(networkErrors)])}`);
console.log('PASS_TABLET_REAL_THREE_SCREENS');
