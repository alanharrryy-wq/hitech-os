import { GET as rootGet } from "../../app/api/pitch-engine/route";
import { GET as capabilitiesGet } from "../../app/api/pitch-engine/capabilities/route";
import { GET as programsGet, POST as programsPost } from "../../app/api/pitch-engine/programs/route";

describe("pitch-engine api security", () => {
  it("returns 404 without debug token or capability mode", async () => {
    const response = await rootGet(new Request("http://localhost:3100/api/pitch-engine"));
    expect(response.status).toBe(404);
  });

  it("allows debug route and returns capability payload", async () => {
    const response = await capabilitiesGet(
      new Request(
        "http://localhost:3100/api/pitch-engine/capabilities?debug=1&requestedMode=debug"
      )
    );

    expect(response.status).toBe(200);
    const payload = (await response.json()) as {
      readonly requestedMode: string;
      readonly appliedMode: string;
      readonly isApiAllowed: boolean;
    };

    expect(payload.requestedMode).toBe("debug");
    expect(payload.isApiAllowed).toBe(true);
  });

  it("supports program create and list endpoints", async () => {
    const create = await programsPost(
      new Request("http://localhost:3100/api/pitch-engine/programs?debug=1", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({
          action: "create",
          name: "API Test Program",
          description: "created in vitest",
          owner: "test-suite"
        })
      })
    );

    expect(create.status).toBe(201);

    const list = await programsGet(
      new Request("http://localhost:3100/api/pitch-engine/programs?debug=1", {
        method: "GET"
      })
    );

    expect(list.status).toBe(200);
    const payload = (await list.json()) as Array<{ readonly name: string }>;
    expect(payload.some((program) => program.name === "API Test Program")).toBe(true);
  });
});
