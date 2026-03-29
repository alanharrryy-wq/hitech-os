import { describe, expect, it } from "vitest";
import { renderToString } from "react-dom/server";
import { DemoGlassCard } from "./DemoGlassCard";

describe("DemoGlassCard", () => {
  it("renders title and subtitle deterministically", () => {
    const html = renderToString(
      <DemoGlassCard title="A" subtitle="B">
        <span>Body</span>
      </DemoGlassCard>
    );
    expect(html).toContain("A");
    expect(html).toContain("B");
    expect(html).toContain("Body");
  });
});
