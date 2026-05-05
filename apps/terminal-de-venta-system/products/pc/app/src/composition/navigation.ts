import { pcModuleRegistry } from "./module-registry";

export function getNavigation() {
  return pcModuleRegistry.map((module) => ({ href: module.route, title: module.title, description: module.description, navGroup: module.navGroup }));
}
