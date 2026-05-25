import { pcModuleRegistry } from "./module-registry";

const GROUP_BY_ROUTE: Record<string, string> = {
  "/sales-control": "Ventas y caja",
  "/cash-sessions": "Ventas y caja",
  "/catalog": "Inventario",
  "/stock": "Inventario",
  "/movements": "Inventario",
  "/counts": "Inventario",
  "/purchasing": "Compras",
  "/receiving": "Compras",
  "/replenishment": "Compras",
  "/proveedores": "Proveedores",
  "/sync": "Sincronización",
  "/tablet-communication": "Sincronización",
  "/devices": "Sistema",
  "/audit": "Sistema",
  "/license-runtime": "Sistema",
  "/data-quality": "Sistema",
  "/settings": "Configuración"
};

export function getNavigation() {
  return pcModuleRegistry.map((module) => ({
    href: module.route,
    title: module.title,
    description: module.description,
    navGroup: module.navGroup,
    groupLabel: GROUP_BY_ROUTE[module.route] ?? (module.navGroup === "control" ? "Sistema" : "Configuración"),
    searchKeywords: `${module.key} ${module.title} ${module.description}`.toLowerCase()
  }));
}
