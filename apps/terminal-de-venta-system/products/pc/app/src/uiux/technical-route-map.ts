// PRISMA PC UIUX V02 technical route relocation map.

export type TechnicalRouteRelocation = {
  technicalLabel: string;
  humanLabel: string;
  oldRoute: string;
  newParent: "Sistema" | "Sincronización" | "Inventario" | "Reportes" | "Configuración" | "Evidencia técnica";
  reason: string;
};

export const TECHNICAL_ROUTE_RELOCATIONS: TechnicalRouteRelocation[] = [
  { technicalLabel: "Runtime", humanLabel: "Sistema", oldRoute: "/runtime", newParent: "Sistema", reason: "La salud interna pertenece a Sistema, no al primer nivel." },
  { technicalLabel: "Data Quality", humanLabel: "Revisión de datos", oldRoute: "/data-quality", newParent: "Sistema", reason: "La revisión de datos es evidencia operativa bajo demanda." },
  { technicalLabel: "License Runtime", humanLabel: "Licencia", oldRoute: "/license-runtime", newParent: "Sistema", reason: "Licencia es estado de plataforma." },
  { technicalLabel: "Tablet Communication", humanLabel: "Tablet", oldRoute: "/tablet-communication", newParent: "Sincronización", reason: "Comunicación tablet-PC es sincronización." },
  { technicalLabel: "Devices", humanLabel: "Equipos", oldRoute: "/devices", newParent: "Sistema", reason: "Equipos es una subpantalla de salud del sistema." },
  { technicalLabel: "Audit", humanLabel: "Historial y auditoría", oldRoute: "/audit", newParent: "Sistema", reason: "Auditoría vive como evidencia y trazabilidad." },
  { technicalLabel: "Counts", humanLabel: "Conteos", oldRoute: "/counts", newParent: "Inventario", reason: "Conteos son operación de inventario." },
  { technicalLabel: "Movements", humanLabel: "Movimientos", oldRoute: "/movements", newParent: "Inventario", reason: "Movimientos son historial de existencias." }
];

export const FIRST_LEVEL_TECHNICAL_DENYLIST = TECHNICAL_ROUTE_RELOCATIONS.map((item) => item.technicalLabel);

export function getTechnicalRelocation(labelOrRoute: string): TechnicalRouteRelocation | undefined {
  const normalized = labelOrRoute.toLowerCase().trim();
  return TECHNICAL_ROUTE_RELOCATIONS.find((item) =>
    item.technicalLabel.toLowerCase() === normalized ||
    item.oldRoute.toLowerCase() === normalized ||
    item.humanLabel.toLowerCase() === normalized
  );
}
