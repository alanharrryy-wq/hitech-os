"use client";

import { useMemo } from "react";
import { usePitchEngineStore, useSelectedSequence } from "../state/use-pitch-engine-store";

function formatMs(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const centiseconds = Math.floor((ms % 1000) / 10);
  return `${seconds.toString().padStart(2, "0")}.${centiseconds.toString().padStart(2, "0")}`;
}

export function ReplayTransportPanel() {
  const sequence = useSelectedSequence();
  const transport = usePitchEngineStore((state) => state.transport);
  const setTransportPlaying = usePitchEngineStore((state) => state.setTransportPlaying);
  const setTransportLooping = usePitchEngineStore((state) => state.setTransportLooping);
  const setTransportMs = usePitchEngineStore((state) => state.setTransportMs);
  const jumpToMarker = usePitchEngineStore((state) => state.jumpToMarker);
  const setTransportRate = usePitchEngineStore((state) => state.setTransportRate);

  const markerButtons = useMemo(() => sequence?.timeline.markers ?? [], [sequence]);

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3">
        <p className="keystone-kicker">Replay Transport</p>
        <h2 className="text-lg font-semibold text-slate-100">Play, pause, scrub, loop, jump-to-markers</h2>
      </header>

      <div className="grid gap-3 lg:grid-cols-[3fr,2fr]">
        <div>
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <button
              className="rounded bg-cyan-700 px-3 py-1 text-xs font-semibold text-white"
              type="button"
              onClick={() => {
                setTransportPlaying(!transport.isPlaying);
              }}
            >
              {transport.isPlaying ? "Pause" : "Play"}
            </button>
            <button
              className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200"
              type="button"
              onClick={() => {
                setTransportLooping(!transport.isLooping);
              }}
            >
              Loop: {transport.isLooping ? "ON" : "OFF"}
            </button>

            <label className="flex items-center gap-1 text-xs text-slate-300">
              Speed
              <select
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-100"
                value={String(transport.playbackRate)}
                onChange={(event) => {
                  setTransportRate(Number(event.target.value) as 0.5 | 1 | 1.25 | 1.5 | 2);
                }}
              >
                <option value="0.5">0.5x</option>
                <option value="1">1.0x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
                <option value="2">2.0x</option>
              </select>
            </label>
          </div>

          <input
            className="w-full"
            type="range"
            min={0}
            max={Math.max(transport.durationMs, 1)}
            value={Math.min(transport.currentMs, transport.durationMs)}
            onChange={(event) => {
              setTransportMs(Number(event.target.value));
            }}
          />

          <p className="mt-2 text-xs text-slate-300">
            {formatMs(transport.currentMs)} / {formatMs(transport.durationMs)}
          </p>
        </div>

        <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
          <p className="m-0 text-xs font-semibold text-slate-200">Jump To Marker</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {markerButtons.map((marker) => (
              <button
                key={marker.id}
                className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
                type="button"
                onClick={() => {
                  jumpToMarker(marker.id);
                }}
              >
                {marker.type} · {Math.round(marker.t)}ms
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
