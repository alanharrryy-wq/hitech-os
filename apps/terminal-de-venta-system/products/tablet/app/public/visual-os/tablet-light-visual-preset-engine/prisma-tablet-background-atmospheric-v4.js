// PRISMA Tablet Background Atmospheric v4
(function(){
  const stage = document.querySelector('[data-atm-stage]');
  const title = document.querySelector('[data-atm-title]');
  const desc = document.querySelector('[data-atm-desc]');
  const tone = document.querySelector('[data-atm-tone]');
  const motion = document.querySelector('[data-atm-motion]');
  const apply = document.querySelector('[data-atm-apply]');
  const cards = document.querySelector('[data-atm-cards]');
  const buttons = Array.from(document.querySelectorAll('[data-atm-preset]'));
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const presets = {
    'tablet-soft-gray-clouds': {
      title:'Tablet Soft Gray Clouds', tone:'Light / Tablet-safe', motion: reduced ? 'Static reduced-motion frame' : '96s slow cloud drift', apply:'Default candidate: YES',
      desc:'Fondo claro perla con nubes grises tenues. Borroso pero con forma, más escena atmosférica y menos degradado de lonchería triste.',
      cards:[['Light-first','Base clara, premium y táctil para Tablet.'],['Cloud form','Nubes grises suaves con blur medio, no humo lavado.'],['Motion','Drift lento, casi invisible y congelado en reduced motion.'],['Use','Buen candidato para revisar como base visual futura.']]
    },
    'obsidian-cloud-motion': {
      title:'Obsidian Cloud Motion', tone:'Dark / Showcase only', motion: reduced ? 'Static cinematic frame' : '118s deep mist drift', apply:'Default candidate: NO',
      desc:'Nube mineral oscura con humo lento y textura viva. Está aquí para explorar carácter visual, no para volver dark la Tablet productiva.',
      cards:[['Image layer','SVG atmosférico con ruido y nubes, no puro gradient.'],['Mood','Obsidiana sobria, sin azul chillón ni cybercafé.'],['Motion','Humo lento con parallax mínimo.'],['Guardrail','Dark showcase explícito, no default Tablet.']]
    },
    'storm-glass-horizon': {
      title:'Storm Glass Horizon', tone:'Dark / Showcase only', motion: reduced ? 'Static cinematic frame' : '132s horizon haze drift', apply:'Default candidate: NO',
      desc:'Escena oscura con horizonte nuboso, bruma y luz difusa. Más composición tipo imagen y menos fondo de PowerPoint con esteroides.',
      cards:[['Scene','Horizon abstracto con masa nubosa.'],['Depth','Frente oscuro, luz posterior y niebla.'],['Motion','Haze horizontal lentísimo.'],['Use','Demo premium para ver glass/rim en contraste.']]
    },
    'aurora-slate-veil': {
      title:'Aurora Slate Veil', tone:'Dark / Showcase only', motion: reduced ? 'Static cinematic frame' : '124s aurora veil breath', apply:'Default candidate: NO',
      desc:'Pizarra oscura con velo aurora muy tenue. Color frío controlado, textura viva y nada de “RGB gamer con garnacha”.',
      cards:[['Aurora','Velo tenue azul/violeta/mint sin dominar.'],['Slate','Base pizarra profunda con nubes bajas.'],['Motion','Respiración visual lenta.'],['Guardrail','Showcase visual, no aplicación productiva automática.']]
    }
  };
  function renderCards(list){
    if(!cards) return;
    cards.innerHTML = list.map(([k,v]) => '<article class="atm-card"><span class="atm-chip">'+k+'</span><h3>'+k+'</h3><p>'+v+'</p></article>').join('');
  }
  function setPreset(id){
    const data = presets[id] || presets['tablet-soft-gray-clouds'];
    stage && stage.setAttribute('data-preset', id);
    title && (title.textContent = data.title);
    desc && (desc.textContent = data.desc);
    tone && (tone.textContent = data.tone);
    motion && (motion.textContent = data.motion);
    apply && (apply.textContent = data.apply);
    buttons.forEach(btn => btn.setAttribute('aria-pressed', btn.getAttribute('data-atm-preset') === id ? 'true' : 'false'));
    renderCards(data.cards);
  }
  buttons.forEach(btn => btn.addEventListener('click', () => setPreset(btn.getAttribute('data-atm-preset'))));
  setPreset('tablet-soft-gray-clouds');
})();
