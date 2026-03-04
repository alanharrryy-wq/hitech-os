import { POST as triagePost } from "../../app/api/pitch-engine/triage/route";

describe("triage api", () => {
  it("writes notes for selected artifact item", async () => {
    const response = await triagePost(
      new Request("http://localhost:3100/api/pitch-engine/triage?debug=1", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({
          action: "notes",
          runId: "test-run",
          sceneId: "scene-01",
          sequenceId: "seq-01",
          notes: "triage notes from vitest"
        })
      })
    );

    expect(response.status).toBe(200);
    const payload = (await response.json()) as {
      readonly ok: boolean;
      readonly notesPath: string | null;
      readonly action: string;
    };

    expect(payload.ok).toBe(true);
    expect(payload.action).toBe("notes");
    expect(payload.notesPath).toContain("DIFF_NOTES.md");
  });
});
