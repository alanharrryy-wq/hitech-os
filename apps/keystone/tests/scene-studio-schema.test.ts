import { describe, expect, it } from "vitest";
import {
  buildCanonicalSceneQuery,
  inferLayersFromQuery,
  migrateScene,
  normalizeSceneInput,
  parseSceneUrlState,
  resolveSceneQueryPrecedence,
  validateScene
} from "../lib/scene-studio";

describe("scene studio schema + url contracts", () => {
  it("validates canonical scene payloads", () => {
    const normalized = normalizeSceneInput({
      id: "pitch-02-layered",
      title: "Pitch 02 Layered",
      route: "/pitch/02-industrial-flow",
      query: "motion=off&layers=stage.vignette,stage.haze",
      viewport: { preset: "desktop" },
      layerProfile: "neutral",
      layers: {
        mode: "list",
        layerIds: ["stage.haze", "stage.vignette"]
      },
      motion: "off",
      tags: ["pitch", "02"],
      createdAt: "2026-03-03T00:00:00.000Z",
      updatedAt: "2026-03-03T00:00:00.000Z"
    });

    const result = validateScene({
      schemaVersion: 2,
      ...normalized
    });

    expect(result.ok).toBe(true);
    expect(result.scene?.query).toBe("layers=stage.vignette,stage.haze&motion=off");
  });

  it("migrates legacy v1 scenes into v2", () => {
    const migrated = migrateScene({
      schemaVersion: 1,
      id: "Legacy Scene",
      title: "Legacy",
      route: "pitch/02-industrial-flow",
      viewport: "mobile",
      layers: ["stage.haze", "stage.vignette", "unknown.layer"],
      layerProfile: "fx",
      motion: "off"
    });

    expect(migrated.migrated).toBe(true);
    expect(migrated.scene.id).toBe("legacy-scene");
    expect(migrated.scene.route).toBe("/pitch/02-industrial-flow");
    expect(migrated.scene.layers.mode).toBe("list");
    expect(migrated.scene.layers.layerIds).toEqual(["stage.haze", "stage.vignette"]);
  });

  it("keeps URL precedence deterministic with layers override winning", () => {
    const query = buildCanonicalSceneQuery({
      route: "/pitch/02-industrial-flow",
      query: "foo=1",
      layerProfile: "fx",
      layersMode: "list",
      layerIds: ["stage.haze", "stage.vignette"],
      motion: "off",
      debug: true
    });

    expect(query).toBe("layers=stage.haze,stage.vignette&layerProfile=fx&motion=off&debug=1&foo=1");

    const parsed = parseSceneUrlState("/pitch/02-industrial-flow", query);
    expect(parsed.layersMode).toBe("list");
    expect(parsed.layerIds).toEqual(["stage.haze", "stage.vignette"]);

    const resolved = resolveSceneQueryPrecedence({
      route: parsed.route,
      query: parsed.query,
      layerProfile: parsed.layerProfile,
      layersMode: parsed.layersMode,
      layerIds: parsed.layerIds,
      motion: parsed.motion,
      debug: parsed.debug
    });

    expect(resolved.baseSource).toBe("layers");
    expect(resolved.flags["stage.haze"]).toBe(true);
    expect(resolved.flags["motion.enabled"]).toBe(false);
  });

  it("captures unknown layer tokens without poisoning known layers", () => {
    const parsed = inferLayersFromQuery("layers=stage.haze,unknown.layer,motion.enabled");

    expect(parsed.mode).toBe("list");
    expect(parsed.layerIds).toEqual(["stage.haze"]);
    expect(parsed.unknownLayerTokens).toEqual(["unknown.layer"]);
    expect(parsed.motionAliasOn).toBe(true);
  });
});
