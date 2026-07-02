/**
 * PRISMA PC product navigation manifest.
 *
 * Authority: surfverdict 3006 + automesh mesh1 3006 0635 result.
 * Purpose: group the backoffice into final business modules while hiding lab/internal/reference routes.
 * Phase: safe contract/documentation only. Runtime menu wiring must be done only after confirming the AppShell owner.
 */

export type PcRouteVisibility = 'final' | 'submenu' | 'internal' | 'lab' | 'alias';
export type PcRole = 'dueno' | 'gerente' | 'auditor' | 'soporte' | 'dev' | 'qa';

export interface PcProductRoute {
  route: string;
  label: string;
  module: string;
  roles: PcRole[];
  visibility: PcRouteVisibility;
  canonicalRoute: string;
  finalMenu: boolean;
  order: number;
}

const BUSINESS_ROLES: PcRole[] = ['dueno', 'gerente', 'auditor', 'soporte'];
const LAB_ROLES: PcRole[] = ['dev', 'qa'];

export const PC_PRODUCT_ROUTES: PcProductRoute[] = [
  { route: '/', label: 'Entrada', module: 'Hoy', roles: BUSINESS_ROLES, visibility: 'alias', canonicalRoute: '/dashboard', finalMenu: false, order: 0 },
  { route: '/dashboard', label: 'Hoy', module: 'Hoy', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/dashboard', finalMenu: true, order: 10 },
  { route: '/alertas-ejecutivas', label: 'Alertas ejecutivas', module: 'Hoy', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/alertas-ejecutivas', finalMenu: false, order: 11 },
  { route: '/alertas-operativas', label: 'Alertas operativas', module: 'Hoy', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/alertas-operativas', finalMenu: false, order: 12 },

  { route: '/catalog', label: 'Catálogo', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/catalog', finalMenu: true, order: 20 },
  { route: '/stock', label: 'Stock', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/stock', finalMenu: false, order: 21 },
  { route: '/catalogo-activo', label: 'Catálogo activo', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/catalogo-activo', finalMenu: false, order: 22 },
  { route: '/movements', label: 'Movimientos', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/movements', finalMenu: false, order: 23 },
  { route: '/counts', label: 'Conteos', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/counts', finalMenu: false, order: 24 },
  { route: '/conteos-operativos', label: 'Conteos operativos', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/conteos-operativos', finalMenu: false, order: 25 },
  { route: '/existencias-criticas', label: 'Existencias críticas', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/existencias-criticas', finalMenu: false, order: 26 },
  { route: '/validacion-catalogo', label: 'Validación de catálogo', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/validacion-catalogo', finalMenu: false, order: 27 },
  { route: '/salud-barcodes', label: 'Salud de códigos', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/salud-barcodes', finalMenu: false, order: 28 },
  { route: '/politica-precios', label: 'Política de precios', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/politica-precios', finalMenu: false, order: 29 },
  { route: '/ajustes-inventario', label: 'Ajustes de inventario', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/ajustes-inventario', finalMenu: false, order: 30 },
  { route: '/auditoria-inventario', label: 'Auditoría de inventario', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/auditoria-inventario', finalMenu: false, order: 31 },
  { route: '/integridad-barcodes', label: 'Integridad de códigos', module: 'Inventario', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/integridad-barcodes', finalMenu: false, order: 32 },

  { route: '/purchasing', label: 'Compras', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/purchasing', finalMenu: true, order: 40 },
  { route: '/proveedores', label: 'Proveedores', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/proveedores', finalMenu: true, order: 41 },
  { route: '/ordenes-compra', label: 'Órdenes de compra', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/ordenes-compra', finalMenu: false, order: 42 },
  { route: '/receiving', label: 'Recepción', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/receiving', finalMenu: false, order: 43 },
  { route: '/recepcion-proveedor', label: 'Recepción proveedor', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/recepcion-proveedor', finalMenu: false, order: 44 },
  { route: '/incidencias-recepcion', label: 'Incidencias de recepción', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/incidencias-recepcion', finalMenu: false, order: 45 },
  { route: '/replenishment', label: 'Reabasto', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/replenishment', finalMenu: false, order: 46 },
  { route: '/senal-reabasto', label: 'Señal de reabasto', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/senal-reabasto', finalMenu: false, order: 47 },
  { route: '/forecast-basico', label: 'Pronóstico básico', module: 'Compras y proveedores', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/forecast-basico', finalMenu: false, order: 48 },

  { route: '/sales-control', label: 'Ventas y caja', module: 'Ventas y caja', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/sales-control', finalMenu: true, order: 50 },
  { route: '/cash-sessions', label: 'Sesiones de caja', module: 'Ventas y caja', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/cash-sessions', finalMenu: false, order: 51 },
  { route: '/metricas-dia', label: 'Métricas del día', module: 'Ventas y caja', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/metricas-dia', finalMenu: false, order: 52 },

  { route: '/sync', label: 'Sincronización', module: 'Sync y Tablet Ops', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/sync', finalMenu: true, order: 60 },
  { route: '/devices', label: 'Equipos', module: 'Sync y Tablet Ops', roles: ['soporte', 'gerente'], visibility: 'final', canonicalRoute: '/devices', finalMenu: true, order: 61 },
  { route: '/sync-operativo', label: 'Sync operativo', module: 'Sync y Tablet Ops', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/sync-operativo', finalMenu: false, order: 62 },
  { route: '/outbox-operativo', label: 'Outbox operativo', module: 'Sync y Tablet Ops', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/outbox-operativo', finalMenu: false, order: 63 },
  { route: '/tablet-communication', label: 'Comunicación Tablet', module: 'Sync y Tablet Ops', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/tablet-communication', finalMenu: false, order: 64 },

  { route: '/exportables', label: 'Descargas', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/exportables', finalMenu: true, order: 70 },
  { route: '/prisma-insights', label: 'Análisis', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/prisma-insights', finalMenu: true, order: 71 },
  { route: '/scorecards-negocio', label: 'Scorecards de negocio', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/scorecards-negocio', finalMenu: false, order: 72 },
  { route: '/tablero-kpi', label: 'Tablero KPI', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/tablero-kpi', finalMenu: false, order: 73 },
  { route: '/vistas-ejecutivas', label: 'Vistas ejecutivas', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/vistas-ejecutivas', finalMenu: false, order: 74 },
  { route: '/tablas-operativas', label: 'Tablas operativas', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/tablas-operativas', finalMenu: false, order: 75 },
  { route: '/contratos-reporte', label: 'Contratos de reporte', module: 'Reportes y BI', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/contratos-reporte', finalMenu: false, order: 76 },

  { route: '/settings', label: 'Configuración', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/settings', finalMenu: true, order: 80 },
  { route: '/settings/license', label: 'Licencia', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/settings/license', finalMenu: false, order: 81 },
  { route: '/data-quality', label: 'Calidad de datos', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/data-quality', finalMenu: false, order: 82 },
  { route: '/audit', label: 'Auditoría', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/audit', finalMenu: false, order: 83 },
  { route: '/detalle-registros', label: 'Detalle de registros', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/detalle-registros', finalMenu: false, order: 84 },
  { route: '/estados-operativos', label: 'Estados operativos', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/estados-operativos', finalMenu: false, order: 85 },
  { route: '/license-runtime', label: 'Runtime de licencia', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/license-runtime', finalMenu: false, order: 86 },
  { route: '/acciones-masivas', label: 'Acciones masivas', module: 'Sistema y calidad', roles: BUSINESS_ROLES, visibility: 'submenu', canonicalRoute: '/acciones-masivas', finalMenu: false, order: 87 },

  { route: '/glosario', label: 'Glosario', module: 'Ayuda', roles: BUSINESS_ROLES, visibility: 'final', canonicalRoute: '/glosario', finalMenu: true, order: 90 },

  { route: '/gobierno', label: 'Gobierno', module: 'Soporte interno', roles: ['soporte'], visibility: 'internal', canonicalRoute: '/gobierno', finalMenu: false, order: 900 },
  { route: '/filtros-avanzados', label: 'Filtros avanzados', module: 'Soporte interno', roles: ['soporte'], visibility: 'internal', canonicalRoute: '/filtros-avanzados', finalMenu: false, order: 901 },
  { route: '/filtros-fecha', label: 'Filtros de fecha', module: 'Soporte interno', roles: ['soporte'], visibility: 'internal', canonicalRoute: '/filtros-fecha', finalMenu: false, order: 902 },
  { route: '/laboratorio-pc', label: 'Laboratorio PC', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/dev/pc/laboratorio-pc', finalMenu: false, order: 950 },
  { route: '/laboratorio-pc/chart-lab', label: 'Chart Lab', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/dev/pc/chart-lab', finalMenu: false, order: 951 },
  { route: '/laboratorio-pc/dashboard-governor', label: 'Dashboard Governor', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/dev/pc/dashboard-governor', finalMenu: false, order: 952 },
  { route: '/laboratorio-pc/referencia-visual', label: 'Referencia visual', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/dev/pc/referencia-visual', finalMenu: false, order: 953 },
  { route: '/laboratorio-pc/referencia-visual/liquid-glass', label: 'Liquid Glass', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/dev/pc/referencia-visual/liquid-glass', finalMenu: false, order: 954 },
  { route: '/laboratorio-pc/referencia-visual/liquid-glass-capsules', label: 'Liquid Glass Capsules', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/dev/pc/referencia-visual/liquid-glass-capsules', finalMenu: false, order: 955 },
  { route: '/referencia-visual', label: 'Referencia visual alias', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'alias', canonicalRoute: '/laboratorio-pc/referencia-visual', finalMenu: false, order: 956 },
  { route: '/referencia-visual/liquid-glass', label: 'Liquid Glass alias', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'alias', canonicalRoute: '/laboratorio-pc/referencia-visual/liquid-glass', finalMenu: false, order: 957 },
  { route: '/referencia-visual/liquid-glass-capsules', label: 'Liquid Glass Capsules alias', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'alias', canonicalRoute: '/laboratorio-pc/referencia-visual/liquid-glass-capsules', finalMenu: false, order: 958 },
  { route: '/prisma-insights/chart-lab', label: 'Chart Lab alias', module: 'Laboratorio PC', roles: LAB_ROLES, visibility: 'lab', canonicalRoute: '/laboratorio-pc/chart-lab', finalMenu: false, order: 959 },
];

export const PC_FINAL_NAVIGATION = PC_PRODUCT_ROUTES.filter((route) => route.finalMenu);
export const PC_HIDDEN_FROM_FINAL_MENU = PC_PRODUCT_ROUTES.filter((route) => ['internal', 'lab', 'alias'].includes(route.visibility));
