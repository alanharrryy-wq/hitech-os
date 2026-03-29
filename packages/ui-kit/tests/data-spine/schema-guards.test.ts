import { describe, expect, it } from "vitest";
import { DataShapeGuardError, validateMatrix } from "../../src/data-spine/schema/guards.js";
import { validateDataShape } from "../../src/data-spine/schema/registry.js";

describe("data-shape guards", () => {
  it("produces human-readable matrix errors", () => {
    const result = validateMatrix({
      rows: ["A", "B"],
      columns: ["X", "Y"],
      values: [[10], [20, 30, 40]]
    });

    expect(result.ok).toBe(false);

    if (!result.ok) {
      expect(result.errors[0]?.path).toContain("matrix.values");
      expect(result.errors[0]?.message.toLowerCase()).toContain("exactly");
    }
  });

  it("throws DataShapeGuardError with details from registry validation", () => {
    expect(() =>
      validateDataShape("gauge", {
        min: 100,
        max: 50,
        value: 999
      })
    ).toThrow(DataShapeGuardError);

    try {
      validateDataShape("gauge", {
        min: 100,
        max: 50,
        value: 999
      });
    } catch (error) {
      expect(error).toBeInstanceOf(DataShapeGuardError);
      const parsed = error as DataShapeGuardError;
      expect(parsed.message).toContain("gauge");
      expect(parsed.message).toContain("min");
      expect(parsed.issues.length).toBeGreaterThan(0);
    }
  });
});


