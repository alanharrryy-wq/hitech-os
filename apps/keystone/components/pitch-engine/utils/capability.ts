import type {
  CapabilityEvaluationInput,
  CapabilityEvaluationResult,
  CapabilityMode,
  CapabilityStatus,
  PitchEngineUiState
} from "../types";

function downgradeMode(mode: CapabilityMode): CapabilityMode {
  if (mode === "debug") {
    return "full";
  }
  if (mode === "full") {
    return "lite";
  }
  return "off";
}

export function evaluateCapability(input: CapabilityEvaluationInput): CapabilityEvaluationResult {
  if (!input.isDevEnvironment) {
    return {
      requestedMode: input.requestedMode,
      appliedMode: "off",
      degradeReasons: ["production"]
    };
  }

  let appliedMode = input.requestedMode;
  const degradeReasons: CapabilityEvaluationResult["degradeReasons"] = [];

  if (!input.debugTokenPresent && !input.envOverrideEnabled && input.requestedMode !== "off") {
    appliedMode = "off";
    degradeReasons.push("debug-missing", "env-missing", "capability-missing");
    return {
      requestedMode: input.requestedMode,
      appliedMode,
      degradeReasons
    };
  }

  if (input.prefersReducedMotion && appliedMode !== "off") {
    appliedMode = downgradeMode(appliedMode);
    degradeReasons.push("reduced-motion");
  }

  if (input.viewportWidth < 1024 && appliedMode !== "off") {
    appliedMode = downgradeMode(appliedMode);
    degradeReasons.push("viewport");
  }

  const memoryLow = input.deviceMemoryGb !== null && input.deviceMemoryGb < 4;
  const cpuLow = input.hardwareConcurrency !== null && input.hardwareConcurrency <= 4;
  if ((memoryLow || cpuLow) && appliedMode !== "off") {
    appliedMode = downgradeMode(appliedMode);
    degradeReasons.push("perf");
  }

  if (input.requestedMode === "off" && appliedMode === "off") {
    degradeReasons.push("user-request");
  }

  return {
    requestedMode: input.requestedMode,
    appliedMode,
    degradeReasons
  };
}

export function toCapabilityStatus(input: {
  readonly evalResult: CapabilityEvaluationResult;
  readonly isDev: boolean;
  readonly debugTokenPresent: boolean;
  readonly envOverrideEnabled: boolean;
}): CapabilityStatus {
  const routeAllowed = input.isDev && input.evalResult.appliedMode !== "off";
  const apiAllowed = input.isDev && input.evalResult.appliedMode !== "off";

  return {
    requestedMode: input.evalResult.requestedMode,
    appliedMode: input.evalResult.appliedMode,
    degradeReasons: input.evalResult.degradeReasons,
    isDev: input.isDev,
    isRouteAllowed: routeAllowed,
    isApiAllowed: apiAllowed,
    debugTokenPresent: input.debugTokenPresent,
    envOverrideEnabled: input.envOverrideEnabled
  };
}

export function buildInitialUiError(state: PitchEngineUiState): string | null {
  if (!state.capabilityStatus.isDev) {
    return "Pitch Engine is only available in development mode.";
  }

  if (!state.capabilityStatus.isRouteAllowed) {
    return "Route access blocked. Provide debug=1, env override, or capability mode.";
  }

  return null;
}
