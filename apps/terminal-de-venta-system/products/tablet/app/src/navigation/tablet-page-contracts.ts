/**
 * PRISMA Tablet page contracts.
 *
 * Authority: surfverdict 3006 + automesh mesh1 3006 0635 result.
 * Purpose: separate final product navigation from QA/lab/dev/reference/internal routes.
 * Phase: safe contract/documentation only. This file does not wire runtime menus by itself.
 */

export type TabletRouteVisibility =
  | 'final'
  | 'submenu'
  | 'step'
  | 'dynamic'
  | 'alias'
  | 'internal-support'
  | 'candidate-support'
  | 'lab';

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

export const TABLET_PAGE_CONTRACTS: TabletPageContract[] = [
  { route: '/', label: 'Inicio Tablet', module: 'Home Tablet', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/pos', finalMenu: false, order: 0, rationale: 'Home debe redirigir o seleccionar rol; no debe mostrarse como ruta técnica.' },
  { route: '/pos', label: 'Vender', module: 'Venta', roles: ['cajero'], visibility: 'final', canonicalRoute: '/pos', finalMenu: true, order: 10, rationale: 'Entrada principal del cajero.' },
  { route: '/checkout', label: 'Cobro', module: 'Venta', roles: ['cajero'], visibility: 'step', canonicalRoute: '/pos', finalMenu: false, order: 20, rationale: 'Paso del flujo de venta; se abre desde carrito/cobro.' },
  { route: '/shift', label: 'Turno y caja', module: 'Turno y caja', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/shift', finalMenu: true, order: 30, rationale: 'Módulo operativo de turno.' },
  { route: '/stock', label: 'Inventario para vender', module: 'Inventario', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/stock', finalMenu: true, order: 40, rationale: 'Canonical de inventario vendible.' },
  { route: '/catalog', label: 'Catálogo', module: 'Inventario', roles: ['supervisor', 'admin'], visibility: 'submenu', canonicalRoute: '/catalog', finalMenu: false, order: 41, rationale: 'Secundaria; no desplaza a POS como operación principal.' },
  { route: '/existencias', label: 'Existencias', module: 'Inventario', roles: ['supervisor'], visibility: 'submenu', canonicalRoute: '/stock', finalMenu: false, order: 42, rationale: 'Vista avanzada bajo Inventario.' },
  { route: '/inventory', label: 'Inventario', module: 'Inventario', roles: ['supervisor'], visibility: 'alias', canonicalRoute: '/stock', finalMenu: false, order: 43, rationale: 'Alias técnico; no aparece en navegación final.' },
  { route: '/inventory/low-stock', label: 'Stock bajo', module: 'Inventario', roles: ['supervisor'], visibility: 'submenu', canonicalRoute: '/inventory/low-stock', finalMenu: false, order: 44, rationale: 'Secundaria de inventario.' },
  { route: '/sales/today', label: 'Ventas de hoy', module: 'Ventas', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/sales/today', finalMenu: true, order: 50, rationale: 'Lista operativa de tickets del día.' },
  { route: '/sales/history', label: 'Historial de ventas', module: 'Ventas', roles: ['supervisor'], visibility: 'submenu', canonicalRoute: '/sales/history', finalMenu: false, order: 51, rationale: 'Consulta secundaria de ventas.' },
  { route: '/sales', label: 'Ventas', module: 'Ventas', roles: ['cajero', 'supervisor'], visibility: 'alias', canonicalRoute: '/sales/today', finalMenu: false, order: 52, rationale: 'Alias a Ventas de hoy.' },
  { route: '/sales/today/:saleId', label: 'Detalle de venta de hoy', module: 'Ventas', roles: ['cajero', 'supervisor'], visibility: 'dynamic', canonicalRoute: '/sales/today', finalMenu: false, order: 53, rationale: 'Detalle abierto desde listas; nunca botón raíz.' },
  { route: '/sales/history/:saleId', label: 'Detalle histórico de venta', module: 'Ventas', roles: ['supervisor'], visibility: 'dynamic', canonicalRoute: '/sales/history', finalMenu: false, order: 54, rationale: 'Detalle abierto desde historial.' },
  { route: '/returns', label: 'Devoluciones', module: 'Devoluciones', roles: ['cajero', 'supervisor'], visibility: 'final', canonicalRoute: '/returns', finalMenu: true, order: 60, rationale: 'Módulo final de devolución.' },
  { route: '/sales/today/:saleId/return', label: 'Devolución desde ticket', module: 'Devoluciones', roles: ['cajero', 'supervisor'], visibility: 'dynamic', canonicalRoute: '/returns', finalMenu: false, order: 61, rationale: 'Flujo contextual desde ticket.' },
  { route: '/sync', label: 'Sincronización', module: 'Sync y offline', roles: ['cajero', 'supervisor', 'soporte'], visibility: 'final', canonicalRoute: '/sync', finalMenu: true, order: 70, rationale: 'Pendientes y conexión.' },
  { route: '/offline', label: 'Offline y export', module: 'Sync y offline', roles: ['cajero', 'supervisor'], visibility: 'submenu', canonicalRoute: '/sync', finalMenu: false, order: 71, rationale: 'Secundaria dentro de Sync.' },
  { route: '/events/outbox', label: 'Outbox operativo', module: 'Sync y offline', roles: ['soporte', 'supervisor'], visibility: 'internal-support', canonicalRoute: '/sync', finalMenu: false, order: 72, rationale: 'Detalle técnico-operativo para soporte.' },
  { route: '/settings/license', label: 'Licencia', module: 'Configuración', roles: ['supervisor', 'admin'], visibility: 'final', canonicalRoute: '/settings/license', finalMenu: true, order: 80, rationale: 'Configuración operativa visible para supervisor/admin.' },
  { route: '/settings/export', label: 'Exportaciones', module: 'Configuración', roles: ['supervisor', 'admin'], visibility: 'submenu', canonicalRoute: '/settings/export', finalMenu: false, order: 81, rationale: 'Secundaria de configuración.' },
  { route: '/settings/data', label: 'Datos', module: 'Configuración', roles: ['admin'], visibility: 'alias', canonicalRoute: '/settings/license', finalMenu: false, order: 82, rationale: 'Alias actual; futura Datos/backup sólo con implementación real.' },
  { route: '/prisma-pulse', label: 'Estado operativo', module: 'Soporte interno', roles: ['supervisor', 'soporte'], visibility: 'candidate-support', canonicalRoute: '/prisma-pulse', finalMenu: false, order: 90, rationale: 'Candidata a producto si se renombra y se limpia branding técnico.' },
  { route: '/prisma-dark-pos-reference', label: 'Dark POS Reference', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/prisma-dark-pos-reference', finalMenu: false, order: 900, rationale: 'Referencia visual; fuera de usuario final.' },
  { route: '/prisma-visual-catalog', label: 'Visual Catalog', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/prisma-visual-catalog', finalMenu: false, order: 901, rationale: 'Catálogo visual; fuera de usuario final.' },
  { route: '/referencia-visual', label: 'Referencia visual', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/referencia-visual', finalMenu: false, order: 902, rationale: 'Referencia visual; fuera de usuario final.' },
  { route: '/release-gate', label: 'Release gate', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/release-gate', finalMenu: false, order: 903, rationale: 'Gate/lab; fuera de producto final.' },
  { route: '/screen-standard-preview', label: 'Screen standard preview', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/screen-standard-preview', finalMenu: false, order: 904, rationale: 'Preview técnico; fuera de producto final.' },
  { route: '/visual-os', label: 'Visual OS', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os', finalMenu: false, order: 905, rationale: 'Visual OS es laboratorio.' },
  { route: '/visual-os/detached', label: 'Visual OS detached', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os/detached', finalMenu: false, order: 906, rationale: 'Visual OS es laboratorio.' },
  { route: '/visual-os/materiality-catalog', label: 'Materiality catalog', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os/materiality-catalog', finalMenu: false, order: 907, rationale: 'Catálogo de materialidad; laboratorio.' },
  { route: '/visual-os/pro', label: 'Visual OS Pro', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os/pro', finalMenu: false, order: 908, rationale: 'Visual OS Pro es laboratorio.' },
  { route: '/visual-os/realtime', label: 'Visual OS realtime', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os/realtime', finalMenu: false, order: 909, rationale: 'Bridge realtime; laboratorio.' },
  { route: '/visual-os/tablet-background-gallery', label: 'Background gallery', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os/tablet-background-gallery', finalMenu: false, order: 910, rationale: 'Galería; laboratorio.' },
  { route: '/visual-os/tablet-codex-gallery', label: 'Codex gallery', module: 'Laboratorio visual', roles: ['dev', 'qa'], visibility: 'lab', canonicalRoute: '/dev/tablet/visual-os/tablet-codex-gallery', finalMenu: false, order: 911, rationale: 'Galería; laboratorio.' },
];

export const TABLET_FINAL_NAVIGATION = TABLET_PAGE_CONTRACTS.filter((contract) => contract.finalMenu);
export const TABLET_INTERNAL_OR_LAB_ROUTES = TABLET_PAGE_CONTRACTS.filter((contract) => ['internal-support', 'candidate-support', 'lab'].includes(contract.visibility));
