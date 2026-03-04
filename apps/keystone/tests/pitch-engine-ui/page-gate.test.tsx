import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  notFound: () => {
    throw new Error("NOT_FOUND");
  }
}));

import PitchEnginePage from "../../app/dev/pitch-engine/page";

describe("pitch-engine page gate", () => {
  it("throws notFound when debug token is missing", () => {
    expect(() => PitchEnginePage({ searchParams: {} })).toThrow("NOT_FOUND");
  });

  it("renders workbench when debug token is present", () => {
    const element = PitchEnginePage({
      searchParams: {
        debug: "1",
        mode: "debug"
      }
    });

    expect(element).toBeTruthy();
  });
});
