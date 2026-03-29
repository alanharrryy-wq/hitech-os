import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const notFoundMock = vi.fn(() => {
  throw new Error("NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound: notFoundMock
}));

describe("dev routes smoke", () => {
  const env = process.env as Record<string, string | undefined>;
  const previousNodeEnv = env["NODE_ENV"];
  const previousSceneStudioEnv = env["NEXT_PUBLIC_SCENE_STUDIO"];

  beforeEach(() => {
    notFoundMock.mockClear();
    env["NODE_ENV"] = "development";
    env["NEXT_PUBLIC_SCENE_STUDIO"] = "";
  });

  afterEach(() => {
    env["NODE_ENV"] = previousNodeEnv;
    env["NEXT_PUBLIC_SCENE_STUDIO"] = previousSceneStudioEnv;
  });

  it("/dev/scene-studio?debug=1 resolves", async () => {
    const module = await import("../app/dev/scene-studio/page");
    const result = await module.default({
      searchParams: { debug: "1" }
    });

    expect(result).toBeTruthy();
    expect(notFoundMock).not.toHaveBeenCalled();
  });

  it("/dev/style-lab resolves in development", async () => {
    const module = await import("../app/dev/style-lab/page");
    const result = module.default();

    expect(result).toBeTruthy();
    expect(notFoundMock).not.toHaveBeenCalled();
  });

  it("/dev/kpi-supermarket resolves in development", async () => {
    const module = await import("../app/dev/kpi-supermarket/page");
    const result = module.default();

    expect(result).toBeTruthy();
    expect(notFoundMock).not.toHaveBeenCalled();
  });
});
