import { TWIN_CAPABILITY_MANIFEST } from "./twin-capability-manifest";
import type { TwinCapabilityDomain, TwinCapabilityStatus, TwinSurface } from "../types/capability";

export type TwinParityTarget = {
  domain: TwinCapabilityDomain;
  minimumReady: number;
  requiredSurface: TwinSurface[];
  releaseGate: "blocker" | "warning";
  reason: string;
};

export const TWIN_PARITY_TARGETS: TwinParityTarget[] = [
  { domain: "catalog", minimumReady: 1, requiredSurface: ["pc", "tablet"], releaseGate: "blocker", reason: "Sin catálogo común, la venta se vuelve lotería de barrio." },
  { domain: "inventory", minimumReady: 1, requiredSurface: ["pc", "tablet"], releaseGate: "blocker", reason: "Stock sin paridad es promesa de mostrador, no sistema." },
  { domain: "sales", minimumReady: 2, requiredSurface: ["pc", "tablet"], releaseGate: "blocker", reason: "Ventas y cobros deben verse en ambas superficies." },
  { domain: "cash", minimumReady: 1, requiredSurface: ["pc", "tablet"], releaseGate: "blocker", reason: "Caja sin auditoría central es alcancía con Excel." },
  { domain: "sync", minimumReady: 1, requiredSurface: ["pc", "tablet"], releaseGate: "blocker", reason: "El estado de sincronización tiene que ser visible antes de crecer." },
  { domain: "audit", minimumReady: 1, requiredSurface: ["pc", "tablet"], releaseGate: "warning", reason: "Auditoría puede madurar por fases, pero no desaparecer." },
  { domain: "reporting", minimumReady: 0, requiredSurface: ["pc", "tablet"], releaseGate: "warning", reason: "KPIs deben compartir fuente antes de ponerse bonitos." }
];

export function summarizeTwinParityTargets() {
  return TWIN_PARITY_TARGETS.map((target) => {
    const capabilities = TWIN_CAPABILITY_MANIFEST.filter((capability) => capability.domain === target.domain);
    const ready = capabilities.filter((capability) => capability.status === "ready").length;
    const partial = capabilities.filter((capability) => capability.status === "partial").length;
    const planned = capabilities.filter((capability) => capability.status === "planned").length;
    const status: TwinCapabilityStatus | "under_minimum" = ready >= target.minimumReady ? "ready" : "under_minimum";
    return { ...target, capabilityCount: capabilities.length, ready, partial, planned, status };
  });
}
