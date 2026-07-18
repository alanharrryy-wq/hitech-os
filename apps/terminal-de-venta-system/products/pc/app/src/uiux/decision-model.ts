// PRISMA PC UIUX V02 decision model.

import { PC_PAGE_CONTRACTS, type PcPageContract, type PcEvidenceRecord, type PcUiuxGroup } from "./page-contracts";
import { humanizePcConfidence, humanizePcFreshness, humanizePcStatus } from "./status-translator";

export type PcSubnavItem = { label: string; href: string; kind: "standard" | "optional" };
export type PcRouteAction = { label: string; href: string; primary?: boolean; destructive?: boolean };

export const PC_GROUP_LABELS: Record<PcUiuxGroup, string> = {
  hoy: "Hoy",
  "ventas-caja": "Ventas y caja",
  inventario: "Inventario",
  compras: "Compras",
  proveedores: "Proveedores",
  sincronizacion: "Sincronización",
  reportes: "Reportes",
  analisis: "Análisis",
  sistema: "Sistema",
  configuracion: "Configuración",
  ayuda: "Ayuda"
};

export const PC_CANONICAL_ROUTE_ALIASES: Record<string, string> = {
  "/": "/dashboard",
  "/referencia-visual": "/laboratorio-pc/referencia-visual",
  "/referencia-visual/liquid-glass": "/laboratorio-pc/referencia-visual/liquid-glass",
  "/referencia-visual/liquid-glass-capsules": "/laboratorio-pc/referencia-visual/liquid-glass-capsules",
  "/prisma-insights/chart-lab": "/laboratorio-pc/chart-lab"
};

export const PC_STANDARD_SUBNAV: Record<PcUiuxGroup, PcSubnavItem[]> = {
  hoy: [
    { label: "Resumen", href: "/dashboard", kind: "standard" },
    { label: "Pendientes", href: "/alertas-operativas", kind: "standard" },
    { label: "Historial", href: "/audit", kind: "optional" },
    { label: "Evidencia", href: "/detalle-registros", kind: "optional" }
  ],
  "ventas-caja": [
    { label: "Resumen", href: "/sales-control", kind: "standard" },
    { label: "Clientes", href: "/clientes", kind: "standard" },
    { label: "Pendientes", href: "/cash-sessions", kind: "standard" },
    { label: "Historial", href: "/metricas-dia", kind: "standard" },
    { label: "Exportar", href: "/exportables", kind: "optional" },
    { label: "Evidencia", href: "/audit", kind: "optional" }
  ],
  inventario: [
    { label: "Resumen", href: "/catalog", kind: "standard" },
    { label: "Pendientes", href: "/stock?state=critical", kind: "standard" },
    { label: "Historial", href: "/movements", kind: "standard" },
    { label: "Configurar", href: "/politica-precios", kind: "standard" },
    { label: "Evidencia", href: "/auditoria-inventario", kind: "optional" }
  ],
  compras: [
    { label: "Resumen", href: "/purchasing", kind: "standard" },
    { label: "Órdenes", href: "/ordenes-compra", kind: "standard" },
    { label: "Recepción", href: "/receiving", kind: "standard" },
    { label: "Recibir proveedor", href: "/recepcion-proveedor", kind: "standard" },
    { label: "Reabasto", href: "/replenishment", kind: "standard" },
    { label: "Señal", href: "/senal-reabasto", kind: "standard" },
    { label: "Forecast", href: "/forecast-basico", kind: "optional" },
    { label: "Diferencias", href: "/incidencias-recepcion", kind: "optional" }
  ],
  proveedores: [
    { label: "Resumen", href: "/proveedores", kind: "standard" },
    { label: "Auditoría", href: "/audit", kind: "optional" },
    { label: "Contratos", href: "/contratos-reporte", kind: "optional" }
  ],
  sincronizacion: [
    { label: "Resumen", href: "/sync", kind: "standard" },
    { label: "Pendientes", href: "/outbox-operativo", kind: "standard" },
    { label: "Historial", href: "/sync-operativo", kind: "standard" },
    { label: "Evidencia", href: "/tablet-communication", kind: "optional" }
  ],
  reportes: [
    { label: "Resumen", href: "/exportables", kind: "standard" },
    { label: "Contratos", href: "/contratos-reporte", kind: "standard" },
    { label: "Indicadores", href: "/scorecards-negocio", kind: "standard" },
    { label: "Evidencia", href: "/tablas-operativas", kind: "optional" }
  ],
  analisis: [
    { label: "Resumen", href: "/prisma-insights", kind: "standard" },
    { label: "Pendientes", href: "/tablero-kpi", kind: "standard" },
    { label: "Historial", href: "/vistas-ejecutivas", kind: "standard" }
  ],
  sistema: [
    { label: "Resumen", href: "/devices", kind: "standard" },
    { label: "Pendientes", href: "/data-quality", kind: "standard" },
    { label: "Historial", href: "/audit", kind: "standard" },
    { label: "Configurar", href: "/settings", kind: "optional" },
    { label: "Evidencia", href: "/detalle-registros", kind: "optional" }
  ],
  configuracion: [
    { label: "Resumen", href: "/settings", kind: "standard" },
    { label: "Pendientes", href: "/settings/license", kind: "standard" },
    { label: "Historial", href: "/audit", kind: "optional" },
    { label: "Evidencia", href: "/gobierno", kind: "optional" }
  ],
  ayuda: [
    { label: "Resumen", href: "/glosario", kind: "standard" }
  ]
};

const CONTRACTS_BY_ROUTE = new Map<string, PcPageContract>(PC_PAGE_CONTRACTS.map((contract) => [contract.route, contract]));

export function normalizePcPathname(pathname: string): string {
  const clean = (pathname || "/").split("?")[0]?.split("#")[0] || "/";
  const withoutPcPrefix = clean.startsWith("/pc/") ? clean.slice(3) : clean;
  const normalized = withoutPcPrefix.length > 1 && withoutPcPrefix.endsWith("/") ? withoutPcPrefix.slice(0, -1) : withoutPcPrefix;
  return PC_CANONICAL_ROUTE_ALIASES[normalized] ?? normalized;
}

export function getPcRouteContract(pathname: string): PcPageContract {
  const normalized = normalizePcPathname(pathname);
  const exact = CONTRACTS_BY_ROUTE.get(normalized);
  if (exact) return exact;

  const nested = [...CONTRACTS_BY_ROUTE.values()]
    .filter((contract) => contract.route !== "/" && normalized.startsWith(`${contract.route}/`))
    .sort((a, b) => b.route.length - a.route.length)[0];

  return nested ?? CONTRACTS_BY_ROUTE.get("/dashboard") ?? PC_PAGE_CONTRACTS[0];
}

export function getPcSubnavItems(pathname: string): PcSubnavItem[] {
  const contract = getPcRouteContract(pathname);
  return PC_STANDARD_SUBNAV[contract.group] ?? PC_STANDARD_SUBNAV.sistema;
}

export function getPrimaryRouteActions(pathname: string): PcRouteAction[] {
  const contract = getPcRouteContract(pathname);
  const subnav = getPcSubnavItems(pathname);
  const primaryHref = subnav.find((item) => normalizePcPathname(item.href) === contract.route)?.href ?? contract.route;
  return [
    { label: contract.primaryAction, href: primaryHref, primary: true },
    { label: "Ver detalle", href: contract.route },
    { label: "Ver evidencia", href: subnav.find((item) => item.label === "Evidencia")?.href ?? contract.route }
  ];
}

export function buildEvidenceDrawerItems(pathname: string, extra: PcEvidenceRecord[] = []): PcEvidenceRecord[] {
  const contract = getPcRouteContract(pathname);
  const confidence = humanizePcConfidence(contract.dataSourceKind);
  return [
    { label: "Pantalla", value: contract.humanName, kind: "operational" },
    { label: "Pregunta", value: contract.primaryQuestion, kind: "operational" },
    { label: "Módulo", value: PC_GROUP_LABELS[contract.group], kind: "operational" },
    { label: "Confianza", value: confidence.label, kind: "technical" },
    { label: "Actualización", value: humanizePcFreshness("live"), kind: "technical" },
    ...contract.evidence,
    ...extra
  ];
}

export function getHumanRouteStatus(pathname: string) {
  const contract = getPcRouteContract(pathname);
  return humanizePcStatus(contract.dataSourceKind === "demo" ? "demo" : "healthy");
}

export function getRouteEmptyState(pathname: string) {
  return getPcRouteContract(pathname).emptyState;
}

export function getRouteErrorState(pathname: string) {
  return getPcRouteContract(pathname).errorState;
}

export function routeHasRequiredBlocks(pathname: string): boolean {
  const contract = getPcRouteContract(pathname);
  return ["decisionHeader", "attentionSummary", "nextBestAction", "evidenceDrawer"].every((block) => contract.requiredBlocks.includes(block as any));
}
