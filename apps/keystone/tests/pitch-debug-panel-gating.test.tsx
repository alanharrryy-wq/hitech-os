import { afterAll, beforeEach, describe, expect, it } from "vitest";
import {
  countInHtml,
  PITCH_CANONICAL_ROUTES,
  renderPitchRoute,
  resetNavigationMockState
} from "./_utils/pitch-test-harness";

const ORIGINAL_NODE_ENV = process.env["NODE_ENV"];

describe("pitch debug panel gating", () => {
  beforeEach(() => {
    process.env["NODE_ENV"] = "test";
    resetNavigationMockState();
  });

  afterAll(() => {
    if (ORIGINAL_NODE_ENV === undefined) {
      delete process.env["NODE_ENV"];
      return;
    }
    process.env["NODE_ENV"] = ORIGINAL_NODE_ENV;
  });

  it("does not render debug panel when debug query is missing", () => {
    for (const route of PITCH_CANONICAL_ROUTES) {
      const html = renderPitchRoute(route);
      expect(html).not.toContain("Layer Toggle Debugging");
      expect(html).not.toContain('aria-label="Layer Debug Panel"');
    }
  });

  it("renders debug panel when debug=1 outside production", () => {
    for (const route of PITCH_CANONICAL_ROUTES) {
      const html = renderPitchRoute(route, "debug=1");
      expect(html).toContain("Layer Toggle Debugging");
      expect(html).toContain('aria-label="Layer Debug Panel"');
      expect(html).toContain("source=default");
      expect(html).toContain("profile=neutral");
    }
  });

  it("hides debug panel in production even with debug=1", () => {
    process.env["NODE_ENV"] = "production";

    for (const route of PITCH_CANONICAL_ROUTES) {
      const html = renderPitchRoute(route, "debug=1&layers=all");
      expect(html).not.toContain("Layer Toggle Debugging");
      expect(countInHtml(html, 'aria-label="Layer Debug Panel"')).toBe(0);
    }
  });
});
