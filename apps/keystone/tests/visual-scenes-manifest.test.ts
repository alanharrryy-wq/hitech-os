import { describe, expect, it } from "vitest";
import { loadSceneManifest } from "../visual-tests/helpers/scene-manifest";

describe("visual scene manifest", () => {
  it("contains reproducible scenes with route/query/viewport", async () => {
    const scenes = await loadSceneManifest();

    expect(scenes.length).toBeGreaterThanOrEqual(8);

    for (const scene of scenes) {
      expect(scene.id.length).toBeGreaterThan(0);
      expect(scene.route.startsWith("/")).toBe(true);
      expect(["desktop", "mobile", "tablet", "custom"]).toContain(scene.viewport);
      expect(typeof scene.canonicalQuery).toBe("string");
    }
  });
});
