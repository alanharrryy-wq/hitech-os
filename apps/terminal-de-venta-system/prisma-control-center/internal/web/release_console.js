
/* PRISMA Iteration 5 - Ultra Polish + Release companion */
(function(){
  const $=(id)=>document.getElementById(id);
  const esc=(v)=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
  const tone=(v)=>{const s=String(v||'').toLowerCase(); if(['ready','pass','ok','true'].some(x=>s.includes(x)))return'pass'; if(['warning','degraded','warn'].some(x=>s.includes(x)))return'warn'; if(['fail','error','blocked'].some(x=>s.includes(x)))return'fail'; return'subtle';};
  const chip=(v,label=v)=>`<span class="state-chip ${tone(v)}">${esc(label)}</span>`;
  async function getJson(url){const r=await fetch(url,{cache:'no-store',headers:{Accept:'application/json'}}); if(!r.ok)throw new Error(`${url} ${r.status}`); return r.json();}
  function ensureDock(){
    if($('release-dock'))return;
    const dock=document.createElement('div');
    dock.className='release-dock'; dock.id='release-dock';
    dock.innerHTML='<span id="release-dot" class="release-dot warn"></span><button id="release-refresh" type="button">Release Check</button><button id="release-copy" type="button">Copy Release Brief</button><a href="/api/release/status" target="_blank" rel="noreferrer">Release JSON</a><a href="/latest/health.html" target="_blank" rel="noreferrer">Latest Report</a>';
    document.body.appendChild(dock);
    $('release-refresh')?.addEventListener('click',refreshRelease);
    $('release-copy')?.addEventListener('click',copyReleaseBrief);
  }
  function ensurePanel(){
    if($('release-panel'))return;
    const anchor=$('ops-command')||$('blackbox-command')||$('reports')||document.querySelector('.workspace-grid');
    if(!anchor)return;
    const panel=document.createElement('article');
    panel.className='glass-card release-panel'; panel.id='release-panel'; panel.dataset.panel='release';
    panel.innerHTML='<div class="release-shimmer"></div><div class="card-heading"><div><p class="eyebrow">Ultra Polish + Release</p><h3>Estado final, checklist y manifiesto</h3></div><span id="release-chip" class="state-chip subtle">cargando</span></div><div class="release-scoreboard"><div class="release-tile"><small>Status</small><strong id="release-status">-</strong></div><div class="release-tile"><small>Features</small><strong id="release-features">0/5</strong></div><div class="release-tile"><small>Health</small><strong id="release-health">-</strong></div><div class="release-tile"><small>Incidents</small><strong id="release-incidents">-</strong></div><div class="release-tile"><small>Bridge</small><strong id="release-bridge">-</strong></div></div><div class="release-grid"><section><div class="card-heading"><div><p class="eyebrow">Checklist</p><h3>Iteraciones detectadas</h3></div></div><div class="release-checklist" id="release-checklist"></div></section><section><div class="card-heading"><div><p class="eyebrow">Release manifest</p><h3>Snapshot tecnico</h3></div></div><pre class="release-terminal" id="release-terminal">cargando...</pre></section></div>';
    anchor.insertAdjacentElement('afterend',panel);
  }
  function render(data){
    ensureDock(); ensurePanel();
    const ready=String(data.status||'').includes('READY');
    document.body.classList.toggle('release-ready',data.status==='READY');
    document.body.classList.toggle('release-warning',data.status!=='READY');
    $('release-dot').className='release-dot '+(data.status==='READY'?'':'warn');
    $('release-chip').textContent=data.status||'UNKNOWN'; $('release-chip').className=`state-chip ${tone(data.status)}`;
    $('release-status').textContent=data.status||'-';
    const features=data.features||{}; const passed=Object.values(features).filter(Boolean).length; const total=Object.keys(features).length||5;
    $('release-features').textContent=`${passed}/${total}`; $('release-health').textContent=`${data.health?.overallStatus||'-'} ${data.health?.healthScore??''}`; $('release-incidents').textContent=data.counts?.activeIncidents??'-'; $('release-bridge').textContent=data.bridge?.status||'-';
    $('release-checklist').innerHTML=Object.entries(features).map(([k,v])=>`<div class="release-check"><span>${esc(k)}</span><b>${chip(v?'PASS':'MISSING',v?'PASS':'MISSING')}</b></div>`).join('')+(data.blockers?.length?data.blockers.map(x=>`<div class="release-check"><span>${esc(x)}</span><b>${chip('WARN')}</b></div>`).join(''):'');
    $('release-terminal').textContent=JSON.stringify(data,null,2);
  }
  async function refreshRelease(){ensureDock(); ensurePanel(); try{const data=await getJson('/api/release/status'); render(data);}catch(error){$('release-terminal')&&($('release-terminal').textContent='ERROR '+error.message);}}
  async function copyReleaseBrief(){try{const d=await getJson('/api/release/status'); const f=d.features||{}; const brief=`PRISMA Crystal Ops Release\nStatus: ${d.status}\nFeatures: ${Object.values(f).filter(Boolean).length}/${Object.keys(f).length}\nHealth: ${d.health?.overallStatus} ${d.health?.healthScore}\nIncidents: ${d.counts?.activeIncidents}\nBridge: ${d.bridge?.status}/${d.bridge?.severity}\nNext: ${d.health?.recommendedNextAction||'Sin accion inmediata'}`; await navigator.clipboard.writeText(brief); $('release-terminal')&&($('release-terminal').textContent='Release brief copiado.\n\n'+brief);}catch(error){$('release-terminal')&&($('release-terminal').textContent='ERROR '+error.message);}}
  window.PRISMA_RELEASE_ITER5={refresh:refreshRelease};
  window.addEventListener('DOMContentLoaded',()=>{ensureDock(); ensurePanel(); refreshRelease(); setInterval(refreshRelease,15000);});
})();
