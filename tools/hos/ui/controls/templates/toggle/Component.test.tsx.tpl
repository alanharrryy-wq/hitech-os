import { describe, expect, it, vi } from "vitest";
import { renderToString } from "react-dom/server";
import { {{COMPONENT_NAME}} } from "./{{COMPONENT_NAME}}";

describe("{{COMPONENT_NAME}}", () => {
  it("renders deterministic label/hint", () => {
    const html = renderToString(
      <{{COMPONENT_NAME}}
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

