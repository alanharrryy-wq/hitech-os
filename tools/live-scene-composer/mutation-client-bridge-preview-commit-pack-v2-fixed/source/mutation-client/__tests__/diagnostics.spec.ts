import { createDiagnosticsEvent } from "../diagnostics";

describe("createDiagnosticsEvent", () => {
  it("creates stable event shape", () => {
    const event = createDiagnosticsEvent({
      category: "validation",
      level: "warn",
      message: "example"
    });
    expect(event.eventId).toContain("diagnostic-");
  });
});
