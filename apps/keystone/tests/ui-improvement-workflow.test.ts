import { describe, expect, it } from "vitest";
import { classifyVisualChange } from "../visual-tests/helpers/report.js";
import {
  buildScenePath,
  parseSceneLayerParams,
  type VisualSceneDefinition
} from "../visual-tests/helpers/scene-manifest.js";

describe("ui improvement workflow helpers", () => {
  it("classifies pixel diff thresholds deterministically", () => {
    expect(classifyVisualChange(0)).toEqual({
      category: "NO_CHANGE",
      band: "none",
      evidenceScore: 0
    });

    expect(classifyVisualChange(0.12)).toEqual({
      category: "SMALL_CHANGE",
      band: "small",
      evidenceScore: 35
    });

    expect(classifyVisualChange(2.4)).toEqual({
      category: "SIGNIFICANT_CHANGE",
      band: "moderate",
      evidenceScore: 70
    });

    expect(classifyVisualChange(9.3)).toEqual({
      category: "SIGNIFICANT_CHANGE",
      band: "significant",
      evidenceScore: 90
    });
  });

  it("builds canonical scene path and extracts layer params", () => {
    const scene: VisualSceneDefinition = {
      id: "scene-a",
      route: "/pitch/02-industrial-flow",
      viewport: "desktop",
      query: "debug=1&motion=off&layers=stage.noise",
      canonicalQuery: "layers=stage.noise&motion=off&debug=1"
    };

    expect(buildScenePath(scene)).toBe("/pitch/02-industrial-flow?layers=stage.noise&motion=off&debug=1");
    expect(parseSceneLayerParams(scene)).toEqual({
      layers: "stage.noise",
      layerProfile: "",
      motion: "off"
    });
  });
});
