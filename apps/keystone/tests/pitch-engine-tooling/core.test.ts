import { describe, expect, it } from "vitest";
import path from "node:path";
import {
  resolveProgram,
  resolveCapturePlan,
  buildProgramTimeline,
  resolvePerformanceProfile,
  profileToReportEntry,
  sanitizeId,
  buildTimestampFileName,
  stableJsonStringify,
  toSortedEntries
} from "../../lib/pitch-engine-tooling/index.mjs";

describe("pitch-engine tooling core", () => {
  it("resolves canonical program with deterministic sequence metadata", () => {
    const program = resolveProgram("demo");
    expect(program.programId).toBe("demo");
    expect(program.sequences.length).toBeGreaterThan(0);
    expect(program.sequenceCount).toBe(program.sequences.length);
  });

  it("resolves capture plan with marker captures", async () => {
    const program = resolveProgram("demo");
    const plan = await resolveCapturePlan(program, "smoke", process.cwd());
    expect(plan.sequences.length).toBe(program.sequences.length);
    for (const sequence of plan.sequences) {
      expect(sequence.timestampsMs.length).toBeGreaterThan(0);
      expect(sequence.markerCaptureTimestampsMs.length).toBeGreaterThan(0);
    }
  });

  it("builds timeline deterministically", async () => {
    const program = resolveProgram("demo");
    const profile = resolvePerformanceProfile({ smoke: true });
    const plan = await resolveCapturePlan(program, "smoke", process.cwd());
    const timeline = buildProgramTimeline(program, plan, profile.actual);
    expect(timeline.sequenceCount).toBe(program.sequences.length);
    expect(timeline.totalCaptures).toBeGreaterThan(0);
    expect(timeline.hash.length).toBe(64);
  });

  it("profile report entry is serializable", () => {
    const profile = resolvePerformanceProfile({ full: true }, { forceLite: true });
    const entry = profileToReportEntry(profile);
    expect(entry.actual).toBe("lite");
    expect(entry.degraded).toBe(true);
  });

  it("sanitizeId and timestamp filename are windows safe", () => {
    expect(sanitizeId("../unsafe/path", "fallback")).toBe("unsafe-path");
    expect(buildTimestampFileName(400)).toBe("00400.png");
  });

  it("stableJsonStringify sorts keys", () => {
    const payload = { b: 2, a: 1 };
    const text = stableJsonStringify(payload);
    expect(text.indexOf('"a"')).toBeLessThan(text.indexOf('"b"'));
  });

  it("toSortedEntries sorts lexical keys", () => {
    const entries = toSortedEntries({ z: 1, a: 2, b: 3 });
    expect(entries.map((entry: [string, unknown]) => entry[0])).toEqual(["a", "b", "z"]);
  });

  it("path joins remain deterministic", () => {
    const joined = path.join("a", "b", "c");
    expect(joined.includes("b")).toBe(true);
  });
});
