import { describe, expect, it } from "vitest";
import {
  buildSceneStudioRunnerArgs,
  parseSceneStudioRunPayload
} from "../app/api/scene-studio/run/run-contract";

describe("scene studio run payload contract", () => {
  it("applies deterministic defaults for debug API runs", () => {
    const parsed = parseSceneStudioRunPayload({});
    expect(parsed.ok).toBe(true);

    if (!parsed.ok) {
      return;
    }

    expect(parsed.payload.mode).toBe("smoke");
    expect(parsed.payload.serverMode).toBe("dev");
    expect(parsed.payload.timeoutMs).toBe(300_000);
    expect(parsed.payload.sceneIds).toEqual([]);
  });

  it("rejects malformed payload fields", () => {
    const parsed = parseSceneStudioRunPayload({
      sceneIds: "pitch-01"
    });

    expect(parsed.ok).toBe(false);
    if (!parsed.ok) {
      expect(parsed.error).toContain("sceneIds");
    }
  });

  it("builds a stable runner command with advanced filters and passthrough args", () => {
    const parsed = parseSceneStudioRunPayload({
      sceneIds: ["pitch-01-double-engine-neutral-desktop"],
      tags: ["pitch", "smoke"],
      mode: "full",
      route: "/pitch/01-double-engine",
      updateBaseline: true,
      strict: true,
      strictThreshold: "0.98",
      timeoutMs: 120_000,
      passthroughArgs: ["--project=keystone-scenes"]
    });

    expect(parsed.ok).toBe(true);
    if (!parsed.ok) {
      return;
    }

    const args = buildSceneStudioRunnerArgs(
      "F:\\repos\\hitech-os\\apps\\keystone\\scripts\\scene-studio-runner.mjs",
      parsed.payload
    );

    expect(args).toEqual([
      "F:\\repos\\hitech-os\\apps\\keystone\\scripts\\scene-studio-runner.mjs",
      "--json",
      "--server-mode=dev",
      "--full",
      "--timeout-ms=120000",
      "--update-baseline",
      "--strict",
      "--strict-threshold=0.98",
      "--route=/pitch/01-double-engine",
      "--scene-id=pitch-01-double-engine-neutral-desktop",
      "--tag=pitch",
      "--tag=smoke",
      "--",
      "--project=keystone-scenes"
    ]);
  });
});
