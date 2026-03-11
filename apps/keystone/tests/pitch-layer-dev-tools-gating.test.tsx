import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { DevConsoleProvider } from "../components/dev-console/DevConsoleContext";
import { PitchLayerDevTools } from "../components/pitch/debug/pitch-layer-dev-tools";

const navState = vi.hoisted(() => ({
  search: "",
  replace: vi.fn<(target: string) => void>()
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: navState.replace
  }),
  usePathname: () => "/pitch/02-industrial-flow",
  useSearchParams: () => new URLSearchParams(navState.search)
}));

vi.mock("../components/pitch/debug/pitch-scene-runtime-bridge", () => ({
  PitchSceneRuntimeBridge: () => <div data-tool="runtime-bridge" />
}));

describe("PitchLayerDevTools floating-console-only mode", () => {
  it("renders only the runtime bridge in non-DevConsole contexts", () => {
    const html = renderToStaticMarkup(<PitchLayerDevTools visible />);

    expect(html).toContain('data-tool="runtime-bridge"');
    expect(html).not.toContain("visual-overlay");
    expect(html).not.toContain("share-look");
    expect(html).not.toContain("layer-debug");
  });

  it("renders only the runtime bridge when DevConsole is mounted", () => {
    const html = renderToStaticMarkup(
      <DevConsoleProvider>
        <PitchLayerDevTools visible />
      </DevConsoleProvider>
    );

    expect(html).toContain('data-tool="runtime-bridge"');
    expect(html).not.toContain("visual-overlay");
    expect(html).not.toContain("share-look");
    expect(html).not.toContain("layer-debug");
  });
});
