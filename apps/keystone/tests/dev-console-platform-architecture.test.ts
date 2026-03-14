import { describe, expect, it } from "vitest";
import { buildDevConsoleRegistry } from "../components/dev-console/DevConsoleRegistry";
import { DEFAULT_SCENE_LOOK_MODEL, mergeSceneLookModel, sceneLookModelToDatasetEntries } from "../components/dev-console/look";
import { DEV_CONSOLE_EVENT_CONTRACTS } from "../components/dev-console/console-core/console-core-contracts";
import { BRIDGE_HEARTBEAT_MS } from "../components/pitch/debug/pitch-scene-runtime-bridge";

describe("Dev Console hardened platform architecture", () => {
  it("declares both InspectConsole and ComposeConsole panel domains", () => {
    const registry = buildDevConsoleRegistry({
      bindings: {},
      activeTool: "home",
      setActiveTool: () => undefined,
      flags: {
        showGrid: false,
        motionEnabled: false,
        reducedMotion: false,
        showSafeAreas: false,
        showDebugLabels: false
      },
      setFlags: () => undefined
    });

    expect(registry.some((panel) => panel.domain === "inspect")).toBe(true);
    expect(registry.some((panel) => panel.domain === "compose")).toBe(true);
    expect(registry.some((panel) => panel.domain === "core")).toBe(true);
  });

  it("uses heartbeat cadence compatible with stale threshold expectations", () => {
    expect(BRIDGE_HEARTBEAT_MS).toBeGreaterThan(0);
    expect(BRIDGE_HEARTBEAT_MS).toBeLessThan(15_000);
  });

  it("applies SceneLookModel composition deterministically", () => {
    const composed = mergeSceneLookModel(DEFAULT_SCENE_LOOK_MODEL, {
      background: "cinematic",
      overlays: {
        grid: true,
        safeAreas: true
      },
      visualEffects: {
        bloom: true
      },
      motion: "reduced"
    });

    const datasets = sceneLookModelToDatasetEntries(composed);
    expect(datasets["sceneLookBackground"]).toBe("cinematic");
    expect(datasets["sceneLookOverlays"]).toContain("grid");
    expect(datasets["sceneLookOverlays"]).toContain("safe-areas");
    expect(datasets["sceneLookEffects"]).toContain("bloom");
    expect(datasets["sceneLookMotion"]).toBe("reduced");
  });

  it("defines hard action events with required consumers", () => {
    const requiredActionSymbols = new Set([
      "DEV_CONSOLE_SNAPSHOT_EVENT",
      "DEV_CONSOLE_OPEN_SCENE_EVENT",
      "DEV_CONSOLE_VALIDATE_SCENE_EVENT"
    ]);

    const actionContracts = DEV_CONSOLE_EVENT_CONTRACTS.filter((contract) =>
      requiredActionSymbols.has(contract.symbol)
    );

    expect(actionContracts).toHaveLength(3);
    for (const contract of actionContracts) {
      expect(contract.mustHaveEmitter).toBe(true);
      expect(contract.mustHaveListener).toBe(true);
    }
  });
});
