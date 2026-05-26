// PRISMA Tablet Storm Glass Cards v8
(function(){
  const stage = document.querySelector('[data-liq-stage]');
  const title = document.querySelector('[data-liq-title]');
  const desc = document.querySelector('[data-liq-desc]');
  const tone = document.querySelector('[data-liq-tone]');
  const motion = document.querySelector('[data-liq-motion]');
  const buttons = Array.from(document.querySelectorAll('[data-liq-preset]'));
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const presets = {
    'storm-cloud-operations-real': {
      title:'Hoy', tone:'Real storm image / glass reference',
      motion: reduced ? 'Static storm glass frame' : '138s real storm drift + soft glass shimmer',
      desc:'Centro de decisiones con imagen real de tormenta, scrim de legibilidad, cristal líquido y borde refractivo.'
    },
    'liquid-operations-smoke': {
      title:'Liquid Ops', tone:'Dark / procedural smoke fallback',
      motion: reduced ? 'Static liquid glass frame' : '132s smoky liquid drift',
      desc:'Fallback oscuro con humo mineral procedural. Útil para comparar contra la imagen real.'
    },
    'tablet-soft-gray-clouds': {
      title:'Soft Gray Clouds', tone:'Light / Tablet-safe',
      motion: reduced ? 'Static reduced-motion frame' : '108s soft cloud drift',
      desc:'Versión clara con nubes grises visibles. Sigue siendo el candidato productivo light-first.'
    },
    'obsidian-cloud-motion': {
      title:'Obsidian Cloud', tone:'Dark / Showcase only',
      motion: reduced ? 'Static cinematic frame' : '128s deep mist drift',
      desc:'Obsidiana con humo lento y textura viva. Showcase Visual OS, no default productivo.'
    },
    'aurora-slate-veil': {
      title:'Aurora Slate', tone:'Dark / Showcase only',
      motion: reduced ? 'Static cinematic frame' : '136s aurora veil breath',
      desc:'Pizarra oscura con aurora tenue y color frío controlado.'
    }
  };
  function setPreset(id){
    const data = presets[id] || presets['storm-cloud-operations-real'];
    stage && stage.setAttribute('data-preset', id);
    title && (title.textContent = data.title);
    desc && (desc.textContent = data.desc);
    tone && (tone.textContent = data.tone);
    motion && (motion.textContent = data.motion);
    buttons.forEach(btn => btn.setAttribute('aria-pressed', btn.getAttribute('data-liq-preset') === id ? 'true' : 'false'));
  }
  buttons.forEach(btn => btn.addEventListener('click', () => setPreset(btn.getAttribute('data-liq-preset'))));
  setPreset('storm-cloud-operations-real');
})();
