import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, create } from "react-test-renderer";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { resolvePitchLayerFlags } from "../lib/pitch/layer-resolution";

const navState = vi.hoisted(() => ({
  search: "",
  replace: vi.fn<(target: string) => void>()
}));

vi.mock("next/navigation", () => {
  return {
    useRouter: () => ({
      replace: navState.replace
    }),
    usePathname: () => "/pitch/02-industrial-flow",
    useSearchParams: () => new URLSearchParams(navState.search)
  };
});

(globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

interface MockDocumentElement {
  readonly attributes: Map<string, string>;
  setAttribute: (name: string, value: string) => void;
  removeAttribute: (name: string) => void;
  getAttribute: (name: string) => string | null;
  hasAttribute: (name: string) => boolean;
  getAttributeNames: () => string[];
}

function createMockDocumentElement(): MockDocumentElement {
  const attributes = new Map<string, string>();

  return {
    attributes,
    setAttribute(name, value) {
      attributes.set(name, value);
    },
    removeAttribute(name) {
      attributes.delete(name);
    },
    getAttribute(name) {
      return attributes.get(name) ?? null;
    },
    hasAttribute(name) {
      return attributes.has(name);
    },
    getAttributeNames() {
      return [...attributes.keys()];
    }
  };
}

describe("pitch layer DOM root application", () => {
  beforeEach(() => {
    navState.search = "";
    navState.replace.mockReset();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("applies query-derived layer flags to html and clears them on unmount", () => {
    const documentElement = createMockDocumentElement();
    vi.stubGlobal("document", {
      documentElement
    });

    const initialResolved = resolvePitchLayerFlags({
      layers: "card.blur,stage.noise,motion.enabled,unknown.layer",
      debug: "1"
    });

    let tree: ReturnType<typeof create> | null = null;

    act(() => {
      tree = create(
        <LayerFlagsProvider initialResolved={initialResolved}>
          <div>probe</div>
        </LayerFlagsProvider>
      );
    });

    expect(documentElement.getAttribute("data-layer-card-blur")).toBe("1");
    expect(documentElement.getAttribute("data-layer-stage-noise")).toBe("1");
    expect(documentElement.hasAttribute("data-layer-stage-scanlines")).toBe(false);
    expect(documentElement.getAttribute("data-layer-motion-enabled")).toBe("1");
    expect(documentElement.getAttribute("data-layer-source")).toBe("layers");
    expect(documentElement.getAttribute("data-layer-profile")).toBe("neutral");
    expect(initialResolved.unknownTokens).toEqual(["unknown.layer"]);

    act(() => {
      tree?.unmount();
    });

    expect(documentElement.hasAttribute("data-layer-card-blur")).toBe(false);
    expect(documentElement.hasAttribute("data-layer-stage-noise")).toBe(false);
    expect(documentElement.hasAttribute("data-layer-motion-enabled")).toBe(false);
    expect(documentElement.hasAttribute("data-layer-source")).toBe(false);
    expect(documentElement.hasAttribute("data-layer-profile")).toBe(false);
  });
});
