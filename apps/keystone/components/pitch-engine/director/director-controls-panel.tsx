"use client";

import { useState } from "react";
import { usePitchEngineStore, useSelectedProgram, useSelectedScene } from "../state/use-pitch-engine-store";
import { TIMELINE_PRESET_SCRIPTS } from "../timeline/preset-scripts";

export function DirectorControlsPanel() {
  const program = useSelectedProgram();
  const scene = useSelectedScene();
  const createSequence = usePitchEngineStore((state) => state.createSequence);
  const selectSequence = usePitchEngineStore((state) => state.selectSequence);
  const sequenceId = usePitchEngineStore((state) => state.library.selectedSequenceId);

  const [sequenceName, setSequenceName] = useState("New Sequence");
  const [sequenceDescription, setSequenceDescription] = useState("Generated from cinematic preset script");
  const [presetId, setPresetId] = useState(TIMELINE_PRESET_SCRIPTS[0]?.id ?? "preset-01-01");

  if (!program || !scene) {
    return (
      <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
        <p className="m-0 text-sm text-slate-300">Select a scene to manage director controls.</p>
      </section>
    );
  }

  const sceneSequences = program.sequences.filter((item) => item.sceneId === scene.id);

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3">
        <p className="keystone-kicker">Director Controls</p>
        <h2 className="text-lg font-semibold text-slate-100">Sequence creation, selection, preset injection</h2>
      </header>

      <div className="grid gap-3 lg:grid-cols-[3fr,2fr]">
        <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
          <p className="m-0 text-sm font-semibold text-slate-200">Scene Sequences</p>
          <div className="mt-2 max-h-52 overflow-auto rounded border border-slate-800">
            <ul className="m-0 list-none p-0">
              {sceneSequences.map((sequence) => {
                const selected = sequence.id === sequenceId;
                return (
                  <li key={sequence.id} className="border-b border-slate-800 last:border-b-0">
                    <button
                      type="button"
                      className={`w-full px-2 py-2 text-left ${
                        selected ? "bg-cyan-900/40 text-cyan-200" : "text-slate-200 hover:bg-slate-900"
                      }`}
                      onClick={() => {
                        selectSequence(sequence.id);
                      }}
                    >
                      <p className="m-0 text-sm font-semibold">{sequence.name}</p>
                      <p className="m-0 text-xs text-slate-400">{sequence.cinematicPresetId}</p>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
          <p className="m-0 text-sm font-semibold text-slate-200">Inject Preset Script</p>
          <p className="mt-1 text-xs text-slate-400">
            Sequence = base scene + timeline DSL. Preset scripts inject tracks + marker templates.
          </p>

          <div className="mt-3 grid gap-2">
            <label className="grid gap-1 text-xs text-slate-300">
              Sequence Name
              <input
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                value={sequenceName}
                onChange={(event) => {
                  setSequenceName(event.target.value);
                }}
              />
            </label>

            <label className="grid gap-1 text-xs text-slate-300">
              Description
              <textarea
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                rows={3}
                value={sequenceDescription}
                onChange={(event) => {
                  setSequenceDescription(event.target.value);
                }}
              />
            </label>

            <label className="grid gap-1 text-xs text-slate-300">
              Cinematic Preset Script
              <select
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
                value={presetId}
                onChange={(event) => {
                  setPresetId(event.target.value);
                }}
              >
                {TIMELINE_PRESET_SCRIPTS.map((preset) => (
                  <option key={preset.id} value={preset.id}>
                    {preset.label} ({preset.style})
                  </option>
                ))}
              </select>
            </label>

            <button
              className="rounded bg-emerald-700 px-3 py-1 text-xs font-semibold text-white"
              type="button"
              onClick={() => {
                createSequence({
                  baseSceneId: scene.id,
                  name: sequenceName,
                  description: sequenceDescription,
                  presetId
                });
              }}
            >
              Create Sequence From Preset
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
