import { useEffect } from "react";
import { describe, expect, it, beforeEach, vi } from "vitest";
import { create, act } from "react-test-renderer";
import { ALL_LAYERS, LayerFlagsProvider, useLayerFlags } from "@hitech/ui-kit";
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
    usePathname: () => "/pitch/04-valuation",
    useSearchParams: () => new URLSearchParams(navState.search)
  };
});

(globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let setProfileAction: ((profile: "neutral" | "fx" | "perf") => void) | null = null;

function CaptureLayerActions() {
  const { setProfile } = useLayerFlags();

  useEffect(() => {
    setProfileAction = setProfile;

    return () => {
      setProfileAction = null;
    };
  }, [setProfile]);

  return null;
}

describe("pitch query stability", () => {
  beforeEach(() => {
    navState.search = "";
    navState.replace.mockReset();
    setProfileAction = null;
    navState.replace.mockImplementation((target: string) => {
      const query = target.includes("?") ? target.split("?")[1] ?? "" : "";
      navState.search = query;
    });
  });

  it("does not rewrite URL on mount when query is absent", () => {
    const initialResolved = resolvePitchLayerFlags({});

    act(() => {
      create(
        <LayerFlagsProvider initialResolved={initialResolved}>
          <div>probe</div>
        </LayerFlagsProvider>
      );
    });

    expect(navState.replace).toHaveBeenCalledTimes(0);
    expect(navState.search).toBe("");
  });

  it("does not rewrite long layers query on mount", () => {
    const longLayers = ALL_LAYERS.join(",");
    navState.search = `layers=${encodeURIComponent(longLayers)}`;
    const initialResolved = resolvePitchLayerFlags({ layers: longLayers });

    act(() => {
      create(
        <LayerFlagsProvider initialResolved={initialResolved}>
          <div>probe</div>
        </LayerFlagsProvider>
      );
    });

    expect(navState.replace).toHaveBeenCalledTimes(0);
    expect(navState.search).toContain("layers=");
  });

  it("does not rewrite layerProfile=perf query on mount", () => {
    navState.search = "layerProfile=perf";
    const initialResolved = resolvePitchLayerFlags({ layerProfile: "perf" });

    act(() => {
      create(
        <LayerFlagsProvider initialResolved={initialResolved}>
          <div>probe</div>
        </LayerFlagsProvider>
      );
    });

    expect(navState.replace).toHaveBeenCalledTimes(0);
    expect(navState.search).toBe("layerProfile=perf");
  });

  it("updates URL once when user changes profile", () => {
    const initialResolved = resolvePitchLayerFlags({});

    act(() => {
      create(
        <LayerFlagsProvider initialResolved={initialResolved}>
          <CaptureLayerActions />
        </LayerFlagsProvider>
      );
    });

    act(() => {
      setProfileAction?.("perf");
    });

    expect(navState.replace).toHaveBeenCalledTimes(1);
    const [target] = navState.replace.mock.calls[0] ?? [];
    expect(target).toContain("layerProfile=perf");
  });
});
