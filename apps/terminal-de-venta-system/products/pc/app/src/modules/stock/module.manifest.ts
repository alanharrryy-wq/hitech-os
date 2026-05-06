import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const StockModule: TwinModuleManifest = {
  key: "stock",
  route: "/stock",
  title: "Existencias",
  description: "Cobertura, quiebres y sobreinventario.",
  navGroup: "control"
};
