import { describe, expect, it } from "vitest";

import { createTimelineEntries, ensureRecordState, normalizePreviewFields } from "@/lib/ui/record-contracts";
import { createRuntimeUiContext } from "@/lib/ui/runtime";

describe("ui additive contracts", () => {
  it("falls back to safe record state", () => {
    expect(ensureRecordState("approved")).toBe("approved");
    expect(ensureRecordState("weird-state")).toBe("draft");
  });

  it("normalizes preview fields and removes bad entries", () => {
    expect(
      normalizePreviewFields([
        { label: "Owner", value: "Ada" },
        { label: "Owner", value: "Grace" },
        { label: "", value: "bad" },
        { nope: true }
      ])
    ).toEqual([{ label: "Owner", value: "Ada" }]);
  });

  it("creates timeline entries sorted by freshest item first", () => {
    const entries = createTimelineEntries({
      submissions: [{ id: "s1", recordId: "r1", payload: { a: 1 }, createdAt: new Date("2026-01-01T00:00:00Z") } as never],
      dispatchJobs: [{ id: "d1", recordId: "r1", adapterId: "webhook", status: "succeeded", payload: {}, attempts: 1, createdAt: new Date("2026-01-02T00:00:00Z"), updatedAt: new Date("2026-01-02T00:00:00Z") } as never]
    });

    expect(entries[0]?.id).toBe("dispatch:d1");
    expect(entries[1]?.id).toBe("submission:s1");
  });

  it("builds runtime context with safe defaults", () => {
    const context = createRuntimeUiContext({ area: "flow", motion: "reduced" });
    expect(context.area).toBe("flow");
    expect(context.motion).toBe("reduced");
    expect(context.density).toBe("spacious");
  });
});
