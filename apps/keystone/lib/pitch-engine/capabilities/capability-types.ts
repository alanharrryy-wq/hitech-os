import type { DirectorCapabilityMode } from "../contracts/program-types.js";

export type CapabilityName = "director";
export type CapabilityMode = DirectorCapabilityMode;

export type CapabilitySource = "env" | "query" | "localStorage" | "defaults";

export interface CapabilityCatalogEntry {
  readonly capability: CapabilityName;
  readonly modes: readonly CapabilityMode[];
  readonly defaultMode: CapabilityMode;
  readonly owner: string;
  readonly description: string;
}

export interface CapabilityAuditEvent {
  readonly source: CapabilitySource;
  readonly value: CapabilityMode | null;
  readonly selected: boolean;
  readonly notes?: string;
}

export interface CapabilityResolution {
  readonly capability: CapabilityName;
  readonly requested: CapabilityMode;
  readonly applied: CapabilityMode;
  readonly reasons: readonly string[];
  readonly auditTrail: readonly CapabilityAuditEvent[];
}

export interface CapabilityResolutionInput {
  readonly defaults: Partial<Record<CapabilityName, CapabilityMode>>;
  readonly env?: Readonly<Record<string, string | undefined>>;
  readonly query?: URLSearchParams | Readonly<Record<string, string | undefined>>;
  readonly localStorage?: CapabilityStorage;
  readonly nodeEnv?: string;
}

export interface CapabilityStorage {
  readonly getItem: (key: string) => string | null;
}

export interface CapabilityQuerySpec {
  readonly queryKey: string;
  readonly envKey: string;
  readonly storageKey: string;
}
