import { PITCH_ROUTES, PITCH_SCREEN_ORDER } from "@hitech/contracts";
import { beforeEach, describe, expect, it } from "vitest";
import {
  countInHtml,
  getNavigationReplaceCalls,
  normalizeHtml,
  PITCH_CANONICAL_ROUTES,
  renderPitchRoute,
  resetNavigationMockState,
  setNavigationMockState,
  toSearchParamsLike
} from "./_utils/pitch-test-harness";

describe("pitch test harness", () => {
  beforeEach(() => {
    resetNavigationMockState();
  });

  it("converts query-like inputs into SearchParamsLike records", () => {
    expect(toSearchParamsLike(undefined)).toEqual({});

    const fromString = toSearchParamsLike("?layers=all&debug=1&layerProfile=fx");
    expect(fromString).toEqual({
      layers: "all",
      debug: "1",
      layerProfile: "fx"
    });

    const fromParams = toSearchParamsLike(
      new URLSearchParams("layers=stage.haze&layers=stage.vignette&debug=1")
    );
    expect(fromParams).toEqual({
      layers: ["stage.haze", "stage.vignette"],
      debug: "1"
    });

    const fromRecord = toSearchParamsLike({
      debug: "1",
      layers: ["stage.haze", "stage.vignette"]
    });
    expect(fromRecord).toEqual({
      debug: "1",
      layers: ["stage.haze", "stage.vignette"]
    });
  });

  it("keeps route rendering deterministic for the same input", () => {
    const first = renderPitchRoute("/pitch/01-double-engine", "debug=1&layers=all");
    const second = renderPitchRoute("/pitch/01-double-engine", "layers=all&debug=1");

    expect(normalizeHtml(first)).toBe(normalizeHtml(second));
    expect(first).toContain("Layer Toggle Debugging");
    expect(first).toContain("source=layers");
    expect(first).toContain("enabled=13");
  });

  it("tracks and resets navigation mock state", () => {
    setNavigationMockState("/pitch/03-hitech-os", "debug=1");
    expect(getNavigationReplaceCalls()).toHaveLength(0);

    renderPitchRoute("/pitch/03-hitech-os", "debug=1");
    expect(getNavigationReplaceCalls()).toHaveLength(0);

    resetNavigationMockState();
    expect(getNavigationReplaceCalls()).toHaveLength(0);
  });

  it("includes canonical routes aligned with contracts", () => {
    expect(PITCH_CANONICAL_ROUTES[0]).toBe("/pitch");
    expect(PITCH_CANONICAL_ROUTES.slice(1)).toEqual(PITCH_SCREEN_ORDER.map((slug) => PITCH_ROUTES[slug]));
  });

  it("counts deterministic string occurrences in rendered markup", () => {
    const html = renderPitchRoute("/pitch");
    expect(countInHtml(html, "href=\"/pitch/")).toBe(PITCH_SCREEN_ORDER.length * 2);
  });
});
