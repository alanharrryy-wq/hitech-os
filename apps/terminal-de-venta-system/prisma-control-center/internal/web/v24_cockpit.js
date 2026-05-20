const THEMES = {
  liquid:{
    subtitle:'Obsidian Rose Royale · reactor, rutas, señales, evidencia y auditoría.',
    material:'vidrio oscuro profundo, metal líquido pulido, caústicas cian/violeta y brillo óptico vivo.',
    reactor:'Halo periférico, sweep parcial y luces vivas alrededor; sin efecto rueda de la fortuna.'
  },
  tactical:{
    subtitle:'Tactical Graphite · reactor, rutas, señales, evidencia y auditoría.',
    material:'grafito táctico, fibra oscura, bordes secos, cortes angulares y lectura instrumental sin glow de más.',
    reactor:'Lectura técnica, halo bajo y foco en precisión más que en ornamento.'
  },
  piel:{
    subtitle:'Obsidian Rose Royale · reactor, rutas, señales, evidencia y auditoría.',
    material:'obsidiana lacada, negro vantal, cristal ahumado y rose gold noble con cuarzo rosé: lujo suizo-inglés, frío, caro y perfectamente peinado; cero madera, cero rosa penoso.',
    reactor:'Dial joya: obsidiana espejo, aro rose gold fino, pulso rosé metálico y reflejo de cristal negro como reloj suizo de bóveda privada.'
  },
  pearl:{
    subtitle:'Pearl Ice · reactor, rutas, señales, evidencia y auditoría.',
    material:'vidrio hielo transparente, titanio/plata óptica, brillos fríos y azul eléctrico medido; cero beige.',
    reactor:'Cristal óptico claro, borde plata, reflejos de lente y contraste frío con lectura nítida.'
  }
};
const CHARTS={
  liquid:{
    support:`<svg viewBox="0 0 360 132"><defs><linearGradient id="ls1" x1="0" x2="1"><stop stop-color="currentColor" stop-opacity=".02"/><stop offset="1" stop-color="currentColor" stop-opacity=".16"/></linearGradient></defs><g stroke="var(--line)"><path d="M8 104H352"/><path d="M8 72H352"/><path d="M8 40H352"/></g><path d="M10 92 C 52 34, 96 104, 142 48 S 220 28, 268 54 S 322 68, 350 24 L350 132 L10 132Z" fill="url(#ls1)"/><path class="chartStroke" d="M10 92 C 52 34, 96 104, 142 48 S 220 28, 268 54 S 322 68, 350 24" fill="none" stroke="currentColor" stroke-width="4.5"/><path class="chartStroke2" d="M10 100 C 50 86, 94 82, 142 70 S 222 62, 268 68 S 322 52, 350 46" fill="none" stroke="currentColor" stroke-opacity=".32" stroke-width="2.5"/></svg>`,
    core:`<svg viewBox="0 0 240 100"><defs><linearGradient id="lc1" x1="0" x2="1"><stop stop-color="currentColor" stop-opacity=".03"/><stop offset="1" stop-color="currentColor" stop-opacity=".16"/></linearGradient></defs><g stroke="var(--line)"><path d="M0 84H240"/><path d="M0 56H240"/><path d="M0 28H240"/></g><path d="M0 74 C26 66,44 70,62 52 S96 56,122 34 S166 24,200 18 S226 16,240 10 L240 100 L0 100Z" fill="url(#lc1)"/><path class="chartStroke" d="M0 74 C26 66,44 70,62 52 S96 56,122 34 S166 24,200 18 S226 16,240 10" fill="none" stroke="currentColor" stroke-width="4.3"/></svg>`,
    routes:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M12 72 C42 24,86 76,126 42 S190 20,228 30" fill="none" stroke="currentColor" stroke-width="4.4"/><path class="chartStroke2" d="M12 82 C48 64,88 62,126 58 S188 46,228 40" fill="none" stroke="currentColor" stroke-opacity=".3" stroke-width="2.4"/><circle cx="126" cy="42" r="4.4" fill="currentColor"/></svg>`,
    queue:`<svg viewBox="0 0 240 100"><defs><linearGradient id="lq" x1="0" x2="1"><stop stop-color="currentColor" stop-opacity=".03"/><stop offset="1" stop-color="currentColor" stop-opacity=".18"/></linearGradient></defs><path d="M0 84 C28 78,64 72,96 58 S148 46,182 34 S214 24,240 18 L240 100 L0 100Z" fill="url(#lq)"/><path class="chartStroke" d="M0 84 C28 78,64 72,96 58 S148 46,182 34 S214 24,240 18" fill="none" stroke="currentColor" stroke-width="4.4"/></svg>`,
    audit:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M16 74 H56 L84 46 L116 70 L154 30 L190 50 L224 38" fill="none" stroke="currentColor" stroke-width="4.4" stroke-linejoin="round"/><circle cx="154" cy="30" r="4.8" fill="currentColor"/></svg>`
  },
  tactical:{
    support:`<svg viewBox="0 0 360 132"><g stroke="var(--line)"><path d="M12 106H348"/><path d="M12 76H348"/><path d="M12 46H348"/><path d="M40 18V118"/><path d="M100 18V118"/><path d="M160 18V118"/><path d="M220 18V118"/><path d="M280 18V118"/></g><g fill="currentColor"><rect x="26" y="86" width="30" height="20" opacity=".28"/><rect x="72" y="66" width="30" height="40" opacity=".42"/><rect x="118" y="46" width="30" height="60" opacity=".62"/><rect x="164" y="60" width="30" height="46" opacity=".46"/><rect x="210" y="34" width="30" height="72" opacity=".78"/><rect x="256" y="54" width="30" height="52" opacity=".52"/><rect x="302" y="24" width="30" height="82" opacity=".9"/></g></svg>`,
    core:`<svg viewBox="0 0 240 100"><g stroke="var(--line)"><path d="M0 84H240"/><path d="M0 56H240"/><path d="M0 28H240"/></g><g fill="currentColor"><rect x="16" y="70" width="22" height="14" opacity=".30"/><rect x="48" y="58" width="22" height="26" opacity=".48"/><rect x="80" y="42" width="22" height="42" opacity=".68"/><rect x="112" y="26" width="22" height="58" opacity=".9"/><rect x="144" y="42" width="22" height="42" opacity=".62"/><rect x="176" y="18" width="22" height="66" opacity=".84"/></g></svg>`,
    routes:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M16 34 H72 V54 H126 V38 H226" fill="none" stroke="currentColor" stroke-width="4.4"/><path class="chartStroke2" d="M16 78 H88 V64 H156 V50 H226" fill="none" stroke="currentColor" stroke-opacity=".34" stroke-width="2.5"/></svg>`,
    queue:`<svg viewBox="0 0 240 100"><g stroke="var(--line)"><path d="M0 84H240"/><path d="M0 56H240"/><path d="M0 28H240"/></g><path class="chartStroke" d="M10 84 H42 V78 H74 V68 H106 V56 H138 V44 H170 V32 H230" fill="none" stroke="currentColor" stroke-width="4.4"/></svg>`,
    audit:`<svg viewBox="0 0 240 100"><rect x="20" y="22" width="82" height="52" fill="none" stroke="currentColor" stroke-opacity=".15"/><rect x="138" y="22" width="82" height="52" fill="none" stroke="currentColor" stroke-opacity=".10"/><path class="chartStroke" d="M34 48 L52 64 L90 28" fill="none" stroke="currentColor" stroke-width="3.8"/><path class="chartStroke2" d="M152 48 L170 64 L208 28" fill="none" stroke="currentColor" stroke-width="3.8" stroke-opacity=".7"/></svg>`
  },
  piel:{
    support:`<svg viewBox="0 0 360 132"><defs><linearGradient id="orSupport" x1="0" x2="1"><stop stop-color="#94606c" stop-opacity=".05"/><stop offset=".46" stop-color="#d9a0aa" stop-opacity=".22"/><stop offset="1" stop-color="#fff1f4" stop-opacity=".14"/></linearGradient></defs><g stroke="var(--line)"><path d="M10 104H350"/><path d="M10 72H350"/><path d="M10 40H350"/></g><path d="M12 98 C54 54,92 110,138 62 S220 34,272 50 S322 64,350 32 L350 132 L12 132Z" fill="url(#orSupport)"/><path class="chartStroke" d="M12 98 C54 54,92 110,138 62 S220 34,272 50 S322 64,350 32" fill="none" stroke="currentColor" stroke-width="5.1"/><path class="chartStroke2" d="M12 108 C54 88,98 82,142 72 S226 60,276 68 S322 56,350 46" fill="none" stroke="#ffe7ee" stroke-opacity=".34" stroke-width="2.4"/><circle cx="272" cy="50" r="5" fill="currentColor"/></svg>`,
    core:`<svg viewBox="0 0 240 100"><path d="M20 74 A100 100 0 0 1 220 74" fill="none" stroke="currentColor" stroke-opacity=".16" stroke-width="9"/><path class="chartStroke" d="M20 74 A100 100 0 0 1 178 36" fill="none" stroke="currentColor" stroke-width="9"/><path class="chartStroke2" d="M120 74L178 36" fill="none" stroke="#ffe7ee" stroke-opacity=".42" stroke-width="3.2"/><path d="M54 74V62 M88 52L84 40 M120 40V22 M154 50L160 38 M188 74V62" stroke="currentColor" stroke-width="2" opacity=".72"/></svg>`,
    routes:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M16 74 C42 36,78 70,112 48 S172 28,224 34" fill="none" stroke="currentColor" stroke-width="4.8"/><path class="chartStroke2" d="M16 84 C52 68,88 64,124 60 S188 48,224 44" fill="none" stroke="#ffe7ee" stroke-opacity=".30" stroke-width="2.3"/><circle cx="112" cy="48" r="4.6" fill="currentColor"/><circle cx="190" cy="30" r="4.4" fill="#ffe7ee" opacity=".42"/></svg>`,
    queue:`<svg viewBox="0 0 240 100"><defs><linearGradient id="orQueue" x1="0" x2="1"><stop stop-color="currentColor" stop-opacity=".05"/><stop offset="1" stop-color="currentColor" stop-opacity=".20"/></linearGradient></defs><g stroke="var(--line)"><path d="M0 84H240"/><path d="M0 56H240"/><path d="M0 28H240"/></g><path d="M12 82 C46 78,72 70,98 58 S146 38,178 42 S216 30,230 22 L230 100 L12 100Z" fill="url(#orQueue)"/><path class="chartStroke" d="M12 82 C46 78,72 70,98 58 S146 38,178 42 S216 30,230 22" fill="none" stroke="currentColor" stroke-width="4.6"/></svg>`,
    audit:`<svg viewBox="0 0 240 100"><rect x="20" y="24" width="48" height="34" rx="10" fill="none" stroke="currentColor" opacity=".55"/><rect x="96" y="24" width="48" height="34" rx="10" fill="none" stroke="currentColor" opacity=".36"/><rect x="172" y="24" width="48" height="34" rx="10" fill="none" stroke="#ffe7ee" opacity=".22"/><path class="chartStroke" d="M30 42 L40 52 L58 32" fill="none" stroke="currentColor" stroke-width="3.4"/><path class="chartStroke2" d="M106 42 L116 52 L134 32" fill="none" stroke="#ffe7ee" stroke-opacity=".42" stroke-width="3.4"/></svg>`
  },
  pearl:{
    support:`<svg viewBox="0 0 360 132"><defs><linearGradient id="ps1" x1="0" x2="1"><stop stop-color="currentColor" stop-opacity=".02"/><stop offset="1" stop-color="currentColor" stop-opacity=".14"/></linearGradient></defs><g stroke="var(--line)"><path d="M10 104H350"/><path d="M10 72H350"/><path d="M10 40H350"/></g><path d="M10 90 C 52 52, 96 102, 148 50 S 234 26, 288 48 S 328 62, 350 30 L350 132 L10 132Z" fill="url(#ps1)"/><path class="chartStroke" d="M10 90 C 52 52, 96 102, 148 50 S 234 26, 288 48 S 328 62, 350 30" fill="none" stroke="currentColor" stroke-width="4.1"/><path class="chartStroke2" d="M12 100 C 54 84, 96 80, 148 68 S 234 60, 288 68 S 328 58, 350 52" fill="none" stroke="currentColor" stroke-opacity=".24" stroke-width="2.2"/></svg>`,
    core:`<svg viewBox="0 0 240 100"><defs><linearGradient id="pc1" x1="0" x2="1"><stop stop-color="currentColor" stop-opacity=".03"/><stop offset="1" stop-color="currentColor" stop-opacity=".12"/></linearGradient></defs><g stroke="var(--line)"><path d="M0 84H240"/><path d="M0 56H240"/><path d="M0 28H240"/></g><path d="M0 74 C28 58,52 64,82 42 S134 38,166 24 S210 18,240 12 L240 100 L0 100Z" fill="url(#pc1)"/><path class="chartStroke" d="M0 74 C28 58,52 64,82 42 S134 38,166 24 S210 18,240 12" fill="none" stroke="currentColor" stroke-width="4"/></svg>`,
    routes:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M12 70 C42 28,88 76,126 42 S186 22,226 28" fill="none" stroke="currentColor" stroke-width="4.1"/><path class="chartStroke2" d="M14 80 C52 64,92 60,126 56 S188 44,228 40" fill="none" stroke="currentColor" stroke-opacity=".22" stroke-width="2.2"/></svg>`,
    queue:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M18 80 L62 62 L104 56 L146 38 L188 28 L222 20" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="104" cy="56" r="4.5" fill="currentColor"/><circle cx="188" cy="28" r="4.5" fill="currentColor"/></svg>`,
    audit:`<svg viewBox="0 0 240 100"><path class="chartStroke" d="M18 58 C36 40,52 74,72 54 S108 34,126 54 S164 72,186 48 S212 34,224 44" fill="none" stroke="currentColor" stroke-width="4"/></svg>`
  }
};
const subtitle = document.getElementById('subtitle');
const materialText = document.getElementById('materialText');
const reactorText = document.getElementById('reactorText');
const themeSelect = document.getElementById('themeSelect');
const supportChart = document.getElementById('supportChart');
const charts = [...document.querySelectorAll('.miniChart')];
const freshness = document.getElementById('freshness');
function applyTheme(theme){
  document.body.dataset.theme = theme;
  themeSelect.value = theme;
  subtitle.textContent = THEMES[theme].subtitle;
  materialText.textContent = THEMES[theme].material;
  reactorText.textContent = THEMES[theme].reactor;
  supportChart.innerHTML = CHARTS[theme].support;
  charts.forEach(el=>{ el.innerHTML = CHARTS[theme][el.dataset.chart]; });
  restartDraw();
  try{ localStorage.setItem('prisma-v28-theme', theme); }catch(e){}
}
function restartDraw(){
  document.querySelectorAll('.chartStroke,.chartStroke2').forEach(el=>{ el.style.animation='none'; el.getBoundingClientRect(); el.style.animation=''; });
}
function setXY(el, e){
  const r = el.getBoundingClientRect();
  el.style.setProperty('--mx', ((e.clientX-r.left)/r.width)*100 + '%');
  el.style.setProperty('--my', ((e.clientY-r.top)/r.height)*100 + '%');
}
document.querySelectorAll('.topbar,.panel,.card,.dockBtn,.dockSearch,.signal,.metric,.timelineCard,.picker,.node,.miniChartWrap').forEach(el=>{
  el.addEventListener('pointermove', e => setXY(el,e), {passive:true});
  el.addEventListener('pointerleave', ()=>{el.style.setProperty('--mx','50%'); el.style.setProperty('--my','50%');});
});
themeSelect.addEventListener('change', e => applyTheme(e.target.value));


function syncTopbarHeight(){
  const topbar = document.getElementById('topbar');
  if(!topbar) return;
  requestAnimationFrame(()=>{
    document.documentElement.style.setProperty('--topbar-height', Math.ceil(topbar.offsetHeight) + 'px');
  });
}
window.addEventListener('load', syncTopbarHeight);
window.addEventListener('resize', syncTopbarHeight);
themeSelect.addEventListener('change', ()=>setTimeout(syncTopbarHeight, 0));
syncTopbarHeight();

setInterval(()=>{ freshness.textContent = `Frescura ${3 + Math.floor(Math.random()*3)} s`; }, 1800);
applyTheme((()=>{ try{return localStorage.getItem('prisma-v28-theme') || 'liquid';}catch(e){return 'liquid';} })());


// V23 tactile motion: subtle node tilt, no carousel nonsense.
(function(){
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce) return;
  document.querySelectorAll('.node').forEach(node=>{
    node.addEventListener('pointermove', e=>{
      const r=node.getBoundingClientRect();
      const x=((e.clientX-r.left)/r.width-.5)*4;
      const y=((e.clientY-r.top)/r.height-.5)*-4;
      const base=node.classList.contains('n2')||node.classList.contains('n6') ? 'translateX(-50%) ' : '';
      node.style.transform = base + `translateY(-5px) rotateX(${y}deg) rotateY(${x}deg)`;
    },{passive:true});
    node.addEventListener('pointerleave', ()=>{
      const base=node.classList.contains('n2')||node.classList.contains('n6') ? 'translateX(-50%) ' : '';
      node.style.transform = base + 'translateY(0) rotateX(0deg) rotateY(0deg)';
    });
  });
})();


// PRISMA_V25_COMMAND_BUTTONS_JS_BEGIN
function showOpToast(title, message, kind){
  let toast = document.getElementById('opToast');
  if(!toast){
    toast = document.createElement('div');
    toast.id = 'opToast';
    toast.className = 'opToast';
    toast.innerHTML = '<b></b><span></span>';
    document.body.appendChild(toast);
  }
  toast.dataset.kind = kind || 'info';
  toast.querySelector('b').textContent = title || 'PRISMA';
  toast.querySelector('span').textContent = message || '';
  toast.classList.add('show');
  clearTimeout(showOpToast._t);
  showOpToast._t = setTimeout(()=>toast.classList.remove('show'), 5600);
}
function setCommandStatus(text, state){
  const status = document.getElementById('commandStatusText');
  const mode = document.getElementById('commandMode');
  if(status) status.textContent = text;
  if(mode){
    mode.textContent = state || 'LOCAL ACTIONS';
    mode.classList.toggle('warn', state === 'RUNNING');
    mode.classList.toggle('ok', state !== 'RUNNING');
  }
}
async function runPrismaAction(btn){
  const url = btn.dataset.url;
  const action = btn.dataset.action || btn.textContent.trim();
  const confirmText = btn.dataset.confirm;
  if(confirmText && !window.confirm(confirmText)) return;
  const label = btn.querySelector('strong')?.textContent || btn.textContent.trim();
  btn.disabled = true;
  btn.classList.add('running');
  setCommandStatus(`Ejecutando ${label}...`, 'RUNNING');
  showOpToast('Motor arrancando', `${label}: enviando orden al Control Center.`, 'running');
  try{
    const response = await fetch(url, {headers:{'Accept':'application/json'}, cache:'no-store'});
    const payload = await response.json().catch(()=>({ok:false,status:'BAD_JSON'}));
    const ok = response.ok && (payload.ok !== false);
    if(action === 'brief' && payload.briefText){
      showOpToast('Operator Brief', payload.briefText.replace(/\n/g,' · '), 'ok');
      setCommandStatus('Brief generado correctamente.', 'OK');
    }else if(ok){
      const pid = payload.pid ? ` PID ${payload.pid}.` : '';
      const log = payload.log ? ` Log: ${payload.log}` : '';
      showOpToast('Orden enviada', `${label} iniciado.${pid}${log}`, 'ok');
      setCommandStatus(`${label} iniciado. Revisa evidencia/latest si aplica.`, 'OK');
    }else{
      showOpToast('No se pudo ejecutar', `${label}: ${payload.status || response.status} ${payload.reason || payload.error || ''}`, 'error');
      setCommandStatus(`${label} no arrancó. Revisa respuesta del endpoint.`, 'ERROR');
    }
  }catch(err){
    showOpToast('Error de conexión', `${label}: ${err.message || err}`, 'error');
    setCommandStatus('No respondió el endpoint local. ¿Panel 3150 activo?', 'ERROR');
  }finally{
    setTimeout(()=>{btn.disabled=false; btn.classList.remove('running');}, 900);
  }
}
function wirePrismaButtons(){
  document.querySelectorAll('[data-url][data-action]').forEach(btn=>{
    if(btn.dataset.wired === '1') return;
    btn.dataset.wired = '1';
    btn.addEventListener('click', ()=>runPrismaAction(btn));
    btn.addEventListener('pointermove', e => setXY(btn,e), {passive:true});
    btn.addEventListener('pointerleave', ()=>{btn.style.setProperty('--mx','50%'); btn.style.setProperty('--my','50%');});
  });
}
window.addEventListener('load', wirePrismaButtons);
wirePrismaButtons();
// PRISMA_V25_COMMAND_BUTTONS_JS_END

// PRISMA_V29_TOPOLOGY_REAL_STATUS_JS_BEGIN
(function(){
  const PATCH_ID = 'PRISMA_V29_TOPOLOGY_REAL_STATUS';

  function $(id){
    return document.getElementById(id);
  }

  function setStatus(el, status){
    if(!el) return;
    el.dataset.status = status;
  }

  function setTag(status, label){
    const tag = $('topology-status-tag');
    if(!tag) return;
    tag.textContent = label;
    tag.dataset.status = status;
    tag.className = status === 'pass' ? 'tag ok' : status === 'degraded' ? 'tag warn' : 'tag';
  }

  function endpointOk(value){
    if(value === true) return true;
    if(!value || typeof value !== 'object') return false;
    return Boolean(
      value.ok ||
      value.status === 'PASS' ||
      value.status === 'OK' ||
      Number(value.statusCode) === 200
    );
  }

  function routeFromHealth(payload){
    const health = payload && typeof payload === 'object' ? payload : {};
    const cf = health.cloudflare || {};
    const cc = health.control_center || {};
    const endpoints = Array.isArray(cf.publicEndpoints) ? cf.publicEndpoints : [];
    const endpoint =
      endpoints.find(item => String(item.url || item.name || item.host || '').includes('control.hitechrts.com')) ||
      endpoints[0] ||
      {};
    const probe = endpoint.probe || {};
    const publicHealth = cc.public_health || {};
    const statusCode =
      publicHealth.statusCode ??
      probe.statusCode ??
      cf.config?.controlRoute?.statusCode ??
      '-';
    const latencyMs =
      publicHealth.latencyMs ??
      probe.latencyMs ??
      '-';
    const ok = Boolean(
      publicHealth.ok ||
      probe.ok ||
      cf.config?.controlRoute?.ok ||
      endpointOk(publicHealth) ||
      endpointOk(probe)
    );
    const hasEvidence = Boolean(
      endpoints.length ||
      cc.public_health ||
      cf.status ||
      cf.state ||
      cc.cloudflare ||
      statusCode !== '-'
    );
    const cfStatus = String(cf.status || cf.state || cc.cloudflare || '').toUpperCase();
    return {ok, hasEvidence, statusCode, latencyMs, cfStatus};
  }

  async function refreshTopologyStatus(){
    const tag = $('topology-status-tag');
    const node = $('topology-cf-node');
    const state = $('topology-cf-state');
    const path = $('topology-cf-path');
    const note = $('topology-cf-note');

    if(!tag && !node) return;

    try{
      const response = await fetch('/api/health', {
        cache: 'no-store',
        headers: {Accept: 'application/json'}
      });

      if(!response.ok) {
        throw new Error('api-health-' + response.status);
      }

      const payload = await response.json();
      const route = routeFromHealth(payload);

      let status = 'pending';
      let label = 'Topology pending';
      let routeLabel = 'route pending';
      let cfLabel = 'checking';

      if(route.ok){
        status = 'pass';
        label = 'Topology healthy';
        routeLabel = route.statusCode === '-' ? 'public ok' : String(route.statusCode);
        cfLabel = 'healthy';
      }else if(
        route.hasEvidence &&
        (
          route.cfStatus === 'DEGRADED' ||
          route.cfStatus === 'FAIL' ||
          route.cfStatus === 'ERROR' ||
          route.statusCode !== '-'
        )
      ){
        status = 'degraded';
        label = '1 degraded';
        routeLabel = route.statusCode === '-' ? 'public route' : String(route.statusCode);
        cfLabel = 'degraded';
      }

      setTag(status, label);

      if(node) node.dataset.health = status;
      if(state){
        state.textContent = cfLabel;
        setStatus(state, status);
      }
      if(path) path.textContent = routeLabel;
      if(note){
        note.textContent = route.latencyMs !== '-'
          ? `Edge routing · ${route.latencyMs} ms`
          : 'Edge routing';
      }
    }catch(error){
      setTag('pending', 'Topology pending');
      if(node) node.dataset.health = 'pending';
      if(state){
        state.textContent = 'checking';
        setStatus(state, 'pending');
      }
      if(path) path.textContent = 'no health yet';
    }
  }

  window.PRISMA_TOPOLOGY_REAL_STATUS = {
    PATCH_ID,
    refresh: refreshTopologyStatus
  };

  window.addEventListener('load', refreshTopologyStatus);
  setInterval(refreshTopologyStatus, 5000);
})();
// PRISMA_V29_TOPOLOGY_REAL_STATUS_JS_END


/* === PRISMA V42 TOPBAR CHART LIFE JS START === */
(function(){
  const PATCH_ID = "PRISMA_V43_TOPBAR_CHART_LIFE_QUALITY_BAY_POSITION";
  const GHOST_ACTIONS = new Set(["local","cloudflare","all","web-control","diagnose"]);

  function $(id){ return document.getElementById(id); }

  function ensureTitle(){
    const h1 = document.querySelector(".topbar .titles h1");
    if(h1) h1.textContent = "CONTROL CENTER PRISMA";
    document.title = "CONTROL CENTER PRISMA";
  }

  function ensureConfirmDialog(){
    let dialog = $("prismaConfirmDialog");
    if(dialog) return dialog;

    dialog = document.createElement("dialog");
    dialog.id = "prismaConfirmDialog";
    dialog.className = "prismaConfirmDialog";
    dialog.innerHTML = `
      <div class="prismaConfirmInner">
        <p class="prismaConfirmEyebrow">CONTROL CENTER PRISMA</p>
        <h3 class="prismaConfirmTitle" id="prismaConfirmTitle">CONFIRMAR ACCION</h3>
        <p class="prismaConfirmText" id="prismaConfirmText">Estas seguro?</p>
      </div>
      <form method="dialog" class="prismaConfirmActions">
        <button value="cancel">Cancelar</button>
        <button value="confirm">Ejecutar</button>
      </form>
    `;
    document.body.appendChild(dialog);
    return dialog;
  }

  function labelFor(btn){
    const strong = btn && btn.querySelector ? btn.querySelector("strong") : null;
    return (strong && strong.textContent.trim()) || (btn && btn.textContent ? btn.textContent.trim() : "accion");
  }

  function actionCopy(btn){
    const action = btn.dataset.action || "";
    const label = labelFor(btn);
    const isDanger = action === "kill" || btn.classList.contains("danger");
    const isGhost = btn.classList.contains("opGhost") || document.body.dataset.opsHealthy === "1";

    if(isDanger){
      return {
        danger:true,
        title:"CONFIRMAR APAGADO",
        text:"Esto intentara detener procesos PRISMA conocidos. Confirmar solo si de verdad quieres apagar."
      };
    }

    if(isGhost && GHOST_ACTIONS.has(action)){
      return {
        danger:false,
        title:"YA PARECE ACTIVO",
        text:`${label} esta en modo fantasma porque el tablero se ve estable. Confirmas relanzar esta accion?`
      };
    }

    return {
      danger:false,
      title:"CONFIRMAR ACCION",
      text:`Estas seguro de ejecutar ${label}?`
    };
  }

  function askConfirm(btn){
    const copy = actionCopy(btn);

    if(!("HTMLDialogElement" in window) || typeof HTMLDialogElement.prototype.showModal !== "function"){
      return Promise.resolve(window.confirm(copy.text));
    }

    const dialog = ensureConfirmDialog();
    const title = $("prismaConfirmTitle");
    const text = $("prismaConfirmText");

    if(title) title.textContent = copy.title;
    if(text) text.textContent = copy.text;

    dialog.dataset.danger = copy.danger ? "1" : "0";

    return new Promise(resolve => {
      const onClose = () => resolve(dialog.returnValue === "confirm");
      dialog.addEventListener("close", onClose, {once:true});
      try{
        if(dialog.open) dialog.close("cancel");
        dialog.showModal();
      }catch(_error){
        resolve(window.confirm(copy.text));
      }
    });
  }

  function countWarningLike(value){
    if(!value) return 0;
    const list = Array.isArray(value) ? value : (typeof value === "object" ? Object.values(value) : [value]);
    let count = 0;
    for(const item of list){
      const s = typeof item === "object"
        ? String(item.status || item.state || item.severity || item.level || item.message || item.reason || "")
        : String(item);
      if(/warn|watch|degraded|error|fail|broken/i.test(s)) count++;
    }
    return count;
  }

  async function healthLooksOk(){
    const headerText = Array.from(document.querySelectorAll(".chip,.tag,#commandMode,#reactorState,#reactorSubline"))
      .map(el => el.textContent || "")
      .join(" ")
      .toLowerCase();

    const headerStable = headerText.includes("stable") || headerText.includes("no warnings");

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 1200);

    try{
      const response = await fetch("/api/health", {
        cache:"no-store",
        headers:{Accept:"application/json,text/plain,*/*"},
        signal:controller.signal
      });

      clearTimeout(timer);

      if(!response.ok) return headerStable;

      const payload = await response.json().catch(() => ({}));
      if(payload && payload.ok === false) return false;

      const warnings =
        Number(payload.warningCount || payload.warningsCount || payload.warnCount || 0) ||
        countWarningLike(payload.warnings) ||
        countWarningLike(payload.alerts) ||
        countWarningLike(payload.issues);

      const errors =
        Number(payload.errorCount || payload.errorsCount || 0) ||
        countWarningLike(payload.errors);

      return warnings === 0 && errors === 0;
    }catch(_error){
      clearTimeout(timer);
      return headerStable;
    }
  }

  async function refreshGhostButtons(){
    const ok = await healthLooksOk();
    document.body.dataset.opsHealthy = ok ? "1" : "0";

    document.querySelectorAll("[data-url][data-action]").forEach(btn => {
      const action = btn.dataset.action || "";
      const ghost = ok && GHOST_ACTIONS.has(action);
      btn.classList.toggle("opGhost", ghost);
      if(ghost){
        btn.setAttribute("title", "Sistema estable. Click para confirmar relanzamiento.");
      }else{
        btn.removeAttribute("title");
      }
    });
  }

  function installActionConfirm(){
    const prior = window.runPrismaAction;

    if(prior && prior.__prismaV42Wrapped) return;

    window.runPrismaAction = async function(btn){
      const confirmed = await askConfirm(btn);
      if(!confirmed) return;

      const priorConfirm = btn.dataset.confirm;
      if(priorConfirm !== undefined){
        delete btn.dataset.confirm;
      }

      try{
        if(typeof prior === "function"){
          await prior(btn);
        }else{
          const url = btn.dataset.url;
          const label = labelFor(btn);
          btn.disabled = true;
          btn.classList.add("running");
          const response = await fetch(url, {headers:{Accept:"application/json"}, cache:"no-store"});
          const payload = await response.json().catch(() => ({}));
          if(response.ok && payload.ok !== false){
            if(typeof window.showOpToast === "function") window.showOpToast("Orden enviada", `${label} ejecutado.`, "ok");
          }else{
            if(typeof window.showOpToast === "function") window.showOpToast("No se pudo ejecutar", `${label}: ${response.status}`, "error");
          }
        }
      }finally{
        if(priorConfirm !== undefined){
          btn.dataset.confirm = priorConfirm;
        }
        btn.disabled = false;
        btn.classList.remove("running");
        setTimeout(refreshGhostButtons, 1000);
        setTimeout(refreshGhostButtons, 3500);
      }
    };

    window.runPrismaAction.__prismaV42Wrapped = true;
  }

  function wakeCharts(){
    document.querySelectorAll(".miniChartWrap,.supportChart,.bar").forEach((el, idx) => {
      el.dataset.liveGlow = "v42";
      el.style.setProperty("--v42-delay", `${idx * 140}ms`);
    });
  }

  window.PRISMA_V43_TOPBAR_CHART_LIFE_QUALITY_BAY_POSITION = {
    patch: PATCH_ID,
    refreshGhostButtons,
    askConfirm,
    wakeCharts
  };

  ensureTitle();
  installActionConfirm();
  wakeCharts();
  refreshGhostButtons();

  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", () => {
      ensureTitle();
      installActionConfirm();
      wakeCharts();
      refreshGhostButtons();
    }, {once:true});
  }

  window.addEventListener("load", () => {
    ensureTitle();
    installActionConfirm();
    wakeCharts();
    refreshGhostButtons();
  }, {once:true});

  setInterval(refreshGhostButtons, 5000);
})();
/* === PRISMA V42 TOPBAR CHART LIFE JS END === */

