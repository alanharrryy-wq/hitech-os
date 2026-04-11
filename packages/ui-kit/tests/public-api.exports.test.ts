import { describe, expect, it } from "vitest";

import * as UiKit from "../src/index";

describe("public api exports", () => {
  it("exports the package surface without being empty", () => {
    const keys = Object.keys(UiKit).sort();
    expect(keys.length).toBeGreaterThan(0);
  });

  it("exposes expected foundational exports", () => {
    expect(UiKit).toHaveProperty("Button");
    expect(UiKit).toHaveProperty("Card");
    expect(UiKit).toHaveProperty("Section");
    expect(UiKit).toHaveProperty("Text");
  });
});
