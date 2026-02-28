import { RunsQueryResponseSchema } from "@hitech/contracts";
import { GET as getRunsRoute } from "../app/api/runs/route";

describe("runs API route", () => {
  it("returns contract-valid payload", async () => {
    const response = await getRunsRoute();
    expect(response.status).toBe(200);

    const json = (await response.json()) as unknown;
    const parsed = RunsQueryResponseSchema.parse(json);

    expect(parsed.items.length).toBeGreaterThan(0);
    expect(parsed.meta.requestId.startsWith("req_")).toBe(true);
  });
});
