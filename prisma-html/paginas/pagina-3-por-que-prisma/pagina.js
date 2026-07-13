const CASES = Object.freeze({
  restaurant: Object.freeze({
    kicker: 'RESTAURANTE',
    title: 'La orden nace en la mesa y conserva su historia.',
    description: 'El mesero registra; cocina sabe qué preparar; caja conoce qué cobrar; administración recibe el mismo estado.',
    person: 'Mesero',
    action: 'Toma una orden',
    evidence: 'Comanda',
    decision: 'Preparar y cobrar'
  }),
  retail: Object.freeze({
    kicker: 'TIENDA',
    title: 'La venta mueve inventario sin partir la realidad en dos.',
    description: 'El cajero cobra; existencias entienden el movimiento; el dueño consulta el mismo resultado desde otra superficie.',
    person: 'Cajero',
    action: 'Cobra productos',
    evidence: 'Ticket',
    decision: 'Reponer y reportar'
  }),
  services: Object.freeze({
    kicker: 'SERVICIOS',
    title: 'La cita deja de depender de la memoria de una persona.',
    description: 'La agenda ubica el compromiso; el servicio deja evidencia; el seguimiento continúa con contexto completo.',
    person: 'Especialista',
    action: 'Realiza servicio',
    evidence: 'Firma e historial',
    decision: 'Cobrar y dar seguimiento'
  })
});

function setText(root, selector, value) {
  const element = root.querySelector(selector);
  if (element) element.textContent = value;
}

function selectCase(root, key, { moveFocus = false } = {}) {
  const selected = CASES[key];
  if (!selected) return;

  const tabs = [...root.querySelectorAll('.case-tab')];

  tabs.forEach((tab) => {
    const active = tab.dataset.case === key;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });

  root.querySelectorAll('[data-scene]').forEach((scene) => {
    scene.hidden = scene.dataset.scene !== key;
  });

  setText(root, '[data-case-kicker]', selected.kicker);
  setText(root, '[data-case-title]', selected.title);
  setText(root, '[data-case-description]', selected.description);
  setText(root, '[data-flow-person]', selected.person);
  setText(root, '[data-flow-action]', selected.action);
  setText(root, '[data-flow-evidence]', selected.evidence);
  setText(root, '[data-flow-decision]', selected.decision);
}

function resolveKeyboardTarget(event, index, total) {
  switch (event.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      return (index + 1) % total;
    case 'ArrowLeft':
    case 'ArrowUp':
      return (index - 1 + total) % total;
    case 'Home':
      return 0;
    case 'End':
      return total - 1;
    default:
      return null;
  }
}

function initWhyPrisma(root = document) {
  const tabs = [...root.querySelectorAll('.case-tab')];
  if (!tabs.length) return;

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      selectCase(root, tab.dataset.case);
    });

    tab.addEventListener('mouseenter', () => {
      if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        selectCase(root, tab.dataset.case);
      }
    });

    tab.addEventListener('keydown', (event) => {
      const targetIndex = resolveKeyboardTarget(event, index, tabs.length);
      if (targetIndex === null) return;

      event.preventDefault();
      const target = tabs[targetIndex];
      selectCase(root, target.dataset.case, { moveFocus: true });
    });
  });

  const initial = tabs.find((tab) => tab.getAttribute('aria-selected') === 'true') ?? tabs[0];
  selectCase(root, initial.dataset.case);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initWhyPrisma(), { once: true });
} else {
  initWhyPrisma();
}
