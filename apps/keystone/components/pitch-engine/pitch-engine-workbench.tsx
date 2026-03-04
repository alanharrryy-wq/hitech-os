"use client";

import { useMemo, useState } from "react";
import { usePitchEngineBootstrap } from "./hooks/use-pitch-engine-bootstrap";
import { useTransportTicker } from "./hooks/use-transport-ticker";
import { ProgramLibraryPanel } from "./program-library/program-library-panel";
import { SceneRecorderPanel } from "./recorder/scene-recorder-panel";
import { DirectorControlsPanel } from "./director/director-controls-panel";
import { OperatorStatusHud } from "./hud/operator-status-hud";
import { SupportBundlePanel } from "./support/support-bundle-panel";
import { TimelineEditorPanel } from "./timeline/timeline-editor-panel";
import { TimelinePreviewPanel } from "./timeline/timeline-preview-panel";
import { ReplayTransportPanel } from "./timeline/replay-transport-panel";
import { TriagePanel } from "./triage/triage-panel";
import { CapabilityPanel } from "./capability-panel";
import { usePitchEngineStore } from "./state/use-pitch-engine-store";
import type { CapabilityMode } from "./types";

interface PitchEngineWorkbenchProps {
  readonly requestedMode: CapabilityMode;
}

export function PitchEngineWorkbench({ requestedMode }: PitchEngineWorkbenchProps) {
  const [activeTab, setActiveTab] = useState<"studio" | "triage">("studio");
  const uiError = usePitchEngineStore((state) => state.uiError);

  usePitchEngineBootstrap(requestedMode);
  useTransportTicker();

  const title = useMemo(
    () =>
      activeTab === "studio"
        ? "Pitch Engine Studio"
        : "Pitch Engine Diff Triage",
    [activeTab]
  );

  return (
    <div className="mx-auto min-h-screen w-full max-w-[1500px] px-4 py-6 text-slate-100">
      <header className="mb-4 rounded-lg border border-slate-700 bg-slate-950/40 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="keystone-kicker">/dev/pitch-engine?debug=1</p>
            <h1 className="text-2xl font-semibold text-slate-100">{title}</h1>
            <p className="m-0 text-xs text-slate-400">
              Dev-only operator UX: timeline authoring, recorder, triage, and support diagnostics.
            </p>
          </div>

          <div className="flex gap-2">
            <button
              className={`rounded px-3 py-1 text-xs font-semibold ${
                activeTab === "studio" ? "bg-cyan-700 text-white" : "bg-slate-800 text-slate-300"
              }`}
              type="button"
              onClick={() => {
                setActiveTab("studio");
              }}
            >
              Studio
            </button>
            <button
              className={`rounded px-3 py-1 text-xs font-semibold ${
                activeTab === "triage" ? "bg-cyan-700 text-white" : "bg-slate-800 text-slate-300"
              }`}
              type="button"
              onClick={() => {
                setActiveTab("triage");
              }}
            >
              Triage
            </button>
          </div>
        </div>
      </header>

      {uiError ? (
        <div className="mb-4 rounded border border-rose-700 bg-rose-950/40 px-3 py-2 text-xs text-rose-200">
          {uiError}
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[3fr,1fr]">
        <main className="grid gap-4">
          <CapabilityPanel />
          <ProgramLibraryPanel />

          {activeTab === "studio" ? (
            <>
              <DirectorControlsPanel />
              <TimelineEditorPanel />
              <ReplayTransportPanel />
              <TimelinePreviewPanel />
              <SceneRecorderPanel />
            </>
          ) : (
            <TriagePanel />
          )}
        </main>

        <aside className="grid gap-4">
          <OperatorStatusHud />
          <SupportBundlePanel />
        </aside>
      </div>
    </div>
  );
}
