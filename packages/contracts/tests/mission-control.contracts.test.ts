import { describe, expect, it } from "vitest";
import {
  ACTIVITY_FIXTURES,
  ACTIVITY_RESPONSE_FIXTURE,
  ActivityEventSchema,
  ActivityQueryResponseSchema,
  EVIDENCE_FIXTURES,
  EvidenceRefSchema,
  FILTER_FIXTURE_ABSOLUTE,
  FILTER_FIXTURE_DEFAULT,
  FILTER_FIXTURE_LAST_24H,
  LAYOUT_FIXTURE,
  QueryFiltersSchema,
  RUN_FIXTURES,
  RUNS_RESPONSE_FIXTURE,
  RunSummarySchema,
  RunsQueryResponseSchema,
  WIDGET_COLLECTION_FIXTURE,
  WIDGET_FIXTURES,
  WidgetCollectionSchema,
  WidgetConfigSchema,
  normalizeZodError,
  parseOrThrow,
  safeParseResult
} from "../dist/index.js";

describe("contracts fixtures", () => {
  it("validates run fixtures", () => {
    for (const fixture of RUN_FIXTURES) {
      const parsed = RunSummarySchema.parse(fixture);
      expect(parsed.id).toBe(fixture.id);
    }
  });

  it("validates evidence fixtures", () => {
    for (const fixture of EVIDENCE_FIXTURES) {
      const parsed = EvidenceRefSchema.parse(fixture);
      expect(parsed.id).toBe(fixture.id);
    }
  });

  it("validates activity fixtures", () => {
    for (const fixture of ACTIVITY_FIXTURES) {
      const parsed = ActivityEventSchema.parse(fixture);
      expect(parsed.id).toBe(fixture.id);
    }
  });

  it("validates widget fixtures", () => {
    for (const fixture of WIDGET_FIXTURES) {
      const parsed = WidgetConfigSchema.parse(fixture);
      expect(parsed.id).toBe(fixture.id);
    }

    const collection = WidgetCollectionSchema.parse(WIDGET_COLLECTION_FIXTURE);
    expect(collection.widgets.length).toBeGreaterThan(0);
  });

  it("validates layout fixture", () => {
    const parsed = parseOrThrow(WidgetCollectionSchema, WIDGET_COLLECTION_FIXTURE);
    expect(parsed.widgets.length).toBe(WIDGET_FIXTURES.length);

    expect(() => parseOrThrow(RunsQueryResponseSchema, RUNS_RESPONSE_FIXTURE)).not.toThrow();
    expect(() =>
      parseOrThrow(ActivityQueryResponseSchema, ACTIVITY_RESPONSE_FIXTURE)
    ).not.toThrow();
  });

  it("validates filter fixtures", () => {
    expect(() => QueryFiltersSchema.parse(FILTER_FIXTURE_DEFAULT)).not.toThrow();
    expect(() => QueryFiltersSchema.parse(FILTER_FIXTURE_LAST_24H)).not.toThrow();
    expect(() => QueryFiltersSchema.parse(FILTER_FIXTURE_ABSOLUTE)).not.toThrow();
  });
});

describe("contracts roundtrip", () => {
  it("roundtrips runs response payload", () => {
    const encoded = JSON.stringify(RUNS_RESPONSE_FIXTURE);
    const decoded = JSON.parse(encoded) as unknown;
    const parsed = RunsQueryResponseSchema.parse(decoded);
    expect(parsed.total).toBe(RUN_FIXTURES.length);
    expect(parsed.items[0]?.id).toBe(RUN_FIXTURES[0]?.id);
  });

  it("roundtrips activity response payload", () => {
    const encoded = JSON.stringify(ACTIVITY_RESPONSE_FIXTURE);
    const decoded = JSON.parse(encoded) as unknown;
    const parsed = ActivityQueryResponseSchema.parse(decoded);
    expect(parsed.items.length).toBe(ACTIVITY_FIXTURES.length);
  });

  it("roundtrips widgets collection payload", () => {
    const encoded = JSON.stringify(WIDGET_COLLECTION_FIXTURE);
    const decoded = JSON.parse(encoded) as unknown;
    const parsed = WidgetCollectionSchema.parse(decoded);
    expect(parsed.widgets.length).toBe(WIDGET_FIXTURES.length);
  });
});

describe("contracts invalid cases", () => {
  it("rejects invalid run status", () => {
    const invalid = {
      ...RUN_FIXTURES[0],
      status: "done"
    };

    const result = safeParseResult(RunSummarySchema, invalid);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("VALIDATION_ERROR");
      expect(result.error.status).toBe(400);
    }
  });

  it("rejects invalid widget dial bounds", () => {
    const invalidWidget = {
      ...WIDGET_FIXTURES.find((item) => item.kind === "dial-placeholder"),
      config: {
        min: 90,
        max: 40,
        value: 110,
        warningThreshold: 70,
        criticalThreshold: 85,
        unit: "%"
      }
    };

    const result = safeParseResult(WidgetConfigSchema, invalidWidget);
    expect(result.ok).toBe(false);
  });

  it("normalizes zod errors", () => {
    const parsed = RunSummarySchema.safeParse({ foo: "bar" });
    expect(parsed.success).toBe(false);

    if (!parsed.success) {
      const normalized = normalizeZodError(parsed.error);
      expect(normalized.issues.length).toBeGreaterThan(0);
      expect(normalized.message.toLowerCase()).toContain("validation failed");
    }
  });

  it("rejects invalid activity severity", () => {
    const invalid = {
      ...ACTIVITY_FIXTURES[0],
      severity: "fatal"
    };

    expect(() => ActivityEventSchema.parse(invalid)).toThrow();
  });

  it("rejects invalid query filter time range", () => {
    const invalid = {
      ...FILTER_FIXTURE_ABSOLUTE,
      timeRange: {
        type: "absolute",
        from: "2026-02-12T00:00:00.000Z",
        to: "2026-02-11T00:00:00.000Z"
      }
    };

    expect(() => QueryFiltersSchema.parse(invalid)).toThrow();
  });

  it("keeps deterministic fixture order", () => {
    const firstRunId = RUN_FIXTURES[0]?.id;
    const firstActivityId = ACTIVITY_FIXTURES[0]?.id;
    const firstWidgetId = WIDGET_FIXTURES[0]?.id;

    expect(firstRunId).toBe("run_alpha-001");
    expect(firstActivityId).toBe("act_20260215-run-alpha-created");
    expect(firstWidgetId).toBe("wid_table-001");
  });
});

describe("contract API fixtures", () => {
  it("runs response fixture is valid and paginated", () => {
    const parsed = RunsQueryResponseSchema.parse(RUNS_RESPONSE_FIXTURE);
    expect(parsed.page).toBe(1);
    expect(parsed.pageSize).toBe(25);
  });

  it("activity response fixture is valid", () => {
    const parsed = ActivityQueryResponseSchema.parse(ACTIVITY_RESPONSE_FIXTURE);
    expect(parsed.hasMore).toBe(false);
  });

  it("layout fixture stays deterministic", () => {
    expect(LAYOUT_FIXTURE.breakpoints.length).toBe(4);
    expect(LAYOUT_FIXTURE.breakpoints[0]?.breakpoint).toBe("xs");
    expect(LAYOUT_FIXTURE.breakpoints[1]?.breakpoint).toBe("sm");
    expect(LAYOUT_FIXTURE.breakpoints[2]?.breakpoint).toBe("md");
    expect(LAYOUT_FIXTURE.breakpoints[3]?.breakpoint).toBe("lg");
  });
});
