import fs from "node:fs";
import path from "node:path";

const base = process.env.RUNTIME_URL || "http://127.0.0.1:3120";
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9223);
const out = path.resolve(process.env.EVIDENCE_DIR || "evidence/tablet-sync-wave2-postmerge");
const shots = path.join(out, "screenshots");
fs.mkdirSync(shots, { recursive: true });
const NOW = "2026-08-25T14:20:00.000Z";
let state = "clean";
const runtimeErrors = [], consoleErrors = [], networkErrors = [], requests = [], manifest = [];

function item(status) {
  const remote = ["sent","acked","conflict"].includes(status);
  return {
    id:`fixture-${status}-01`, eventId:`evt-${status}-01`,
    title:status === "conflict" ? "Venta por revisar" : "Venta registrada",
    description:status === "conflict" ? "Venta registrada en la Tablet. Requiere revisión; no se reintenta automáticamente." : status === "failed" ? "Venta registrada en la Tablet. Necesita revisión antes de volver a enviar." : "Venta registrada en la Tablet. Guardado localmente para continuidad de operación.",
    status, statusLabel:{pending:"Pendiente",failed:"Fallido",sent:"Enviado",acked:"Confirmado",conflict:"Revisión"}[status],
    risk:["failed","conflict"].includes(status)?"danger":["pending","sent"].includes(status)?"warn":"ok",
    attempts:status === "failed" ? 3 : status === "conflict" ? 2 : 1,
    createdAt:"2026-08-25T14:00:00.000Z", canRetry:["pending","failed"].includes(status),
    provenance:{source:"tablet-pos",businessId:"biz_hitech_default",storeId:"store-centro",terminalId:"terminal-tablet-01",deviceId:"device-tablet-01",actorId:"cashier-ana",aggregateId:"sale-20260825-001",originRecordId:"sale-20260825-001",idempotencyKey:"idem-wave2-001",correlationId:"corr-wave2-001",traceId:"trace-wave2-001"},
    delivery:{sentAt:remote?"2026-08-25T14:12:00.000Z":null,syncedAt:status==="acked"?"2026-08-25T14:13:00.000Z":null,ackedAt:status==="acked"?"2026-08-25T14:13:00.000Z":null,failedAt:status==="failed"?"2026-08-25T14:10:00.000Z":null,conflictedAt:status==="conflict"?"2026-08-25T14:10:00.000Z":null,lastAttemptAt:["failed","sent","acked","conflict"].includes(status)?"2026-08-25T14:10:00.000Z":null,nextRetryAt:status==="failed"?"2026-08-25T14:30:00.000Z":null,remoteEventId:remote?`remote-${status}-01`:null,remoteLedgerId:remote?`ledger-${status}-01`:null,remoteLifecycleStatus:status==="acked"?"reconciled":status==="sent"?"sent":status==="conflict"?"conflict":status==="failed"?"failed":null,remoteConflictCode:status==="conflict"?"stale_sequence":null,remoteRejectedReason:status==="failed"?"PC_TIMEOUT":null},
    resolutionOwner:status==="conflict"?"pc_backoffice":null,
    resolutionLabel:status==="conflict"?"Revisión en PC / Backoffice":null
  };
}
function panel(s) {
  if (["clean","license-deny"].includes(s)) return {summary:{total:0,pending:0,failed:0,sent:0,acked:0,conflict:0,risk:"ok",headline:"Todo enviado",operatorMessage:"Sin pendientes.",offlineVisible:false,lastCheckedAt:NOW},items:[],diagnostics:["Venta local disponible","No hay pendientes visibles"]};
  const status=s==="pc-offline"?"pending":s, row=item(status);
  const summary={total:1,pending:0,failed:0,sent:0,acked:0,conflict:0,risk:row.risk,headline:"Operación visible",operatorMessage:"Revisar operación.",offlineVisible:s==="pc-offline",lastCheckedAt:NOW};
  summary[status]=1; return {summary,items:[row],diagnostics:["Venta local disponible",s==="pc-offline"?"Hay trabajo local por enviar":"Cola visible"]};
}
const b64 = o => Buffer.from(JSON.stringify(o)).toString("base64");

class Cdp {
  constructor(url){this.url=url;this.id=1;this.pending=new Map;this.handlers=new Map}
  async connect(){this.ws=new WebSocket(this.url);await new Promise((ok,no)=>{const t=setTimeout(()=>no(new Error("CDP_CONNECT_TIMEOUT")),10000);this.ws.addEventListener("open",()=>{clearTimeout(t);ok()},{once:true});this.ws.addEventListener("error",()=>{clearTimeout(t);no(new Error("CDP_CONNECT_ERROR"))},{once:true})});this.ws.addEventListener("message",async e=>{let raw=typeof e.data==="string"?e.data:Buffer.from(await e.data.arrayBuffer()).toString();const m=JSON.parse(raw);if(m.id){const p=this.pending.get(m.id);if(!p)return;this.pending.delete(m.id);m.error?p.no(new Error(`${p.method}:${JSON.stringify(m.error)}`)):p.ok(m.result||{});return}for(const fn of this.handlers.get(m.method)||[]) Promise.resolve(fn(m.params||{})).catch(x=>runtimeErrors.push(`handler:${m.method}:${x.stack||x}`))})}
  on(m,f){this.handlers.set(m,[...(this.handlers.get(m)||[]),f])}
  send(method,params={}){const id=this.id++;return new Promise((ok,no)=>{this.pending.set(id,{ok,no,method});this.ws.send(JSON.stringify({id,method,params}))})}
}

let target;
for(let i=0;i<40&&!target;i++){try{const r=await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(base+"/sync")}`,{method:"PUT"});if(r.ok)target=await r.json()}catch{}if(!target)await new Promise(r=>setTimeout(r,250))}
if(!target)throw new Error("CHROME_DEBUG_TARGET_UNAVAILABLE");
const cdp=new Cdp(target.webSocketDebuggerUrl); await cdp.connect();
for(const m of ["Page.enable","Runtime.enable","Log.enable","Network.enable"]) await cdp.send(m);
await cdp.send("Emulation.setDeviceMetricsOverride",{width:1365,height:900,deviceScaleFactor:1,mobile:false});
await cdp.send("Fetch.enable",{patterns:[{urlPattern:`${base}/api/*`,requestStage:"Request"}]});
cdp.on("Runtime.exceptionThrown",p=>runtimeErrors.push(`exception:${p.exceptionDetails?.text||"unknown"}`));
cdp.on("Runtime.consoleAPICalled",p=>{if(p.type==="error")consoleErrors.push((p.args||[]).map(x=>x.value??x.description??"").join(" ")||"console.error")});
cdp.on("Log.entryAdded",p=>{
  const entry=p.entry||{};
  const text=String(entry.text||"");
  const url=String(entry.url||"");
  const genericAccessory404=text==="Failed to load resource: the server responded with a status of 404 (Not Found)";
  if(entry.level==="error"&&!text.includes("favicon")&&!(genericAccessory404&&!url)) consoleErrors.push(`log:${text}${url?` @ ${url}`:""}`);
});
cdp.on("Network.responseReceived",p=>{
  const response=p.response||{};
  const statusCode=Number(response.status||0);
  const url=String(response.url||"");
  const type=String(p.type||"");
  if(statusCode<400) return;
  if(url.startsWith(`${base}/api/`)) return;
  if(type==="Image"||type==="Other"||url.endsWith("/favicon.ico")) return;
  networkErrors.push(`${statusCode} ${type||"Unknown"} ${url}`);
});
cdp.on("Fetch.requestPaused",async p=>{
  const u=new URL(p.request.url); requests.push(`${state} ${p.request.method} ${u.pathname}`); let code=200,payload;
  if(u.pathname==="/api/pos/sync/panel"){if(state==="unconfirmed"){code=503;payload={ok:false,error:"SYNC_PANEL_UNVERIFIED",message:"Estado de pendientes sin confirmar."}}else payload={ok:true,data:panel(state)}}
  else if(u.pathname==="/api/license/status")payload={ok:true,data:{status:{state:state==="license-deny"?"revoked":"active",plan:"PRISMA Operación",assignmentState:state==="license-deny"?"unassigned":"assigned",operationalDecision:state==="license-deny"?"deny":"allow"}}};
  else if(u.pathname==="/api/pos/sync/health/pc")payload=state==="pc-offline"?{ok:false,enabled:true,status:"offline",url:"http://pc.local",error:"PC sin respuesta"}:{ok:true,enabled:true,status:"online",url:"http://pc.local",error:null};
  else if(u.pathname==="/api/pos/sync/pull")payload=p.request.method==="GET"?{ok:true,data:{stream:"catalog",targetBusinessId:"biz_hitech_default",terminalId:"terminal-tablet-01",pc:{enabled:true,origin:"http://pc.local",exportPath:"/api/catalog/export"},checkpoint:null,tableCounts:{Product:12,PriceListItem:12}}}:{ok:true,reason:"empty",mode:"delta",sourceBusinessId:"biz_hitech_default",targetBusinessId:"biz_hitech_default",terminalId:"terminal-tablet-01",cursorBefore:null,cursorAfter:null,checkpoint:null,counts:{received:0,applied:0,rejected:0,conflict:0,duplicate:0,byEntity:{}},findings:[],errors:[],health:{enabled:true,origin:"http://pc.local",url:"http://pc.local",status:"online",httpStatus:200}};
  else if(u.pathname==="/api/pos/sync/retry")payload={ok:true,data:{scope:"all_failed",requested:null,eligible:1,updated:1,skipped:null,eligibleIds:[],skippedIds:[],message:"Preparadas 1 operación(es) fallida(s). Se enviarán cuando haya conexión."}};
  else if(u.pathname==="/api/pos/sync/dispatch")payload={ok:false,reason:"pc_unavailable",dispatched:0,forced:true,health:{ok:false,enabled:true,status:"offline",url:"http://pc.local",error:"PC sin respuesta"}};
  else payload={ok:true,data:{}};
  await cdp.send("Fetch.fulfillRequest",{requestId:p.requestId,responseCode:code,responseHeaders:[{name:"content-type",value:"application/json; charset=utf-8"},{name:"cache-control",value:"no-store"}],body:b64(payload)});
});

async function evalv(expression){const r=await cdp.send("Runtime.evaluate",{expression,returnByValue:true});return r.result?.value}
async function text(){return String(await evalv("document.body ? document.body.innerText : ''")||"")}
async function wait(expression,label,ms=25000){const start=Date.now();while(Date.now()-start<ms){if(await evalv(`Boolean(${expression})`))return;await new Promise(r=>setTimeout(r,180))}const t=(await text()).slice(0,3000);fs.writeFileSync(path.join(out,`timeout-${label.replaceAll(':','-')}.txt`),t);throw new Error(`WAIT_TIMEOUT:${label}`)}
async function click(label){const ok=await evalv(`(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()===${JSON.stringify(label)});if(!b)return false;b.click();return true})()`);if(!ok)throw new Error(`BUTTON_NOT_FOUND:${label}`);await new Promise(r=>setTimeout(r,500))}
async function openDetails(){await evalv("document.querySelectorAll('details').forEach(d=>d.open=true);true");await new Promise(r=>setTimeout(r,250))}
async function shot(name){const r=await cdp.send("Page.captureScreenshot",{format:"png",captureBeyondViewport:true,fromSurface:true});fs.writeFileSync(path.join(shots,name),Buffer.from(r.data,"base64"))}

const cases=[
 ["clean",null,["Pendientes al día","No hay pendientes para enviar."]],
 ["pending","Pendientes",["Detalles de operación","Tienda: store-centro","Reintento disponible"]],
 ["failed","Fallidos",["Último rechazo: PC_TIMEOUT","Reintento disponible","Último intento:"]],
 ["sent","Enviados",["Estado PC: sent","Ledger: ledger-sent-01","Sin acción requerida"]],
 ["acked","Confirmados",["Estado PC: reconciled","Confirmado:","Sin acción requerida"]],
 ["conflict","Revisión",["Revisión en PC / Backoffice.","Motivo de conflicto: stale_sequence","Revisión requerida"]],
 ["pc-offline","Pendientes",["PC sin respuesta","Venta local disponible aunque PC no responda","Tienda: store-centro"]],
 ["license-deny",null,["Licencia detenida","Tablet pendiente","Pendientes al día"]],
 ["unconfirmed",null,["Cola sin confirmar","Estado de pendientes sin confirmar","—"]]
];
for(const [s,filter,expects] of cases){state=s;const er=runtimeErrors.length,ce=consoleErrors.length,ne=networkErrors.length;await cdp.send("Page.navigate",{url:`${base}/sync?wave2Evidence=${encodeURIComponent(s)}&t=${Date.now()}`});await wait("document.readyState === 'complete' && document.body && document.body.innerText.includes('Continuidad operativa')",`${s}:ready`);await new Promise(r=>setTimeout(r,650));if(filter)await click(filter);await openDetails();const body=await text();for(const x of expects)if(!body.includes(x))throw new Error(`ASSERT_TEXT_MISSING:${s}:${x}`);if(s==="conflict"&&body.includes("Reintento disponible"))throw new Error("CONFLICT_ADVERTISED_RETRY");if(["sent","acked","conflict"].includes(s)&&body.includes(`evt-${s}-01`))throw new Error(`RAW_EVENT_ID_VISIBLE:${s}`);if(runtimeErrors.length!==er)throw new Error(`RUNTIME_EXCEPTION:${s}:${runtimeErrors.slice(er).join(" | ")}`);if(consoleErrors.length!==ce)throw new Error(`CONSOLE_ERROR:${s}:${consoleErrors.slice(ce).join(" | ")}`);if(networkErrors.length!==ne)throw new Error(`NETWORK_ERROR:${s}:${networkErrors.slice(ne).join(" | ")}`);const name=`${String(manifest.length+1).padStart(2,"0")}-${s}.png`;await shot(name);manifest.push({state:s,screenshot:name,assertions:expects});if(s==="failed"){await click("Reintentar fallidos");await wait("document.body && document.body.innerText.includes('Reintento: 1 operación(es) preparadas.')","failed:retry-result",15000);await openDetails();const t=await text();if(!t.includes("PC no disponible"))throw new Error("RETRY_PC_UNAVAILABLE_COPY_MISSING");const n=`${String(manifest.length+1).padStart(2,"0")}-failed-retry-result.png`;await shot(n);manifest.push({state:"failed-retry-result",screenshot:n,assertions:["Reintento: 1 operación(es) preparadas.","PC no disponible"]})}}
fs.writeFileSync(path.join(out,"screenshot-manifest.json"),JSON.stringify({targetSha:process.env.TARGET_SHA,viewport:"1365x900",screenshots:manifest},null,2)+"\n");
fs.writeFileSync(path.join(out,"browser-runtime-errors.json"),JSON.stringify({runtimeErrors,consoleErrors,networkErrors},null,2)+"\n");
fs.writeFileSync(path.join(out,"browser-api-requests.log"),requests.join("\n")+"\n");
if(runtimeErrors.length||consoleErrors.length||networkErrors.length)throw new Error(`BROWSER_ANOMALIES runtime=${runtimeErrors.length} console=${consoleErrors.length} network=${networkErrors.length}`);
console.log(`PASS_TABLET_SYNC_WAVE2_BROWSER_SCREENSHOTS ${manifest.length}/${manifest.length}`);
cdp.ws.close();
