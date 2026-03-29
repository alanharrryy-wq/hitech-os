import { describe, expect, it, vi } from "vitest";
import { renderToString } from "react-dom/server";
import { {{COMPONENT_NAME}} } from "./{{COMPONENT_NAME}}";

describe("{{COMPONENT_NAME}}", () => {
  it("renders deterministic select options", () => {
    const html = renderToString(
      <{{COMPONENT_NAME}}
        label="L"
        value="a"
        options={[
          { value: "a", label: "A" },
          { value: "b", label: "B" }
        ]}
        onChange={vi.fn()}
      />
    );
    expect(html).toContain("<select");
    expect(html).toContain("A");
    expect(html).toContain("B");
  });
});

