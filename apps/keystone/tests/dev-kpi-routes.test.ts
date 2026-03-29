import { validateDataShape } from "@hitech/ui-kit";
import { GET as getDatasetListRoute } from "../app/api/dev/kpi/datasets/route";
import { GET as getDatasetByIdRoute } from "../app/api/dev/kpi/datasets/[id]/route";
import { GET as getSeedRoute } from "../app/api/dev/kpi/seed/[seed]/route";

function withNodeEnv<T>(nodeEnv: string, cb: () => Promise<T>): Promise<T> {
  const env = process.env as Record<string, string | undefined>;
  const original = env["NODE_ENV"];
  env["NODE_ENV"] = nodeEnv;
  return cb().finally(() => {
    if (original === undefined) {
      env["NODE_ENV"] = undefined;
    } else {
      env["NODE_ENV"] = original;
    }
  });
}

describe("dev KPI routes", () => {
  it("lists registered datasets in non-production env", async () => {
    const response = await withNodeEnv("development", () => getDatasetListRoute());
    expect(response.status).toBe(200);

    const payload = (await response.json()) as {
      count: number;
      datasets: Array<{ datasetId: string; dataShapeId: string }>;
    };

    expect(payload.count).toBeGreaterThan(0);
    expect(payload.datasets.some((item) => item.datasetId === "kpi-revenue-12m")).toBe(true);
  });

  it("returns a validated dataset payload by id", async () => {
    const response = await withNodeEnv("development", () =>
      getDatasetByIdRoute(new Request("http://localhost/api/dev/kpi/datasets/kpi-revenue-12m"), {
        params: { id: "kpi-revenue-12m" }
      })
    );

    expect(response.status).toBe(200);

    const payload = (await response.json()) as {
      datasetId: string;
      dataShapeId: string;
      payload: unknown;
    };

    expect(payload.datasetId).toBe("kpi-revenue-12m");
    expect(() => validateDataShape(payload.dataShapeId as never, payload.payload)).not.toThrow();
  });

  it("returns deterministic seed variations", async () => {
    const first = await withNodeEnv("development", () =>
      getSeedRoute(new Request("http://localhost/api/dev/kpi/seed/seed-99"), {
        params: { seed: "seed-99" }
      })
    );

    const second = await withNodeEnv("development", () =>
      getSeedRoute(new Request("http://localhost/api/dev/kpi/seed/seed-99"), {
        params: { seed: "seed-99" }
      })
    );

    expect(first.status).toBe(200);
    expect(second.status).toBe(200);

    const payloadA = (await first.json()) as { datasets: readonly unknown[] };
    const payloadB = (await second.json()) as { datasets: readonly unknown[] };

    expect(payloadA.datasets).toEqual(payloadB.datasets);
    expect(payloadA.datasets.length).toBeGreaterThan(0);
  });

  it("gates routes in production", async () => {
    const listResponse = await withNodeEnv("production", () => getDatasetListRoute());
    expect(listResponse.status).toBe(404);

    const datasetResponse = await withNodeEnv("production", () =>
      getDatasetByIdRoute(new Request("http://localhost/api/dev/kpi/datasets/kpi-revenue-12m"), {
        params: { id: "kpi-revenue-12m" }
      })
    );
    expect(datasetResponse.status).toBe(404);

    const seedResponse = await withNodeEnv("production", () =>
      getSeedRoute(new Request("http://localhost/api/dev/kpi/seed/seed-99"), {
        params: { seed: "seed-99" }
      })
    );
    expect(seedResponse.status).toBe(404);
  });
});

