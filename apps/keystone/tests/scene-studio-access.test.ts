import { afterEach, describe, expect, it } from "vitest";
import { resolveSceneStudioAccess } from "../lib/scene-studio";

describe("scene studio access resolver", () => {
  const env = process.env as Record<string, string | undefined>;
  const previousNodeEnv = env["NODE_ENV"];
  const previousFlag = env["NEXT_PUBLIC_SCENE_STUDIO"];

  afterEach(() => {
    env["NODE_ENV"] = previousNodeEnv;
    env["NEXT_PUBLIC_SCENE_STUDIO"] = previousFlag;
  });

  it("allows development debug query", () => {
    env["NODE_ENV"] = "development";
    env["NEXT_PUBLIC_SCENE_STUDIO"] = "";

    const access = resolveSceneStudioAccess({ debug: "1" });
    expect(access.allowed).toBe(true);
  });

  it("denies production even with debug query", () => {
    env["NODE_ENV"] = "production";
    env["NEXT_PUBLIC_SCENE_STUDIO"] = "1";

    const access = resolveSceneStudioAccess({ debug: "1" });
    expect(access.allowed).toBe(false);
  });
});
