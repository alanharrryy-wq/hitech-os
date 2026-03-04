import {
  evaluateSceneStudioAccess,
  hasDebugToken,
  parseCapabilityMode,
  evaluateClientCapability
} from "../../lib/scene-studio/scene-access";

describe("scene access gate", () => {
  it("parses valid capability modes and falls back to off", () => {
    expect(parseCapabilityMode("debug")).toBe("debug");
    expect(parseCapabilityMode("lite")).toBe("lite");
    expect(parseCapabilityMode("invalid")).toBe("off");
    expect(parseCapabilityMode(null)).toBe("off");
  });

  it("detects debug token values", () => {
    expect(hasDebugToken("1")).toBe(true);
    expect(hasDebugToken("true")).toBe(true);
    expect(hasDebugToken("0")).toBe(false);
    expect(hasDebugToken(undefined)).toBe(false);
  });

  it("blocks access in production", () => {
    const result = evaluateSceneStudioAccess({
      debugToken: true,
      envOverride: true,
      requestedMode: "debug",
      isProductionBuild: true
    });

    expect(result.allowed).toBe(false);
    expect(result.capability.appliedMode).toBe("off");
    expect(result.capability.degradeReasons).toContain("production");
  });

  it("allows access in dev with debug token and non-off mode", () => {
    const result = evaluateSceneStudioAccess({
      debugToken: true,
      envOverride: false,
      requestedMode: "full",
      isProductionBuild: false
    });

    expect(result.allowed).toBe(true);
    expect(result.capability.appliedMode).toBe("full");
  });

  it("downgrades capability under reduced motion and perf pressure", () => {
    const result = evaluateClientCapability({
      requestedMode: "debug",
      debugToken: true,
      envOverride: false,
      viewportWidth: 900,
      prefersReducedMotion: true,
      lowPerf: true
    });

    expect(result.appliedMode).toBe("off");
    expect(result.degradeReasons).toEqual(
      expect.arrayContaining(["reduced-motion", "viewport", "perf"])
    );
  });
});
