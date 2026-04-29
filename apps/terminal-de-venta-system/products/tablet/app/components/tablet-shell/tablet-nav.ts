import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";

export type TabletNavItem = {
  href: string;
  label: string;
  shortLabel: string;
  description: string;
  icon: PrismaIconName;
  group: "operacion" | "control" | "soporte";
};

export const TABLET_NAV_ITEMS: TabletNavItem[] = [
  { href: "/", label: "Inicio", shortLabel: "Inicio", description: "Pulso operativo de la terminal.", icon: "dashboard", group: "operacion" },
  { href: "/pos", label: "Vender", shortLabel: "Vender", description: "Caja rápida para buscar, agregar y cobrar productos.", icon: "cart", group: "operacion" },
  { href: "/checkout", label: "Cobro", shortLabel: "Cobro", description: "Revisión final del ticket y método de pago.", icon: "credit-card", group: "operacion" },
  { href: "/catalog", label: "Catálogo", shortLabel: "Catálogo", description: "Productos locales disponibles para venta.", icon: "tag", group: "operacion" },
  { href: "/sales/today", label: "Ventas de hoy", shortLabel: "Ventas", description: "Resumen de tickets y productos vendidos.", icon: "receipt", group: "operacion" },
  { href: "/inventory/low-stock", label: "Existencias", shortLabel: "Exist.", description: "Alertas de productos con pocas piezas.", icon: "package", group: "control" },
  { href: "/returns", label: "Devoluciones", shortLabel: "Dev.", description: "Flujo guiado para corregir tickets.", icon: "receipt", group: "control" },
  { href: "/shift", label: "Turno", shortLabel: "Turno", description: "Apertura, corte y cierre operativo.", icon: "terminal", group: "control" },
  { href: "/sync", label: "Sincronización", shortLabel: "Sinc.", description: "Estado de conexión, pendientes y conflictos.", icon: "chart", group: "soporte" },
  { href: "/settings/export", label: "Exportar", shortLabel: "Exportar", description: "Descarga de ventas, eventos y movimientos.", icon: "save", group: "soporte" }
];

export function isTabletNavActive(currentPath: string, href: string) {
  if (href === "/") return currentPath === "/";
  if (href === "/inventory/low-stock") return currentPath === href || currentPath === "/stock";
  if (href === "/sync") return currentPath === href || currentPath === "/events/outbox";
  return currentPath === href || currentPath.startsWith(`${href}/`);
}
