// PRISMA PC UIUX V02 human route map.
// First level is human business language; technical routes are secondary/internal.

export type PcRouteStatus = "primary" | "secondary" | "internal" | "lab";
export type PcRouteGroup = "hoy" | "ventas-caja" | "inventario" | "compras" | "proveedores" | "sincronizacion" | "reportes" | "analisis" | "sistema" | "configuracion" | "ayuda";

export type PcRouteMapEntry = {
  route: string;
  humanName: string;
  group: PcRouteGroup;
  status: PcRouteStatus;
};

export const PC_ROUTE_MAP = [
  {
    "route": "/",
    "humanName": "Entrada",
    "group": "hoy",
    "status": "primary"
  },
  {
    "route": "/acciones-masivas",
    "humanName": "Acciones masivas",
    "group": "sistema",
    "status": "secondary"
  },
  {
    "route": "/ajustes-inventario",
    "humanName": "Ajustes de inventario",
    "group": "inventario",
    "status": "internal"
  },
  {
    "route": "/alertas-ejecutivas",
    "humanName": "Alertas ejecutivas",
    "group": "hoy",
    "status": "internal"
  },
  {
    "route": "/alertas-operativas",
    "humanName": "Alertas operativas",
    "group": "hoy",
    "status": "internal"
  },
  {
    "route": "/audit",
    "humanName": "Historial y auditoría",
    "group": "sistema",
    "status": "secondary"
  },
  {
    "route": "/auditoria-inventario",
    "humanName": "Historial de inventario",
    "group": "inventario",
    "status": "secondary"
  },
  {
    "route": "/cash-sessions",
    "humanName": "Cortes de caja",
    "group": "ventas-caja",
    "status": "secondary"
  },
  {
    "route": "/clientes",
    "humanName": "Clientes",
    "group": "ventas-caja",
    "status": "primary"
  },
  {
    "route": "/catalog",
    "humanName": "Catálogo",
    "group": "inventario",
    "status": "primary"
  },
  {
    "route": "/catalogo-activo",
    "humanName": "Productos activos",
    "group": "inventario",
    "status": "internal"
  },
  {
    "route": "/conteos-operativos",
    "humanName": "Conteos operativos",
    "group": "inventario",
    "status": "internal"
  },
  {
    "route": "/contratos-reporte",
    "humanName": "Contratos de reporte",
    "group": "reportes",
    "status": "secondary"
  },
  {
    "route": "/counts",
    "humanName": "Conteos",
    "group": "inventario",
    "status": "secondary"
  },
  {
    "route": "/dashboard",
    "humanName": "Hoy",
    "group": "hoy",
    "status": "primary"
  },
  {
    "route": "/data-quality",
    "humanName": "Revisión de datos",
    "group": "sistema",
    "status": "internal"
  },
  {
    "route": "/detalle-registros",
    "humanName": "Detalle de registros",
    "group": "sistema",
    "status": "secondary"
  },
  {
    "route": "/devices",
    "humanName": "Equipos",
    "group": "sistema",
    "status": "primary"
  },
  {
    "route": "/estados-operativos",
    "humanName": "Estados operativos",
    "group": "sistema",
    "status": "secondary"
  },
  {
    "route": "/stock?state=critical",
    "humanName": "Productos críticos",
    "group": "inventario",
    "status": "secondary"
  },
  {
    "route": "/exportables",
    "humanName": "Descargas",
    "group": "reportes",
    "status": "primary"
  },
  {
    "route": "/filtros-avanzados",
    "humanName": "Filtros avanzados",
    "group": "sistema",
    "status": "internal"
  },
  {
    "route": "/filtros-fecha",
    "humanName": "Filtros por fecha",
    "group": "sistema",
    "status": "internal"
  },
  {
    "route": "/forecast-basico",
    "humanName": "Pronóstico básico",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/glosario",
    "humanName": "Glosario",
    "group": "ayuda",
    "status": "primary"
  },
  {
    "route": "/gobierno",
    "humanName": "Gobierno",
    "group": "sistema",
    "status": "internal"
  },
  {
    "route": "/incidencias-recepcion",
    "humanName": "Diferencias de recepción",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/integridad-barcodes",
    "humanName": "Códigos repetidos",
    "group": "inventario",
    "status": "internal"
  },

  {
    "route": "/laboratorio-pc",
    "humanName": "Laboratorio PC",
    "group": "ayuda",
    "status": "lab"
  },
  {
    "route": "/laboratorio-pc/referencia-visual",
    "humanName": "Referencia visual PC",
    "group": "ayuda",
    "status": "lab"
  },
  {
    "route": "/laboratorio-pc/referencia-visual/liquid-glass",
    "humanName": "Liquid Glass Lab",
    "group": "ayuda",
    "status": "lab"
  },
  {
    "route": "/laboratorio-pc/referencia-visual/liquid-glass-capsules",
    "humanName": "Glass Capsules Lab",
    "group": "ayuda",
    "status": "lab"
  },
  {
    "route": "/laboratorio-pc/chart-lab",
    "humanName": "Chart Lab",
    "group": "analisis",
    "status": "lab"
  },
  {
    "route": "/laboratorio-pc/dashboard-governor",
    "humanName": "Dashboard Governor Lab",
    "group": "ayuda",
    "status": "lab"
  },
  {
    "route": "/license-runtime",
    "humanName": "Licencia",
    "group": "sistema",
    "status": "internal"
  },
  {
    "route": "/metricas-dia",
    "humanName": "Métricas del día",
    "group": "ventas-caja",
    "status": "secondary"
  },
  {
    "route": "/movements",
    "humanName": "Movimientos",
    "group": "inventario",
    "status": "secondary"
  },
  {
    "route": "/ordenes-compra",
    "humanName": "Órdenes de compra",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/outbox-operativo",
    "humanName": "Cambios pendientes",
    "group": "sincronizacion",
    "status": "secondary"
  },
  {
    "route": "/politica-precios",
    "humanName": "Política de precios",
    "group": "inventario",
    "status": "internal"
  },
  {
    "route": "/prisma-insights",
    "humanName": "Análisis",
    "group": "analisis",
    "status": "primary"
  },
  {
    "route": "/prisma-insights/chart-lab",
    "humanName": "Chart Lab",
    "group": "analisis",
    "status": "lab"
  },
  {
    "route": "/proveedores",
    "humanName": "Proveedores",
    "group": "proveedores",
    "status": "primary"
  },
  {
    "route": "/purchasing",
    "humanName": "Compras",
    "group": "compras",
    "status": "primary"
  },
  {
    "route": "/receiving",
    "humanName": "Recepción",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/recepcion-proveedor",
    "humanName": "Recibir proveedor",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/referencia-visual",
    "humanName": "Referencia visual",
    "group": "ayuda",
    "status": "internal"
  },
  {
    "route": "/replenishment",
    "humanName": "Reabasto",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/sales-control",
    "humanName": "Ventas",
    "group": "ventas-caja",
    "status": "primary"
  },
  {
    "route": "/salud-barcodes",
    "humanName": "Salud de códigos",
    "group": "inventario",
    "status": "secondary"
  },
  {
    "route": "/scorecards-negocio",
    "humanName": "Indicadores de negocio",
    "group": "reportes",
    "status": "secondary"
  },
  {
    "route": "/senal-reabasto",
    "humanName": "Señal de reabasto",
    "group": "compras",
    "status": "secondary"
  },
  {
    "route": "/settings",
    "humanName": "Configuración",
    "group": "configuracion",
    "status": "primary"
  },
  {
    "route": "/settings/license",
    "humanName": "Licencia",
    "group": "configuracion",
    "status": "secondary"
  },
  {
    "route": "/stock",
    "humanName": "Existencias",
    "group": "inventario",
    "status": "secondary"
  },
  {
    "route": "/sync",
    "humanName": "Sincronización",
    "group": "sincronizacion",
    "status": "primary"
  },
  {
    "route": "/sync-operativo",
    "humanName": "Sincronización operativa",
    "group": "sincronizacion",
    "status": "internal"
  },
  {
    "route": "/tablas-operativas",
    "humanName": "Tablas operativas",
    "group": "reportes",
    "status": "secondary"
  },
  {
    "route": "/tablero-kpi",
    "humanName": "Tablero KPI",
    "group": "reportes",
    "status": "secondary"
  },
  {
    "route": "/tablet-communication",
    "humanName": "Tablet",
    "group": "sincronizacion",
    "status": "internal"
  },
  {
    "route": "/validacion-catalogo",
    "humanName": "Validación de catálogo",
    "group": "inventario",
    "status": "internal"
  },
  {
    "route": "/vistas-ejecutivas",
    "humanName": "Vistas ejecutivas",
    "group": "reportes",
    "status": "secondary"
  },
  {
      "route": "/referencia-visual/liquid-glass",
      "humanName": "Liquid Glass Lab alias",
      "group": "ayuda",
      "status": "internal"
  },
  {
      "route": "/referencia-visual/liquid-glass-capsules",
      "humanName": "Glass Capsules Lab alias",
      "group": "ayuda",
      "status": "internal"
  }
] as const satisfies readonly PcRouteMapEntry[];
