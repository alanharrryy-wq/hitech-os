import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const PosModule: TwinModuleManifest = {
  key: "pos",
  route: "/pos",
  title: "POS",
  description: "Venta local standalone con búsqueda, ticket, cobro y outbox.",
  navGroup: "operation"
};
