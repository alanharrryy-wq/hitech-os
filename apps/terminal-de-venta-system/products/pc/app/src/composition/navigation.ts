import { pcModuleRegistry } from "./module-registry";

const GROUP_BY_ROUTE: Record<string, string> = {
  "/dashboard": "Overview",
  "/sales-control": "Sales Control",
  "/cash-sessions": "Sales Control",
  "/catalog": "Inventory",
  "/stock": "Inventory",
  "/movements": "Inventory",
  "/counts": "Inventory",
  "/purchasing": "Purchasing",
  "/receiving": "Purchasing",
  "/replenishment": "Purchasing",
  "/proveedores": "Purchasing",
  "/sync": "Sync",
  "/tablet-communication": "Sync",
  "/devices": "Devices",
  "/audit": "Audit",
  "/license-runtime": "Runtime",
  "/data-quality": "Runtime",
  "/settings": "Settings"
};

export function getNavigation() {
  return pcModuleRegistry.map((module) => ({
    href: module.route,
    title: module.title,
    description: module.description,
    navGroup: module.navGroup,
    groupLabel: GROUP_BY_ROUTE[module.route] ?? (module.navGroup === "control" ? "Control" : "Settings"),
    searchKeywords: `${module.key} ${module.title} ${module.description}`.toLowerCase()
  }));
}
