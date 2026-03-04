"use client";

import { useMemo } from "react";
import { usePitchEngineStore } from "../state/use-pitch-engine-store";
import type { ArtifactTriageItem } from "../types";

interface DiffCanvasProps {
  readonly item: ArtifactTriageItem | null;
}

export function DiffCanvas({ item }: DiffCanvasProps) {
  const wipePercent = usePitchEngineStore((state) => state.timelineWipePercent);
  const setWipePercent = usePitchEngineStore((state) => state.setTimelineWipePercent);
  const zoom = usePitchEngineStore((state) => state.timelineZoom);
  const setZoom = usePitchEngineStore((state) => state.setTimelineZoom);
  const pan = usePitchEngineStore((state) => state.timelinePan);
  const setPan = usePitchEngineStore((state) => state.setTimelinePan);

  const transform = useMemo(() => `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, [pan.x, pan.y, zoom]);

  if (!item) {
    return (
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-300">
        Select a triage item to inspect before/after/diff frames.
      </div>
    );
  }

  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
      <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-300">
        <span>{item.sceneId}</span>
        <span>•</span>
        <span>{item.sequenceId}</span>
        <span>•</span>
        <span>status: {item.status}</span>
      </div>

      <div className="relative h-72 overflow-hidden rounded border border-slate-700 bg-slate-950">
        <div className="absolute inset-0" style={{ transform, transformOrigin: "center center" }}>
          {item.diff.beforePath ? (
            <img
              src={item.diff.beforePath}
              alt="Before"
              className="absolute inset-0 h-full w-full object-cover opacity-80"
            />
          ) : (
            <div className="absolute inset-0 grid place-items-center text-xs text-slate-400">No before frame</div>
          )}

          <div className="absolute inset-0 overflow-hidden" style={{ width: `${wipePercent}%` }}>
            {item.diff.afterPath ? (
              <img src={item.diff.afterPath} alt="After" className="h-full w-full object-cover" />
            ) : (
              <div className="grid h-full place-items-center text-xs text-slate-400">No after frame</div>
            )}
          </div>

          {item.diff.diffPath ? (
            <img
              src={item.diff.diffPath}
              alt="Diff"
              className="pointer-events-none absolute bottom-2 right-2 h-16 w-16 rounded border border-slate-700"
            />
          ) : null}
        </div>
      </div>

      <div className="mt-3 grid gap-2 md:grid-cols-3">
        <label className="grid gap-1 text-xs text-slate-300">
          Wipe
          <input
            type="range"
            min={0}
            max={100}
            value={wipePercent}
            onChange={(event) => {
              setWipePercent(Number(event.target.value));
            }}
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Zoom
          <input
            type="range"
            min={0.5}
            max={4}
            step={0.1}
            value={zoom}
            onChange={(event) => {
              setZoom(Number(event.target.value));
            }}
          />
        </label>

        <div className="flex items-end gap-2">
          <button
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
            type="button"
            onClick={() => {
              setPan({ x: pan.x - 20, y: pan.y });
            }}
          >
            ←
          </button>
          <button
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
            type="button"
            onClick={() => {
              setPan({ x: pan.x + 20, y: pan.y });
            }}
          >
            →
          </button>
          <button
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
            type="button"
            onClick={() => {
              setPan({ x: pan.x, y: pan.y - 20 });
            }}
          >
            ↑
          </button>
          <button
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
            type="button"
            onClick={() => {
              setPan({ x: pan.x, y: pan.y + 20 });
            }}
          >
            ↓
          </button>
        </div>
      </div>
    </div>
  );
}
