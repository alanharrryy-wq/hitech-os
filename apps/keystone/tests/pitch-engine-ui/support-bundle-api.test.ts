import { POST as supportBundlePost } from "../../app/api/pitch-engine/support-bundle/route";

describe("support bundle api", () => {
  it("returns bundle payload for debug requests", async () => {
    const response = await supportBundlePost(
      new Request("http://localhost:3100/api/pitch-engine/support-bundle?debug=1", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({
          selectedProgramId: null,
          selectedSceneId: null,
          selectedSequenceId: null,
          links: ["tools/codex/runs"],
          capabilityStatus: {
            requestedMode: "debug",
            appliedMode: "debug",
            degradeReasons: [],
            isDev: true,
            isRouteAllowed: true,
            isApiAllowed: true,
            debugTokenPresent: true,
            envOverrideEnabled: false
          },
          operatorHud: {
            serverStatus: "ready",
            lastRunStatus: "ok",
            lastRunPath: "tools/codex/runs",
            lastErrorTail: null,
            lastArtifactRunId: "test",
            updatedAt: new Date().toISOString()
          },
          environment: {
            userAgent: "vitest",
            viewport: {
              width: 1280,
              height: 720,
              dpr: 1
            },
            flags: ["debug=1"]
          }
        })
      })
    );

    expect(response.status).toBe(200);

    const bundle = (await response.json()) as {
      readonly route: string;
      readonly app: string;
      readonly diagnostics: {
        readonly links: string[];
      };
    };

    expect(bundle.route).toBe("/dev/pitch-engine");
    expect(bundle.app).toBe("keystone");
    expect(bundle.diagnostics.links).toContain("tools/codex/runs");
  });
});
