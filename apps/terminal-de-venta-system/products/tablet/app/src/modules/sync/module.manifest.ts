import type { TwinModuleManifest } from "@shared-kernel/types/module";
export const SyncModule: TwinModuleManifest = {
  key: "sync",
  route: "/sync",
  title: "Centro de sincronización",
  description: "Sincronización sin conexión, latencia y reintentos.",
  navGroup: "control"
};
