import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";

export type TabletNavItem = {
  href: string;
  label: string;
  shortLabel: string;
  description: string;
  icon: PrismaIconName;
  group: "operacion" | "control" | "soporte";
  primary?: boolean;
};

export type TabletFlowStage = "inicio" | "venta" | "operacion" | "control";

export const TABLET_NAV_ITEMS: TabletNavItem[] = [
  { href: "/", label: "Inicio", shortLabel: "Inicio", description: "Pulso operativo de la terminal.", icon: "dashboard", group: "operacion" },
  { href: "/pos", label: "Vender", shortLabel: "Vender", description: "Caja rapida para buscar, agregar y cobrar productos.", icon: "cart", group: "operacion", primary: true },
  { href: "/sales/today", label: "Ventas de hoy", shortLabel: "Ventas", description: "Resumen de tickets y productos vendidos.", icon: "receipt", group: "operacion" },
  { href: "/catalog", label: "Catalogo", shortLabel: "Catalogo", description: "Productos locales disponibles para venta.", icon: "tag", group: "operacion" },
  { href: "/stock", label: "Existencias", shortLabel: "Exist.", description: "Stock operativo local, quiebres y senales de reabasto.", icon: "package", group: "control" },
  { href: "/shift", label: "Turno", shortLabel: "Turno", description: "Apertura, corte y cierre operativo.", icon: "terminal", group: "control" },
  { href: "/sync", label: "Pendientes", shortLabel: "Pend.", description: "Envios pendientes, fallidos y trabajo local por revisar.", icon: "bell", group: "soporte" },
  { href: "/release-gate", label: "Estado del sistema", shortLabel: "Estado", description: "Revision operativa de flujos criticos antes de liberar.", icon: "settings", group: "soporte" }
];

const CONTROL_PATHS = new Set(["/catalog", "/stock", "/inventory", "/existencias", "/inventory/low-stock", "/release-gate", "/settings/export", "/settings/license"]);
const OPERATION_PATHS = new Set(["/sales", "/sales/today", "/shift", "/sync", "/events/outbox", "/returns"]);

export function isTabletNavActive(currentPath: string, href: string) {
  if (href === "/") return currentPath === "/";
  if (href === "/stock") return currentPath === href || currentPath === "/inventory" || currentPath === "/existencias" || currentPath === "/inventory/low-stock";
  if (href === "/sync") return currentPath === href || currentPath === "/events/outbox";
  if (href === "/sales/today") return currentPath === href || currentPath.startsWith("/sales/today");
  return currentPath === href || currentPath.startsWith(`${href}/`);
}

export function getTabletFlowStage(currentPath: string): TabletFlowStage {
  if (currentPath === "/") return "inicio";
  if (currentPath === "/pos" || currentPath.startsWith("/pos/") || currentPath === "/checkout" || currentPath.startsWith("/checkout/")) return "venta";
  if (Array.from(CONTROL_PATHS).some((path) => currentPath === path || currentPath.startsWith(`${path}/`))) return "control";
  if (Array.from(OPERATION_PATHS).some((path) => currentPath === path || currentPath.startsWith(`${path}/`))) return "operacion";
  return "operacion";
}

function hasPendingWork(snapshot: TabletRuntimeSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents > 0;
}

function hasSystemAttention(snapshot: TabletRuntimeSnapshot) {
  return snapshot.warnings.length > 0 || snapshot.connection.state === "offline" || snapshot.connection.state === "review" || snapshot.catalog.state === "empty" || snapshot.catalog.state === "review" || snapshot.catalog.state === "stale";
}

function uniqueNav(items: TabletNavItem[]) {
  const seen = new Set<string>();
  return items.filter((item) => {
    if (seen.has(item.href)) return false;
    seen.add(item.href);
    return true;
  });
}

function navByHref(href: string) {
  const item = TABLET_NAV_ITEMS.find((candidate) => candidate.href === href);
  if (!item) throw new Error(`Tablet nav item not found: ${href}`);
  return item;
}

function activeCanonicalHref(currentPath: string) {
  const active = TABLET_NAV_ITEMS.find((item) => isTabletNavActive(currentPath, item.href));
  return active?.href ?? null;
}

export function getTabletFlowCopy(stage: TabletFlowStage, snapshot: TabletRuntimeSnapshot) {
  if (stage === "inicio") {
    return {
      label: "Inicio guiado",
      helper: "Primero revisa el pulso. Las demas rutas aparecen cuando el flujo las necesita."
    };
  }
  if (stage === "venta") {
    return {
      label: snapshot.shift.state === "open" ? "Venta activa" : "Venta guiada",
      helper: snapshot.shift.state === "open" ? "Caja enfocada en vender, cobrar y dejar rastro." : "Abre turno si la politica lo pide; la Tablet sigue siendo POS standalone."
    };
  }
  if (stage === "control") {
    return {
      label: "Control contextual",
      helper: "Solo aparecen consulta, stock o sistema cuando la ruta lo amerita."
    };
  }
  return {
    label: "Operacion diaria",
    helper: "Turno, ventas y pendientes sin convertir la Tablet en backoffice miniatura."
  };
}

export function getVisibleTabletNavItems(currentPath: string, snapshot: TabletRuntimeSnapshot) {
  const stage = getTabletFlowStage(currentPath);
  const activeHref = activeCanonicalHref(currentPath);

  if (stage === "inicio") {
    return [navByHref("/")];
  }

  const items: TabletNavItem[] = [navByHref("/"), navByHref("/pos")];

  if (snapshot.shift.state !== "open" || stage === "venta" || activeHref === "/shift") {
    items.push(navByHref("/shift"));
  }

  if (stage === "venta" || stage === "operacion" || activeHref === "/sales/today") {
    items.push(navByHref("/sales/today"));
  }

  if (activeHref === "/catalog" || (stage === "control" && currentPath.startsWith("/catalog"))) {
    items.push(navByHref("/catalog"));
  }

  if (activeHref === "/stock" || (stage === "control" && (currentPath.startsWith("/stock") || currentPath.startsWith("/inventory") || currentPath.startsWith("/existencias")))) {
    items.push(navByHref("/stock"));
  }

  if (hasPendingWork(snapshot) || activeHref === "/sync") {
    items.push(navByHref("/sync"));
  }

  if (hasSystemAttention(snapshot) || activeHref === "/release-gate") {
    items.push(navByHref("/release-gate"));
  }

  if (activeHref && !items.some((item) => item.href === activeHref)) {
    items.push(navByHref(activeHref));
  }

  return uniqueNav(items);
}
