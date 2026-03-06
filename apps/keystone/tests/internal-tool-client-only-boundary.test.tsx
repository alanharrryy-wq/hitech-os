import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { InternalToolClientOnlyBoundary } from "../components/internal-tooling/internal-tool-client-only-boundary";

describe("InternalToolClientOnlyBoundary", () => {
  it("renders fallback during server render when enabled", () => {
    const html = renderToStaticMarkup(
      <InternalToolClientOnlyBoundary
        componentName="ToolPanelUnderTest"
        fallback={<div data-state="fallback" />}
      >
        <div data-state="children" />
      </InternalToolClientOnlyBoundary>
    );

    expect(html).toContain('data-state="fallback"');
    expect(html).not.toContain('data-state="children"');
  });

  it("renders children immediately when disabled", () => {
    const html = renderToStaticMarkup(
      <InternalToolClientOnlyBoundary componentName="ToolPanelUnderTest" enabled={false}>
        <div data-state="children" />
      </InternalToolClientOnlyBoundary>
    );

    expect(html).toContain('data-state="children"');
  });
});

