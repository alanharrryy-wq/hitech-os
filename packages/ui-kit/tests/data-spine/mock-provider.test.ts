import { describe, expect, it } from "vitest";
import { createMockProvider } from "../../src/data-spine/providers/mock.js";
import { createSpine } from "../../src/data-spine/spine.js";

describe("mock provider", () => {
  it("returns deterministic payloads for equal seed", async () => {
    const spine = createSpine({
      defaultProviderId: "mock",
      providers: [createMockProvider()]
    });

    const first = await spine.query({
      providerId: "mock",
      datasetId: "kpi-revenue-12m",
      dataShapeId: "timeSeries",
      seed: "seed-42"
    });

    const second = await spine.query({
      providerId: "mock",
      datasetId: "kpi-revenue-12m",
      dataShapeId: "timeSeries",
      seed: "seed-42",
      forceRefresh: true
    });

    expect(second.data).toEqual(first.data);
    expect(second.determinism?.seed).toBe("seed-42");
  });

  it("changes output when seed changes", async () => {
    const spine = createSpine({
      defaultProviderId: "mock",
      providers: [createMockProvider()]
    });

    const alpha = await spine.query({
      providerId: "mock",
      datasetId: "kpi-revenue-12m",
      dataShapeId: "timeSeries",
      seed: "alpha"
    });

    const beta = await spine.query({
      providerId: "mock",
      datasetId: "kpi-revenue-12m",
      dataShapeId: "timeSeries",
      seed: "beta",
      forceRefresh: true
    });

    expect(beta.data).not.toEqual(alpha.data);
  });

  it("reduces generated cardinality in perf profile", async () => {
    const spine = createSpine({
      defaultProviderId: "mock",
      providers: [createMockProvider()]
    });

    const normal = await spine.query({
      providerId: "mock",
      dataShapeId: "timeSeries",
      seed: "perf-check"
    });

    const perf = await spine.query({
      providerId: "mock",
      dataShapeId: "timeSeries",
      seed: "perf-check",
      perfProfile: "perf",
      forceRefresh: true
    });

    const normalPoints = (normal.data as { points: readonly unknown[] }).points.length;
    const perfPoints = (perf.data as { points: readonly unknown[] }).points.length;

    expect(perfPoints).toBeLessThan(normalPoints);
  });
});

