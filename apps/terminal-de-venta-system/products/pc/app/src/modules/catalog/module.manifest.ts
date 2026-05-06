import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const CatalogModule: TwinModuleManifest = {
  key: "catalog",
  route: "/catalog",
  title: "Catálogo",
  description: "Gestión de SKUs, códigos de barras y vigencia.",
  navGroup: "control"
};
