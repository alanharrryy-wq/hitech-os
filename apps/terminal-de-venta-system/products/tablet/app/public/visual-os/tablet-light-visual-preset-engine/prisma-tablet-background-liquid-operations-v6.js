// PRISMA Tablet Background Liquid Operations v6
(function(){
  const stage = document.querySelector('[data-liq-stage]');
  const title = document.querySelector('[data-liq-title]');
  const desc = document.querySelector('[data-liq-desc]');
  const tone = document.querySelector('[data-liq-tone]');
  const motion = document.querySelector('[data-liq-motion]');
  const buttons = Array.from(document.querySelectorAll('[data-liq-preset]'));
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const presets = {
    'liquid-operations-smoke': {
      title:'Hoy', tone:'Dark / Liquid Operations reference',
      motion: reduced ? 'Static liquid glass frame' : '132s smoky liquid drift',
      desc:'Centro de decisiones con fondo oscuro, humo mineral, glass suave y acentos vivos. Esta es la dirección visual de la referencia.'
    },
    'tablet-soft-gray-clouds': {
      title:'Soft Gray Clouds', tone:'Light / Tablet-safe',
      motion: reduced ? 'Static reduced-motion frame' : '108s soft cloud drift',
      desc:'Versión clara: nubes grises visibles, sin estética oscura productiva. Útil si se quiere mantener Tablet light-first.'
    },
    'obsidian-cloud-motion': {
      title:'Obsidian Cloud', tone:'Dark / Showcase only',
      motion: reduced ? 'Static cinematic frame' : '128s deep mist drift',
      desc:'Obsidiana con humo lento y textura viva. Showcase Visual OS, no default productivo.'
    },
    'storm-glass-horizon': {
      title:'Storm Horizon', tone:'Dark / Showcase only',
      motion: reduced ? 'Static cinematic frame' : '148s horizon haze drift',
      desc:'Horizonte oscuro con bruma y luz difusa para probar glass/rim con más drama.'
    },
    'aurora-slate-veil': {
      title:'Aurora Slate', tone:'Dark / Showcase only',
      motion: reduced ? 'Static cinematic frame' : '136s aurora veil breath',
      desc:'Pizarra oscura con aurora tenue y color frío controlado.'
    }
  };
  function setPreset(id){
    const data = presets[id] || presets['liquid-operations-smoke'];
    stage && stage.setAttribute('data-preset', id);
    title && (title.textContent = data.title);
    desc && (desc.textContent = data.desc);
    tone && (tone.textContent = data.tone);
    motion && (motion.textContent = data.motion);
    buttons.forEach(btn => btn.setAttribute('aria-pressed', btn.getAttribute('data-liq-preset') === id ? 'true' : 'false'));
  }
  buttons.forEach(btn => btn.addEventListener('click', () => setPreset(btn.getAttribute('data-liq-preset'))));
  setPreset('liquid-operations-smoke');
})();
