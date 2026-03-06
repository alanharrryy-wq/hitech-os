import { describe, expect, it } from "vitest";
import { canStartFloatingWindowDrag } from "../app/dev/scene-studio/floating-window-drag-policy";

describe("floating window drag policy", () => {
  it("allows drag when the path includes a delegated drag handle and no interactive descendants", () => {
    const allowed = canStartFloatingWindowDrag([
      { tagName: "DIV" },
      { tagName: "DIV", dragHandle: true },
      { tagName: "DIV" }
    ]);

    expect(allowed).toBe(true);
  });

  it("blocks drag for interactive descendants inside a drag handle", () => {
    const allowed = canStartFloatingWindowDrag([
      { tagName: "SPAN" },
      { tagName: "BUTTON" },
      { tagName: "DIV", dragHandle: true },
      { tagName: "DIV" }
    ]);

    expect(allowed).toBe(false);
  });

  it("blocks drag when a no-drag ancestor is present", () => {
    const allowed = canStartFloatingWindowDrag([
      { tagName: "DIV" },
      { tagName: "DIV", noDrag: true },
      { tagName: "DIV", dragHandle: true },
      { tagName: "DIV" }
    ]);

    expect(allowed).toBe(false);
  });

  it("requires at least one drag handle in the path", () => {
    const allowed = canStartFloatingWindowDrag([{ tagName: "DIV" }, { tagName: "DIV" }]);

    expect(allowed).toBe(false);
  });
});
