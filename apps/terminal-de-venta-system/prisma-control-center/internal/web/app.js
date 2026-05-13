
/* PRISMA Crystal Ops Console - Iteration 2: Data Core Vivo */
const PUBLIC_HOSTS = new Set(['control.hitechrts.com']);
const LOCAL_HOSTS = new Set(['127.0.0.1', 'localhost', '::1']);
const REFRESH_MS = 5000;
const STALE_AFTER_MS = 90_000;
const STORE_VIEW = 'prisma-crystal-ops-view-v2';
let activeView = localStorage.getItem(STORE_VIEW) || 'overview';
let autoRefresh = localStorage.getItem('prisma-crystal-paused') !== 'yes';
let timer = null;
let lastHealth = null;
let lastIncidents = null;
let lastModel = null;
const $ = (id) => document.getElementById(id);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const isPublic = () => PUBLIC_HOSTS.has(location.hostname) || !LOCAL_HOSTS.has(location.hostname);
const mode = () => isPublic() ? 'PUBLIC_REDACTED' : 'LOCAL_FULL';

function esc(value){return String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');}
function text(value, fallback='sin dato'){return value === null || value === undefined || value === '' ? fallback : String(value);}
function asNumber(value, fallback=0){const n=Number(value); return Number.isFinite(n)?n:fallback;}
function clamp(value,min=0,max=100){return Math.max(min,Math.min(max,value));}
function statusOf(value){if(value===true)return 'PASS'; if(value===false)return 'FAIL'; return String(value || 'EMPTY').toUpperCase();}
function tone(value){const s=statusOf(value).toLowerCase(); if(['pass','ok','true','running','healthy','connected','visible'].includes(s))return 'pass'; if(['degraded','warn','warning','review','unstable','attention'].includes(s))return 'warn'; if(['fail','false','down','error','missing','unreachable','404','blocked'].includes(s))return s.includes('blocked')?'blocked':'fail'; if(s.includes('blocked'))return 'blocked'; if(s.includes('local')||s.includes('redacted')||s.includes('full')||s.includes('public'))return 'info'; return 'subtle';}
function chip(value,label=value){return `<span class="state-chip ${tone(value)}">${esc(text(label,'EMPTY'))}</span>`;}
function setText(id,value){const node=$(id); if(node)node.textContent=value;}
function setClass(id,value){const node=$(id); if(node)node.className=value;}
function toast(message){const node=$('toast'); if(!node)return; node.textContent=message; node.classList.add('show'); setTimeout(()=>node.classList.remove('show'),2200);}

function sensitiveKey(key){const k=String(key).toLowerCase(); return ['pid','process','command','cmd','cwd','path','token','secret','cookie','authorization','stdout','stderr','credentials','executable','blackboxroot','log'].some(part=>k.includes(part));}
function sanitize(value){if(Array.isArray(value))return value.map(sanitize); if(value&&typeof value==='object'){const out={}; for(const [k,v] of Object.entries(value))out[k]=sensitiveKey(k)?'<redacted>':sanitize(v); return out;} if(typeof value==='string' && /[A-Z]:\\|[A-Z]:\//i.test(value))return '<redacted>'; return value;}
function parseDate(value){if(!value)return null; const d=new Date(value); return Number.isNaN(d.getTime())?null:d;}
function ageMs(value){const d=parseDate(value); return d?Math.max(0,Date.now()-d.getTime()):Infinity;}
function ageLabel(value){const ms=ageMs(value); if(!Number.isFinite(ms))return 'sin timestamp'; const sec=Math.round(ms/1000); if(sec<60)return `${sec}s`; const min=Math.round(sec/60); if(min<60)return `${min}m`; const hr=Math.round(min/60); return `${hr}h`;}
function formatMs(value){const n=asNumber(value,NaN); if(!Number.isFinite(n))return '-'; return `${Math.round(n)} ms`;}
function formatPercent(value){const n=asNumber(value,NaN); if(!Number.isFinite(n))return '-'; return `${n.toFixed(n>=10?0:1)}%`;}

function normalizeHealth(payload){
  const base=payload && !payload.__error ? payload : {};
  const safe=mode()==='PUBLIC_REDACTED'?sanitize(base):base;
  safe.services=safe.services||safe.control_center?.services_summary||safe.serviceStatus||[];
  safe.cloudflare=safe.cloudflare||safe.control_center?.cloudflare_summary||{};
  safe.recommendedNextAction=safe.recommendedNextAction||safe.control_center?.recommendations?.[0]||safe.recommendation||deriveRecommendation(safe);
  return safe;
}
function normalizeIncidents(payload){
  const base=payload && !payload.__error ? payload : {};
  const safe=mode()==='PUBLIC_REDACTED'?sanitize(base):base;
  safe.activeIncidents=safe.activeIncidents||safe.active||[];
  safe.latestBridge=safe.latestBridge||{};
  return safe;
}
function services(payload){const order={'admin-health':0,'eit':0,'tablet-core':1,'pc-adder':2,'mobile-adder':3,'control-center':4}; return [...(payload.services||[])].sort((a,b)=>(order[a.productRole]??99)-(order[b.productRole]??99));}
function roleLabel(service){return {'admin-health':'EIT / Admin','eit':'EIT / Admin','tablet-core':'Tablet Core','pc-adder':'PC Backoffice','mobile-adder':'Mobile Adder','control-center':'Control Center'}[service.productRole]||service.name||service.id||'Servicio';}
function servicePort(service){return service.port||service.localPort||service.address?.port||'-';}
function endpointOk(value){if(value===true)return true; if(value===false)return false; if(value&&typeof value==='object')return Boolean(value.ok||value.status==='PASS'||value.status==='OK'||value.statusCode===200); return false;}
function serviceStatus(service){return statusOf(service.status || (endpointOk(service.localHttp)&&endpointOk(service.lanHttp)&&endpointOk(service.publicHttp)?'PASS':'DEGRADED'));}
function counts(payload){const rows=services(payload); const pass=rows.filter(s=>tone(serviceStatus(s))==='pass').length; return {total:rows.length,pass,attention:rows.length-pass};}
function latencyValues(payload){return services(payload).flatMap(s=>[s.localHttp?.latencyMs,s.lanHttp?.latencyMs,s.publicHttp?.latencyMs]).map(Number).filter(Number.isFinite);}
function avgLatency(payload){const nums=latencyValues(payload); return nums.length?Math.round(nums.reduce((a,b)=>a+b,0)/nums.length):null;}
function worstLatency(payload){const nums=latencyValues(payload); return nums.length?Math.max(...nums):null;}
function statusRank(status){return {PASS:0,OK:0,EMPTY:1,UNKNOWN:1,WARN:2,WARNING:2,DEGRADED:2,FAIL:3,ERROR:3,BLOCKED:4}[statusOf(status)]??1;}
function worstStatus(items){return items.map(statusOf).sort((a,b)=>statusRank(b)-statusRank(a))[0]||'EMPTY';}
function cloudflareRoute(payload){const cf=payload.cloudflare||{}; const cc=payload.control_center||{}; const endpoint=(cf.publicEndpoints||[]).find(item=>String(item.url||item.name||'').includes('control.hitechrts.com'));
  return {ok:Boolean(cc.public_health?.ok||endpoint?.probe?.ok||cf.config?.controlRoute?.ok),statusCode:cc.public_health?.statusCode||endpoint?.probe?.statusCode||cf.config?.controlRoute?.statusCode||'-',latencyMs:cc.public_health?.latencyMs||endpoint?.probe?.latencyMs||'-',url:cc.public_url||endpoint?.url||'https://control.hitechrts.com/',diagnosis:cf.diagnosis||cf.reason||''};
}
function healthTimestamp(payload){return payload.generatedAt||payload.lastUpdated||payload.control_center?.last_updated||payload.timestamp||payload.time;}
function deriveFreshness(payload){const t=healthTimestamp(payload); const stale=ageMs(t)>STALE_AFTER_MS; return {timestamp:t,age:ageLabel(t),stale};}
function deriveCloudflareStatus(payload){const cf=payload.cloudflare||{}; const r=cloudflareRoute(payload); if(r.ok)return 'PASS'; if(r.statusCode===404||String(r.statusCode)==='404')return 'DEGRADED'; return statusOf(cf.status||cf.state||payload.control_center?.cloudflare||'UNKNOWN');}
function deriveRecommendation(payload){const cf=deriveCloudflareStatus(payload); if(cf==='DEGRADED')return 'Revisar ruta publica de control.hitechrts.com, origen del tunnel y binding de servicio Control Center.'; const c=counts(payload); if(c.attention)return `Revisar ${c.attention} servicio(s) fuera de PASS y validar Local/LAN/Public.`; return 'Operacion sin accion inmediata.';}
function deriveModel(healthRaw, incidentsRaw){
  // PATCH_ID: PRISMA_HEALTH_EMPTY_SCORE_LOGO_20260513_FINAL
  const health=normalizeHealth(healthRaw);
  const incidents=normalizeIncidents(incidentsRaw);
  const active=incidents.activeIncidents||[];
  const rows=services(health);
  const c=counts(health);
  const fresh=deriveFreshness(health);
  const cfStatus=deriveCloudflareStatus(health);
  const latency=avgLatency(health);
  const worstLat=worstLatency(health);
  const serviceWorst=worstStatus(rows.map(serviceStatus));
  const incidentWorst=worstStatus(active.map(i=>i.severity||i.status));
  const route=cloudflareRoute(health);

  const rawScore=health.healthScore??health.control_center?.health_score;
  const hasScore=Number.isFinite(Number(rawScore));
  const hasTimestamp=Boolean(healthTimestamp(health));
  const explicitStatus=statusOf(health.overallStatus||health.control_center?.status||'EMPTY');
  const hasCloudflareEvidence=Boolean(
    health.cloudflare?.publicEndpoints?.length ||
    health.cloudflare?.status ||
    health.cloudflare?.state ||
    health.control_center?.cloudflare ||
    health.control_center?.cloudflare_summary ||
    health.control_center?.public_health ||
    route.ok ||
    (route.statusCode && route.statusCode !== '-')
  );
  const hasHealthEvidence=Boolean(
    hasScore ||
    hasTimestamp ||
    health.runId ||
    rows.length ||
    active.length ||
    hasCloudflareEvidence ||
    health.overallStatus ||
    health.control_center?.status
  );

  const componentOverall=worstStatus([serviceWorst,cfStatus,incidentWorst]);
  const blockers=[];
  if(c.attention)blockers.push(`${c.attention} servicio(s) requieren atencion`);
  if(active.length)blockers.push(`${active.length} incidente(s) activos`);
  if(hasCloudflareEvidence && cfStatus!=='PASS')blockers.push(`Cloudflare ${cfStatus}${route.statusCode&&route.statusCode!=='-'?` (${route.statusCode})`:''}`);
  if(hasHealthEvidence && fresh.stale)blockers.push(`health stale ${fresh.age}`);

  let overall=explicitStatus;
  if(!hasHealthEvidence){
    overall='EMPTY';
  }else if(['EMPTY','UNKNOWN'].includes(overall)){
    overall=blockers.length?'DEGRADED':componentOverall;
  }else if(overall==='PASS' && blockers.length){
    overall='DEGRADED';
  }

  let sourceScore=asNumber(rawScore,NaN);
  if(!hasHealthEvidence){
    sourceScore=0;
  }else if(!Number.isFinite(sourceScore)){
    const base=componentOverall==='PASS'?100:92;
    sourceScore=base-(c.attention*10)-(active.length*7)-(cfStatus==='DEGRADED'?8:0)-(['UNKNOWN','EMPTY'].includes(cfStatus)?4:0)-(fresh.stale?12:0);
  }
  const score=clamp(sourceScore);
  const recommendation=!hasHealthEvidence?'Corre health para encender la consola.':(health.recommendedNextAction||deriveRecommendation(health));
  return {health,incidents,active,c,fresh,cfStatus,latency,worstLat,serviceWorst,incidentWorst,overall,score,blockers,route,recommendation,hasHealthEvidence};
}

function renderShell(healthRaw, incidentsRaw){
  const model=deriveModel(healthRaw, incidentsRaw); lastModel=model; lastHealth=model.health; lastIncidents=model.incidents;
  const {health,incidents,active,c,fresh,cfStatus,latency,worstLat,overall,score,blockers,route,recommendation}=model;
  document.body.dataset.status=overall.toLowerCase();
  setText('header-score',score.toFixed(0)); setText('hero-title',overall==='PASS'?'Operacion cristalina':overall==='DEGRADED'?'Operacion local fuerte, visibilidad degradada':overall==='EMPTY'?'Esperando telemetria':`Estado ${overall}`); setText('hero-recommendation',recommendation);
  setText('gauge-score',score.toFixed(0)); setText('gauge-label',overall); $('mega-gauge')?.style.setProperty('--score',score);
  setText('overall-chip',overall); setClass('overall-chip',`state-chip ${tone(overall)}`); setText('fresh-chip',`health hace ${fresh.age}${fresh.stale?' / stale':''}`); setClass('fresh-chip',`state-chip ${fresh.stale?'warn':'subtle'}`); setText('run-chip',health.runId?`run ${health.runId}`:'run pendiente');
  setText('rail-status',overall); $('rail-meter').style.width=`${score}%`; setText('rail-bridge',incidents.latestBridge?.ok?'OK':'CHECK'); setText('rail-blackbox',incidents.blackBoxRoot?'ACTIVO':'SIN DATO'); setText('rail-api',incidents.activeIncidents?'OK':'CHECK');
  setText('bridge-state',incidents.source?'conectado':'consultando'); setText('mode-chip',mode()); setText('kpi-public-mode',mode()==='PUBLIC_REDACTED'?'PUBLIC':'LOCAL'); setText('kpi-public-note',mode()==='PUBLIC_REDACTED'?'sanitized':'full telemetry');
  setText('kpi-services',`${c.pass}/${c.total}`); setText('kpi-services-note',c.attention?`${c.attention} en atencion`:'todos limpios'); setText('kpi-incidents',String(active.length)); setText('kpi-incidents-note',incidents.latestBridge?.severity||'Black-box');
  setText('kpi-cloudflare',cfStatus); setText('kpi-control-route',`${route.statusCode} ${route.url}`); setText('kpi-latency',latency===null?'-':`${latency} ms`); setText('kpi-last-health',fresh.age); setText('kpi-last-health-note',fresh.timestamp||'sin timestamp');
  renderServices(model); renderIncidents(model); renderBlackbox(model); renderCloudflare(model); renderTables(model); renderRaw(model); renderDataCoreOverlay(model); 
}

function renderDataCoreOverlay(model){
  const block=model.blockers.length?model.blockers:['Sin bloqueadores derivados'];
  const html=block.map(item=>`<div class="soft-row"><span>Diagnostico</span><strong>${esc(item)}</strong></div>`).join('');
  const list=$('blackbox-list');
  if(list && !list.dataset.iter2){list.insertAdjacentHTML('beforeend', html); list.dataset.iter2='yes';}
}
function renderServices(model){const rows=services(model.health); setText('services-status',`${rows.length} servicios / peor ${model.serviceWorst}`); $('service-matrix').innerHTML=rows.map(s=>{const st=serviceStatus(s); return `<article class="service-tile"><strong>${esc(roleLabel(s))}</strong><small>Puerto ${esc(servicePort(s))}</small><div class="chip-row">${chip(st)}${chip(s.criticality||'info')}</div><div class="mini-bars" title="local lan public"><span class="${endpointOk(s.localHttp)?'on':''}"></span><span class="${endpointOk(s.lanHttp)?'on':''}"></span><span class="${endpointOk(s.publicHttp)?'on':''}"></span></div><small>local ${formatMs(s.localHttp?.latencyMs)} / public ${formatMs(s.publicHttp?.latencyMs)}</small></article>`}).join('') || '<div class="soft-row"><span>Servicios</span><strong>sin datos</strong></div>';}
function renderIncidents(model){const active=model.active; setText('incident-count',String(active.length)); const node=$('incident-spotlight'); if(!active.length){node.className='incident-spotlight empty'; node.textContent='Sin incidentes activos.'; return;} node.className='incident-spotlight'; node.innerHTML=active.slice(0,4).map(inc=>`<article class="incident-card"><div class="chip-row">${chip(inc.severity)}${chip(inc.status)}${chip(inc.state)}</div><h4>${esc(inc.id)}</h4><p>${esc(inc.recommendedNextAction||'Sin recomendacion')}</p><div class="soft-row"><span>Run</span><strong>${esc(inc.runId||'-')}</strong></div><div class="soft-row"><span>Score</span><strong>${esc(inc.healthScore??'-')}</strong></div><div class="soft-row"><span>Cloudflare</span><strong>${esc(inc.cloudflareStatus||'-')}</strong></div></article>`).join('');}
function renderBlackbox(model){const incidents=model.incidents; const latest=incidents.latestBridge||{}; setText('blackbox-chip',latest.ok?'conectado':'sin dato'); $('blackbox-list').dataset.iter2=''; $('blackbox-list').innerHTML=[['Root',incidents.blackBoxRoot||'<redacted>'],['Source',incidents.source||'-'],['Latest status',latest.status||'-'],['Severity',latest.severity||'-'],['Active incident',latest.activeIncident||'-'],['Freshness',model.fresh.age],['Derived score',model.score.toFixed(0)]].map(([a,b])=>`<div class="soft-row"><span>${esc(a)}</span><strong>${esc(b)}</strong></div>`).join('');}
function renderCloudflare(model){const payload=model.health; const status=model.cfStatus; setText('cloudflare-chip',status); setClass('cloudflare-chip',`state-chip ${tone(status)}`); const endpoints=payload.cloudflare?.publicEndpoints||[]; const cards=[{name:'control.hitechrts.com',url:model.route.url,status:model.route.ok?'PASS':'DEGRADED',note:`${model.route.statusCode} / ${model.route.latencyMs}ms`},...endpoints.slice(0,11).map(e=>({name:e.name||e.host||e.url,url:e.url,status:e.probe?.ok?'PASS':(e.status||'UNKNOWN'),note:e.probe?.statusCode||e.status||'-'}))]; $('route-grid').innerHTML=cards.map(e=>`<article class="route-card"><div>${chip(e.status)}</div><strong>${esc(e.name||'endpoint')}</strong><small>${esc(e.url||'')}</small><small>${esc(e.note||'')}</small></article>`).join('');}
function renderTables(model){const payload=model.health; const query=($('service-search')?.value||'').toLowerCase(); const rows=services(payload).filter(s=>JSON.stringify(s).toLowerCase().includes(query)); $('services-table').innerHTML='<thead><tr><th>Servicio</th><th>Puerto</th><th>Estado</th><th>Local</th><th>LAN</th><th>Publico</th><th>Latencia</th></tr></thead><tbody>'+rows.map(s=>`<tr><td>${esc(roleLabel(s))}</td><td>${esc(servicePort(s))}</td><td>${chip(serviceStatus(s))}</td><td>${chip(endpointOk(s.localHttp),formatMs(s.localHttp?.latencyMs))}</td><td>${chip(endpointOk(s.lanHttp),formatMs(s.lanHttp?.latencyMs))}</td><td>${chip(endpointOk(s.publicHttp),formatMs(s.publicHttp?.latencyMs))}</td><td>${formatMs(s.localHttp?.latencyMs)}</td></tr>`).join('')+'</tbody>'; const endpoints=payload.cloudflare?.publicEndpoints||[]; $('public-table').innerHTML='<thead><tr><th>Endpoint</th><th>URL</th><th>Status</th><th>Latencia</th></tr></thead><tbody>'+endpoints.map(e=>`<tr><td>${esc(e.name||e.host||'-')}</td><td>${esc(e.url||'-')}</td><td>${chip(e.probe?.ok||e.status,e.probe?.statusCode||e.status)}</td><td>${formatMs(e.probe?.latencyMs)}</td></tr>`).join('')+'</tbody>';}
function renderRaw(model){$('raw-block').textContent=JSON.stringify(mode()==='PUBLIC_REDACTED'?sanitize(model):model,null,2);}
function clockTick(){const now=new Date(); setText('clock-time',now.toLocaleTimeString('es-MX',{hour12:false})); setText('clock-date',now.toLocaleDateString('es-MX',{day:'2-digit',month:'short',year:'numeric'}).toUpperCase());}
function showView(view){activeView=view; localStorage.setItem(STORE_VIEW,view); $$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.view===view)); const target=document.querySelector(`[data-panel="${view}"]`); if(target)target.scrollIntoView({behavior:'smooth',block:'start'});}
async function refresh(){document.body.classList.add('loading'); try{const [health,incidents]=await fetchJsonBatch(['/api/health','/api/incidents']); renderShell(health.__error?{}:health,incidents.__error?{}:incidents); toast('Data Core actualizado');}catch(error){toast(`Error: ${error.message}`);}finally{document.body.classList.remove('loading');}}
function fetchJson(url){return fetch(url,{cache:'no-store',headers:{Accept:'application/json'}}).then(r=>{if(!r.ok)throw new Error(`${url} ${r.status}`); return r.json();});}
function fetchJsonBatch(urls){return Promise.all(urls.map(u=>fetchJson(u).catch(error=>({__error:String(error),url:u}))));}
function copyBrief(){const m=lastModel; if(!m){toast('Sin datos para copiar'); return;} const brief=`PRISMA Data Core brief\nStatus: ${m.overall}\nScore: ${m.score.toFixed(0)}\nServices PASS: ${m.c.pass}/${m.c.total}\nIncidents: ${m.active.length}\nCloudflare: ${m.cfStatus} ${m.route.statusCode}\nFreshness: ${m.fresh.age}\nBlockers: ${m.blockers.join('; ')||'none'}\nAction: ${m.recommendation}`; navigator.clipboard?.writeText(brief).then(()=>toast('Brief copiado')).catch(()=>toast('No se pudo copiar'));}
function boot(){clockTick(); setInterval(clockTick,1000); $$('.nav-item').forEach(b=>b.addEventListener('click',()=>showView(b.dataset.view))); $('refresh-button')?.addEventListener('click',refresh); $('pause-button')?.addEventListener('click',()=>{autoRefresh=!autoRefresh; localStorage.setItem('prisma-crystal-paused',autoRefresh?'no':'yes'); setText('pause-button',autoRefresh?'Pause':'Resume'); toast(autoRefresh?'Auto-refresh activo':'Auto-refresh pausado');}); $('copy-brief')?.addEventListener('click',copyBrief); $('service-search')?.addEventListener('input',()=>lastModel&&renderTables(lastModel)); showView(activeView); refresh(); timer=setInterval(()=>{if(autoRefresh)refresh();},REFRESH_MS);}
window.addEventListener('DOMContentLoaded',boot);