import type { TwinModuleManifest } from "../types/module";

export function sortModules(modules: TwinModuleManifest[]) {
  return [...modules].sort((a, b) => a.title.localeCompare(b.title));
}
