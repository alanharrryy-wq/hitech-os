import { BASIC_POS_FEATURES, PC_BACKOFFICE_FEATURES, TABLET_PRO_FEATURES } from "./feature-keys";
import type { LicensePlan } from "./license-types";

export type PlanDefinition = {
  plan: LicensePlan;
  label: string;
  rank: number;
  description: string;
  features: Set<string>;
};

function union(...sets: Set<string>[]) {
  return new Set(sets.flatMap((set) => [...set]));
}

export const PLAN_CATALOG: Record<LicensePlan, PlanDefinition> = {
  TABLET_SOLO: {
    plan: "TABLET_SOLO",
    label: "Tablet Solo",
    rank: 10,
    description: "POS autónomo con venta, ticket, stock local, corte y exportación básica.",
    features: new Set(BASIC_POS_FEATURES)
  },
  TABLET_PRO: {
    plan: "TABLET_PRO",
    label: "Tablet Pro",
    rank: 20,
    description: "Tablet con turnos, devoluciones, outbox visible, reportes operativos y export avanzado.",
    features: union(BASIC_POS_FEATURES, TABLET_PRO_FEATURES)
  },
  TABLET_PC_REQUIRED: {
    plan: "TABLET_PC_REQUIRED",
    label: "Tablet + PC",
    rank: 30,
    description: "Operación administrada con backoffice, sync, auditoría e inventario avanzado.",
    features: union(BASIC_POS_FEATURES, TABLET_PRO_FEATURES, PC_BACKOFFICE_FEATURES)
  },
  DEVELOPMENT: {
    plan: "DEVELOPMENT",
    label: "Desarrollo",
    rank: 99,
    description: "Modo local de desarrollo con todas las funciones habilitadas.",
    features: union(BASIC_POS_FEATURES, TABLET_PRO_FEATURES, PC_BACKOFFICE_FEATURES)
  },
  TABLET_SOLO_FALLBACK: {
    plan: "TABLET_SOLO_FALLBACK",
    label: "Tablet Solo Fallback",
    rank: 1,
    description: "Modo de continuidad: venta básica disponible y funciones avanzadas bloqueadas.",
    features: new Set(BASIC_POS_FEATURES)
  }
};

export function planIncludesFeature(plan: LicensePlan, featureKey: string): boolean {
  return PLAN_CATALOG[plan]?.features.has(featureKey) ?? false;
}

export function requiredPlanForFeature(featureKey: string): LicensePlan | undefined {
  if (PLAN_CATALOG.TABLET_SOLO.features.has(featureKey)) return "TABLET_SOLO";
  if (PLAN_CATALOG.TABLET_PRO.features.has(featureKey)) return "TABLET_PRO";
  if (PLAN_CATALOG.TABLET_PC_REQUIRED.features.has(featureKey)) return "TABLET_PC_REQUIRED";
  return undefined;
}
