"use client";

import { useMemo, useState } from "react";
import { TIMELINE_PRESET_SCRIPTS } from "./preset-scripts";
import { usePitchEngineStore, useSelectedProgram } from "../state/use-pitch-engine-store";
import type { SceneStudioSceneRef } from "../types";

interface SceneStudioTimelineTabProps {
  readonly scenes: SceneStudioSceneRef[];
}

export function SceneStudioTimelineTab({ scenes }: SceneStudioTimelineTabProps) {
  const program = useSelectedProgram();
  const library = usePitchEngineStore((state) => state.library);
  const selectProgram = usePitchEngineStore((state) => state.selectProgram);
  const selectScene = usePitchEngineStore((state) => state.selectScene);
  const createSequence = usePitchEngineStore((state) => state.createSequence);
  const selectSequence = usePitchEngineStore((state) => state.selectSequence);
  const transport = usePitchEngineStore((state) => state.transport);
  const setTransportMs = usePitchEngineStore((state) => state.setTransportMs);
  const setTransportPlaying = usePitchEngineStore((state) => state.setTransportPlaying);

  const [presetId, setPresetId] = useState(TIMELINE_PRESET_SCRIPTS[0]?.id ?? "preset-01-01");

  const selectedSceneRef = useMemo(
    () => scenes.find((scene) => scene.id === library.selectedSceneId) ?? scenes[0] ?? null,
    [library.selectedSceneId, scenes]
  );

  const sceneSequence = useMemo(() => {
    if (!program || !selectedSceneRef) {
      return null;
    }

    return (
      program.sequences.find((sequence) => sequence.sceneId === selectedSceneRef.id) ??
      program.sequences[0] ??
      null
    );
  }, [program, selectedSceneRef]);

  const injectPreset = () => {
    if (!selectedSceneRef) {
      return;
    }

    createSequence({
      baseSceneId: selectedSceneRef.id,
      name: `${selectedSceneRef.name} · ${presetId}`,
      description: `Injected from Scene Studio timeline tab preset ${presetId}`,
      presetId
    });

    if (sceneSequence) {
      selectSequence(sceneSequence.id);
    }
  };

  return (
    <div className="grid gap-3">
      <div className="grid gap-2 md:grid-cols-3">
        <label className="grid gap-1 text-xs text-slate-300">
          Program
          <select
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={library.selectedProgramId ?? ""}
            onChange={(event) => {
              if (event.target.value) {
                selectProgram(event.target.value);
              }
            }}
          >
            {library.programs.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Scene (from Scene Studio)
          <select
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={selectedSceneRef?.id ?? ""}
            onChange={(event) => {
              selectScene(event.target.value);
            }}
          >
            {scenes.map((scene) => (
              <option key={scene.id} value={scene.id}>
                {scene.name}
              </option>
            ))}
          </select>
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
                {preset.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          className="rounded bg-emerald-700 px-3 py-1 text-xs font-semibold text-white"
          type="button"
          onClick={injectPreset}
          disabled={!selectedSceneRef}
        >
          Apply Preset Script
        </button>

        <button
          className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-200"
          type="button"
          onClick={() => {
            setTransportPlaying(!transport.isPlaying);
          }}
        >
          {transport.isPlaying ? "Pause Live Preview" : "Play Live Preview"}
        </button>
      </div>

      <div className="rounded border border-slate-800 bg-slate-900/40 p-3">
        <p className="m-0 text-sm font-semibold text-slate-100">Live timeline scrub</p>
        <p className="m-0 text-xs text-slate-400">
          Scrub applies immediately to the selected sequence for in-studio preview.
        </p>

        <input
          className="mt-2 w-full"
          type="range"
          min={0}
          max={Math.max(transport.durationMs, 1)}
          value={Math.min(transport.currentMs, transport.durationMs)}
          onChange={(event) => {
            setTransportMs(Number(event.target.value));
          }}
        />

        <p className="mt-2 text-xs text-slate-300">
          scene: {selectedSceneRef?.name ?? "none"} · sequence: {sceneSequence?.name ?? "none"} · {Math.round(transport.currentMs)}ms
        </p>
      </div>
    </div>
  );
}
