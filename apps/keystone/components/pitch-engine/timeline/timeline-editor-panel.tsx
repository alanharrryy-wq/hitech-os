"use client";

import { useMemo, useState } from "react";
import { usePitchEngineStore, useSelectedProgram, useSelectedSequence } from "../state/use-pitch-engine-store";

export function TimelineEditorPanel() {
  const program = useSelectedProgram();
  const sequence = useSelectedSequence();
  const selectScene = usePitchEngineStore((state) => state.selectScene);
  const selectSequence = usePitchEngineStore((state) => state.selectSequence);
  const updateTrack = usePitchEngineStore((state) => state.updateTrack);
  const addMarker = usePitchEngineStore((state) => state.addMarker);
  const removeMarker = usePitchEngineStore((state) => state.removeMarker);

  const [markerLabel, setMarkerLabel] = useState("Reveal");
  const [markerType, setMarkerType] = useState<"Reveal" | "Settle" | "CTA">("Reveal");
  const [markerMs, setMarkerMs] = useState("1200");
  const [markerNote, setMarkerNote] = useState("Auto marker");

  const sceneSequences = useMemo(() => {
    if (!program || !sequence) {
      return [];
    }

    return program.sequences.filter((item) => item.sceneId === sequence.sceneId);
  }, [program, sequence]);

  if (!program || !sequence) {
    return (
      <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
        <p className="m-0 text-sm text-slate-300">Select a program and sequence to edit timeline tracks.</p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3">
        <p className="keystone-kicker">Timeline Editor</p>
        <h2 className="text-lg font-semibold text-slate-100">Steps, transitions, markers</h2>
      </header>

      <div className="mb-3 grid gap-2 md:grid-cols-2">
        <label className="grid gap-1 text-xs text-slate-300">
          Scene
          <select
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={sequence.sceneId}
            onChange={(event) => {
              selectScene(event.target.value);
            }}
          >
            {program.scenes.map((scene) => (
              <option key={scene.id} value={scene.id}>
                {scene.name}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Sequence
          <select
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={sequence.id}
            onChange={(event) => {
              selectSequence(event.target.value);
            }}
          >
            {sceneSequences.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid gap-3 lg:grid-cols-[3fr,2fr]">
        <div className="space-y-3">
          {sequence.timeline.tracks.map((track) => (
            <div key={track.id} className="rounded border border-slate-800 bg-slate-900/40 p-3">
              <div className="mb-2 flex items-center justify-between">
                <p className="m-0 text-sm font-semibold text-slate-100">{track.label}</p>
                <label className="flex items-center gap-1 text-xs text-slate-300">
                  <input
                    checked={track.enabled}
                    type="checkbox"
                    onChange={(event) => {
                      updateTrack(sequence.id, track.id, (current) => ({
                        ...current,
                        enabled: event.target.checked
                      }));
                    }}
                  />
                  Enabled
                </label>
              </div>

              <div className="max-h-44 overflow-auto rounded border border-slate-800">
                <table className="min-w-full text-xs text-slate-200">
                  <thead className="bg-slate-900 text-slate-400">
                    <tr>
                      <th className="px-2 py-1 text-left">t (ms)</th>
                      <th className="px-2 py-1 text-left">easing</th>
                      <th className="px-2 py-1 text-left">values</th>
                    </tr>
                  </thead>
                  <tbody>
                    {track.keyframes.map((keyframe) => (
                      <tr key={keyframe.id} className="border-t border-slate-800">
                        <td className="px-2 py-1">{Math.round(keyframe.t)}</td>
                        <td className="px-2 py-1">{keyframe.easing}</td>
                        <td className="px-2 py-1">
                          {keyframe.values.map((value) => `${value.key}:${String(value.value)}`).join(" · ")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>

        <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
          <p className="m-0 text-sm font-semibold text-slate-100">Marker Editor</p>
          <p className="mt-1 text-xs text-slate-400">Create Reveal / Settle / CTA markers and adjust playback anchors.</p>

          <div className="mt-3 grid gap-2">
            <label className="grid gap-1 text-xs text-slate-300">
              Type
              <select
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                value={markerType}
                onChange={(event) => {
                  setMarkerType(event.target.value as "Reveal" | "Settle" | "CTA");
                }}
              >
                <option value="Reveal">Reveal</option>
                <option value="Settle">Settle</option>
                <option value="CTA">CTA</option>
              </select>
            </label>

            <label className="grid gap-1 text-xs text-slate-300">
              Label
              <input
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                value={markerLabel}
                onChange={(event) => {
                  setMarkerLabel(event.target.value);
                }}
              />
            </label>

            <label className="grid gap-1 text-xs text-slate-300">
              Time (ms)
              <input
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                value={markerMs}
                onChange={(event) => {
                  setMarkerMs(event.target.value);
                }}
              />
            </label>

            <label className="grid gap-1 text-xs text-slate-300">
              Note
              <textarea
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                rows={2}
                value={markerNote}
                onChange={(event) => {
                  setMarkerNote(event.target.value);
                }}
              />
            </label>

            <button
              className="rounded bg-cyan-700 px-3 py-1 text-xs font-semibold text-white"
              type="button"
              onClick={() => {
                const t = Number(markerMs);
                if (Number.isNaN(t)) {
                  return;
                }

                addMarker(sequence.id, {
                  type: markerType,
                  label: markerLabel,
                  t,
                  note: markerNote
                });
              }}
            >
              Add Marker
            </button>
          </div>

          <div className="mt-3 max-h-56 overflow-auto rounded border border-slate-800">
            <table className="min-w-full text-xs text-slate-200">
              <thead className="bg-slate-900 text-slate-400">
                <tr>
                  <th className="px-2 py-1 text-left">type</th>
                  <th className="px-2 py-1 text-left">label</th>
                  <th className="px-2 py-1 text-left">ms</th>
                  <th className="px-2 py-1 text-left">action</th>
                </tr>
              </thead>
              <tbody>
                {sequence.timeline.markers.map((marker) => (
                  <tr key={marker.id} className="border-t border-slate-800">
                    <td className="px-2 py-1">{marker.type}</td>
                    <td className="px-2 py-1">{marker.label}</td>
                    <td className="px-2 py-1">{Math.round(marker.t)}</td>
                    <td className="px-2 py-1">
                      <button
                        className="rounded border border-rose-600 px-2 py-0.5 text-[11px] text-rose-300"
                        type="button"
                        onClick={() => {
                          removeMarker(sequence.id, marker.id);
                        }}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
