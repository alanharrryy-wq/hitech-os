import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const ReceivingModule: TwinModuleManifest = {
  key: "receiving",
  route: "/receiving",
  title: "Recepción",
  description: "Confirmación física y discrepancias.",
  navGroup: "control"
};
