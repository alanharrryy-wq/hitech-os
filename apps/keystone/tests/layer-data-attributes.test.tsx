import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

vi.mock("next/navigation", () => {
  return {
    useRouter: () => ({
      replace: vi.fn()
    }),
    usePathname: () => "/pitch/01-double-engine",
    useSearchParams: () => new URLSearchParams("")
  };
});

import { LayerFlagsProvider, Stage, resolveLayerFlags } from "@hitech/ui-kit";

describe("layer data attributes", () => {
  it("enabling stage.noise sets data-layer-stage-noise=on on Stage root", () => {
    const resolved = resolveLayerFlags({ layers: "stage.noise" });

    const html = renderToStaticMarkup(
      <LayerFlagsProvider initialResolved={resolved}>
        <Stage>
          <div>content</div>
        </Stage>
      </LayerFlagsProvider>
    );

    expect(html).toContain('data-layer-stage-noise="on"');
    expect(html).toContain('data-layer-stage-scanlines="off"');
  });
});
