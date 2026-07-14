const CATEGORY_DATA = Object.freeze({
  pos: Object.freeze({
    title: 'POS',
    solves: 'Registra productos, cobra y emite el ticket.',
    loses: 'El contexto posterior: sincronización, procedencia, decisiones administrativas y otras superficies.',
    prisma: 'La venta como evento trazable, asociada a persona, caja, dispositivo, evidencia y estado canónico.',
    conclusion: 'PRISMA no sustituye el acto de cobrar. Impide que el cobro pierda su historia al salir del POS.'
  }),
  erp: Object.freeze({
    title: 'ERP',
    solves: 'Centraliza administración, contabilidad, compras y procesos corporativos.',
    loses: 'La inmediatez de la operación real, la experiencia por rol y la evidencia capturada desde el origen.',
    prisma: 'Conecta la acción cotidiana con la gobernanza central sin obligar al operador a trabajar como administrador.',
    conclusion: 'PRISMA no compite por convertir cada acción en un trámite corporativo. Lleva la verdad operacional al gobierno correcto.'
  }),
  dashboard: Object.freeze({
    title: 'Dashboard',
    solves: 'Resume indicadores y permite detectar patrones o desviaciones.',
    loses: 'La causa, el origen, la responsabilidad y el estado que explican por qué una cifra cambió.',
    prisma: 'Cada métrica puede volver al evento, la evidencia y la superficie que la produjo.',
    conclusion: 'PRISMA no se conforma con mostrar que algo cambió. Conserva la ruta para explicar por qué cambió.'
  }),
  integrations: Object.freeze({
    title: 'Integraciones',
    solves: 'Mueven datos entre sistemas y reducen recapturas manuales.',
    loses: 'Un significado común cuando cada sistema define entidades, estados y reglas de manera distinta.',
    prisma: 'Usa conceptos neutrales para que la transferencia no convierta una diferencia semántica en una falsa equivalencia.',
    conclusion: 'PRISMA no sólo conecta tuberías. Define qué significa lo que viaja por ellas.'
  })
});

const ROLE_DATA = Object.freeze({
  operator: Object.freeze({
    kicker: 'TABLET · ACCIÓN INMEDIATA',
    title: 'Necesita terminar la venta sin interpretar un sistema entero.',
    description: 'Ve productos, pago, ticket y estado de continuidad. La complejidad queda detrás.',
    points: ['Acción clara y táctil', 'Estado de pago visible', 'Continuidad autorizada'],
    outcome: 'Opera rápido sin romper la trazabilidad.'
  }),
  admin: Object.freeze({
    kicker: 'PC · GOBIERNO OPERACIONAL',
    title: 'Necesita saber qué ocurrió, qué falta y quién puede corregirlo.',
    description: 'Ve excepciones, procedencia, auditoría, inventario, usuarios y configuración con contexto suficiente.',
    points: ['Excepciones explicadas', 'Procedencia y responsabilidad', 'Corrección gobernada'],
    outcome: 'Gobierna sin reconstruir la historia manualmente.'
  }),
  owner: Object.freeze({
    kicker: 'MOBILE · DECISIÓN EJECUTIVA',
    title: 'Necesita responder sin cargar toda la operación en el bolsillo.',
    description: 'Ve resumen, riesgo, tendencia y alertas accionables construidas sobre la misma verdad.',
    points: ['Resumen confiable', 'Alertas con contexto', 'Decisiones desde cualquier lugar'],
    outcome: 'Decide con síntesis, no con una versión recortada de la realidad.'
  })
});

const RECONCILIATION_STEPS = Object.freeze([
  Object.freeze({ value: 0, text: '0% · cifras sin contexto común', active: 0 }),
  Object.freeze({ value: 25, text: '25% · scope identificado', active: 1 }),
  Object.freeze({ value: 50, text: '50% · eventos alineados', active: 2 }),
  Object.freeze({ value: 75, text: '75% · evidencia reconciliada', active: 3 }),
  Object.freeze({ value: 100, text: '100% · estado canónico explicado', active: 4 })
]);

function setText(root, selector, value) {
  const element = root.querySelector(selector);
  if (element) element.textContent = value;
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

function initializeTabGroup(root, selector, dataAttribute, onSelect) {
  const tabs = [...root.querySelectorAll(selector)];
  if (!tabs.length) return;

  const select = (tab, { moveFocus = false } = {}) => {
    tabs.forEach((candidate) => {
      const active = candidate === tab;
      candidate.setAttribute('aria-selected', String(active));
      candidate.tabIndex = active ? 0 : -1;
    });

    onSelect(tab.dataset[dataAttribute]);
    if (moveFocus) tab.focus();
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(tab));

    tab.addEventListener('keydown', (event) => {
      const nextIndex = resolveKeyboardTarget(event, index, tabs.length);
      if (nextIndex === null) return;
      event.preventDefault();
      select(tabs[nextIndex], { moveFocus: true });
    });
  });

  const initial = tabs.find((tab) => tab.getAttribute('aria-selected') === 'true') ?? tabs[0];
  select(initial);
}

function initCategoryComparison(root) {
  initializeTabGroup(root, '.category-tab', 'category', (key) => {
    const data = CATEGORY_DATA[key];
    if (!data) return;

    setText(root, '[data-category-title]', data.title);
    setText(root, '[data-category-solves]', data.solves);
    setText(root, '[data-category-loses]', data.loses);
    setText(root, '[data-category-prisma]', data.prisma);
    setText(root, '[data-category-conclusion]', data.conclusion);
  });
}

function initRoleLens(root) {
  initializeTabGroup(root, '.role-tab', 'role', (key) => {
    const data = ROLE_DATA[key];
    if (!data) return;

    setText(root, '[data-role-kicker]', data.kicker);
    setText(root, '[data-role-title]', data.title);
    setText(root, '[data-role-description]', data.description);
    setText(root, '[data-role-outcome]', data.outcome);

    data.points.forEach((point, index) => {
      setText(root, `[data-role-point="${index}"]`, point);
    });
  });
}

function initReconciliation(root) {
  const stage = root.querySelector('.reconcile-stage');
  const range = root.querySelector('#truthRange');
  const status = root.querySelector('#truthStatus');
  const steps = [...root.querySelectorAll('.reconcile-steps [data-step]')];

  if (!stage || !range || !status) return;

  const update = () => {
    const value = Number(range.value);
    const state = RECONCILIATION_STEPS.find((item) => item.value === value) ?? RECONCILIATION_STEPS[0];

    stage.style.setProperty('--compare-progress', `${value}%`);
    status.value = state.text;
    status.textContent = state.text;
    range.setAttribute('aria-valuetext', state.text);

    steps.forEach((step, index) => {
      step.dataset.active = String(index < state.active);
    });
  };

  range.addEventListener('input', update);
  range.addEventListener('change', update);
  update();
}

function initWhyPrisma(root = document) {
  initCategoryComparison(root);
  initRoleLens(root);
  initReconciliation(root);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initWhyPrisma(), { once: true });
} else {
  initWhyPrisma();
}
