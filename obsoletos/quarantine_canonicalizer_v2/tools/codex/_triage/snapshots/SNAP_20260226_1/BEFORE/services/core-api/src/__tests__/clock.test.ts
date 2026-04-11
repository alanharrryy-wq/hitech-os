import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createCoreClock } from "../lib/clock.ts";

describe("createCoreClock", () => {
  it("uses fixed deterministic timestamp when provided", () => {
    const clock = createCoreClock("2026-01-01T05:00:00-05:00");
    assert.equal(clock.source, "fixed");
    assert.equal(clock.nowUtcIso(), "2026-01-01T10:00:00.000Z");
    assert.equal(clock.nowUtcIso(), "2026-01-01T10:00:00.000Z");
  });

  it("falls back to system clock when fixed value is invalid", () => {
    const clock = createCoreClock("invalid-date");
    assert.equal(clock.source, "system");
    assert.equal(Number.isNaN(new Date(clock.nowUtcIso()).getTime()), false);
  });
});
