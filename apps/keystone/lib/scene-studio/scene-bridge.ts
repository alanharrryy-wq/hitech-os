import type { LayerFlags, LayerId, LayerResolutionSource } from "@hitech/ui-kit";

export const SCENE_STUDIO_BRIDGE_NAMESPACE = "keystone:scene-studio";
export const SCENE_STUDIO_REQUEST_DIAGNOSTICS = `${SCENE_STUDIO_BRIDGE_NAMESPACE}:request-diagnostics`;
export const SCENE_STUDIO_RESPONSE_DIAGNOSTICS = `${SCENE_STUDIO_BRIDGE_NAMESPACE}:response-diagnostics`;

export interface SceneDiagnosticsResolved {
  readonly source: LayerResolutionSource;
  readonly baseSource: "default" | "profile" | "layers";
  readonly motionSource: "default" | "profile" | "layers" | "motion";
  readonly profile: "neutral" | "fx" | "perf";
  readonly flags: LayerFlags;
  readonly unknownTokens: readonly string[];
}

export interface SceneDiagnosticsPayload {
  readonly requestId: string;
  readonly route: string;
  readonly query: string;
  readonly timestamp: string;
  readonly resolved: SceneDiagnosticsResolved;
  readonly enabledLayerIds: readonly LayerId[];
  readonly unknownTokens: readonly string[];
  readonly domDataAttributes: Readonly<Record<string, string>>;
  readonly missingDataAttributes: readonly string[];
  readonly sceneReady: string | null;
  readonly userAgent: string;
}

export interface SceneStudioDiagnosticsRequest {
  readonly type: typeof SCENE_STUDIO_REQUEST_DIAGNOSTICS;
  readonly requestId: string;
}

export interface SceneStudioDiagnosticsResponse {
  readonly type: typeof SCENE_STUDIO_RESPONSE_DIAGNOSTICS;
  readonly payload: SceneDiagnosticsPayload;
}

export type SceneStudioBridgeMessage =
  | SceneStudioDiagnosticsRequest
  | SceneStudioDiagnosticsResponse;

export function isDiagnosticsRequestMessage(data: unknown): data is SceneStudioDiagnosticsRequest {
  if (!data || typeof data !== "object") {
    return false;
  }

  const candidate = data as Partial<SceneStudioDiagnosticsRequest>;
  return candidate.type === SCENE_STUDIO_REQUEST_DIAGNOSTICS && typeof candidate.requestId === "string";
}

export function isDiagnosticsResponseMessage(data: unknown): data is SceneStudioDiagnosticsResponse {
  if (!data || typeof data !== "object") {
    return false;
  }

  const candidate = data as Partial<SceneStudioDiagnosticsResponse>;
  return candidate.type === SCENE_STUDIO_RESPONSE_DIAGNOSTICS && Boolean(candidate.payload);
}

export function isAllowedSceneStudioOrigin(origin: string): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  return origin === window.location.origin;
}
