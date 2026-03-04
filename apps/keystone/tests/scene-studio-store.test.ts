import { describe, expect, it } from "vitest";
import { InMemorySceneStore, createDefaultSceneLibrary, serializeSceneExport } from "../lib/scene-studio";

describe("scene store", () => {
  it("supports export and merge import", () => {
    const defaults = createDefaultSceneLibrary("2026-03-03T00:00:00.000Z");
    const store = new InMemorySceneStore(defaults.slice(0, 2));

    const exported = serializeSceneExport(store.exportScenes());
    const mergeResult = store.importScenes(JSON.parse(exported), "merge");

    expect(mergeResult.errors).toEqual([]);
    expect(mergeResult.imported).toBe(2);
    expect(store.list().length).toBe(2);
  });

  it("replaces store data in replace mode", () => {
    const defaults = createDefaultSceneLibrary("2026-03-03T00:00:00.000Z");
    const store = new InMemorySceneStore(defaults.slice(0, 3));

    const payload = {
      schemaVersion: 2,
      exportedAt: "2026-03-03T00:00:00.000Z",
      scenes: [defaults[4]]
    };

    const result = store.importScenes(payload, "replace");
    expect(result.errors).toEqual([]);
    expect(store.list().length).toBe(1);
    expect(store.list()[0]?.id).toBe(defaults[4]?.id);
  });
});
