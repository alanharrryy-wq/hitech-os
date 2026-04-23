import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const StockModule: TwinModuleManifest = {
  key: "stock",
  route: "/stock",
  title: "Stock operativo",
  description: "Existencias, quiebres y reabasto ligero para venta.",
  navGroup: "control"
};
