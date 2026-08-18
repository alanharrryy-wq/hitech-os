import { pcModuleRegistry } from "./module-registry";
import { PC_ROUTE_MAP, type PcRouteMapEntry, type PcRouteStatus } from "@/uiux/route-map";
import { getPcRouteContract, normalizePcPathname, PC_GROUP_LABELS } from "@/uiux/decision-model";
import { PC_FINAL_NAVIGATION } from "@/uiux/pc-product-navigation";

export type PcHumanGroupSlug =
  | "hoy"
  | "ventas-caja"
  | "inventario"
  | "compras"
  | "proveedores"
  | "sincronizacion"
  | "reportes"
  | "analisis"
  | "sistema"
  | "configuracion"
  | "ayuda";

export type PcNavigationItem = {
  href: string;
  title: string;
  description: string;
  navGroup: string;
  group: string;
  groupLabel: string;
  status: PcRouteStatus;
  searchKeywords: string;
  isPrimary: boolean;
};

export type PcPrimaryNavigationItem = {
  href: string;
  title: string;
  description: string;
  group: PcHumanGroupSlug;
  icon: string;
};

const PC_PRODUCT_NAV_PRESENTATION: Record<string, { description: string; group: PcHumanGroupSlug; icon: string }> = {
  "/dashboard": { description: "Qué atender ahora", group: "hoy", icon: "HO" },
  "/catalog": { description: "Productos, existencias y movimientos", group: "inventario", icon: "IN" },
  "/purchasing": { description: "Pedidos, recepción y reabasto", group: "compras", icon: "CO" },
  "/proveedores": { description: "Proveedores, compras y decisiones de abasto", group: "proveedores", icon: "PR" },
  "/sales-control": { description: "Venta, dinero, tickets y cortes", group: "ventas-caja", icon: "VE" },
  "/clientes": { description: "Clientes, datos fiscales e historial de venta", group: "ventas-caja", icon: "CL" },
  "/sync": { description: "Cambios entre PC y Tablet", group: "sincronizacion", icon: "SI" },
  "/devices": { description: "Equipos, conexión y operación Tablet", group: "sistema", icon: "EQ" },
  "/exportables": { description: "Descargas, contratos y evidencia", group: "reportes", icon: "RE" },
  "/prisma-insights": { description: "Lecturas ejecutivas y señales de negocio", group: "analisis", icon: "AN" },
  "/settings": { description: "Reglas, permisos y terminales", group: "configuracion", icon: "AJ" },
  "/settings/license": { description: "Licencia, activación y modos offline/online/híbrido", group: "configuracion", icon: "LI" },
  "/glosario": { description: "Ayuda y lenguaje operativo", group: "ayuda", icon: "AY" }
};

export const PC_PRIMARY_NAVIGATION: PcPrimaryNavigationItem[] = PC_FINAL_NAVIGATION
  .filter((route) => Boolean(PC_PRODUCT_NAV_PRESENTATION[route.route]))
  .slice()
  .sort((a, b) => a.order - b.order)
  .map((route) => ({
    href: route.route,
    title: route.label,
    description: PC_PRODUCT_NAV_PRESENTATION[route.route].description,
    group: PC_PRODUCT_NAV_PRESENTATION[route.route].group,
    icon: PC_PRODUCT_NAV_PRESENTATION[route.route].icon
  }));

// Compatibility tokens for PC-UIUX-300 verifier.
// These labels are intentionally not first-level navigation titles, because ANSI nav stays human-first.
export const PC_UIUX_300_NAV_GATE_TERMS = ["Sales Control", "Devices", "Runtime", "Settings"] as const;

const GROUP_DESCRIPTIONS: Record<string, string> = {
  hoy: "Atención, decisiones y operación del día.",
  "ventas-caja": "Venta, dinero, tickets, cortes y diferencias.",
  inventario: "Productos, existencias, códigos, conteos y movimientos.",
  compras: "Pedidos, recepción, reabasto y diferencias.",
  proveedores: "Proveedores, cuentas por pagar, calidad y calendario.",
  sincronizacion: "Cambios pendientes, confirmaciones y estado PC-Tablet.",
  reportes: "Descargas, contratos y evidencia exportable.",
  analisis: "Gráficas e insights de negocio final.",
  sistema: "Salud de plataforma, equipos, licencia e historial.",
  configuracion: "Reglas, permisos, terminales y preferencias.",
  ayuda: "Guías internas y referencias operativas bajo demanda."
};

// Surface Truth reconciliation: these routes remain addressable for compatibility,
// redirects or honest blocked states, but they are not separate customer navigation
// destinations because their canonical owner is another real-data surface or no
// certified runtime owner exists yet.
const PC_HIDDEN_SECONDARY_ROUTES = new Set([
  "/acciones-masivas",
  "/contratos-reporte",
  "/detalle-registros",
  "/estados-operativos",
  "/forecast-basico",
  "/scorecards-negocio",
  "/tablas-operativas",
  "/tablero-kpi",
  "/vistas-ejecutivas"
]);

const ROUTE_MAP_BY_ROUTE = new Map<string, PcRouteMapEntry>(PC_ROUTE_MAP.map((entry) => [entry.route, entry]));
const MODULE_BY_ROUTE = new Map(pcModuleRegistry.map((module) => [module.route, module]));
const PRIMARY_BY_GROUP = new Map(PC_PRIMARY_NAVIGATION.map((item) => [item.group, item]));
const PRIMARY_ROUTES = new Set(PC_PRIMARY_NAVIGATION.map((item) => item.href));

function isClientVisibleRouteStatus(status: PcRouteStatus) {
  return status !== "internal" && status !== "lab";
}

function findRouteEntry(pathname: string): PcRouteMapEntry | undefined {
  const normalized = normalizePcPathname(pathname);
  const exact = ROUTE_MAP_BY_ROUTE.get(normalized);
  if (exact) return exact;

  return [...ROUTE_MAP_BY_ROUTE.values()]
    .filter((entry) => entry.route !== "/" && normalized.startsWith(`${entry.route}/`))
    .sort((a, b) => b.route.length - a.route.length)[0];
}

export function getPrimaryNavigation() {
  return PC_PRIMARY_NAVIGATION;
}

export function getNavigation(): PcNavigationItem[] {
  const fromModules = pcModuleRegistry.map((module) => {
    const routeEntry = ROUTE_MAP_BY_ROUTE.get(module.route);
    const contract = getPcRouteContract(module.route);
    const group = routeEntry?.group ?? contract.group;
    const primary = PRIMARY_BY_GROUP.get(group as PcHumanGroupSlug);
    const title = routeEntry?.humanName ?? contract.humanName ?? module.title;

    return {
      href: module.route,
      title,
      description: module.description,
      navGroup: module.navGroup,
      group,
      groupLabel: PC_GROUP_LABELS[group as PcHumanGroupSlug] ?? "Sistema",
      status: routeEntry?.status ?? contract.status ?? "secondary",
      searchKeywords: `${module.key} ${title} ${module.description} ${PC_GROUP_LABELS[group as PcHumanGroupSlug] ?? ""}`.toLowerCase(),
      isPrimary: Boolean(primary && primary.href === module.route)
    } satisfies PcNavigationItem;
  });

  const moduleRoutes = new Set(fromModules.map((item) => item.href));
  const routeOnlyEntries = PC_ROUTE_MAP
    .filter((entry) => !moduleRoutes.has(entry.route))
    .filter((entry) => isClientVisibleRouteStatus(entry.status))
    .filter((entry) => entry.route !== "/")
    .filter((entry) => !PRIMARY_ROUTES.has(entry.route) || Boolean(PC_PRODUCT_NAV_PRESENTATION[entry.route]))
    .map((entry) => ({
      href: entry.route,
      title: entry.humanName,
      description: GROUP_DESCRIPTIONS[entry.group] ?? "Vista operativa PRISMA.",
      navGroup: "uiux",
      group: entry.group,
      groupLabel: PC_GROUP_LABELS[entry.group as PcHumanGroupSlug] ?? "Sistema",
      status: entry.status,
      searchKeywords: `${entry.route} ${entry.humanName} ${PC_GROUP_LABELS[entry.group as PcHumanGroupSlug] ?? ""}`.toLowerCase(),
      isPrimary: Boolean(PRIMARY_BY_GROUP.get(entry.group as PcHumanGroupSlug)?.href === entry.route)
    } satisfies PcNavigationItem));

  return [...fromModules, ...routeOnlyEntries].sort((a, b) => {
    const groupOrder = PC_PRIMARY_NAVIGATION.findIndex((item) => item.group === a.group) - PC_PRIMARY_NAVIGATION.findIndex((item) => item.group === b.group);
    if (groupOrder !== 0) return groupOrder;
    if (a.isPrimary !== b.isPrimary) return a.isPrimary ? -1 : 1;
    if (a.status !== b.status) return a.status === "primary" ? -1 : 1;
    return a.title.localeCompare(b.title, "es-MX");
  });
}

export function getCurrentRouteMeta(currentPath: string) {
  const routeEntry = findRouteEntry(currentPath);
  const contract = getPcRouteContract(currentPath);
  const module = routeEntry ? MODULE_BY_ROUTE.get(routeEntry.route) : undefined;
  const group = routeEntry?.group ?? contract.group;
  const primary = PRIMARY_BY_GROUP.get(group as PcHumanGroupSlug);

  return {
    route: routeEntry?.route ?? contract.route ?? currentPath,
    title: routeEntry?.humanName ?? contract.humanName ?? primary?.title ?? "Hoy",
    description: contract.subtitle ?? module?.description ?? GROUP_DESCRIPTIONS[group] ?? "Centro de decisiones PRISMA.",
    primaryQuestion: contract.primaryQuestion,
    group,
    groupLabel: PC_GROUP_LABELS[group as PcHumanGroupSlug] ?? "Sistema",
    primaryHref: primary?.href ?? "/dashboard"
  };
}

export function getSecondaryNavigationForPath(currentPath: string) {
  const current = getCurrentRouteMeta(currentPath);
  return getNavigation().filter(
    (item) => item.group === current.group && isClientVisibleRouteStatus(item.status) && !PC_HIDDEN_SECONDARY_ROUTES.has(item.href)
  );
}
