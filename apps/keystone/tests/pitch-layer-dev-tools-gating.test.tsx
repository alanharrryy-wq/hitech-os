import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { DevConsoleProvider } from "../components/dev-console/DevConsoleContext";
import { PitchLayerDevTools } from "../components/pitch/debug/pitch-layer-dev-tools";

vi.mock("@hitech/ui-kit", () => ({
  LayerDebugPanel: () => <div data-tool="layer-debug" />
}));

vi.mock("../components/pitch/debug/pitch-scene-runtime-bridge", () => ({
  PitchSceneRuntimeBridge: () => <div data-tool="runtime-bridge" />
}));

vi.mock("../components/pitch/debug/pitch-visual-scene-overlay", () => ({
  PitchVisualSceneOverlay: () => <div data-tool="visual-overlay" />
}));

vi.mock("../components/pitch/debug/pitch-share-look-button", () => ({
  PitchShareLookButton: () => <div data-tool="share-look" />
}));

describe("PitchLayerDevTools legacy HUD gating", () => {
  it("keeps legacy HUD components in non-DevConsole contexts", () => {
    const html = renderToStaticMarkup(<PitchLayerDevTools visible />);

    expect(html).toContain('data-tool="runtime-bridge"');
    expect(html).toContain('data-tool="visual-overlay"');
    expect(html).toContain('data-tool="share-look"');
    expect(html).toContain('data-tool="layer-debug"');
  });

  it("renders runtime bridge only when DevConsole is mounted", () => {
    const html = renderToStaticMarkup(
      <DevConsoleProvider>
        <PitchLayerDevTools visible />
      </DevConsoleProvider>
    );

    expect(html).toContain('data-tool="runtime-bridge"');
    expect(html).not.toContain('data-tool="visual-overlay"');
    expect(html).not.toContain('data-tool="share-look"');
    expect(html).not.toContain('data-tool="layer-debug"');
  });
});
