import { TABLET_FINAL_NAVIGATION, TABLET_PAGE_CONTRACTS, type TabletPageContract } from "@/navigation/tablet-page-contracts";

/**
 * CUSTOMER_SURFACE_REDUCTION_1507
 * Runtime navigation is derived only from active customer contracts.
 */
export type TabletNavigationItem = {
  href: string;
  title: string;
  description: string;
  module: string;
  canonicalRoute: string;
  visibility: TabletPageContract["visibility"];
  isPrimary: boolean;
};

const TABLET_ROUTE_DESCRIPTIONS: Record<string, string> = {
  "/pos": "Venta touch-first, carrito, cobro y tickets en espera.",
  "/shift": "Apertura, cierre y estado de caja para operar sin confusión.",
  "/stock": "Existencias vendibles, stock bajo y consulta rápida de inventario.",
  "/sales/today": "Tickets del día y acceso al detalle operativo de venta.",
  "/returns": "Devoluciones desde venta o ticket, sin exponer rutas dinámicas.",
  "/sync": "Pendientes, conexión y estado de sincronización PC-Tablet.",
  "/settings/license": "Licencia y configuración operativa autorizada."
};

function normalizeTabletPathname(pathname: string) {
  const clean = (pathname || "/").split("?")[0]?.split("#")[0] || "/";
  return clean.length > 1 && clean.endsWith("/") ? clean.slice(0, -1) : clean;
}

function contractToNavigationItem(contract: TabletPageContract): TabletNavigationItem {
  return {
    href: contract.route,
    title: contract.label,
    description: TABLET_ROUTE_DESCRIPTIONS[contract.route] ?? contract.rationale,
    module: contract.module,
    canonicalRoute: contract.canonicalRoute,
    visibility: contract.visibility,
    isPrimary: contract.finalMenu
  };
}

export function getTabletRouteContract(currentPath: string): TabletPageContract {
  const normalized = normalizeTabletPathname(currentPath);
  const exact = TABLET_PAGE_CONTRACTS.find((contract) => contract.route === normalized);
  if (exact) return exact;

  const nested = TABLET_PAGE_CONTRACTS
    .filter((contract) => !contract.route.includes(":") && contract.route !== "/" && normalized.startsWith(`${contract.route}/`))
    .sort((a, b) => b.route.length - a.route.length)[0];

  return nested ?? TABLET_PAGE_CONTRACTS.find((contract) => contract.route === "/pos") ?? TABLET_PAGE_CONTRACTS[0];
}

export function getNavigation(): TabletNavigationItem[] {
  return TABLET_FINAL_NAVIGATION
    .slice()
    .sort((a, b) => a.order - b.order)
    .map(contractToNavigationItem);
}

export function getTabletSecondaryNavigationForPath(currentPath: string): TabletNavigationItem[] {
  const current = getTabletRouteContract(currentPath);
  return TABLET_PAGE_CONTRACTS
    .filter((contract) => contract.module === current.module)
    .filter((contract) => ["submenu", "step"].includes(contract.visibility))
    .filter((contract) => !contract.route.includes(":"))
    .sort((a, b) => a.order - b.order)
    .map(contractToNavigationItem);
}
