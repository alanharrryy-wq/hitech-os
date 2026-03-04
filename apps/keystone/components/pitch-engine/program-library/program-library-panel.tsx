"use client";

import { useMemo, useRef, useState } from "react";
import {
  createProgram as createProgramRequest,
  deleteProgram,
  importProgram,
  updateProgram
} from "../api-client";
import { PitchProgramSchema } from "../schemas";
import { usePitchEngineStore } from "../state/use-pitch-engine-store";

export function ProgramLibraryPanel() {
  const programs = usePitchEngineStore((state) => state.library.programs);
  const selectedProgramId = usePitchEngineStore((state) => state.library.selectedProgramId);
  const selectProgram = usePitchEngineStore((state) => state.selectProgram);
  const removeProgramLocal = usePitchEngineStore((state) => state.removeProgram);
  const importProgramLocal = usePitchEngineStore((state) => state.importProgram);
  const replaceProgram = usePitchEngineStore((state) => state.replaceProgram);
  const createProgramLocal = usePitchEngineStore((state) => state.createProgram);
  const setUiError = usePitchEngineStore((state) => state.setUiError);

  const [name, setName] = useState("New Program");
  const [description, setDescription] = useState("Dev-only pitch timeline program");
  const [owner, setOwner] = useState("C_features");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const selectedProgram = useMemo(
    () => programs.find((program) => program.id === selectedProgramId) ?? null,
    [programs, selectedProgramId]
  );

  const onCreate = async () => {
    try {
      const local = createProgramLocal({ name, description, owner });
      const fromServer = await createProgramRequest({ name, description, owner });
      replaceProgram(fromServer);
      selectProgram(fromServer.id);
      if (local.id !== fromServer.id) {
        removeProgramLocal(local.id);
      }
    } catch (error) {
      setUiError(error instanceof Error ? error.message : "Failed to create program");
    }
  };

  const onDelete = async () => {
    if (!selectedProgram) {
      return;
    }

    try {
      await deleteProgram(selectedProgram.id);
      removeProgramLocal(selectedProgram.id);
    } catch (error) {
      setUiError(error instanceof Error ? error.message : "Failed to delete program");
    }
  };

  const onExport = () => {
    if (!selectedProgram) {
      return;
    }

    const blob = new Blob([JSON.stringify(selectedProgram, null, 2)], {
      type: "application/json"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${selectedProgram.id}.program.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const onImportClick = () => {
    fileInputRef.current?.click();
  };

  const onImportFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    if (!file) {
      return;
    }

    try {
      const text = await file.text();
      const json = JSON.parse(text) as unknown;
      const parsed = PitchProgramSchema.parse(json);
      const serverProgram = await importProgram(parsed);
      importProgramLocal(serverProgram);
      selectProgram(serverProgram.id);
    } catch (error) {
      setUiError(error instanceof Error ? error.message : "Failed to import program");
    } finally {
      event.target.value = "";
    }
  };

  const onSaveCurrent = async () => {
    if (!selectedProgram) {
      return;
    }

    try {
      const updated = await updateProgram(selectedProgram.id, selectedProgram);
      replaceProgram(updated);
    } catch (error) {
      setUiError(error instanceof Error ? error.message : "Failed to persist program");
    }
  };

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3 flex items-center justify-between gap-3">
        <div>
          <p className="keystone-kicker">Program Library</p>
          <h2 className="text-lg font-semibold text-slate-100">CRUD + Import / Export</h2>
        </div>
        <div className="flex gap-2">
          <button
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
            type="button"
            onClick={onExport}
          >
            Export
          </button>
          <button
            className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200"
            type="button"
            onClick={onImportClick}
          >
            Import
          </button>
          <input
            ref={fileInputRef}
            className="hidden"
            type="file"
            accept="application/json"
            onChange={onImportFile}
          />
        </div>
      </header>

      <div className="grid gap-3 lg:grid-cols-[2fr,3fr]">
        <div className="max-h-[19rem] overflow-auto rounded border border-slate-800">
          <ul className="m-0 list-none p-0">
            {programs.map((program) => {
              const selected = program.id === selectedProgramId;
              return (
                <li key={program.id} className="border-b border-slate-800 last:border-b-0">
                  <button
                    type="button"
                    className={`w-full px-3 py-2 text-left ${
                      selected ? "bg-cyan-900/40 text-cyan-200" : "text-slate-200 hover:bg-slate-900"
                    }`}
                    onClick={() => {
                      selectProgram(program.id);
                    }}
                  >
                    <p className="m-0 text-sm font-semibold">{program.name}</p>
                    <p className="m-0 text-xs text-slate-400">{program.id}</p>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="grid gap-2">
          <label className="grid gap-1 text-xs text-slate-300">
            Name
            <input
              className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
              value={name}
              onChange={(event) => {
                setName(event.target.value);
              }}
            />
          </label>
          <label className="grid gap-1 text-xs text-slate-300">
            Description
            <textarea
              className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
              rows={3}
              value={description}
              onChange={(event) => {
                setDescription(event.target.value);
              }}
            />
          </label>
          <label className="grid gap-1 text-xs text-slate-300">
            Owner
            <input
              className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
              value={owner}
              onChange={(event) => {
                setOwner(event.target.value);
              }}
            />
          </label>

          <div className="mt-2 flex flex-wrap gap-2">
            <button
              className="rounded bg-cyan-700 px-3 py-1 text-xs font-semibold text-white"
              type="button"
              onClick={onCreate}
            >
              Create
            </button>
            <button
              className="rounded bg-slate-700 px-3 py-1 text-xs font-semibold text-slate-100"
              type="button"
              onClick={onSaveCurrent}
            >
              Save Current
            </button>
            <button
              className="rounded bg-rose-700 px-3 py-1 text-xs font-semibold text-white"
              type="button"
              onClick={onDelete}
              disabled={!selectedProgram}
            >
              Delete Selected
            </button>
          </div>

          {selectedProgram ? (
            <div className="mt-2 rounded border border-slate-800 p-2 text-xs text-slate-300">
              <p className="m-0">Scenes: {selectedProgram.scenes.length}</p>
              <p className="m-0">Sequences: {selectedProgram.sequences.length}</p>
              <p className="m-0">Version: {selectedProgram.version}</p>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
