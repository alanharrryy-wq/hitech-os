import { describe, expect, it, vi } from "vitest";
import { renderToString } from "react-dom/server";
import { DemoToggle } from "./DemoToggle";

describe("DemoToggle", () => {
  it("renders deterministic label/hint", () => {
    const html = renderToString(
      <DemoToggle
        label="L"
        hint="H"
        checked={false}
        onChange={vi.fn()}
      />
    );
    expect(html).toContain("L");
    expect(html).toContain("H");
  });
});

