import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const notFoundMock = vi.fn(() => {
  throw new Error("NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound: notFoundMock
}));

describe("scene studio route access", () => {
  const env = process.env as Record<string, string | undefined>;
  const previousNodeEnv = env["NODE_ENV"];
  const previousSceneStudioEnv = env["NEXT_PUBLIC_SCENE_STUDIO"];

  beforeEach(() => {
    notFoundMock.mockClear();
    env["NEXT_PUBLIC_SCENE_STUDIO"] = "";
  });

  afterEach(() => {
    env["NODE_ENV"] = previousNodeEnv;
    env["NEXT_PUBLIC_SCENE_STUDIO"] = previousSceneStudioEnv;
  });

  it("returns notFound in production", async () => {
    env["NODE_ENV"] = "production";
    const module = await import("../app/dev/scene-studio/page");

    await expect(
      module.default({
        searchParams: { debug: "1" }
      })
    ).rejects.toThrow("NOT_FOUND");
  });

  it("requires debug query or env flag in development", async () => {
    env["NODE_ENV"] = "development";
    const module = await import("../app/dev/scene-studio/page");

    await expect(
      module.default({
        searchParams: {}
      })
    ).rejects.toThrow("NOT_FOUND");
  });

});
