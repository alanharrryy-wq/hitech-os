import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const CountsModule: TwinModuleManifest = {
  key: "counts",
  route: "/counts",
  title: "Conteos físicos",
  description: "Ciclos de conteo y conciliación.",
  navGroup: "control"
};
