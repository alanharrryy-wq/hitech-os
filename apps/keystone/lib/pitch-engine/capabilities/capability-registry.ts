import type { CapabilityCatalogEntry, CapabilityMode, CapabilityName, CapabilityQuerySpec } from "./capability-types.js";

export const CAPABILITY_MODES: readonly CapabilityMode[] = ["off", "lite", "full", "debug"];

const DIRECTOR_ENTRY: CapabilityCatalogEntry = {
  capability: "director",
  modes: CAPABILITY_MODES,
  defaultMode: "off",
  owner: "keystone/pitch-engine",
  description: "Controls deterministic director timeline sequencing"
};

const QUERY_SPEC: Readonly<Record<CapabilityName, CapabilityQuerySpec>> = {
  director: {
    queryKey: "capDirector",
    envKey: "PITCH_CAP_DIRECTOR",
    storageKey: "pitch.capability.director"
  }
};

export interface CapabilityRegistrySnapshot {
  readonly schemaVersion: 1;
  readonly capabilities: readonly CapabilityCatalogEntry[];
  readonly querySpec: Readonly<Record<CapabilityName, CapabilityQuerySpec>>;
}

const SNAPSHOT: CapabilityRegistrySnapshot = {
  schemaVersion: 1,
  capabilities: [DIRECTOR_ENTRY],
  querySpec: QUERY_SPEC
};

export function getCapabilityRegistry(): CapabilityRegistrySnapshot {
  return SNAPSHOT;
}

export function getCapabilityCatalogEntry(capability: CapabilityName): CapabilityCatalogEntry {
  const found = SNAPSHOT.capabilities.find((entry) => entry.capability === capability);
  if (!found) {
    throw new Error(`Unknown capability '${capability}'`);
  }
  return found;
}

export function isCapabilityMode(value: string): value is CapabilityMode {
  return CAPABILITY_MODES.includes(value as CapabilityMode);
}

export function getCapabilityQuerySpec(capability: CapabilityName): CapabilityQuerySpec {
  return SNAPSHOT.querySpec[capability];
}
