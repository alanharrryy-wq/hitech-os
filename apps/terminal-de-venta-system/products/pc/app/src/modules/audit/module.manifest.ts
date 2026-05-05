import type { TwinModuleManifest } from "@shared-kernel/types/module";

export const AuditModule: TwinModuleManifest = {
  key: "audit",
  route: "/audit",
  title: "Auditoría",
  description: "Ajustes y trazabilidad.",
  navGroup: "control"
};
