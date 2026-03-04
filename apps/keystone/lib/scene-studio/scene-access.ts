import type {
  CapabilityDegradeReason,
  CapabilityMode,
  CapabilityStatus,
  SceneStudioAccessRequest,
  SceneStudioAccessResult
} from "../../components/pitch-engine/types";

export function parseCapabilityMode(value: string | null | undefined): CapabilityMode {
  if (value === "off" || value === "lite" || value === "full" || value === "debug") {
    return value;
  }

  return "off";
}

function downgrade(mode: CapabilityMode): CapabilityMode {
  if (mode === "debug") {
    return "full";
  }
  if (mode === "full") {
    return "lite";
  }
  return "off";
}

function buildCapabilityStatus(input: {
  readonly requestedMode: CapabilityMode;
  readonly debugToken: boolean;
  readonly envOverride: boolean;
  readonly isProductionBuild: boolean;
  readonly viewportWidth?: number;
  readonly prefersReducedMotion?: boolean;
  readonly lowPerf?: boolean;
}): CapabilityStatus {
  const reasons: CapabilityDegradeReason[] = [];
  let applied: CapabilityMode = input.requestedMode;

  if (input.isProductionBuild) {
    reasons.push("production");
    applied = "off";
  }

  const gateSatisfied = input.debugToken || input.envOverride || input.requestedMode !== "off";
  if (!gateSatisfied && !input.isProductionBuild) {
    reasons.push("debug-missing", "env-missing", "capability-missing");
    applied = "off";
  }

  if ((input.debugToken || input.envOverride) && applied === "off" && !input.isProductionBuild) {
    applied = "debug";
  }

  if (input.prefersReducedMotion && applied !== "off") {
    applied = downgrade(applied);
    reasons.push("reduced-motion");
  }

  if (typeof input.viewportWidth === "number" && input.viewportWidth < 1024 && applied !== "off") {
    applied = downgrade(applied);
    reasons.push("viewport");
  }

  if (input.lowPerf && applied !== "off") {
    applied = downgrade(applied);
    reasons.push("perf");
  }

  if (input.requestedMode === "off" && !input.debugToken && !input.envOverride) {
    reasons.push("user-request");
  }

  const isDev = !input.isProductionBuild;
  const allowed = isDev && applied !== "off";

  return {
    requestedMode: input.requestedMode,
    appliedMode: applied,
    degradeReasons: reasons,
    isDev,
    isRouteAllowed: allowed,
    isApiAllowed: allowed,
    debugTokenPresent: input.debugToken,
    envOverrideEnabled: input.envOverride
  };
}

export function evaluateSceneStudioAccess(request: SceneStudioAccessRequest): SceneStudioAccessResult {
  const capability = buildCapabilityStatus({
    requestedMode: request.requestedMode,
    debugToken: request.debugToken,
    envOverride: request.envOverride,
    isProductionBuild: request.isProductionBuild
  });

  return {
    allowed: capability.isRouteAllowed,
    capability
  };
}

export function evaluateClientCapability(input: {
  readonly requestedMode: CapabilityMode;
  readonly debugToken: boolean;
  readonly envOverride: boolean;
  readonly viewportWidth: number;
  readonly prefersReducedMotion: boolean;
  readonly lowPerf: boolean;
}): CapabilityStatus {
  return buildCapabilityStatus({
    ...input,
    isProductionBuild: false
  });
}

export function isProductionBuild(): boolean {
  return process.env.NODE_ENV === "production";
}

export function envOverrideEnabled(): boolean {
  return process.env.KEYSTONE_DEV_PITCH_ENGINE === "1";
}

export function hasDebugToken(value: string | null | undefined): boolean {
  return value === "1" || value === "true";
}

export function isPitchEngineDevRouteAllowed(input: {
  readonly debugToken: boolean;
  readonly requestedMode: CapabilityMode;
}): SceneStudioAccessResult {
  return evaluateSceneStudioAccess({
    debugToken: input.debugToken,
    envOverride: envOverrideEnabled(),
    requestedMode: input.requestedMode,
    isProductionBuild: isProductionBuild()
  });
}

export function isPitchEngineApiAllowed(input: {
  readonly debugToken: boolean;
  readonly requestedMode: CapabilityMode;
}): SceneStudioAccessResult {
  return evaluateSceneStudioAccess({
    debugToken: input.debugToken,
    envOverride: envOverrideEnabled(),
    requestedMode: input.requestedMode,
    isProductionBuild: isProductionBuild()
  });
}
