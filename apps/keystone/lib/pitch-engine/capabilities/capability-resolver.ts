import {
  getCapabilityCatalogEntry,
  getCapabilityQuerySpec,
  isCapabilityMode
} from "./capability-registry.js";
import type {
  CapabilityAuditEvent,
  CapabilityMode,
  CapabilityName,
  CapabilityResolution,
  CapabilityResolutionInput
} from "./capability-types.js";

function readQueryValue(
  query: CapabilityResolutionInput["query"],
  key: string
): string | undefined {
  if (!query) {
    return undefined;
  }

  if (typeof (query as URLSearchParams).get === "function") {
    return (query as URLSearchParams).get(key) ?? undefined;
  }

  return query[key];
}

function normalizeMode(value: string | undefined | null): CapabilityMode | null {
  if (!value) {
    return null;
  }

  const normalized = value.trim();
  if (!isCapabilityMode(normalized)) {
    return null;
  }

  return normalized;
}

function resolveRequestedMode(
  capability: CapabilityName,
  input: CapabilityResolutionInput
): {
  readonly requested: CapabilityMode;
  readonly auditTrail: readonly CapabilityAuditEvent[];
} {
  const entry = getCapabilityCatalogEntry(capability);
  const spec = getCapabilityQuerySpec(capability);

  const envValue = normalizeMode(input.env?.[spec.envKey]);
  const queryValue = normalizeMode(readQueryValue(input.query, spec.queryKey));
  const localStorageValue = normalizeMode(input.localStorage?.getItem(spec.storageKey) ?? undefined);
  const defaultValue = normalizeMode(input.defaults[capability] ?? entry.defaultMode) ?? entry.defaultMode;

  const auditCandidates: CapabilityAuditEvent[] = [
    {
      source: "env",
      value: envValue,
      selected: false,
      notes: envValue ? "env override candidate" : "env missing"
    },
    {
      source: "query",
      value: queryValue,
      selected: false,
      notes: queryValue ? "query override candidate" : "query missing"
    },
    {
      source: "localStorage",
      value: localStorageValue,
      selected: false,
      notes: localStorageValue ? "localStorage override candidate" : "localStorage missing"
    },
    {
      source: "defaults",
      value: defaultValue,
      selected: false,
      notes: "defaults fallback"
    }
  ];

  const winner = envValue ?? queryValue ?? localStorageValue ?? defaultValue;

  const sourceOrder: readonly ["env" | "query" | "localStorage" | "defaults", CapabilityMode | null][] = [
    ["env", envValue],
    ["query", queryValue],
    ["localStorage", localStorageValue],
    ["defaults", defaultValue]
  ];

  const selectedSource = sourceOrder.find((candidate) => candidate[1] !== null)?.[0] ?? "defaults";

  const auditTrail = auditCandidates.map((event) => ({
    ...event,
    selected: event.source === selectedSource
  }));

  return {
    requested: winner,
    auditTrail
  };
}

export function resolveCapability(
  capability: CapabilityName,
  input: CapabilityResolutionInput
): CapabilityResolution {
  const reasons: string[] = [];
  const { requested, auditTrail } = resolveRequestedMode(capability, input);

  let applied = requested;

  if ((input.nodeEnv ?? process.env.NODE_ENV) === "production") {
    if (applied !== "off") {
      reasons.push("production-hard-gate");
    }
    applied = "off";
  }

  if (applied !== requested) {
    reasons.push(`resolved-${requested}-to-${applied}`);
  }

  if (reasons.length === 0) {
    reasons.push("requested-equals-applied");
  }

  return {
    capability,
    requested,
    applied,
    reasons,
    auditTrail
  };
}

export function resolveDirectorCapability(input: CapabilityResolutionInput): CapabilityResolution {
  return resolveCapability("director", input);
}

export function buildCapabilityResolverInput(params: {
  defaults?: CapabilityResolutionInput["defaults"];
  query?: CapabilityResolutionInput["query"];
  env?: CapabilityResolutionInput["env"];
  localStorage?: CapabilityResolutionInput["localStorage"];
  nodeEnv?: string;
}): CapabilityResolutionInput {
  return {
    defaults: params.defaults ?? { director: "off" },
    query: params.query,
    env: params.env,
    localStorage: params.localStorage,
    nodeEnv: params.nodeEnv
  };
}

export function explainCapabilityResolution(resolution: CapabilityResolution): string {
  return [
    `capability=${resolution.capability}`,
    `requested=${resolution.requested}`,
    `applied=${resolution.applied}`,
    `reasons=${resolution.reasons.join(",")}`
  ].join(" ");
}

export const CAPABILITY_PRIORITY_ORDER = ["env", "query", "localStorage", "defaults"] as const;

