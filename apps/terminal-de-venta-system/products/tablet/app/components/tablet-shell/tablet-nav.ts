import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";
import {
  TABLET_FINAL_NAVIGATION,
  TABLET_PAGE_CONTRACTS,
  type TabletPageContract
} from "@/navigation/tablet-page-contracts";

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

const TABLET_NAV_PRESENTATION: Record<string, Pick<TabletNavItem, "shortLabel" | "icon" | "group" | "primary">> = {
  "/pos": { shortLabel: "Vender", icon: "cart", group: "operacion", primary: true },
  "/shift": { shortLabel: "Turno", icon: "terminal", group: "operacion" },
  "/stock": { shortLabel: "Inventario", icon: "package", group: "consulta" },
  "/sales/today": { shortLabel: "Ventas", icon: "receipt", group: "consulta" },
  "/returns": { shortLabel: "Devol.", icon: "receipt", group: "consulta" },
  "/sync": { shortLabel: "Pendientes", icon: "bell", group: "soporte" },
  "/settings/license": { shortLabel: "Licencia", icon: "settings", group: "soporte" }
};

const DEFAULT_TABLET_NAV_PRESENTATION: Pick<TabletNavItem, "shortLabel" | "icon" | "group" | "primary"> = {
  shortLabel: "Abrir",
  icon: "dashboard",
  group: "operacion"
};

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
  if (!route.includes(":")) {
    return route !== "/" && current.startsWith(`${route}/`);
  }

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

function tabletContractToNavItem(contract: TabletPageContract): TabletNavItem {
  const presentation = TABLET_NAV_PRESENTATION[contract.route] ?? DEFAULT_TABLET_NAV_PRESENTATION;

  return {
    href: contract.route,
    label: contract.label,
    shortLabel: presentation.shortLabel,
    description: contract.rationale,
    icon: presentation.icon,
    group: presentation.group,
    primary: presentation.primary,
    module: contract.module,
    canonicalRoute: contract.canonicalRoute
  };
}

export const TABLET_NAV_ITEMS: TabletNavItem[] = TABLET_FINAL_NAVIGATION
  .slice()
  .sort((a, b) => a.order - b.order)
  .map(tabletContractToNavItem);

export function isTabletNavActive(currentPath: string, href: string) {
  const normalizedPath = normalizeTabletPath(currentPath);

  if (href === "/pos") return normalizedPath === href || normalizedPath.startsWith("/pos/") || normalizedPath === "/checkout" || normalizedPath.startsWith("/checkout/");
  if (href === "/stock") return normalizedPath === href || normalizedPath === "/inventory" || normalizedPath === "/existencias" || normalizedPath === "/inventory/low-stock";
  if (href === "/sync") return normalizedPath === href || normalizedPath === "/offline" || normalizedPath === "/events/outbox";
  if (href === "/settings/license") return normalizedPath === href || normalizedPath === "/settings/data" || normalizedPath === "/settings/export";
  if (href === "/sales/today") return normalizedPath === href || normalizedPath.startsWith("/sales/today") || normalizedPath === "/sales";
  if (href === "/returns") return normalizedPath === href || normalizedPath.includes("/return");
  return normalizedPath === href || normalizedPath.startsWith(`${href}/`);
}

export function getTabletFlowStage(currentPath: string): TabletFlowStage {
  const normalizedPath = normalizeTabletPath(currentPath);
  if (normalizedPath === "/") return "inicio";
  if (normalizedPath === "/pos" || normalizedPath.startsWith("/pos/") || normalizedPath === "/checkout" || normalizedPath.startsWith("/checkout/")) return "venta";

  const contract = getTabletContractForPath(normalizedPath);
  if (contract.module === "Inventario" || contract.module === "Ventas" || contract.module === "Devoluciones") return "consulta";
  if (contract.module === "Sync y offline" || contract.module === "Configuración" || contract.module === "Soporte interno") return "soporte";
  if (contract.module === "Turno y caja") return "operacion";
  return "operacion";
}

export function getTabletPendingCount(snapshot: TabletNavSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

export function getTabletFlowCopy(stage: TabletFlowStage, snapshot: TabletNavSnapshot) {
  if (stage === "inicio") {
    return {
      label: "Mapa de trabajo",
      helper: "Inicio muestra solo lo necesario para vender, revisar y atender pendientes."
    };
  }
  if (stage === "venta") {
    return {
      label: snapshot.shift.state === "open" ? "Venta activa" : "Caja cerrada",
      helper: snapshot.shift.state === "open" ? "Vender queda como acción principal; soporte y consulta siguen a la mano." : "Abre turno para vender; la Tablet no autoabre caja ni depende de PC."
    };
  }
  if (stage === "consulta") {
    return {
      label: "Consulta rápida",
      helper: "Inventario, ventas y devoluciones se revisan sin salir de la Tablet."
    };
  }
  if (stage === "soporte") {
    return {
      label: "Continuidad",
      helper: "Pendientes, respaldo y licencia muestran que hacer para seguir operando."
    };
  }
  return {
    label: "Operación diaria",
    helper: "Turno, tickets y venta quedan visibles en todo momento."
  };
}

export function getVisibleTabletNavItems(_currentPath: string, _snapshot: TabletNavSnapshot) {
  // La navegación de venta debe seguir visible aun con turno cerrado:
  // la pantalla /pos ya decide si permite cobrar, abrir turno o mostrar bloqueo operativo.
  return TABLET_NAV_ITEMS;
}
