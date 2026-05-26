import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";

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
};

export type TabletFlowStage = "inicio" | "venta" | "operacion" | "consulta" | "soporte";

export const TABLET_NAV_GROUP_LABELS: Record<TabletNavGroup, string> = {
  operacion: "Operación",
  consulta: "Consulta rápida",
  soporte: "Soporte"
};

export const TABLET_NAV_ITEMS: TabletNavItem[] = [
  { href: "/", label: "Inicio", shortLabel: "Inicio", description: "Mapa de trabajo y pulso operativo de la terminal.", icon: "dashboard", group: "operacion" },
  { href: "/shift", label: "Turno y caja", shortLabel: "Turno", description: "Apertura, corte y cierre operativo.", icon: "terminal", group: "operacion" },
  { href: "/pos", label: "Vender", shortLabel: "Vender", description: "Cobro rápido: busca, escanea, arma el ticket y cobra.", icon: "cart", group: "operacion", primary: true },
  { href: "/catalog", label: "Catálogo", shortLabel: "Catálogo", description: "Productos locales disponibles para venta.", icon: "tag", group: "consulta" },
  { href: "/stock", label: "Existencias", shortLabel: "Stock", description: "Stock operativo local, quiebres y señales de reabasto.", icon: "package", group: "consulta" },
  { href: "/sales/today", label: "Ventas de hoy", shortLabel: "Ventas", description: "Resumen de tickets y productos vendidos.", icon: "receipt", group: "consulta" },
  { href: "/sales/history", label: "Historial ventas", shortLabel: "Historial", description: "Consulta local acotada de tickets anteriores.", icon: "receipt", group: "consulta" },
  { href: "/returns", label: "Devoluciones", shortLabel: "Dev.", description: "Revisión y creación de devoluciones desde tickets existentes.", icon: "receipt", group: "consulta" },
  { href: "/sync", label: "Sincronización", shortLabel: "Sinc.", description: "Envíos pendientes, fallidos y trabajo local por revisar.", icon: "bell", group: "soporte" },
  { href: "/offline", label: "Sin conexión / Exportar", shortLabel: "Exportar", description: "Auditoría local, exportación y evidencia operativa.", icon: "receipt", group: "soporte" },
  { href: "/release-gate", label: "Estado del sistema", shortLabel: "Estado", description: "Revisión operativa de flujos críticos antes de liberar.", icon: "settings", group: "soporte" },
  { href: "/settings/data", label: "Datos locales", shortLabel: "Datos", description: "Herramientas bloqueadas para reset seguro de ventas.", icon: "settings", group: "soporte" },
  { href: "/settings/license", label: "Licencia", shortLabel: "Lic.", description: "Estado de licencia y permisos de uso de Tablet.", icon: "settings", group: "soporte" }
];

const CONSULTA_PATHS = new Set(["/catalog", "/stock", "/inventory", "/existencias", "/inventory/low-stock", "/sales", "/sales/today", "/sales/history", "/returns"]);
const SOPORTE_PATHS = new Set(["/sync", "/offline", "/settings/export", "/settings/data", "/settings/license", "/release-gate"]);
const OPERATION_PATHS = new Set(["/", "/pos", "/checkout", "/shift"]);

export function isTabletNavActive(currentPath: string, href: string) {
  if (href === "/") return currentPath === "/";
  if (href === "/pos") return currentPath === href || currentPath.startsWith("/pos/") || currentPath === "/checkout" || currentPath.startsWith("/checkout/");
  if (href === "/stock") return currentPath === href || currentPath === "/inventory" || currentPath === "/existencias" || currentPath === "/inventory/low-stock";
  if (href === "/sync") return currentPath === href;
  if (href === "/offline") return currentPath === href || currentPath === "/settings/export";
  if (href === "/sales/today") return currentPath === href || currentPath.startsWith("/sales/today") || currentPath === "/sales";
  if (href === "/sales/history") return currentPath === href || currentPath.startsWith("/sales/history");
  if (href === "/returns") return currentPath === href || currentPath.includes("/return");
  return currentPath === href || currentPath.startsWith(`${href}/`);
}

export function getTabletFlowStage(currentPath: string): TabletFlowStage {
  if (currentPath === "/") return "inicio";
  if (currentPath === "/pos" || currentPath.startsWith("/pos/") || currentPath === "/checkout" || currentPath.startsWith("/checkout/")) return "venta";
  if (Array.from(CONSULTA_PATHS).some((path) => currentPath === path || currentPath.startsWith(`${path}/`))) return "consulta";
  if (Array.from(SOPORTE_PATHS).some((path) => currentPath === path || currentPath.startsWith(`${path}/`))) return "soporte";
  if (Array.from(OPERATION_PATHS).some((path) => currentPath === path || currentPath.startsWith(`${path}/`))) return "operacion";
  return "operacion";
}

export function getTabletPendingCount(snapshot: TabletNavSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

export function getTabletFlowCopy(stage: TabletFlowStage, snapshot: TabletNavSnapshot) {
  if (stage === "inicio") {
    return {
      label: "Mapa de trabajo",
      helper: "Las pantallas principales quedan visibles; Inicio solo orienta el flujo."
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
      helper: "Catálogo y existencias se revisan sin convertir Tablet en backoffice."
    };
  }
  if (stage === "soporte") {
    return {
      label: "Soporte operativo",
      helper: "Pendientes, offline, estado y licencia viven juntos para no esconder puertas."
    };
  }
  return {
    label: "Operación diaria",
    helper: "Turno, tickets y venta quedan visibles en todo momento."
  };
}

export function getVisibleTabletNavItems(_currentPath: string, snapshot: TabletNavSnapshot) {
  const canShowSellNavigation = snapshot.shift.state === "open";
  return TABLET_NAV_ITEMS.filter((item) => item.href !== "/pos" || canShowSellNavigation);
}
