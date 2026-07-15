const SURFACES = Object.freeze({
  tablet: Object.freeze({
    kicker: 'TABLET POS · OPERACIÓN INMEDIATA',
    title: 'La acción debe terminarse con claridad, velocidad y continuidad.',
    description: 'Es la superficie táctil donde la operación sucede. Reduce la complejidad visible sin perder trazabilidad.',
    outcome: 'Vender rápido sin romper la historia de la venta.',
    responsibility: 'Operar ventas, pagos, tickets y continuidad de caja.',
    role: 'Cajero u operador de piso.',
    consumes: 'Catálogo, precios, permisos, sesión e inventario disponible.',
    emits: 'Venta, líneas, pago, ticket, movimiento y estado de sincronización.',
    evidence: 'Ticket, pago registrado, sesión y procedencia del dispositivo.',
    governance: 'Licencia de dispositivo, rol operativo y módulos habilitados.'
  }),
  pc: Object.freeze({
    kicker: 'PC ADMIN · GOBIERNO OPERACIONAL',
    title: 'La administración necesita contexto suficiente para corregir sin borrar la historia.',
    description: 'Concentra configuración, excepciones, usuarios, inventario y auditoría. No replica el POS; gobierna lo que el POS produce.',
    outcome: 'Resolver excepciones sin reconstruir manualmente lo ocurrido.',
    responsibility: 'Gobernar operación, configuración, permisos, inventario y excepciones.',
    role: 'Administrador, supervisor o responsable de negocio.',
    consumes: 'Estados canónicos, eventos, auditoría, alertas y configuración del tenant.',
    emits: 'Autorizaciones, ajustes gobernados, configuración y decisiones administrativas.',
    evidence: 'Procedencia, historial, diferencias, responsables y cambios autorizados.',
    governance: 'Rol administrativo, permisos por módulo y alcance de negocio o tienda.'
  }),
  mobile: Object.freeze({
    kicker: 'MOBILE COMPANION · SUPERVISIÓN EJECUTIVA',
    title: 'El dueño necesita decidir sin cargar toda la operación en el bolsillo.',
    description: 'Resume desempeño, riesgo y alertas accionables. La síntesis cambia; la verdad de origen permanece.',
    outcome: 'Responder rápido con señales confiables y contexto suficiente.',
    responsibility: 'Supervisar indicadores, alertas, estado de tiendas y decisiones urgentes.',
    role: 'Dueño, gerente o responsable itinerante.',
    consumes: 'Métricas canónicas, alertas, tendencias y estados de alto nivel.',
    emits: 'Acuses, decisiones, solicitudes de seguimiento y acciones autorizadas.',
    evidence: 'Tendencia, causa resumida, tienda, fecha, severidad y enlace al detalle.',
    governance: 'Identidad del usuario, alcance ejecutivo y capacidades móviles habilitadas.'
  }),
  chart: Object.freeze({
    kicker: 'CHART LAB · EXPLICACIÓN ANALÍTICA',
    title: 'Una métrica útil debe poder regresar al evento que la produjo.',
    description: 'Explora tendencias, comparaciones y reconciliaciones sin separar la visualización de la procedencia.',
    outcome: 'Explicar por qué cambió una cifra, no sólo mostrar que cambió.',
    responsibility: 'Analizar métricas, tendencias, anomalías y relaciones operacionales.',
    role: 'Analista, administrador o líder de operación.',
    consumes: 'Eventos canónicos, dimensiones de scope, series temporales y evidencia.',
    emits: 'Vistas, consultas, hallazgos, comparaciones y señales interpretables.',
    evidence: 'Fuente, filtros, periodo, scope, eventos incluidos y nivel de confianza.',
    governance: 'Acceso analítico, privacidad, alcance de datos y módulos de observabilidad.'
  }),
  control: Object.freeze({
    kicker: 'CONTROL CENTER · ADMINISTRACIÓN DE PLATAFORMA',
    title: 'La plataforma necesita saber quién puede usar qué, dónde y bajo qué condiciones.',
    description: 'Administra tenants, licencias, dispositivos, módulos y salud operativa sin convertirse en la interfaz diaria del cliente.',
    outcome: 'Escalar clientes y capacidades con control verificable.',
    responsibility: 'Administrar tenants, licencias, dispositivos, módulos y operación SaaS.',
    role: 'Operador de plataforma o soporte autorizado.',
    consumes: 'Estado de licencias, dispositivos, tenants, auditoría y salud de servicios.',
    emits: 'Provisionamiento, revocación, renovación, reemplazo y cambios de capacidad.',
    evidence: 'Auditoría de licencia, claim de dispositivo, estado comercial y confirmaciones.',
    governance: 'Autorización privilegiada, trazabilidad administrativa y separación de tenants.'
  }),
  web: Object.freeze({
    kicker: 'WEB / PORTAL · ENTRADA Y AUTOSERVICIO',
    title: 'La relación comienza antes de instalar una superficie operativa.',
    description: 'Presenta el producto, guía configuración, habilita portales y conecta al cliente con el siguiente paso correcto.',
    outcome: 'Convertir interés y configuración en una relación operacional trazable.',
    responsibility: 'Descubrir, configurar, activar, consultar o solicitar capacidades.',
    role: 'Prospecto, cliente, administrador o usuario invitado.',
    consumes: 'Oferta, configuración, estado de cuenta, setup y capacidades disponibles.',
    emits: 'Solicitudes, configuración inicial, claims, formularios y decisiones comerciales.',
    evidence: 'Confirmaciones, estado de setup, términos, identidad y seguimiento de la solicitud.',
    governance: 'Identidad, permisos de portal, tenant, plan y flujo de activación.'
  })
});

const JOURNEY = Object.freeze({
  scope: Object.freeze({
    kicker: 'CAPA 01 · SCOPE',
    title: 'Antes de contar la venta, PRISMA sabe a quién y a dónde pertenece.',
    description: 'Tenant, negocio, tienda, terminal, dispositivo, usuario, rol, licencia y sesión forman el contexto mínimo.',
    code: 'TEN.prisma_rey · STO.centro · DEV.tb.pos.01 · USR.cashier.01',
    icon: '01',
    status: 'La venta ya tiene domicilio operacional.',
    proof: 'No existe todavía una cifra; existe contexto verificable.'
  }),
  event: Object.freeze({
    kicker: 'CAPA 02 · EVENTO',
    title: 'La acción se registra como algo que ocurrió, no como una celda que simplemente cambió.',
    description: 'La venta conserva acción, entidad, timestamp, origen, usuario y superficie emisora.',
    code: 'EVT.sale.created · ACT.sale.checkout · SOURCE_SURFACE=tb.pos',
    icon: '02',
    status: 'La operación ya tiene identidad temporal.',
    proof: 'Sabemos qué ocurrió, cuándo ocurrió y qué dispositivo lo emitió.'
  }),
  evidence: Object.freeze({
    kicker: 'CAPA 03 · EVIDENCIA',
    title: 'La afirmación queda acompañada por la prueba que permite sostenerla.',
    description: 'Pago, ticket, líneas, sesión, auditoría y estado de sincronización componen la evidencia de la venta.',
    code: 'EVD.receipt · EVD.payment · EVD.cash_session · sync_status=pending',
    icon: '03',
    status: 'La venta puede explicarse y auditarse.',
    proof: 'Una cifra sin procedencia no se presenta como certeza.'
  }),
  canonical: Object.freeze({
    kicker: 'CAPA 04 · PROYECCIÓN CANÓNICA',
    title: 'PRISMA consolida el estado aceptado sin borrar lo que pasó antes.',
    description: 'Pendientes, rechazadas, duplicadas o aceptadas se distinguen antes de construir el total compartido.',
    code: 'CAN.sale · status=accepted · lineage=tablet_outbox→gateway→canonical_sales',
    icon: '04',
    status: 'Existe una verdad compartida y reconciliable.',
    proof: 'El total conserva la ruta hacia los eventos que lo componen.'
  }),
  projection: Object.freeze({
    kicker: 'CAPA 05 · PROYECCIÓN POR SUPERFICIE',
    title: 'La misma venta se traduce según la responsabilidad de cada persona.',
    description: 'Tablet confirma; PC gobierna; Mobile resume; Chart Lab agrega; Control Center observa capacidad y salud.',
    code: 'SURF.tb.pos · SURF.pc.sales_control · SURF.mb.owner_home · SURF.cl.sales_trend',
    icon: '05',
    status: 'Cada superficie recibe significado, no una copia ciega.',
    proof: 'Cambian el nivel de detalle y la acción disponible; no cambia lo ocurrido.'
  }),
  ui: Object.freeze({
    kicker: 'CAPA 06 · COMPONENTE UI',
    title: 'La interfaz es la última representación visible, no la fuente de verdad.',
    description: 'Botones, tablas, tickets, KPIs y gráficas localizan una proyección neutral dentro de una experiencia concreta.',
    code: 'TB-POS-PAY-BTN-01 · PC-SALES-MAIN-TBL-01 · MB-HOME-KPI-01',
    icon: '06',
    status: 'La UI puede cambiar sin reescribir el significado.',
    proof: 'Los componentes localizan y presentan; el núcleo gobierna la identidad.'
  })
});

function setText(selector, value, root = document) {
  const element = root.querySelector(selector);
  if (element) element.textContent = value;
}

function updateTabGroup(tabs, activeKey, dataAttribute, moveFocus = false) {
  tabs.forEach((tab) => {
    const active = tab.dataset[dataAttribute] === activeKey;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });
}

function resolveKeyboardTarget(event, currentIndex, total) {
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') return (currentIndex + 1) % total;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') return (currentIndex - 1 + total) % total;
  if (event.key === 'Home') return 0;
  if (event.key === 'End') return total - 1;
  return null;
}

function selectSurface(key, { moveFocus = false } = {}) {
  const surface = SURFACES[key];
  if (!surface) return;

  const tabs = [...document.querySelectorAll('.surface-tab')];
  updateTabGroup(tabs, key, 'surface', moveFocus);

  document.querySelectorAll('[data-surface-target]').forEach((node) => {
    node.classList.toggle('is-active', node.dataset.surfaceTarget === key);
  });

  setText('[data-surface-kicker]', surface.kicker);
  setText('[data-surface-title]', surface.title);
  setText('[data-surface-description]', surface.description);
  setText('[data-surface-outcome]', surface.outcome);
  setText('[data-surface-responsibility]', surface.responsibility);
  setText('[data-surface-role]', surface.role);
  setText('[data-surface-consumes]', surface.consumes);
  setText('[data-surface-emits]', surface.emits);
  setText('[data-surface-evidence]', surface.evidence);
  setText('[data-surface-governance]', surface.governance);
}

function selectJourney(key, { moveFocus = false } = {}) {
  const step = JOURNEY[key];
  if (!step) return;

  const tabs = [...document.querySelectorAll('.journey-tab')];
  updateTabGroup(tabs, key, 'journey', moveFocus);

  setText('[data-journey-kicker]', step.kicker);
  setText('[data-journey-title]', step.title);
  setText('[data-journey-description]', step.description);
  setText('[data-journey-code]', step.code);
  setText('[data-journey-icon]', step.icon);
  setText('[data-journey-status]', step.status);
  setText('[data-journey-proof]', step.proof);
}

function bindTabs(selector, dataAttribute, select) {
  const tabs = [...document.querySelectorAll(selector)];

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(tab.dataset[dataAttribute]));
    tab.addEventListener('keydown', (event) => {
      const targetIndex = resolveKeyboardTarget(event, index, tabs.length);
      if (targetIndex === null) return;
      event.preventDefault();
      select(tabs[targetIndex].dataset[dataAttribute], { moveFocus: true });
    });
  });
}

function initEcosystem() {
  bindTabs('.surface-tab', 'surface', selectSurface);
  bindTabs('.journey-tab', 'journey', selectJourney);

  document.querySelectorAll('[data-surface-target]').forEach((node) => {
    node.addEventListener('click', () => {
      selectSurface(node.dataset.surfaceTarget);
      document.querySelector('#superficies')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  selectSurface('tablet');
  selectJourney('scope');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initEcosystem, { once: true });
} else {
  initEcosystem();
}
