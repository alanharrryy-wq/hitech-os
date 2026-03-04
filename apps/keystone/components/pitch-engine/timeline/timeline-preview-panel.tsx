"use client";

import { useMemo } from "react";
import { usePitchEngineStore, useSelectedSequence } from "../state/use-pitch-engine-store";

function getMarkerLabel(sequenceId: string, markerId: string | null, markers: { id: string; label: string }[]): string {
  if (!markerId) {
    return `${sequenceId}:none`;
  }

  const marker = markers.find((item) => item.id === markerId);
  return marker ? `${sequenceId}:${marker.label}` : `${sequenceId}:unknown`;
}

export function TimelinePreviewPanel() {
  const sequence = useSelectedSequence();
  const transport = usePitchEngineStore((state) => state.transport);
  const reducedMotionApplied = usePitchEngineStore((state) => state.reducedMotionApplied);

  const progress = useMemo(() => {
    if (!sequence || transport.durationMs <= 0) {
      return 0;
    }

    return Math.min(100, Math.max(0, (transport.currentMs / transport.durationMs) * 100));
  }, [sequence, transport.currentMs, transport.durationMs]);

  if (!sequence) {
    return (
      <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
        <p className="m-0 text-sm text-slate-300">No sequence selected for preview.</p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-2">
        <p className="keystone-kicker">Live Preview</p>
        <h2 className="text-lg font-semibold text-slate-100">Timeline playback state</h2>
      </header>

      {reducedMotionApplied ? (
        <div className="mb-2 rounded border border-amber-600 bg-amber-900/30 px-2 py-1 text-xs text-amber-200">
          Reduced motion applied: preview jumps to final keyframe.
        </div>
      ) : null}

      <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
        <div className="mb-2 flex items-center justify-between text-xs text-slate-300">
          <span>{sequence.name}</span>
          <span>{Math.round(progress)}%</span>
        </div>

        <div className="h-5 w-full overflow-hidden rounded bg-slate-900">
          <div className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500" style={{ width: `${progress}%` }} />
        </div>

        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {sequence.timeline.markers.map((marker) => (
            <div key={marker.id} className="rounded border border-slate-800 p-2 text-xs text-slate-300">
              <p className="m-0 font-semibold text-slate-100">{marker.label}</p>
              <p className="m-0">{marker.type}</p>
              <p className="m-0">{Math.round(marker.t)}ms</p>
            </div>
          ))}
        </div>

        <p className="mt-3 text-xs text-slate-400">
          marker-jump: {getMarkerLabel(sequence.id, transport.markerJumpId, sequence.timeline.markers)}
        </p>
      </div>
    </section>
  );
}
