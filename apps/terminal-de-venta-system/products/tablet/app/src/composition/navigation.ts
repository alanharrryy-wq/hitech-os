import { tabletModuleRegistry } from "./module-registry";

export function getNavigation() {
  return tabletModuleRegistry.map((module) => ({ href: module.route, title: module.title, description: module.description }));
}
