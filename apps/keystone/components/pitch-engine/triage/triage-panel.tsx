"use client";

import { useMemo, useState } from "react";
import { fetchArtifactRuns, triageAction } from "../api-client";
import { usePitchEngineStore, useSelectedTriageItem } from "../state/use-pitch-engine-store";
import { DiffCanvas } from "./diff-canvas";

export function TriagePanel() {
  const triageRuns = usePitchEngineStore((state) => state.triageRuns);
  const selectedTriageItemId = usePitchEngineStore((state) => state.selectedTriageItemId);
  const setArtifactRuns = usePitchEngineStore((state) => state.setArtifactRuns);
  const selectTriageItem = usePitchEngineStore((state) => state.selectTriageItem);
  const applyTriageResult = usePitchEngineStore((state) => state.applyTriageResult);
  const mergeOperatorHud = usePitchEngineStore((state) => state.mergeOperatorHud);
  const setUiError = usePitchEngineStore((state) => state.setUiError);
  const selectedItem = useSelectedTriageItem();

  const [notes, setNotes] = useState("");
  const [isWorking, setIsWorking] = useState(false);

  const items = useMemo(() => triageRuns.flatMap((run) => run.items), [triageRuns]);

  const runAction = async (action: "accept" | "reject" | "rerun" | "notes") => {
    if (!selectedItem) {
      return;
    }

    try {
      setIsWorking(true);
      const result = await triageAction({
        action,
        runId: selectedItem.runId,
        sceneId: selectedItem.sceneId,
        sequenceId: selectedItem.sequenceId,
        notes: action === "notes" ? notes : undefined
      });

      applyTriageResult(result);
      mergeOperatorHud({
        lastRunStatus: result.ok ? "ok" : "fail",
        lastRunPath: result.command,
        lastErrorTail: result.stderr.length > 0 ? result.stderr : null,
        lastArtifactRunId: selectedItem.runId
      });

      const latest = await fetchArtifactRuns();
      setArtifactRuns(latest);
    } catch (error) {
      setUiError(error instanceof Error ? error.message : `Failed triage action ${action}`);
    } finally {
      setIsWorking(false);
    }
  };

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3">
        <p className="keystone-kicker">Diff Triage</p>
        <h2 className="text-lg font-semibold text-slate-100">Before / after / diff + actions</h2>
      </header>

      <div className="grid gap-3 lg:grid-cols-[2fr,3fr]">
        <div className="rounded border border-slate-800 bg-slate-900/40 p-2">
          <div className="max-h-80 overflow-auto">
            <ul className="m-0 list-none p-0">
              {items.map((item) => (
                <li key={item.id} className="border-b border-slate-800 last:border-b-0">
                  <button
                    type="button"
                    className={`w-full px-2 py-2 text-left ${
                      item.id === selectedTriageItemId
                        ? "bg-cyan-900/40 text-cyan-200"
                        : "text-slate-200 hover:bg-slate-900"
                    }`}
                    onClick={() => {
                      selectTriageItem(item.id);
                    }}
                  >
                    <p className="m-0 text-sm font-semibold">{item.sceneId}</p>
                    <p className="m-0 text-xs text-slate-400">
                      {item.sequenceId} • {item.status} • score {item.score.toFixed(2)}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-3 grid gap-2">
            <textarea
              className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-100"
              rows={5}
              value={notes}
              onChange={(event) => {
                setNotes(event.target.value);
              }}
              placeholder="Edit DIFF_NOTES.md for selected run / scene / sequence"
            />

            <div className="flex flex-wrap gap-2">
              <button
                className="rounded bg-emerald-700 px-3 py-1 text-xs font-semibold text-white"
                type="button"
                onClick={() => {
                  void runAction("accept");
                }}
                disabled={!selectedItem || isWorking}
              >
                Accept
              </button>

              <button
                className="rounded bg-rose-700 px-3 py-1 text-xs font-semibold text-white"
                type="button"
                onClick={() => {
                  void runAction("reject");
                }}
                disabled={!selectedItem || isWorking}
              >
                Reject
              </button>

              <button
                className="rounded bg-indigo-700 px-3 py-1 text-xs font-semibold text-white"
                type="button"
                onClick={() => {
                  void runAction("rerun");
                }}
                disabled={!selectedItem || isWorking}
              >
                Re-run
              </button>

              <button
                className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-100"
                type="button"
                onClick={() => {
                  void runAction("notes");
                }}
                disabled={!selectedItem || isWorking}
              >
                Save Notes
              </button>
            </div>
          </div>
        </div>

        <DiffCanvas item={selectedItem} />
      </div>
    </section>
  );
}
