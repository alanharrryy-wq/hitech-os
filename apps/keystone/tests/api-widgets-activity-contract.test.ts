import { ActivityQueryResponseSchema, WidgetsQueryResponseSchema } from "@hitech/contracts";
import { GET as getActivityRoute } from "../app/api/activity/route";
import { GET as getWidgetsRoute } from "../app/api/widgets/route";

describe("widgets/activity API routes", () => {
  it("returns contract-valid widgets payload", async () => {
    const response = await getWidgetsRoute();
    expect(response.status).toBe(200);

    const json = (await response.json()) as unknown;
    const parsed = WidgetsQueryResponseSchema.parse(json);

    expect(parsed.widgets.length).toBeGreaterThan(0);
    expect(parsed.meta.requestId.startsWith("req_")).toBe(true);
  });

  it("returns contract-valid activity payload", async () => {
    const response = await getActivityRoute();
    expect(response.status).toBe(200);

    const json = (await response.json()) as unknown;
    const parsed = ActivityQueryResponseSchema.parse(json);

    expect(parsed.items.length).toBeGreaterThan(0);
    expect(parsed.meta.requestId.startsWith("req_")).toBe(true);
  });
});
