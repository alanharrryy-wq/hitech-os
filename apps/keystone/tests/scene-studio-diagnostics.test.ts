import { describe, expect, it } from "vitest";
import { createAllLayersOff } from "@hitech/ui-kit";
import { buildSceneDiagnosticsPayload } from "../lib/scene-studio";

describe("scene diagnostics payload", () => {
  it("builds deterministic payload shape", () => {
    const flags = createAllLayersOff();
    flags["stage.haze"] = true;

    const payload = buildSceneDiagnosticsPayload({
      requestId: "req-1",
      pathname: "/pitch/02-industrial-flow",
      search: "layers=stage.haze&motion=off",
      resolved: {
        source: "layers",
        baseSource: "layers",
        motionSource: "motion",
        profile: "neutral",
        flags,
        unknownTokens: ["unknown.layer"]
      },
      enabledLayerIds: ["stage.haze"],
      domDataAttributes: {
        "data-layer-stage-haze": "1"
      },
      missingDataAttributes: [],
      sceneReady: "1",
      userAgent: "vitest",
      timestamp: "2026-03-03T00:00:00.000Z"
    });

    expect(payload).toMatchObject({
      requestId: "req-1",
      route: "/pitch/02-industrial-flow",
      query: "layers=stage.haze&motion=off",
      timestamp: "2026-03-03T00:00:00.000Z",
      resolved: {
        source: "layers",
        profile: "neutral"
      },
      enabledLayerIds: ["stage.haze"],
      unknownTokens: ["unknown.layer"],
      sceneReady: "1"
    });

    flags["stage.haze"] = false;
    expect(payload.resolved.flags["stage.haze"]).toBe(true);
  });
});
