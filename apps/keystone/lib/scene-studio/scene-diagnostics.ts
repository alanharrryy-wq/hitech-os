import type { LayerFlags, LayerId, ResolvedLayerFlags } from "@hitech/ui-kit";
import type { SceneDiagnosticsPayload } from "./scene-bridge";

export interface BuildSceneDiagnosticsInput {
  readonly requestId: string;
  readonly pathname: string;
  readonly search: string;
  readonly resolved: Pick<
    ResolvedLayerFlags,
    "source" | "baseSource" | "motionSource" | "profile" | "flags" | "unknownTokens"
  >;
  readonly enabledLayerIds: readonly LayerId[];
  readonly domDataAttributes: Readonly<Record<string, string>>;
  readonly missingDataAttributes: readonly string[];
  readonly sceneReady: string | null;
  readonly userAgent: string;
  readonly timestamp?: string;
}

function cloneFlags(flags: LayerFlags): LayerFlags {
  return {
    ...flags
  };
}

function normalizeQuery(search: string): string {
  if (!search) return "";
  return search.startsWith("?") ? search : `?${search}`;
}

function sortRecord(input: Readonly<Record<string, string>>): Readonly<Record<string, string>> {
  return Object.fromEntries(Object.entries(input).sort(([left], [right]) => left.localeCompare(right)));
}

function uniqueSorted(values: readonly string[]): string[] {
  return Array.from(new Set(values)).sort((left, right) => left.localeCompare(right));
}

export function buildSceneDiagnosticsPayload(input: BuildSceneDiagnosticsInput): SceneDiagnosticsPayload {
  const unknownTokens = uniqueSorted(input.resolved.unknownTokens);
  const enabledLayerIds = [...input.enabledLayerIds].sort((left, right) => left.localeCompare(right));
  const missingDataAttributes = uniqueSorted(input.missingDataAttributes);

  return {
    requestId: input.requestId,
    route: input.pathname,
    query: normalizeQuery(input.search),
    timestamp: input.timestamp ?? new Date().toISOString(),
    resolved: {
      source: input.resolved.source,
      baseSource: input.resolved.baseSource,
      motionSource: input.resolved.motionSource,
      profile: input.resolved.profile,
      flags: cloneFlags(input.resolved.flags),
      unknownTokens
    },
    enabledLayerIds,
    unknownTokens,
    domDataAttributes: sortRecord(input.domDataAttributes),
    missingDataAttributes,
    sceneReady: input.sceneReady,
    userAgent: input.userAgent
  };
}
