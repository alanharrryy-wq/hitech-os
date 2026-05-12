
/* PRISMA Iteration 4 - Cloudflare + Control Actions companion */
(function(){
  const $=(id)=>document.getElementById(id);
  const esc=(v)=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
  const statusOf=(v)=>String(v||'EMPTY').toUpperCase();
  const tone=(v)=>{const s=statusOf(v).toLowerCase(); if(['pass','ok','connected','visible'].includes(s))return'pass'; if(['warn','warning','degraded','active'].includes(s))return'warn'; if(['fail','error','blocked','forbidden'].some(x=>s.includes(x)))return'fail'; return 'subtle';};
  const chip=(v,label=v)=>`<span class="state-chip ${tone(v)}">${esc(label)}</span>`;
  async function getJson(url){const r=await fetch(url,{cache:'no-store',headers:{Accept:'application/json'}}); if(!r.ok)throw new Error(`${url} ${r.status}`); return r.json();}
  function ensurePanel(){
    if($('ops-command'))return;
    const anchor=$('cloudflare')||$('reports')||document.querySelector('.workspace-grid');
    if(!anchor)return;
    const section=document.createElement('article');
    section.className='glass-card ops-command';
    section.id='ops-command';
    section.dataset.panel='ops-command';
    section.innerHTML=`
      <div class="card-heading"><div><p class="eyebrow">Cloudflare + Control Actions</p><h3>Diagnostico publico y acciones locales seguras</h3></div><span id="ops-status-chip" class="state-chip subtle">cargando</span></div>
      <div class="ops-strip">
        <div class="ops-mini"><small>Cloudflare</small><strong id="ops-cf-status">-</strong></div>
        <div class="ops-mini"><small>Score</small><strong id="ops-score">-</strong></div>
        <div class="ops-mini"><small>Incidentes</small><strong id="ops-incidents">-</strong></div>
        <div class="ops-mini"><small>Bridge</small><strong id="ops-bridge">-</strong></div>
        <div class="ops-mini"><small>Modo</small><strong id="ops-mode">-</strong></div>
      </div>
      <div class="ops-grid">
        <section><div class="card-heading"><div><p class="eyebrow">Rutas publicas</p><h3>Endpoint diagnostics</h3></div><button id="ops-refresh" type="button">Refresh ops</button></div><div class="ops-endpoints" id="ops-endpoints"></div><div class="ops-diag-list" id="ops-diagnosis"></div></section>
        <section class="ops-action-panel">
          <article class="ops-action"><h4>Run Health</h4><p>Ejecuta health real desde el panel local y actualiza Black-box.</p><button id="ops-run-health" type="button">Run Health Now</button></article>
          <article class="ops-action"><h4>Operator Brief</h4><p>Copia un resumen operativo con Cloudflare, incidentes y siguiente accion.</p><button id="ops-copy-brief" type="button">Copy Operator Brief</button></article>
          <article class="ops-action"><h4>Latest Report</h4><p>Abre el ultimo reporte HTML generado por Control Center.</p><a href="/latest/health.html" target="_blank" rel="noreferrer">Open Latest Report</a></article>
          <pre class="ops-result" id="ops-result">Esperando accion...</pre>
        </section>
      </div>`;
    anchor.insertAdjacentElement('afterend',section);
    $('ops-refresh')?.addEventListener('click',refreshOps);
    $('ops-run-health')?.addEventListener('click',runHealth);
    $('ops-copy-brief')?.addEventListener('click',copyBrief);
  }
  function render(data){
    $('ops-status-chip').textContent=data.status||'OPS'; $('ops-status-chip').className=`state-chip ${tone(data.status)}`;
    $('ops-cf-status').textContent=data.status||'-'; $('ops-score').textContent=data.healthScore??'-'; $('ops-incidents').textContent=data.activeIncidentCount??0; $('ops-bridge').textContent=data.latestBridge?.status||'-'; $('ops-mode').textContent=data.safetyMode||'-';
    $('ops-endpoints').innerHTML=(data.endpoints||[]).slice(0,12).map(e=>{const probe=e.probe||{}; const ok=probe.ok===true||probe.statusCode===200; return `<article class="ops-endpoint"><div>${chip(ok?'PASS':(probe.statusCode||e.status||'UNKNOWN'))}</div><strong>${esc(e.name||e.host||'endpoint')}</strong><small>${esc(e.url||'')}</small><small>${esc(probe.statusCode||probe.status||'')} ${esc(probe.latencyMs?probe.latencyMs+'ms':'')}</small></article>`;}).join('')||'<div class="ops-endpoint">Sin endpoints.</div>';
    $('ops-diagnosis').innerHTML=(data.diagnosis||[]).map(x=>`<div class="ops-diag">${esc(x)}</div>`).join('');
  }
  async function refreshOps(){ensurePanel(); try{const data=await getJson('/api/ops/cloudflare'); render(data); $('ops-result').textContent=JSON.stringify(data,null,2);}catch(error){$('ops-result').textContent=`ERROR ${error.message}`;}}
  async function runHealth(){ensurePanel(); $('ops-result').textContent='Ejecutando health real...'; try{const data=await getJson('/api/ops/action/run-health'); $('ops-result').textContent=JSON.stringify(data,null,2); await refreshOps(); window.PRISMA_BLACKBOX_COMMAND_ITER3?.refresh?.();}catch(error){$('ops-result').textContent=`ERROR ${error.message}`;}}
  async function copyBrief(){try{const data=await getJson('/api/ops/operator-brief'); await navigator.clipboard.writeText(data.briefText||JSON.stringify(data,null,2)); $('ops-result').textContent='Operator brief copiado.\n\n'+(data.briefText||'');}catch(error){$('ops-result').textContent=`ERROR ${error.message}`;}}
  window.PRISMA_OPS_COMMAND_ITER4={refresh:refreshOps,runHealth};
  window.addEventListener('DOMContentLoaded',()=>{ensurePanel(); refreshOps(); setInterval(refreshOps,12000);});
})();
