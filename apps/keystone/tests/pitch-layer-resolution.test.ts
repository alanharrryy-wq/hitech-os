import { describe, expect, it } from "vitest";
import { resolvePitchLayerFlags, resolvePitchSearchParams } from "../lib/pitch/layer-resolution";

describe("pitch layer resolution", () => {
  it("resolves query overrides from async searchParams input", async () => {
    const resolvedSearchParams = await resolvePitchSearchParams(
      Promise.resolve({
        layers: "stage.haze,stage.vignette",
        motion: "off"
      })
    );

    const resolved = resolvePitchLayerFlags(resolvedSearchParams);

    expect(resolved.baseSource).toBe("layers");
    expect(resolved.flags["stage.haze"]).toBe(true);
    expect(resolved.flags["stage.vignette"]).toBe(true);
    expect(resolved.flags["stage.noise"]).toBe(false);
    expect(resolved.flags["motion.enabled"]).toBe(false);
  });

  it("keeps pitch default profile when no URL overrides exist", async () => {
    const resolvedSearchParams = await resolvePitchSearchParams(undefined);
    const resolved = resolvePitchLayerFlags(resolvedSearchParams);

    expect(resolved.flags["stage.haze"]).toBe(true);
    expect(resolved.flags["stage.noise"]).toBe(true);
    expect(resolved.flags["motion.enabled"]).toBe(true);
  });
});
