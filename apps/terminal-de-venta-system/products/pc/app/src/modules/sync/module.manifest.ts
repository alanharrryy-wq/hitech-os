import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const SyncModule: TwinModuleManifest = {
  key: "sync",
  route: "/sync",
  title: "Sincronización",
  description: "Estado de sincronización con la terminal de venta.",
  navGroup: "control"
};
