"use client";

import { exportSupportBundle } from "../api-client";
import { usePitchEngineStore, useSelectedProgram, useSelectedScene, useSelectedSequence } from "../state/use-pitch-engine-store";

function envSummary(): {
  readonly userAgent: string;
  readonly viewport: { readonly width: number; readonly height: number; readonly dpr: number };
  readonly flags: string[];
} {
  if (typeof window === "undefined") {
    return {
      userAgent: "server",
      viewport: { width: 0, height: 0, dpr: 1 },
      flags: []
    };
  }

  return {
    userAgent: navigator.userAgent,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
      dpr: window.devicePixelRatio
    },
    flags: ["debug=1", "dev-only"]
  };
}

export function SupportBundlePanel() {
  const program = useSelectedProgram();
  const scene = useSelectedScene();
  const sequence = useSelectedSequence();
  const capabilityStatus = usePitchEngineStore((state) => state.capabilityStatus);
  const operatorHud = usePitchEngineStore((state) => state.operatorHud);
  const setUiError = usePitchEngineStore((state) => state.setUiError);

  const onExport = async () => {
    try {
      const bundle = await exportSupportBundle({
        selectedProgramId: program?.id ?? null,
        selectedSceneId: scene?.id ?? null,
        selectedSequenceId: sequence?.id ?? null,
        links: ["tools/codex/runs", "tools/codex/runs/*/C_features"],
        capabilityStatus,
        operatorHud,
        environment: envSummary()
      });

      const blob = new Blob([JSON.stringify(bundle, null, 2)], {
        type: "application/json"
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `pitch-engine-support-${Date.now()}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setUiError(error instanceof Error ? error.message : "Failed to export support bundle");
    }
  };

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-2">
        <p className="keystone-kicker">Support Bundle</p>
        <h2 className="text-lg font-semibold text-slate-100">Diagnostics + artifacts references</h2>
      </header>

      <p className="mb-3 text-xs text-slate-300">
        Exports selected program JSON, scene/sequence diagnostics snapshots, artifact links, last DoD results,
        and environment summary.
      </p>

      <button
        className="rounded bg-indigo-700 px-3 py-1 text-xs font-semibold text-white"
        type="button"
        onClick={onExport}
      >
        Export Bundle JSON
      </button>
    </section>
  );
}
