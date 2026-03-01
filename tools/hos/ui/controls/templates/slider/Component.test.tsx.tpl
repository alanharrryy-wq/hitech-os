import { describe, expect, it, vi } from "vitest";
import { renderToString } from "react-dom/server";
import { {{COMPONENT_NAME}} } from "./{{COMPONENT_NAME}}";

describe("{{COMPONENT_NAME}}", () => {
  it("renders deterministic slider markup", () => {
    const html = renderToString(
      <{{COMPONENT_NAME}}
        label="L"
        min={0}
        max={10}
        value={5}
        step={1}
        onChange={vi.fn()}
      />
    );
    expect(html).toContain("type=\"range\"");
    expect(html).toContain("L");
  });
});

