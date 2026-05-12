
/* PRISMA Iteration 3 - Black-box Command companion */
(function(){
  const $ = (id)=>document.getElementById(id);
  const esc = (v)=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
  const statusOf=(v)=>String(v||'EMPTY').toUpperCase();
  const tone=(v)=>{const s=statusOf(v).toLowerCase(); if(['pass','ok','connected','resolved'].includes(s))return'pass'; if(['warn','warning','degraded','active'].includes(s))return'warn'; if(['fail','error','blocked'].some(x=>s.includes(x)))return'fail'; return 'subtle';};
  const chip=(v,label=v)=>`<span class="state-chip ${tone(v)}">${esc(label)}</span>`;
  const age=(value)=>{if(!value)return'-'; const d=new Date(value); if(Number.isNaN(d.getTime()))return'-'; const sec=Math.max(0,Math.round((Date.now()-d.getTime())/1000)); if(sec<60)return `${sec}s`; const min=Math.round(sec/60); if(min<60)return `${min}m`; return `${Math.round(min/60)}h`;};
  async function getJson(url){const r=await fetch(url,{cache:'no-store',headers:{Accept:'application/json'}}); if(!r.ok)throw new Error(`${url} ${r.status}`); return r.json();}
  function ensurePanel(){
    if($('blackbox-command'))return;
    const anchor=$('blackbox');
    if(!anchor)return;
    const section=document.createElement('article');
    section.className='glass-card blackbox-command';
    section.id='blackbox-command';
    section.dataset.panel='blackbox-command';
    section.innerHTML=`
      <div class="card-heading"><div><p class="eyebrow">Black-box Command</p><h3>Timeline, evidencia y memoria auditable</h3></div><span id="bb-command-chip" class="state-chip subtle">cargando</span></div>
      <div class="bb-command-strip">
        <div class="bb-mini"><small>Activos</small><strong id="bb-active-count">0</strong></div>
        <div class="bb-mini"><small>Resueltos recientes</small><strong id="bb-resolved-count">0</strong></div>
        <div class="bb-mini"><small>Timeline tail</small><strong id="bb-timeline-count">0</strong></div>
        <div class="bb-mini"><small>Event tail</small><strong id="bb-event-count">0</strong></div>
      </div>
      <div class="blackbox-command-grid">
        <section><div class="card-heading"><div><p class="eyebrow">Timeline</p><h3>Eventos auditables</h3></div><button id="bb-refresh" type="button">Refresh Black-box</button></div><div class="bb-timeline" id="bb-timeline"></div></section>
        <section><div class="card-heading"><div><p class="eyebrow">Evidencia</p><h3>Incidente seleccionado</h3></div><span id="bb-selected" class="state-chip subtle">auto</span></div><div class="bb-evidence" id="bb-evidence"></div></section>
      </div>
      <details class="bb-event-log"><summary>Black-box event tail JSONL</summary><pre class="bb-event-tail" id="bb-event-tail">cargando...</pre></details>`;
    anchor.insertAdjacentElement('afterend',section);
    $('bb-refresh')?.addEventListener('click',refreshBlackboxCommand);
  }
  function eventLabel(event){return event.eventType||event.type||event.status||event.source||'event';}
  function eventStatus(event){return event.severity||event.status||event.state||'INFO';}
  function renderTimeline(items){const node=$('bb-timeline'); if(!node)return; if(!items?.length){node.innerHTML='<div class="bb-empty">Sin eventos en timeline.</div>';return;} node.innerHTML=items.slice().reverse().map(ev=>`<article class="bb-event ${tone(eventStatus(ev))}"><div class="bb-event-time">${esc(age(ev.time||ev.updatedAt||ev.createdAt))}<br><small>${esc(ev.time||'')}</small></div><div class="bb-event-body"><div>${chip(eventStatus(ev))}</div><strong>${esc(eventLabel(ev))}</strong><small>${esc(ev.incidentId||ev.activeIncident||ev.runId||ev.source||'')}</small></div></article>`).join('');}
  function renderEvidence(summary){const node=$('bb-evidence'); if(!node)return; const active=summary.activeIncidents||[]; const incident=active[0]||summary.resolvedRecent?.[0]; if(!incident){node.innerHTML='<div class="bb-empty">Sin incidente para mostrar.</div>';return;} const files=incident.evidenceFiles||[]; $('bb-selected').textContent=incident.id||incident.folderName||'auto'; node.innerHTML=`<article class="bb-evidence-card"><div class="chip-row">${chip(incident.severity)}${chip(incident.status)}${chip(incident.state)}</div><h4>${esc(incident.id||incident.folderName)}</h4><p>${esc(incident.recommendedNextAction||'Sin recomendacion')}</p><div class="soft-row"><span>Run</span><strong>${esc(incident.runId||'-')}</strong></div><div class="soft-row"><span>Score</span><strong>${esc(incident.healthScore??'-')}</strong></div></article><div class="bb-file-list">${files.length?files.map(f=>`<div class="bb-file"><span>${esc(f.kind||'file')}</span><strong title="${esc(f.path||'')}">${esc(f.relativePath||f.name)}</strong></div>`).join(''):'<div class="bb-empty">Sin archivos de evidencia listados.</div>'}</div>`;}
  function renderSummary(summary){$('bb-command-chip').textContent=summary.latestBridge?.status||'BLACKBOX'; $('bb-command-chip').className=`state-chip ${tone(summary.latestBridge?.severity||summary.latestBridge?.status)}`; $('bb-active-count').textContent=summary.counts?.active??0; $('bb-resolved-count').textContent=summary.counts?.resolvedRecent??0; $('bb-timeline-count').textContent=summary.counts?.timelineTail??0; $('bb-event-count').textContent=summary.counts?.eventTail??0; renderTimeline(summary.timelineTail||[]); renderEvidence(summary); $('bb-event-tail').textContent=JSON.stringify(summary.eventTail||[],null,2);}
  async function refreshBlackboxCommand(){ensurePanel(); try{const summary=await getJson('/api/blackbox/summary?limit=120'); renderSummary(summary);}catch(error){const chip=$('bb-command-chip'); if(chip){chip.textContent='API ERROR'; chip.className='state-chip fail';} const tl=$('bb-timeline'); if(tl)tl.innerHTML=`<div class="bb-empty">No respondio /api/blackbox/summary: ${esc(error.message)}</div>`;}}
  window.PRISMA_BLACKBOX_COMMAND_ITER3 = {refresh:refreshBlackboxCommand};
  window.addEventListener('DOMContentLoaded',()=>{ensurePanel(); refreshBlackboxCommand(); setInterval(refreshBlackboxCommand,10000);});
})();
