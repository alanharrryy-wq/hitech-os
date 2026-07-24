import type { PrismaIconName } from "@generated/prisma-visual-runtime/prisma-icon-types";
import {
  TABLET_PAGE_CONTRACTS,
  type TabletPageContract
} from "@/navigation/tablet-page-contracts";

/**
 * TABUX_1707_NAVIGATION
 * Four canonical destinations plus the shell-owned More sheet form the five-item dock.
 */
type TabletNavSnapshot = {
  shift: { state: string };
  connection: { pendingEvents: number; failedEvents: number; conflictEvents: number };
};

export type TabletNavGroup = "operacion" | "consulta" | "soporte";

export type TabletNavItem = {
  href: string;
  label: string;
  shortLabel: string;
  description: string;
  icon: PrismaIconName;
  group: TabletNavGroup;
  primary?: boolean;
  module: TabletPageContract["module"];
  canonicalRoute: TabletPageContract["canonicalRoute"];
};

export type TabletFlowStage = "inicio" | "venta" | "operacion" | "consulta" | "soporte";

export const TABLET_NAV_GROUP_LABELS: Record<TabletNavGroup, string> = {
  operacion: "Operación",
  consulta: "Consulta rápida",
  soporte: "Continuidad"
};

export const TABLET_NAV_ITEMS: TabletNavItem[] = [
  {
    href: "/",
    label: "Inicio Tablet",
    shortLabel: "Inicio",
    description: "Resumen operativo y siguiente trabajo.",
    icon: "dashboard",
    group: "operacion",
    primary: true,
    module: "Home Tablet",
    canonicalRoute: "/"
  },
  {
    href: "/pos",
    label: "Vender",
    shortLabel: "Vender",
    description: "Catálogo, ticket y cobro de la venta activa.",
    icon: "cart",
    group: "operacion",
    primary: true,
    module: "Venta",
    canonicalRoute: "/pos"
  },
  {
    href: "/stock",
    label: "Inventario",
    shortLabel: "Inventario",
    description: "Existencias y disponibilidad para vender.",
    icon: "package",
    group: "consulta",
    primary: true,
    module: "Inventario",
    canonicalRoute: "/stock"
  },
  {
    href: "/sales/today",
    label: "Ventas",
    shortLabel: "Ventas",
    description: "Tickets de hoy e historial de ventas.",
    icon: "receipt",
    group: "consulta",
    primary: true,
    module: "Ventas",
    canonicalRoute: "/sales/today"
  }
];

export const TABLET_MORE_ITEMS: TabletNavItem[] = [
  { href: "/catalog", label: "Catálogo", shortLabel: "Catálogo", description: "Productos y datos de venta.", icon: "tag", group: "consulta", module: "Inventario", canonicalRoute: "/catalog" },
  { href: "/returns", label: "Devoluciones", shortLabel: "Devoluciones", description: "Buscar ticket e iniciar devolución.", icon: "receipt", group: "consulta", module: "Devoluciones", canonicalRoute: "/returns" },
  { href: "/shift", label: "Turno y caja", shortLabel: "Turno", description: "Abrir, revisar y cerrar turno.", icon: "terminal", group: "operacion", module: "Turno y caja", canonicalRoute: "/shift" },
  { href: "/sync", label: "Sync y pendientes", shortLabel: "Pendientes", description: "Despacho, reintentos y conexión.", icon: "bell", group: "soporte", module: "Sync y offline", canonicalRoute: "/sync" },
  { href: "/offline", label: "Continuidad offline", shortLabel: "Offline", description: "Respaldo local y auditoría offline.", icon: "save", group: "soporte", module: "Sync y offline", canonicalRoute: "/sync" },
  { href: "/settings/license", label: "Licencia", shortLabel: "Licencia", description: "Estado de licencia y equipo.", icon: "settings", group: "soporte", module: "Configuración", canonicalRoute: "/settings/license" },
  { href: "/settings/export", label: "Exportaciones", shortLabel: "Exportar", description: "Descargar datos operativos disponibles.", icon: "save", group: "soporte", module: "Configuración", canonicalRoute: "/settings/export" }
];

function normalizeTabletPath(currentPath: string) {
  const clean = (currentPath || "/").split("?")[0]?.split("#")[0] || "/";
  return clean.length > 1 && clean.endsWith("/") ? clean.slice(0, -1) : clean;
}

function splitRoute(route: string) {
  return normalizeTabletPath(route).split("/").filter(Boolean);
}

function routePatternMatches(contractRoute: string, currentPath: string) {
  const route = normalizeTabletPath(contractRoute);
  const current = normalizeTabletPath(currentPath);

  if (route === current) return true;
  if (!route.includes(":")) return route !== "/" && current.startsWith(`${route}/`);

  const routeParts = splitRoute(route);
  const currentParts = splitRoute(current);
  if (routeParts.length !== currentParts.length) return false;
  return routeParts.every((part, index) => part.startsWith(":") || part === currentParts[index]);
}

function getTabletContractForPath(currentPath: string): TabletPageContract {
  const normalized = normalizeTabletPath(currentPath);
  const exact = TABLET_PAGE_CONTRACTS.find((contract) => normalizeTabletPath(contract.route) === normalized);
  if (exact) return exact;

  const matched = TABLET_PAGE_CONTRACTS
    .filter((contract) => routePatternMatches(contract.route, normalized))
    .sort((a, b) => b.route.length - a.route.length)[0];

  return matched ?? TABLET_PAGE_CONTRACTS.find((contract) => contract.route === "/pos") ?? TABLET_PAGE_CONTRACTS[0];
}

export function isTabletNavActive(currentPath: string, href: string) {
  const normalizedPath = normalizeTabletPath(currentPath);
  if (href === "/") return normalizedPath === "/";
  if (href === "/pos") return normalizedPath === href || normalizedPath.startsWith("/pos/") || normalizedPath === "/checkout" || normalizedPath.startsWith("/checkout/");
  if (href === "/stock") return ["/stock", "/inventory", "/existencias", "/inventory/low-stock"].includes(normalizedPath);
  if (href === "/sales/today") return normalizedPath === "/sales" || normalizedPath.startsWith("/sales/") && !normalizedPath.includes("/return");
  if (href === "/sync") return normalizedPath === "/sync" || normalizedPath.startsWith("/sync/");
  if (href === "/settings/license") return normalizedPath === href || normalizedPath === "/settings/data";
  if (href === "/returns") return normalizedPath === href || normalizedPath.includes("/return");
  return normalizedPath === href || normalizedPath.startsWith(`${href}/`);
}

export function isTabletMoreActive(currentPath: string) {
  return TABLET_MORE_ITEMS.some((item) => isTabletNavActive(currentPath, item.href));
}

export function getTabletFlowStage(currentPath: string): TabletFlowStage {
  const normalizedPath = normalizeTabletPath(currentPath);
  if (normalizedPath === "/") return "inicio";
  if (normalizedPath === "/pos" || normalizedPath.startsWith("/pos/") || normalizedPath === "/checkout" || normalizedPath.startsWith("/checkout/")) return "venta";

  const contract = getTabletContractForPath(normalizedPath);
  if (contract.module === "Inventario" || contract.module === "Ventas" || contract.module === "Devoluciones") return "consulta";
  if (contract.module === "Sync y offline" || contract.module === "Configuración") return "soporte";
  return "operacion";
}

export function getTabletPendingCount(snapshot: TabletNavSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

export function getTabletFlowCopy(stage: TabletFlowStage, snapshot: TabletNavSnapshot) {
  if (stage === "inicio") return { label: "Resumen operativo", helper: "Inicio prioriza el siguiente trabajo de caja." };
  if (stage === "venta") {
    return {
      label: snapshot.shift.state === "open" ? "Venta activa" : "Caja cerrada",
      helper: snapshot.shift.state === "open" ? "Catálogo, ticket y cobro permanecen en un solo flujo." : "Abre turno para vender; la Tablet no autoabre caja."
    };
  }
  if (stage === "consulta") return { label: "Consulta operativa", helper: "Inventario, ventas y devoluciones conservan su propio espacio." };
  if (stage === "soporte") return { label: "Continuidad", helper: "Pendientes, offline y licencia explican cómo continuar." };
  return { label: "Operación diaria", helper: "Turno y caja muestran el siguiente paso seguro." };
}

export function getVisibleTabletNavItems(_currentPath: string, _snapshot: TabletNavSnapshot) {
  return TABLET_NAV_ITEMS;
}
