
const examples = {
  restaurant: { person: 'Mesero', context: 'Mesa 12', action: 'Toma una orden', event: 'Orden creada', evidence: 'Comanda', truth: 'Venta canónica', decision: 'Preparar y cobrar' },
  retail: { person: 'Cajero', context: 'Caja 2', action: 'Cobra productos', event: 'Venta aceptada', evidence: 'Ticket', truth: 'Venta canónica', decision: 'Reponer y reportar' },
  services: { person: 'Especialista', context: 'Cita del cliente', action: 'Realiza servicio', event: 'Servicio completado', evidence: 'Firma e historial', truth: 'Servicio canónico', decision: 'Cobrar y dar seguimiento' },
  saas: { person: 'Administrador', context: 'Tenant y licencia', action: 'Activa un dispositivo', event: 'Device autorizado', evidence: 'Auditoría', truth: 'Estado canónico', decision: 'Habilitar capacidades' }
};

const tabs = [...document.querySelectorAll('.industry-tab')];
const slots = [...document.querySelectorAll('[data-slot]')];
let transitionTimer = 0;

function selectIndustry(key, focus = false) {
  const data = examples[key];
  if (!data) return;
  tabs.forEach(tab => {
    const selected = tab.dataset.industry === key;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  });
  clearTimeout(transitionTimer);
  slots.forEach(slot => {
    slot.style.opacity = '0';
    slot.style.translate = '0 3px';
  });
  transitionTimer = window.setTimeout(() => {
    slots.forEach(slot => {
      slot.textContent = data[slot.dataset.slot];
      slot.style.opacity = '1';
      slot.style.translate = '0 0';
    });
  }, 110);
}

tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectIndustry(tab.dataset.industry));
  tab.addEventListener('mouseenter', () => {
    if (matchMedia('(hover:hover) and (pointer:fine)').matches) selectIndustry(tab.dataset.industry);
  });
  tab.addEventListener('keydown', event => {
    if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index + (event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0);
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    next = (next + tabs.length) % tabs.length;
    selectIndustry(tabs[next].dataset.industry, true);
  });
});

selectIndustry(tabs.find(tab => tab.getAttribute('aria-selected') === 'true')?.dataset.industry ?? 'restaurant');
