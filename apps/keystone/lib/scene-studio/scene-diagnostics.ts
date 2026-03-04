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

export function buildSceneDiagnosticsPayload(
  input: BuildSceneDiagnosticsInput
): SceneDiagnosticsPayload {
  return {
    requestId: input.requestId,
    route: input.pathname,
    query: input.search,
    timestamp: input.timestamp ?? new Date().toISOString(),
    resolved: {
      source: input.resolved.source,
      baseSource: input.resolved.baseSource,
      motionSource: input.resolved.motionSource,
      profile: input.resolved.profile,
      flags: cloneFlags(input.resolved.flags),
      unknownTokens: [...input.resolved.unknownTokens]
    },
    enabledLayerIds: [...input.enabledLayerIds],
    unknownTokens: [...input.resolved.unknownTokens],
    domDataAttributes: { ...input.domDataAttributes },
    missingDataAttributes: [...input.missingDataAttributes],
    sceneReady: input.sceneReady,
    userAgent: input.userAgent
  };
}
