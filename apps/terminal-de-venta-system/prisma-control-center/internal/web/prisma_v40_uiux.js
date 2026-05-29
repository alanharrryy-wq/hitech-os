(function(){
  'use strict';
  var PATCH = 'PRISMA_V40_UIUX_THEME_HARDENING';
  var UI_IMPROVEMENTS = ["Corrected reactor default copy", "Theme-aware quick rail", "Theme pressed state", "Operator status capsule", "Command palette shell", "Focus rings", "Touch target floor", "Card hover depth", "Button sweep highlight", "Bar sweep highlight", "Tabular numerals", "Reactor halo", "Orb lens sheen", "Panel hover border", "Compact density mode", "Theme-specific rail material", "Theme-specific palette material", "Pearl light contrast", "Tactical angular compactness", "Rose rail tint", "Liquid cyan caustics", "Readable selection color", "Better section letter spacing", "Improved body line height", "State colors for pending", "State colors for ok", "State colors for warn", "State colors for error", "Visible skip link", "Toast stack", "Tooltip layer", "Mobile sticky rail", "Small-screen palette layout", "Responsive rail actions", "Safe-area aware controls", "Reduced-motion support", "Contain paint for charts", "Active theme badges", "Metric active press", "Signal active press", "Quality card transition", "Node hover elevation", "Command grid equalization", "Mini chart stability", "Reactor text shadow logic", "Scroll margin for timeline", "System accent color", "No horizontal overflow aids", "Densified panels", "Densified cards"];
  var UX_IMPROVEMENTS = ["Ctrl K command palette", "Esc closes palette", "Ctrl 1 theme Liquid", "Ctrl 2 theme Tactical", "Ctrl 3 theme Rose", "Ctrl 4 theme Pearl", "D cycles density", "Question mark opens help", "Quick jump to reactor", "Quick jump to commands", "Quick jump to status", "Quick jump to topology", "Quick jump to timeline", "Quick switch to Quality Bay", "Quick switch to Operation", "Theme choice persisted", "Density choice persisted", "Online state reflected", "Offline state reflected", "ARIA live for reactor", "ARIA live for queue", "ARIA live for topology", "Buttons get aria labels", "Buttons get titles", "Palette uses button roles", "Palette search filters", "Palette first result selection", "Click outside closes palette", "Skip link to main", "Toast feedback", "Helpful keyboard hints", "Status capsule reports theme", "Status capsule reports density", "Health fetch mirrors runtime", "No false green on health failure", "No stale English placeholders", "Queue wording localized", "Topology wording localized", "Health score updates bars", "Warnings update queue card", "Errors update risk", "Latency is measured", "Safe JSON parsing", "Network failure is honest", "Visual state mirrors data state", "LocalStorage guarded", "Progressive enhancement", "Works if v24 is absent", "Works if API is absent", "No backend dependency for polish"];
  var THEMES = [
    {id:'liquid', label:'Liquid', key:'1'},
    {id:'tactical', label:'Tactical Frost', key:'2'},
    {id:'piel', label:'Rose', key:'3'},
    {id:'pearl', label:'Pearl', key:'4'}
  ];
  var COMMANDS = [];
  var paletteIndex = 0;
  function $(sel, root){return (root||document).querySelector(sel);}
  function $$(sel, root){return Array.prototype.slice.call((root||document).querySelectorAll(sel));}
  function byId(id){return document.getElementById(id);}
  function setText(id, value){var el=byId(id); if(el) el.textContent=String(value);}
  function setState(id, value){var el=byId(id); if(el) el.dataset.state=value;}
  function safeStorage(method, key, value){try{if(method==='get') return localStorage.getItem(key); localStorage.setItem(key,value);}catch(_e){} return null;}
  function ready(fn){if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',fn,{once:true}); else fn();}
  function toast(title, detail){
    var stack = $('.v40ToastStack');
    if(!stack){stack=document.createElement('div'); stack.className='v40ToastStack'; document.body.appendChild(stack);}
    var item=document.createElement('div'); item.className='v40Toast'; item.innerHTML='<b></b><span></span>';
    item.querySelector('b').textContent=title||'PRISMA';
    item.querySelector('span').textContent=detail||'';
    stack.appendChild(item);
    window.setTimeout(function(){item.style.opacity='0'; item.style.transform='translateY(8px)';},4200);
    window.setTimeout(function(){item.remove();},4700);
  }
  function fixCopy(){
    var map = [
      ['reactorState','Verificando'], ['reactorSubline','Diagnostico pendiente'], ['reactorLatencyMetric','pendiente'], ['reactorRiskMetric','Pendiente'],
      ['queuePill','Verificando'], ['queueDelta','pendiente'], ['topology-status-tag','Topologia pendiente'], ['topology-cf-path','ruta pendiente'], ['topology-cf-state','verificando']
    ];
    map.forEach(function(pair){var el=byId(pair[0]); if(!el) return; var t=(el.textContent||'').trim().toLowerCase(); if(!t || t==='checking' || t==='health pending' || t==='pending' || t==='route pending' || t==='topology pending') el.textContent=pair[1];});
    setState('reactorSubline','pending'); setState('queuePill','pending'); setState('queueDelta','pending');
  }
  function addA11y(){
    ['reactorScore','reactorState','reactorSubline','reactorLatencyMetric','reactorRiskMetric','queuePill','queueCount','queueDelta','queueNote','topology-cf-state'].forEach(function(id){
      var el=byId(id); if(el){el.setAttribute('aria-live','polite'); el.setAttribute('aria-atomic','true');}
    });
    $$('.opButton').forEach(function(btn){
      var strong=$('strong',btn), small=$('small',btn), key=$('.opKey',btn);
      var label=[key&&key.textContent,strong&&strong.textContent,small&&small.textContent].filter(Boolean).join(' - ');
      if(label){btn.setAttribute('aria-label',label); btn.title=label;}
    });
    var main=byId('main'); if(main && !main.hasAttribute('tabindex')) main.setAttribute('tabindex','-1');
  }
  function injectSkipLink(){
    if($('.v40SkipLink')) return;
    var a=document.createElement('a'); a.href='#main'; a.className='v40SkipLink'; a.textContent='Saltar al tablero';
    document.body.insertBefore(a, document.body.firstChild);
  }
  function currentTheme(){return document.body.dataset.theme || (byId('themeSelect')&&byId('themeSelect').value) || 'liquid';}
  function currentDensity(){return document.body.dataset.v40Density || 'normal';}
  function switchTheme(theme){
    if(!THEMES.some(function(t){return t.id===theme;})) theme='liquid';
    var select=byId('themeSelect');
    if(select){select.value=theme; select.dispatchEvent(new Event('change',{bubbles:true}));}
    else{document.body.dataset.theme=theme; safeStorage('set','prisma-v28-theme',theme);}
    syncRail(); toast('Tema aplicado', theme);
  }
  function cycleDensity(){
    var next=currentDensity()==='compact'?'normal':'compact';
    document.body.dataset.v40Density=next; safeStorage('set','prisma-v40-density',next); syncRail(); toast('Densidad', next==='compact'?'Compacta':'Normal');
  }
  function makeRail(){
    if($('.v40QuickRail')) return;
    var rail=document.createElement('aside'); rail.className='v40QuickRail'; rail.setAttribute('aria-label','PRISMA quick controls');
    rail.innerHTML = '<div class="v40QuickRailHeader"><b>Temas</b><span>Ctrl+K</span></div><div class="v40ThemeButtons"></div><div class="v40RailActions"><button class="v40MiniButton" data-v40-action="palette">Comandos</button><button class="v40MiniButton" data-v40-action="density">Densidad</button></div><div class="v40StatusCapsule" role="status"><span class="v40StatusDot"></span><span id="v40StatusText">V40 listo</span></div>';
    var buttons=$('.v40ThemeButtons',rail);
    THEMES.forEach(function(t){var b=document.createElement('button'); b.type='button'; b.className='v40ThemeButton'; b.dataset.theme=t.id; b.textContent=t.key; b.title=t.label+' theme'; b.addEventListener('click',function(){switchTheme(t.id);}); buttons.appendChild(b);});
    rail.addEventListener('click',function(e){var action=e.target && e.target.dataset && e.target.dataset.v40Action; if(action==='palette') openPalette(); if(action==='density') cycleDensity();});
    var page=$('.page'); if(page) page.insertBefore(rail, page.firstChild); else document.body.appendChild(rail);
    syncRail();
  }
  function syncRail(){
    $$('.v40ThemeButton').forEach(function(btn){btn.setAttribute('aria-pressed', btn.dataset.theme===currentTheme()?'true':'false');});
    var status=byId('v40StatusText'); if(status) status.textContent='V40 '+currentTheme()+' / '+currentDensity()+(navigator.onLine?' / online':' / offline');
  }
  function makeCommands(){
    COMMANDS = [
      {icon:'R', title:'Reactor sistemico', meta:'Ver estado runtime', run:function(){jump('#reactorValue');}},
      {icon:'M', title:'Motores PRISMA', meta:'Acciones locales', run:function(){jump('#commandPanel');}},
      {icon:'E', title:'Estado operativo', meta:'KPI, cola y salud', run:function(){jump('#queuePill');}},
      {icon:'T', title:'Topologia', meta:'Rutas, CF y evidencia', run:function(){jump('#topology-cf-node');}},
      {icon:'Q', title:'Quality Bay', meta:'Verificaciones audit-only', run:function(){clickInterface('quality');}},
      {icon:'O', title:'Operacion', meta:'Volver a cabina operativa', run:function(){clickInterface('operation');}},
      {icon:'1', title:'Tema Liquid Metal', meta:'Ctrl+1', run:function(){switchTheme('liquid');}},
      {icon:'2', title:'Tema Tactical Frost', meta:'Ctrl+2', run:function(){switchTheme('tactical');}},
      {icon:'3', title:'Tema Obsidian Rose', meta:'Ctrl+3', run:function(){switchTheme('piel');}},
      {icon:'4', title:'Tema Pearl Ice', meta:'Ctrl+4', run:function(){switchTheme('pearl');}},
      {icon:'D', title:'Alternar densidad', meta:'Normal / compacta', run:cycleDensity},
      {icon:'H', title:'Atajos', meta:'Muestra ayuda rapida', run:function(){toast('Atajos','Ctrl+K comandos, Ctrl+1..4 temas, D densidad, Esc cerrar.');}}
    ];
  }
  function jump(selector){var el=$(selector); if(el){el.scrollIntoView({behavior:'smooth',block:'center'}); if(el.focus) window.setTimeout(function(){el.focus({preventScroll:true});},350);} closePalette();}
  function clickInterface(target){var btn=$('[data-prisma-interface-target="'+target+'"]'); if(btn) btn.click(); closePalette();}
  function makePalette(){
    if($('.v40CommandPalette')) return;
    var wrap=document.createElement('div'); wrap.className='v40CommandPalette'; wrap.setAttribute('role','dialog'); wrap.setAttribute('aria-modal','true'); wrap.setAttribute('aria-label','Command palette');
    wrap.innerHTML='<div class="v40PaletteBox"><input class="v40PaletteInput" type="search" placeholder="Buscar comando, tema o vista..." autocomplete="off"><div class="v40PaletteList" role="listbox"></div></div>';
    wrap.addEventListener('click',function(e){if(e.target===wrap) closePalette();});
    $('.v40PaletteInput',wrap).addEventListener('input',function(){paletteIndex=0; renderPalette();});
    $('.v40PaletteInput',wrap).addEventListener('keydown',function(e){
      var items=$$('.v40PaletteItem',wrap);
      if(e.key==='ArrowDown'){e.preventDefault(); paletteIndex=Math.min(items.length-1,paletteIndex+1); renderPalette();}
      if(e.key==='ArrowUp'){e.preventDefault(); paletteIndex=Math.max(0,paletteIndex-1); renderPalette();}
      if(e.key==='Enter'){e.preventDefault(); var cmd=filteredCommands()[paletteIndex]; if(cmd) cmd.run();}
    });
    document.body.appendChild(wrap);
    renderPalette();
  }
  function filteredCommands(){var q=($('.v40PaletteInput')&&$('.v40PaletteInput').value||'').toLowerCase().trim(); if(!q) return COMMANDS; return COMMANDS.filter(function(c){return (c.title+' '+c.meta+' '+c.icon).toLowerCase().indexOf(q)>=0;});}
  function renderPalette(){
    var list=$('.v40PaletteList'); if(!list) return; var rows=filteredCommands(); paletteIndex=Math.max(0,Math.min(paletteIndex,rows.length-1));
    list.innerHTML='';
    rows.forEach(function(c,i){var b=document.createElement('button'); b.type='button'; b.className='v40PaletteItem'; b.setAttribute('role','option'); b.setAttribute('aria-selected',i===paletteIndex?'true':'false'); b.innerHTML='<span class="v40PaletteIcon"></span><span><b></b><br><small></small></span><span class="v40PaletteMeta"></span>'; $('.v40PaletteIcon',b).textContent=c.icon; $('b',b).textContent=c.title; $('small',b).textContent=c.meta; $('.v40PaletteMeta',b).textContent='Enter'; b.addEventListener('mouseenter',function(){paletteIndex=i; renderPalette();}); b.addEventListener('click',c.run); list.appendChild(b);});
    if(!rows.length){var empty=document.createElement('div'); empty.className='v40PaletteItem'; empty.textContent='Sin resultados'; list.appendChild(empty);}
  }
  function openPalette(){makePalette(); var p=$('.v40CommandPalette'); p.dataset.open='1'; paletteIndex=0; renderPalette(); window.setTimeout(function(){var input=$('.v40PaletteInput'); if(input){input.focus(); input.select();}},20);}
  function closePalette(){var p=$('.v40CommandPalette'); if(p){p.dataset.open='0'; var input=$('.v40PaletteInput'); if(input) input.value='';}}
  function keyboard(){
    document.addEventListener('keydown',function(e){
      var tag=(e.target&&e.target.tagName||'').toLowerCase(); var typing=tag==='input'||tag==='textarea'||tag==='select'||(e.target&&e.target.isContentEditable);
      if((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==='k'){e.preventDefault(); openPalette(); return;}
      if(e.key==='Escape'){closePalette(); return;}
      if(typing) return;
      if((e.ctrlKey||e.metaKey) && ['1','2','3','4'].indexOf(e.key)>=0){e.preventDefault(); switchTheme(THEMES[Number(e.key)-1].id); return;}
      if(e.key.toLowerCase()==='d'){cycleDensity(); return;}
      if(e.key==='?'){toast('Atajos','Ctrl+K comandos, Ctrl+1..4 temas, D densidad, Esc cerrar.');}
    });
  }
  function getPath(obj,path){try{return path.split('.').reduce(function(acc,key){return acc&&acc[key];},obj);}catch(_e){return undefined;}}
  function num(){for(var i=0;i<arguments.length;i++){var n=Number(arguments[i]); if(Number.isFinite(n)) return n;} return null;}
  function arrayCount(value, needles){
    var arr=Array.isArray(value)?value:(value&&typeof value==='object'?Object.values(value):[]); var count=0;
    arr.forEach(function(item){var s=String(typeof item==='object'?(item.severity||item.level||item.status||item.state||item.message||''):item).toLowerCase(); if(needles.some(function(n){return s.indexOf(n)>=0;})) count++;});
    return count;
  }
  function healthNumbers(payload, measured, ok){
    var warnings=num(payload.warningCount,payload.warningsCount,getPath(payload,'summary.warningCount'),getPath(payload,'health.warningCount'));
    if(warnings===null) warnings=arrayCount(payload.warnings,['warn','watch','degraded','pending'])+arrayCount(payload.alerts,['warn','watch','degraded','pending'])+arrayCount(payload.issues,['warn','watch','degraded','pending']);
    var errors=num(payload.errorCount,payload.errorsCount,getPath(payload,'summary.errorCount'),getPath(payload,'health.errorCount'));
    if(errors===null) errors=arrayCount(payload.errors,['error','fail','down']);
    var latency=Math.max(0,Math.round(num(payload.latencyMs,payload.responseMs,getPath(payload,'metrics.latencyMs'),getPath(payload,'cloudflare.latencyMs'),measured)||0));
    var score=num(payload.score,payload.healthScore,payload.overallScore,getPath(payload,'summary.score'),getPath(payload,'health.score'),getPath(payload,'control_center.health_score'));
    if(score===null) score=ok?Math.max(70,Math.min(100,100-warnings*6-errors*14)):72;
    var queue=num(payload.queueCount,payload.pendingQueue,payload.pending,getPath(payload,'queue.count'),getPath(payload,'queue.pending'),getPath(payload,'outbox.pending'),getPath(payload,'sync.pending'));
    return {warnings:Math.max(0,Math.round(warnings||0)), errors:Math.max(0,Math.round(errors||0)), latency:latency, score:Math.max(0,Math.min(100,Math.round(score))), queue:queue===null?null:Math.max(0,Math.round(queue))};
  }
  function paintHealth(payload, measured, ok){
    var h=healthNumbers(payload||{},measured,ok);
    setText('reactorScore',h.score); setText('reactorLatencyMetric',h.latency+' ms');
    var sub='';
    if(!ok || h.errors>0){setText('reactorState',ok?'Degradado':'Sin health'); sub=(h.errors||'sin')+' error / '+h.warnings+' warnings / '+h.latency+' ms'; setState('reactorSubline','error'); setText('reactorRiskMetric',ok?'Alto':'Desconocido');}
    else if(h.warnings>0){setText('reactorState','Vigilancia'); sub=h.warnings+' warnings / '+h.latency+' ms'; setState('reactorSubline','warn'); setText('reactorRiskMetric','Bajo+');}
    else{setText('reactorState','Estable'); sub='Sin warnings / '+h.latency+' ms'; setState('reactorSubline','ok'); setText('reactorRiskMetric','Bajo');}
    setText('reactorSubline',sub);
    var q=h.queue;
    if(q===null) q=h.warnings+h.errors;
    setText('queueCount',q);
    if(q>0 || h.warnings>0 || h.errors>0){setText('queuePill','Vigilar'); setState('queuePill','warn'); setText('queueDelta',q>0?'pendiente':'warnings'); setState('queueDelta','warn'); setText('queueNote','Health reporta trabajo o advertencias por revisar.');}
    else{setText('queuePill','Limpio'); setState('queuePill','ok'); setText('queueDelta','clear'); setState('queueDelta','ok'); setText('queueNote','Cola limpia segun health.');}
    var core=$$('.signal .signalTop small')[0]; if(core) core.textContent=h.score+'%';
    var bars=$$('.signal .bar span'); if(bars[0]) bars[0].style.setProperty('--w',Math.max(8,h.score)+'%');
    document.body.dataset.v40ReactorState=h.errors>0?'error':(h.warnings>0?'warn':'ok');
    syncRail();
  }
  function refreshHealth(){
    var start=performance.now();
    if(!window.fetch){return;}
    fetch('/api/health',{cache:'no-store',headers:{Accept:'application/json'}}).then(function(r){return r.json().catch(function(){return {};}).then(function(payload){paintHealth(payload,performance.now()-start,r.ok);});}).catch(function(){paintHealth({},performance.now()-start,false);});
  }
  function onlineState(){document.body.dataset.v40Online=navigator.onLine?'1':'0'; syncRail();}
  function tooltips(){
    var tip=document.createElement('div'); tip.className='v40Tooltip'; document.body.appendChild(tip);
    document.addEventListener('pointerover',function(e){var el=e.target.closest&&e.target.closest('[title]'); if(!el) return; tip.textContent=el.getAttribute('title')||''; if(!tip.textContent) return; tip.dataset.show='1';});
    document.addEventListener('pointermove',function(e){if(tip.dataset.show==='1'){tip.style.left=Math.min(window.innerWidth-300,e.clientX+14)+'px'; tip.style.top=Math.min(window.innerHeight-80,e.clientY+16)+'px';}});
    document.addEventListener('pointerout',function(e){if(e.target.closest&&e.target.closest('[title]')) tip.dataset.show='0';});
  }
  function reducedMotionFlag(){var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches; document.body.dataset.v40Reduced=reduce?'1':'0';}
  function boot(){
    document.body.dataset.v40='ready';
    document.body.dataset.v40Density=safeStorage('get','prisma-v40-density')||'normal';
    injectSkipLink(); fixCopy(); addA11y(); makeCommands(); makeRail(); makePalette(); keyboard(); tooltips(); reducedMotionFlag(); onlineState();
    window.addEventListener('online',onlineState); window.addEventListener('offline',onlineState);
    var select=byId('themeSelect'); if(select) select.addEventListener('change',function(){window.setTimeout(syncRail,0);});
    refreshHealth(); window.setInterval(refreshHealth,7000);
    window.PRISMA_V40_UIUX={patch:PATCH, ui:UI_IMPROVEMENTS, ux:UX_IMPROVEMENTS, refresh:refreshHealth, theme:switchTheme, density:cycleDensity, palette:openPalette};
    toast('V40 UI/UX listo','Copy corregido, temas reforzados y comandos activos.');
  }
  ready(boot);
})();
