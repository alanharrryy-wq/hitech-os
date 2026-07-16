/**
 * PRISMA Tablet customer-facing page contracts.
 *
 * Authority: Factory Ledger + dbevid 1507 1826 + ScreensQA surface review.
 * Classification: FIX.
 * Purpose: keep only customer/product routes in the active contract while
 * preserving an explicit retired-route ledger for compatibility, QA and rollback.
 * Marker: CUSTOMER_SURFACE_REDUCTION_1507
 */

export type TabletRouteVisibility =
  | 'final'
  | 'submenu'
  | 'step'
  | 'dynamic'
  | 'alias';

export type TabletRole = 'cajero' | 'supervisor' | 'admin' | 'soporte' | 'dev' | 'qa';

export interface TabletPageContract {
  route: string;
  label: string;
  module: string;
  roles: TabletRole[];
  visibility: TabletRouteVisibility;
  canonicalRoute: string;
  finalMenu: boolean;
  order: number;
  rationale: string;
}

export interface TabletRetiredInternalRoute {
  route: string;
  replacement: string | null;
  rationale: string;
}

export const TABLET_PAGE_CONTRACTS: TabletPageContract[] = [
  { route: '/', label: 'Inicio Tablet', module: 'Home Tablet', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/pos', finalMenu: false, order: 0, rationale: 'Home selecciona el siguiente trabajo operativo sin exponer rutas técnicas.' },
  { route: '/pos', label: 'Vender', module: 'Venta', roles: ['cajero'], visibility: 'final', canonicalRoute: '/pos', finalMenu: true, order: 10, rationale: 'Entrada principal del cajero.' },
  { route: '/checkout', label: 'Cobro', module: 'Venta', roles: ['cajero'], visibility: 'step', canonicalRoute: '/pos', finalMenu: false, order: 20, rationale: 'Paso contextual del flujo de venta; conserva sus propiedades y no aparece como módulo raíz.' },
  { route: '/shift', label: 'Turno y caja', module: 'Turno y caja', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/shift', finalMenu: true, order: 30, rationale: 'Módulo operativo de turno.' },
  { route: '/stock', label: 'Inventario para vender', module: 'Inventario', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/stock', finalMenu: true, order: 40, rationale: 'Canonical de inventario vendible.' },
  { route: '/catalog', label: 'Catálogo', module: 'Inventario', roles: ['supervisor', 'admin'], visibility: 'submenu', canonicalRoute: '/catalog', finalMenu: false, order: 41, rationale: 'Administración secundaria del catálogo.' },
  { route: '/existencias', label: 'Existencias', module: 'Inventario', roles: ['supervisor'], visibility: 'submenu', canonicalRoute: '/stock', finalMenu: false, order: 42, rationale: 'Vista avanzada bajo Inventario; se conserva para no perder propiedades.' },
  { route: '/inventory', label: 'Inventario', module: 'Inventario', roles: ['supervisor'], visibility: 'alias', canonicalRoute: '/stock', finalMenu: false, order: 43, rationale: 'Alias técnico compatible; no aparece en navegación final.' },
  { route: '/inventory/low-stock', label: 'Stock bajo', module: 'Inventario', roles: ['supervisor'], visibility: 'submenu', canonicalRoute: '/inventory/low-stock', finalMenu: false, order: 44, rationale: 'Secundaria de inventario.' },
  { route: '/sales/today', label: 'Ventas de hoy', module: 'Ventas', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/sales/today', finalMenu: true, order: 50, rationale: 'Lista operativa de tickets del día.' },
  { route: '/sales/history', label: 'Historial de ventas', module: 'Ventas', roles: ['supervisor'], visibility: 'submenu', canonicalRoute: '/sales/history', finalMenu: false, order: 51, rationale: 'Consulta secundaria de ventas.' },
  { route: '/sales', label: 'Ventas', module: 'Ventas', roles: ['cajero', 'supervisor'], visibility: 'alias', canonicalRoute: '/sales/today', finalMenu: false, order: 52, rationale: 'Alias compatible a Ventas de hoy.' },
  { route: '/sales/today/:saleId', label: 'Detalle de venta de hoy', module: 'Ventas', roles: ['cajero', 'supervisor'], visibility: 'dynamic', canonicalRoute: '/sales/today', finalMenu: false, order: 53, rationale: 'Detalle abierto desde listas; nunca botón raíz.' },
  { route: '/sales/history/:saleId', label: 'Detalle histórico de venta', module: 'Ventas', roles: ['supervisor'], visibility: 'dynamic', canonicalRoute: '/sales/history', finalMenu: false, order: 54, rationale: 'Detalle abierto desde historial.' },
  { route: '/returns', label: 'Devoluciones', module: 'Devoluciones', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/returns', finalMenu: true, order: 60, rationale: 'Módulo final de devolución.' },
  { route: '/sales/today/:saleId/return', label: 'Devolución desde ticket', module: 'Devoluciones', roles: ['cajero', 'supervisor'], visibility: 'dynamic', canonicalRoute: '/returns', finalMenu: false, order: 61, rationale: 'Flujo contextual desde ticket.' },
  { route: '/sync', label: 'Sincronización', module: 'Sync y offline', roles: ['cajero', 'supervisor', 'soporte'], visibility: 'final', canonicalRoute: '/sync', finalMenu: true, order: 70, rationale: 'Pendientes, conexión y continuidad operativa.' },
  { route: '/offline', label: 'Offline y export', module: 'Sync y offline', roles: ['cajero', 'supervisor'], visibility: 'submenu', canonicalRoute: '/sync', finalMenu: false, order: 71, rationale: 'Secundaria dentro de Sync.' },
  { route: '/settings/license', label: 'Licencia', module: 'Configuración', roles: ['supervisor', 'admin'], visibility: 'final', canonicalRoute: '/settings/license', finalMenu: true, order: 80, rationale: 'Configuración operativa visible para supervisor/admin.' },
  { route: '/settings/export', label: 'Exportaciones', module: 'Configuración', roles: ['supervisor', 'admin'], visibility: 'submenu', canonicalRoute: '/settings/export', finalMenu: false, order: 81, rationale: 'Secundaria de configuración.' },
  { route: '/settings/data', label: 'Datos', module: 'Configuración', roles: ['admin'], visibility: 'alias', canonicalRoute: '/settings/license', finalMenu: false, order: 82, rationale: 'Alias actual; futura Datos/backup sólo con implementación real.' }
];

export const TABLET_RETIRED_INTERNAL_ROUTES: TabletRetiredInternalRoute[] = [
  { route: '/events/outbox', replacement: '/sync', rationale: 'La API de outbox se conserva; la pantalla técnica deja de formar parte del cliente final.' },
  { route: '/prisma-pulse', replacement: '/', rationale: 'Superficie experimental no certificada como producto final.' },
  { route: '/prisma-dark-pos-reference', replacement: null, rationale: 'Referencia histórica visual.' },
  { route: '/prisma-visual-catalog', replacement: null, rationale: 'Catálogo técnico compartido, no superficie comercial.' },
  { route: '/referencia-visual', replacement: null, rationale: 'Referencia visual de desarrollo.' },
  { route: '/release-gate', replacement: null, rationale: 'Gate interno de QA.' },
  { route: '/screen-standard-preview', replacement: null, rationale: 'Preview técnico de estándares.' },
  { route: '/tablet-lab', replacement: null, rationale: 'Laboratorio visual interno.' },
  { route: '/visual-os', replacement: null, rationale: 'Visual OS permanece como tooling/shared engine, no como ruta Tablet comercial.' },
  { route: '/visual-os/detached', replacement: null, rationale: 'Variante interna de Visual OS.' },
  { route: '/visual-os/materiality-catalog', replacement: null, rationale: 'Catálogo interno de materialidad.' },
  { route: '/visual-os/pro', replacement: null, rationale: 'Studio Pro interno.' },
  { route: '/visual-os/realtime', replacement: null, rationale: 'Bridge visual interno.' },
  { route: '/visual-os/tablet-background-gallery', replacement: null, rationale: 'Galería interna de fondos.' },
  { route: '/visual-os/tablet-codex-gallery', replacement: null, rationale: 'Galería interna Codex.' }
];

export const TABLET_FINAL_NAVIGATION = TABLET_PAGE_CONTRACTS.filter((contract) => contract.finalMenu);
export const TABLET_INTERNAL_OR_LAB_ROUTES = TABLET_RETIRED_INTERNAL_ROUTES;
